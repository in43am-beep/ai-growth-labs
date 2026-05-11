"""AI Growth Labs — Agency Operating System Dashboard v2"""
import os
import json
import secrets
import io
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt
from passlib.hash import bcrypt

from database import get_db, init_db

app = FastAPI(title="AI Growth Labs OS", docs_url=None, redoc_url=None)

SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
TOKEN_EXPIRE = 24

static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

@app.on_event("startup")
def startup():
    init_db()

# ===== AUTH =====
def create_token(user_id: int, role: str, username: str):
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE)
    return jwt.encode({"sub": str(user_id), "role": role, "username": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request):
    token = request.cookies.get("token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id=? AND is_active=1", (payload["sub"],)).fetchone()
        db.close()
        return dict(user) if user else None
    except Exception:
        return None

def require_auth(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user

def require_role(request: Request, roles: list):
    user = require_auth(request)
    if user["role"] not in roles:
        raise HTTPException(status_code=403, detail="Access denied")
    return user

# ===== LOGIN =====
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=? AND is_active=1", (username,)).fetchone()
    db.close()
    if not user or not bcrypt.verify(password, user["password_hash"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    token = create_token(user["id"], user["role"], user["username"])
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie("token", token, httponly=True, max_age=TOKEN_EXPIRE*3600)
    db = get_db()
    db.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user["id"],))
    db.commit()
    db.close()
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("token")
    return response

# ===== DASHBOARD ROUTER =====
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    role = user["role"]
    db = get_db()
    if role == "super_admin":
        data = _get_admin_data(db)
        template = "admin_dashboard.html"
    elif role in ("worker", "tech_seo"):
        data = _get_worker_data(db, user["id"])
        template = "worker_dashboard.html"
    elif role == "sales":
        data = _get_sales_data(db, user["id"])
        template = "sales_dashboard.html"
    elif role == "social_media":
        data = _get_social_data(db, user["id"])
        template = "social_dashboard.html"
    elif role == "finance":
        data = _get_finance_data(db)
        template = "finance_dashboard.html"
    else:
        data = {}
        template = "worker_dashboard.html"
    db.close()
    data["user"] = user
    data["request"] = request
    return templates.TemplateResponse(template, data)

# ===== SETTINGS PAGE =====
@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    user = get_current_user(request)
    if not user or user["role"] != "super_admin":
        return RedirectResponse(url="/login")
    db = get_db()
    api_settings = [dict(r) for r in db.execute("SELECT * FROM api_settings ORDER BY provider").fetchall()]
    db.close()
    return templates.TemplateResponse("settings.html", {"request": request, "user": user, "api_settings": api_settings})

# ===== CLIENT DETAIL PAGE =====
@app.get("/client/{client_id}", response_class=HTMLResponse)
async def client_detail(client_id: int, request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    if not client:
        db.close()
        raise HTTPException(status_code=404, detail="Client not found")
    client = dict(client)
    credentials = [dict(r) for r in db.execute("SELECT * FROM client_credentials WHERE client_id=?", (client_id,)).fetchall()]
    projects = [dict(r) for r in db.execute("""
        SELECT p.*, u.full_name as worker_name, tl.full_name as leader_name
        FROM projects p LEFT JOIN users u ON p.assigned_worker_id=u.id LEFT JOIN users tl ON p.team_leader_id=tl.id
        WHERE p.client_id=? ORDER BY p.created_at DESC
    """, (client_id,)).fetchall()]
    tasks_by_project = {}
    for p in projects:
        tasks_by_project[p["id"]] = [dict(r) for r in db.execute("""
            SELECT t.*, u.full_name as assigned_name FROM tasks t LEFT JOIN users u ON t.assigned_to=u.id
            WHERE t.project_id=? ORDER BY t.order_num
        """, (p["id"],)).fetchall()]
    payments = [dict(r) for r in db.execute("SELECT * FROM payments WHERE client_id=? ORDER BY created_at DESC", (client_id,)).fetchall()]
    reports = [dict(r) for r in db.execute("SELECT * FROM client_reports WHERE client_id=? ORDER BY created_at DESC", (client_id,)).fetchall()]
    package_tasks = []
    if client.get("package"):
        package_tasks = [dict(r) for r in db.execute("SELECT * FROM package_tasks WHERE package=? ORDER BY category, order_num", (client["package"],)).fetchall()]
    db.close()
    return templates.TemplateResponse("client_detail.html", {
        "request": request, "user": user, "client": client, "credentials": credentials,
        "projects": projects, "tasks_by_project": tasks_by_project, "payments": payments,
        "reports": reports, "package_tasks": package_tasks
    })

# ===== TEAM MONITOR PAGE (Admin) =====
@app.get("/monitor", response_class=HTMLResponse)
async def monitor_page(request: Request):
    user = get_current_user(request)
    if not user or user["role"] != "super_admin":
        return RedirectResponse(url="/login")
    db = get_db()
    workers = [dict(r) for r in db.execute("SELECT * FROM users WHERE role != 'super_admin' AND is_active=1 ORDER BY role, full_name").fetchall()]
    for w in workers:
        w["active_tasks"] = db.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=? AND status='in_progress'", (w["id"],)).fetchone()[0]
        w["pending_tasks"] = db.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=? AND status='pending'", (w["id"],)).fetchone()[0]
        w["completed_tasks"] = db.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=? AND status='completed'", (w["id"],)).fetchone()[0]
        w["total_tasks"] = w["active_tasks"] + w["pending_tasks"] + w["completed_tasks"]
        w["projects"] = [dict(r) for r in db.execute("""
            SELECT p.title, p.progress, p.status, c.business_name FROM projects p 
            LEFT JOIN clients c ON p.client_id=c.id WHERE p.assigned_worker_id=? OR p.team_leader_id=?
        """, (w["id"], w["id"])).fetchall()]
    suggestions = [dict(r) for r in db.execute("""
        SELECT s.*, u.full_name as author_name, p.title as project_title 
        FROM suggestions s LEFT JOIN users u ON s.user_id=u.id LEFT JOIN projects p ON s.project_id=p.id
        ORDER BY s.created_at DESC LIMIT 20
    """).fetchall()]
    chat_requests = [dict(r) for r in db.execute("""
        SELECT cr.*, u.full_name as from_name FROM chat_requests cr 
        LEFT JOIN users u ON cr.from_user_id=u.id WHERE cr.status='pending' ORDER BY cr.created_at DESC
    """).fetchall()]
    db.close()
    return templates.TemplateResponse("monitor.html", {
        "request": request, "user": user, "workers": workers, 
        "suggestions": suggestions, "chat_requests": chat_requests
    })

# ===== CHAT PAGE =====
@app.get("/team-chat", response_class=HTMLResponse)
async def team_chat_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    db = get_db()
    team_members = [dict(r) for r in db.execute("SELECT id, full_name, role, username FROM users WHERE id!=? AND is_active=1 ORDER BY full_name", (user["id"],)).fetchall()]
    # Get approved chat sessions
    approved = [dict(r) for r in db.execute("""
        SELECT cr.*, u1.full_name as from_name, u2.full_name as to_name 
        FROM chat_requests cr 
        LEFT JOIN users u1 ON cr.from_user_id=u1.id LEFT JOIN users u2 ON cr.to_user_id=u2.id
        WHERE cr.status='approved' AND (cr.from_user_id=? OR cr.to_user_id=?)
    """, (user["id"], user["id"])).fetchall()]
    db.close()
    return templates.TemplateResponse("team_chat.html", {
        "request": request, "user": user, "team_members": team_members, "approved_chats": approved
    })

# ===== DATA HELPERS =====
def _get_admin_data(db):
    clients = [dict(r) for r in db.execute("SELECT * FROM clients ORDER BY created_at DESC").fetchall()]
    projects = [dict(r) for r in db.execute("""
        SELECT p.*, c.business_name, c.contact_name, u.full_name as worker_name, tl.full_name as leader_name
        FROM projects p LEFT JOIN clients c ON p.client_id=c.id 
        LEFT JOIN users u ON p.assigned_worker_id=u.id LEFT JOIN users tl ON p.team_leader_id=tl.id
        ORDER BY p.created_at DESC
    """).fetchall()]
    workers = [dict(r) for r in db.execute("SELECT * FROM users WHERE role != 'super_admin' ORDER BY role, full_name").fetchall()]
    tasks = [dict(r) for r in db.execute("""
        SELECT t.*, u.full_name as assigned_name, p.title as project_title
        FROM tasks t LEFT JOIN users u ON t.assigned_to=u.id LEFT JOIN projects p ON t.project_id=p.id
        ORDER BY t.created_at DESC LIMIT 50
    """).fetchall()]
    payments = [dict(r) for r in db.execute("""
        SELECT pay.*, c.business_name FROM payments pay LEFT JOIN clients c ON pay.client_id=c.id ORDER BY pay.created_at DESC
    """).fetchall()]
    suggestions = [dict(r) for r in db.execute("""
        SELECT s.*, u.full_name as author_name, p.title as project_title
        FROM suggestions s LEFT JOIN users u ON s.user_id=u.id LEFT JOIN projects p ON s.project_id=p.id
        ORDER BY s.created_at DESC LIMIT 10
    """).fetchall()]
    chat_requests = [dict(r) for r in db.execute("""
        SELECT cr.*, u.full_name as from_name FROM chat_requests cr 
        LEFT JOIN users u ON cr.from_user_id=u.id WHERE cr.status='pending' ORDER BY cr.created_at DESC
    """).fetchall()]
    unread_chats = db.execute("SELECT COUNT(*) FROM team_chats WHERE to_user_id=1 AND is_read=0").fetchone()[0]
    
    total_revenue = db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='paid'").fetchone()[0]
    pending_revenue = db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status IN ('pending','overdue')").fetchone()[0]
    active_clients = db.execute("SELECT COUNT(*) FROM clients WHERE status='active'").fetchone()[0]
    active_projects = db.execute("SELECT COUNT(*) FROM projects WHERE status='in_progress'").fetchone()[0]
    total_tasks = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'").fetchone()[0]
    
    return {
        "clients": clients, "projects": projects, "workers": workers, "tasks": tasks, "payments": payments,
        "suggestions": suggestions, "chat_requests": chat_requests, "unread_chats": unread_chats,
        "stats": {
            "total_revenue": total_revenue, "pending_revenue": pending_revenue,
            "active_clients": active_clients, "active_projects": active_projects,
            "total_tasks": total_tasks, "completed_tasks": completed_tasks,
            "task_completion": round(completed_tasks/total_tasks*100) if total_tasks else 0,
            "monthly_recurring": db.execute("SELECT COALESCE(SUM(monthly_payment),0) FROM clients WHERE status='active'").fetchone()[0]
        }
    }

def _get_worker_data(db, user_id):
    my_tasks = [dict(r) for r in db.execute("""
        SELECT t.*, p.title as project_title, c.business_name 
        FROM tasks t LEFT JOIN projects p ON t.project_id=p.id LEFT JOIN clients c ON p.client_id=c.id
        WHERE t.assigned_to=? ORDER BY CASE t.priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, t.order_num
    """, (user_id,)).fetchall()]
    my_projects = [dict(r) for r in db.execute("""
        SELECT p.*, c.business_name, c.website, c.industry, c.location, c.package
        FROM projects p LEFT JOIN clients c ON p.client_id=c.id 
        WHERE p.assigned_worker_id=? OR p.team_leader_id=? ORDER BY p.created_at DESC
    """, (user_id, user_id)).fetchall()]
    notifications = [dict(r) for r in db.execute(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 20", (user_id,)).fetchall()]
    audits = [dict(r) for r in db.execute(
        "SELECT a.*, c.business_name FROM seo_audits a LEFT JOIN clients c ON a.client_id=c.id ORDER BY a.created_at DESC LIMIT 10").fetchall()]
    suggestions = [dict(r) for r in db.execute(
        "SELECT s.*, p.title as project_title FROM suggestions s LEFT JOIN projects p ON s.project_id=p.id WHERE s.user_id=? ORDER BY s.created_at DESC", (user_id,)).fetchall()]
    unread_chats = db.execute("SELECT COUNT(*) FROM team_chats WHERE to_user_id=? AND is_read=0", (user_id,)).fetchone()[0]
    
    total = len(my_tasks)
    completed = sum(1 for t in my_tasks if t["status"] == "completed")
    
    return {
        "my_tasks": my_tasks, "my_projects": my_projects, "notifications": notifications, 
        "audits": audits, "suggestions": suggestions, "unread_chats": unread_chats,
        "stats": {
            "total_tasks": total, "completed_tasks": completed, "pending_tasks": total - completed,
            "completion_pct": round(completed/total*100) if total else 0,
            "active_projects": sum(1 for p in my_projects if p["status"] == "in_progress"),
        }
    }

def _get_sales_data(db, user_id):
    leads = [dict(r) for r in db.execute("SELECT * FROM sales_leads ORDER BY created_at DESC").fetchall()]
    recent_clients = [dict(r) for r in db.execute("SELECT * FROM clients ORDER BY created_at DESC LIMIT 10").fetchall()]
    total_leads = len(leads)
    new_leads = sum(1 for l in leads if l["status"] == "new")
    won_leads = sum(1 for l in leads if l["status"] == "won")
    return {
        "leads": leads, "recent_clients": recent_clients,
        "stats": {
            "total_leads": total_leads, "new_leads": new_leads, "won_leads": won_leads,
            "conversion_rate": round(won_leads/total_leads*100) if total_leads else 0,
            "proposals_sent": sum(1 for l in leads if l["status"] == "proposal_sent"),
        }
    }

def _get_social_data(db, user_id):
    posts = [dict(r) for r in db.execute("""
        SELECT sp.*, c.business_name FROM social_posts sp LEFT JOIN clients c ON sp.client_id=c.id ORDER BY sp.created_at DESC LIMIT 50
    """).fetchall()]
    clients = [dict(r) for r in db.execute("SELECT * FROM clients WHERE status='active' ORDER BY business_name").fetchall()]
    # Parse engagement data
    total_likes = 0
    total_comments = 0
    total_shares = 0
    total_reach = 0
    for p in posts:
        if p.get("engagement_data"):
            try:
                eng = json.loads(p["engagement_data"])
                total_likes += eng.get("likes", 0)
                total_comments += eng.get("comments", 0)
                total_shares += eng.get("shares", 0)
                total_reach += eng.get("reach", 0)
            except Exception:
                pass
    return {
        "posts": posts, "clients": clients,
        "stats": {
            "total_posts": len(posts),
            "scheduled": sum(1 for p in posts if p["status"] == "scheduled"),
            "published": sum(1 for p in posts if p["status"] == "published"),
            "drafts": sum(1 for p in posts if p["status"] == "draft"),
            "total_likes": total_likes, "total_comments": total_comments,
            "total_shares": total_shares, "total_reach": total_reach,
        }
    }

def _get_finance_data(db):
    payments = [dict(r) for r in db.execute("""
        SELECT pay.*, c.business_name FROM payments pay LEFT JOIN clients c ON pay.client_id=c.id ORDER BY pay.created_at DESC
    """).fetchall()]
    expenses = [dict(r) for r in db.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()]
    workers = [dict(r) for r in db.execute("SELECT id, full_name, role, rank, salary FROM users WHERE role != 'super_admin'").fetchall()]
    total_income = sum(p["amount"] for p in payments if p["status"] == "paid")
    total_expenses = sum(e["amount"] for e in expenses)
    pending_payments = sum(p["amount"] for p in payments if p["status"] in ("pending", "overdue"))
    total_salaries = sum(w["salary"] for w in workers)
    return {
        "payments": payments, "expenses": expenses, "workers": workers,
        "stats": {
            "total_income": total_income, "total_expenses": total_expenses,
            "net_profit": total_income - total_expenses, "pending_payments": pending_payments,
            "total_salaries": total_salaries,
            "tools_cost": sum(e["amount"] for e in expenses if e["category"] == "tools"),
        }
    }

# ===== API ENDPOINTS =====
@app.post("/api/clients")
async def create_client(request: Request):
    user = require_role(request, ["super_admin", "sales"])
    data = await request.json()
    db = get_db()
    c = db.cursor()
    c.execute("""INSERT INTO clients (business_name, contact_name, email, phone, website, industry, location, status, package, monthly_payment, notes, source)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
              (data.get("business_name"), data.get("contact_name"), data.get("email"), data.get("phone"),
               data.get("website"), data.get("industry"), data.get("location"), data.get("status", "lead"),
               data.get("package"), data.get("monthly_payment", 0), data.get("notes"), data.get("source")))
    client_id = c.lastrowid
    # Auto-generate package tasks if package selected
    if data.get("package"):
        _auto_generate_package_tasks(db, client_id, data["package"])
    db.commit()
    db.close()
    return {"id": client_id, "message": "Client created"}

def _auto_generate_package_tasks(db, client_id, package):
    """Auto-generate tasks from package template when client is created"""
    pkg_tasks = db.execute("SELECT * FROM package_tasks WHERE package=? ORDER BY category, order_num", (package,)).fetchall()
    # Create a project for this client
    c = db.cursor()
    c.execute("""INSERT INTO projects (client_id, title, description, service_type, status, priority)
                 VALUES (?,?,?,?,?,?)""",
              (client_id, f"{package} Campaign", f"Auto-generated {package} project", "Full Service", "pending", "high"))
    project_id = c.lastrowid
    for i, pt in enumerate(pkg_tasks):
        c.execute("""INSERT INTO tasks (project_id, title, description, status, priority, order_num, is_automated)
                     VALUES (?,?,?,?,?,?,?)""",
                  (project_id, pt["title"], pt["description"], "pending", "medium", i, pt["is_automated"]))

@app.post("/api/projects")
async def create_project(request: Request):
    user = require_role(request, ["super_admin"])
    data = await request.json()
    db = get_db()
    c = db.cursor()
    c.execute("""INSERT INTO projects (client_id, title, description, service_type, status, priority, assigned_worker_id, team_leader_id, start_date, due_date)
                 VALUES (?,?,?,?,?,?,?,?,?,?)""",
              (data.get("client_id"), data.get("title"), data.get("description"), data.get("service_type"),
               data.get("status", "pending"), data.get("priority", "medium"), data.get("assigned_worker_id"),
               data.get("team_leader_id"), data.get("start_date"), data.get("due_date")))
    project_id = c.lastrowid
    if data.get("assigned_worker_id"):
        c.execute("INSERT INTO notifications (user_id, title, message, type) VALUES (?,?,?,?)",
                  (data["assigned_worker_id"], "New Project Assigned", f"You've been assigned: {data.get('title')}", "task"))
    db.commit()
    db.close()
    return {"id": project_id, "message": "Project created"}

@app.post("/api/tasks")
async def create_task(request: Request):
    user = require_role(request, ["super_admin", "worker", "tech_seo"])
    data = await request.json()
    db = get_db()
    c = db.cursor()
    c.execute("""INSERT INTO tasks (project_id, title, description, status, assigned_to, priority, due_date, order_num)
                 VALUES (?,?,?,?,?,?,?,?)""",
              (data.get("project_id"), data.get("title"), data.get("description"),
               data.get("status", "pending"), data.get("assigned_to"), data.get("priority", "medium"),
               data.get("due_date"), data.get("order_num", 0)))
    task_id = c.lastrowid
    if data.get("assigned_to"):
        c.execute("INSERT INTO notifications (user_id, title, message, type) VALUES (?,?,?,?)",
                  (data["assigned_to"], "New Task", f"Task: {data.get('title')}", "task"))
    db.commit()
    db.close()
    return {"id": task_id, "message": "Task created"}

@app.put("/api/tasks/{task_id}/status")
async def update_task_status(task_id: int, request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    db.execute("UPDATE tasks SET status=?, completed_date=CASE WHEN ?='completed' THEN datetime('now') ELSE NULL END WHERE id=?",
               (data["status"], data["status"], task_id))
    task = db.execute("SELECT project_id FROM tasks WHERE id=?", (task_id,)).fetchone()
    if task:
        pid = task["project_id"]
        total = db.execute("SELECT COUNT(*) FROM tasks WHERE project_id=?", (pid,)).fetchone()[0]
        done = db.execute("SELECT COUNT(*) FROM tasks WHERE project_id=? AND status='completed'", (pid,)).fetchone()[0]
        progress = round(done/total*100) if total else 0
        db.execute("UPDATE projects SET progress=?, updated_at=datetime('now') WHERE id=?", (progress, pid))
    db.commit()
    db.close()
    return {"message": "Task updated"}

@app.post("/api/users")
async def create_user(request: Request):
    user = require_role(request, ["super_admin"])
    data = await request.json()
    db = get_db()
    pw_hash = bcrypt.hash(data.get("password", "changeme123"))
    try:
        db.execute("""INSERT INTO users (username, password_hash, full_name, email, role, rank, salary) VALUES (?,?,?,?,?,?,?)""",
                   (data["username"], pw_hash, data["full_name"], data.get("email"), data["role"], data.get("rank", "junior"), data.get("salary", 0)))
        db.commit()
    except Exception as e:
        db.close()
        return JSONResponse({"error": str(e)}, status_code=400)
    db.close()
    return {"message": "User created"}

@app.post("/api/leads")
async def create_lead(request: Request):
    user = require_role(request, ["super_admin", "sales"])
    data = await request.json()
    db = get_db()
    db.execute("""INSERT INTO sales_leads (business_name, contact_name, email, phone, website, industry, location, source, status, assigned_to, notes)
                  VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
               (data.get("business_name"), data.get("contact_name"), data.get("email"), data.get("phone"),
                data.get("website"), data.get("industry"), data.get("location"), data.get("source", "other"),
                data.get("status", "new"), data.get("assigned_to"), data.get("notes")))
    db.commit()
    db.close()
    return {"message": "Lead created"}

@app.put("/api/leads/{lead_id}/status")
async def update_lead_status(lead_id: int, request: Request):
    user = require_role(request, ["super_admin", "sales"])
    data = await request.json()
    db = get_db()
    db.execute("UPDATE sales_leads SET status=?, updated_at=datetime('now') WHERE id=?", (data["status"], lead_id))
    db.commit()
    db.close()
    return {"message": "Lead updated"}

@app.post("/api/social-posts")
async def create_social_post(request: Request):
    user = require_role(request, ["super_admin", "social_media"])
    data = await request.json()
    db = get_db()
    db.execute("""INSERT INTO social_posts (client_id, platform, content, status, scheduled_date, created_by)
                  VALUES (?,?,?,?,?,?)""",
               (data.get("client_id"), data.get("platform"), data.get("content"),
                data.get("status", "draft"), data.get("scheduled_date"), user["id"]))
    db.commit()
    db.close()
    return {"message": "Post created"}

@app.post("/api/audit")
async def create_audit(request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    c = db.cursor()
    c.execute("""INSERT INTO seo_audits (client_id, website_url, status, ai_provider, created_by) VALUES (?,?,?,?,?)""",
              (data.get("client_id"), data["website_url"], "pending", data.get("ai_provider", "claude"), user["id"]))
    audit_id = c.lastrowid
    db.commit()
    db.close()
    return {"id": audit_id, "message": "Audit created — processing will begin when AI API key is configured"}

@app.post("/api/notifications/{notif_id}/read")
async def mark_notification_read(notif_id: int, request: Request):
    user = require_auth(request)
    db = get_db()
    db.execute("UPDATE notifications SET is_read=1 WHERE id=? AND user_id=?", (notif_id, user["id"]))
    db.commit()
    db.close()
    return {"message": "Marked as read"}

@app.post("/api/expenses")
async def create_expense(request: Request):
    user = require_role(request, ["super_admin", "finance"])
    data = await request.json()
    db = get_db()
    db.execute("""INSERT INTO expenses (category, description, amount, date, approved_by) VALUES (?,?,?,?,?)""",
               (data["category"], data["description"], data["amount"], data.get("date"), user["id"]))
    db.commit()
    db.close()
    return {"message": "Expense recorded"}

# ===== NEW API ENDPOINTS =====

# Client Credentials
@app.post("/api/client-credentials")
async def add_client_credential(request: Request):
    user = require_role(request, ["super_admin", "sales", "worker", "tech_seo"])
    data = await request.json()
    db = get_db()
    db.execute("""INSERT INTO client_credentials (client_id, credential_type, label, username, password_enc, api_key, access_url, notes, added_by)
                  VALUES (?,?,?,?,?,?,?,?,?)""",
               (data["client_id"], data["credential_type"], data.get("label"), data.get("username"),
                data.get("password_enc"), data.get("api_key"), data.get("access_url"), data.get("notes"), user["id"]))
    db.commit()
    db.close()
    return {"message": "Credential saved"}

# API Settings
@app.post("/api/settings/api")
async def update_api_setting(request: Request):
    user = require_role(request, ["super_admin"])
    data = await request.json()
    db = get_db()
    db.execute("""UPDATE api_settings SET api_key=?, is_active=?, config_json=?, updated_by=?, updated_at=datetime('now')
                  WHERE provider=?""",
               (data.get("api_key"), 1 if data.get("api_key") else 0, data.get("config_json"), user["id"], data["provider"]))
    db.commit()
    db.close()
    return {"message": f"{data['provider']} settings updated"}

# Suggestions
@app.post("/api/suggestions")
async def create_suggestion(request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    db.execute("""INSERT INTO suggestions (user_id, project_id, title, description) VALUES (?,?,?,?)""",
               (user["id"], data.get("project_id"), data["title"], data.get("description")))
    db.commit()
    db.close()
    return {"message": "Suggestion submitted"}

@app.put("/api/suggestions/{sugg_id}")
async def update_suggestion(sugg_id: int, request: Request):
    user = require_role(request, ["super_admin"])
    data = await request.json()
    db = get_db()
    db.execute("UPDATE suggestions SET status=?, admin_response=? WHERE id=?", (data["status"], data.get("admin_response"), sugg_id))
    db.commit()
    db.close()
    return {"message": "Suggestion updated"}

# Chat Requests
@app.post("/api/chat-request")
async def create_chat_request(request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    to_id = data["to_user_id"]
    db.execute("INSERT INTO chat_requests (from_user_id, to_user_id) VALUES (?,?)", (user["id"], to_id))
    db.execute("INSERT INTO notifications (user_id, title, message, type) VALUES (?,?,?,?)",
               (to_id, "Chat Request", f"{user['full_name']} wants to chat with you", "chat_request"))
    db.commit()
    db.close()
    return {"message": "Chat request sent"}

@app.put("/api/chat-request/{req_id}")
async def update_chat_request(req_id: int, request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    db.execute("UPDATE chat_requests SET status=?, resolved_at=datetime('now') WHERE id=?", (data["status"], req_id))
    db.commit()
    db.close()
    return {"message": f"Chat request {data['status']}"}

# Team Chat Messages
@app.get("/api/chat-messages/{other_user_id}")
async def get_chat_messages(other_user_id: int, request: Request):
    user = require_auth(request)
    db = get_db()
    messages = [dict(r) for r in db.execute("""
        SELECT tc.*, u.full_name as sender_name FROM team_chats tc 
        LEFT JOIN users u ON tc.from_user_id=u.id
        WHERE (tc.from_user_id=? AND tc.to_user_id=?) OR (tc.from_user_id=? AND tc.to_user_id=?)
        ORDER BY tc.created_at ASC LIMIT 100
    """, (user["id"], other_user_id, other_user_id, user["id"])).fetchall()]
    db.execute("UPDATE team_chats SET is_read=1 WHERE to_user_id=? AND from_user_id=?", (user["id"], other_user_id))
    db.commit()
    db.close()
    return {"messages": messages}

@app.post("/api/chat-messages")
async def send_chat_message(request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    db.execute("INSERT INTO team_chats (from_user_id, to_user_id, message) VALUES (?,?,?)",
               (user["id"], data["to_user_id"], data["message"]))
    db.commit()
    db.close()
    return {"message": "Sent"}

# Generate PDF Report
@app.post("/api/reports/generate")
async def generate_report(request: Request):
    user = require_role(request, ["super_admin", "finance", "worker", "tech_seo"])
    data = await request.json()
    client_id = data["client_id"]
    db = get_db()
    client = dict(db.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone())
    projects = [dict(r) for r in db.execute("SELECT * FROM projects WHERE client_id=?", (client_id,)).fetchall()]
    tasks_all = []
    for p in projects:
        tasks_all += [dict(r) for r in db.execute("SELECT * FROM tasks WHERE project_id=?", (p["id"],)).fetchall()]
    payments = [dict(r) for r in db.execute("SELECT * FROM payments WHERE client_id=?", (client_id,)).fetchall()]
    
    report_data = json.dumps({
        "client": client, "projects": projects, "tasks": tasks_all, "payments": payments,
        "generated_at": datetime.now().isoformat(), "generated_by": user["full_name"]
    })
    
    c = db.cursor()
    c.execute("""INSERT INTO client_reports (client_id, report_type, title, report_data, created_by) VALUES (?,?,?,?,?)""",
              (client_id, data.get("report_type", "monthly"), f"Report - {client['business_name']} - {datetime.now().strftime('%B %Y')}",
               report_data, user["id"]))
    report_id = c.lastrowid
    db.commit()
    db.close()
    return {"id": report_id, "message": "Report generated"}

# Download report as HTML
@app.get("/api/reports/{report_id}/download")
async def download_report(report_id: int, request: Request):
    user = require_auth(request)
    db = get_db()
    report = db.execute("SELECT r.*, c.business_name FROM client_reports r LEFT JOIN clients c ON r.client_id=c.id WHERE r.id=?", (report_id,)).fetchone()
    db.close()
    if not report:
        raise HTTPException(status_code=404)
    report = dict(report)
    rdata = json.loads(report["report_data"]) if report["report_data"] else {}
    client = rdata.get("client", {})
    projects = rdata.get("projects", [])
    tasks = rdata.get("tasks", [])
    payments = rdata.get("payments", [])
    
    completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
    total_tasks = len(tasks)
    total_paid = sum(p.get("amount", 0) for p in payments if p.get("status") == "paid")
    
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{report['title']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:Inter,sans-serif;background:#fff;color:#333;padding:40px}}
.header{{background:linear-gradient(135deg,#0A1628,#1E3A5F);color:#fff;padding:40px;border-radius:12px;margin-bottom:30px}}
.header h1{{font-size:24px;margin-bottom:8px}}.header p{{opacity:.8}}
.section{{margin-bottom:30px}}.section h2{{font-size:18px;color:#0A1628;border-bottom:2px solid #00D4FF;padding-bottom:8px;margin-bottom:16px}}
table{{width:100%;border-collapse:collapse;margin-top:12px}}th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid #eee}}
th{{background:#f7f9fc;font-weight:600}}.stat-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:30px}}
.stat-card{{background:#f7f9fc;padding:20px;border-radius:8px;text-align:center}}.stat-card .num{{font-size:28px;font-weight:700;color:#0A1628}}
.stat-card .label{{font-size:12px;color:#666;margin-top:4px}}.badge{{padding:3px 8px;border-radius:4px;font-size:11px;font-weight:600}}
.badge-paid{{background:#d1fae5;color:#059669}}.badge-pending{{background:#fef3c7;color:#d97706}}.badge-completed{{background:#d1fae5;color:#059669}}
.badge-progress{{background:#dbeafe;color:#2563eb}}.footer{{margin-top:40px;padding-top:20px;border-top:2px solid #eee;text-align:center;color:#999;font-size:12px}}
@media print{{body{{padding:20px}}.header{{break-after:avoid}}}}
</style></head><body>
<div class="header"><h1>AI Growth Labs — Client Report</h1><p>{report['title']}</p><p>Generated: {rdata.get('generated_at','')[:10]} | By: {rdata.get('generated_by','System')}</p></div>
<div class="stat-grid">
<div class="stat-card"><div class="num">{len(projects)}</div><div class="label">Active Projects</div></div>
<div class="stat-card"><div class="num">{completed_tasks}/{total_tasks}</div><div class="label">Tasks Completed</div></div>
<div class="stat-card"><div class="num">{round(completed_tasks/total_tasks*100) if total_tasks else 0}%</div><div class="label">Completion Rate</div></div>
<div class="stat-card"><div class="num">${total_paid:,.0f}</div><div class="label">Total Invested</div></div>
</div>
<div class="section"><h2>Client Information</h2><table>
<tr><td><strong>Business</strong></td><td>{client.get('business_name','')}</td><td><strong>Package</strong></td><td>{client.get('package','')}</td></tr>
<tr><td><strong>Contact</strong></td><td>{client.get('contact_name','')}</td><td><strong>Industry</strong></td><td>{client.get('industry','')}</td></tr>
<tr><td><strong>Website</strong></td><td>{client.get('website','')}</td><td><strong>Location</strong></td><td>{client.get('location','')}</td></tr>
</table></div>
<div class="section"><h2>Projects Overview</h2><table><thead><tr><th>Project</th><th>Service</th><th>Progress</th><th>Status</th></tr></thead><tbody>"""
    for p in projects:
        badge = "badge-completed" if p.get("status") == "completed" else "badge-progress"
        html += f'<tr><td>{p.get("title","")}</td><td>{p.get("service_type","")}</td><td>{p.get("progress",0)}%</td><td><span class="badge {badge}">{p.get("status","")}</span></td></tr>'
    html += """</tbody></table></div>
<div class="section"><h2>Task Breakdown</h2><table><thead><tr><th>Task</th><th>Priority</th><th>Status</th></tr></thead><tbody>"""
    for t in tasks:
        badge = "badge-completed" if t.get("status") == "completed" else ("badge-progress" if t.get("status") == "in_progress" else "badge-pending")
        html += f'<tr><td>{t.get("title","")}</td><td>{t.get("priority","")}</td><td><span class="badge {badge}">{t.get("status","")}</span></td></tr>'
    html += """</tbody></table></div>
<div class="section"><h2>Payment History</h2><table><thead><tr><th>Invoice</th><th>Amount</th><th>Due Date</th><th>Status</th></tr></thead><tbody>"""
    for pay in payments:
        badge = "badge-paid" if pay.get("status") == "paid" else "badge-pending"
        html += f'<tr><td>{pay.get("invoice_number","")}</td><td>${pay.get("amount",0):,.0f}</td><td>{pay.get("due_date","")}</td><td><span class="badge {badge}">{pay.get("status","")}</span></td></tr>'
    html += f"""</tbody></table></div>
<div class="footer"><p>AI Growth Labs | AI-Powered SEO &amp; Reputation Management Agency</p><p>This report is confidential and prepared exclusively for {client.get('business_name','')}.</p></div>
</body></html>"""
    
    return HTMLResponse(content=html)

# Mark report as sent
@app.post("/api/reports/{report_id}/send")
async def send_report(report_id: int, request: Request):
    user = require_role(request, ["super_admin", "finance"])
    db = get_db()
    db.execute("UPDATE client_reports SET sent_to_client=1, sent_date=datetime('now'), sent_by=? WHERE id=?", (user["id"], report_id))
    db.commit()
    db.close()
    return {"message": "Report marked as sent to client"}

# Run automated DNA task
@app.post("/api/tasks/{task_id}/run-auto")
async def run_automated_task(task_id: int, request: Request):
    user = require_auth(request)
    db = get_db()
    task = db.execute("SELECT t.*, p.client_id FROM tasks t LEFT JOIN projects p ON t.project_id=p.id WHERE t.id=?", (task_id,)).fetchone()
    if not task:
        db.close()
        raise HTTPException(status_code=404)
    task = dict(task)
    
    # Get client website
    client = db.execute("SELECT * FROM clients WHERE id=?", (task["client_id"],)).fetchone()
    client_url = dict(client)["website"] if client else ""
    
    # Get API settings
    api = db.execute("SELECT * FROM api_settings WHERE is_active=1 LIMIT 1").fetchone()
    
    if not api or not api["api_key"]:
        db.close()
        return JSONResponse({"error": "No AI API key configured. Go to Settings to add one."}, status_code=400)
    
    # For now, store that automation was triggered
    db.execute("UPDATE tasks SET status='in_progress', auto_result=? WHERE id=?",
               (json.dumps({"status": "triggered", "provider": api["provider"], "url": client_url, "triggered_at": datetime.now().isoformat()}), task_id))
    db.commit()
    db.close()
    return {"message": f"Automated task triggered using {api['provider']}. Results will appear when processing completes.", "provider": api["provider"]}

# Website chatbot API
@app.post("/api/chat")
async def save_chat(request: Request):
    data = await request.json()
    db = get_db()
    db.execute("""INSERT INTO chat_messages (session_id, visitor_name, visitor_email, business_name, industry, location, website_url, messages, status)
                  VALUES (?,?,?,?,?,?,?,?,?)""",
               (data.get("session_id"), data.get("visitor_name"), data.get("visitor_email"),
                data.get("business_name"), data.get("industry"), data.get("location"),
                data.get("website_url"), json.dumps(data.get("messages", [])), "active"))
    db.commit()
    db.close()
    return {"message": "Chat saved"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
