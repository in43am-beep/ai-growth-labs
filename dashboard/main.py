"""AI Growth Labs — Agency Operating System Dashboard"""
import os
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt
from passlib.hash import bcrypt

from database import get_db, init_db

app = FastAPI(title="AI Growth Labs OS", docs_url=None, redoc_url=None)

SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
TOKEN_EXPIRE = 24  # hours

# Static files & templates
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()

# ===== AUTH HELPERS =====
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
    # Update last login
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

# ===== DATA HELPERS =====
def _get_admin_data(db):
    clients = [dict(r) for r in db.execute("SELECT * FROM clients ORDER BY created_at DESC").fetchall()]
    projects = [dict(r) for r in db.execute("""
        SELECT p.*, c.business_name, c.contact_name, u.full_name as worker_name, tl.full_name as leader_name
        FROM projects p 
        LEFT JOIN clients c ON p.client_id=c.id 
        LEFT JOIN users u ON p.assigned_worker_id=u.id
        LEFT JOIN users tl ON p.team_leader_id=tl.id
        ORDER BY p.created_at DESC
    """).fetchall()]
    workers = [dict(r) for r in db.execute("SELECT * FROM users WHERE role != 'super_admin' ORDER BY role, full_name").fetchall()]
    tasks = [dict(r) for r in db.execute("""
        SELECT t.*, u.full_name as assigned_name, p.title as project_title
        FROM tasks t 
        LEFT JOIN users u ON t.assigned_to=u.id
        LEFT JOIN projects p ON t.project_id=p.id
        ORDER BY t.created_at DESC LIMIT 50
    """).fetchall()]
    payments = [dict(r) for r in db.execute("""
        SELECT pay.*, c.business_name FROM payments pay 
        LEFT JOIN clients c ON pay.client_id=c.id 
        ORDER BY pay.created_at DESC
    """).fetchall()]
    
    # Stats
    total_revenue = db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='paid'").fetchone()[0]
    pending_revenue = db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status IN ('pending','overdue')").fetchone()[0]
    active_clients = db.execute("SELECT COUNT(*) FROM clients WHERE status='active'").fetchone()[0]
    active_projects = db.execute("SELECT COUNT(*) FROM projects WHERE status='in_progress'").fetchone()[0]
    total_tasks = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'").fetchone()[0]
    
    return {
        "clients": clients, "projects": projects, "workers": workers, "tasks": tasks, "payments": payments,
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
        FROM tasks t 
        LEFT JOIN projects p ON t.project_id=p.id 
        LEFT JOIN clients c ON p.client_id=c.id
        WHERE t.assigned_to=? 
        ORDER BY CASE t.priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, t.order_num
    """, (user_id,)).fetchall()]
    my_projects = [dict(r) for r in db.execute("""
        SELECT p.*, c.business_name, c.website, c.industry, c.location 
        FROM projects p LEFT JOIN clients c ON p.client_id=c.id 
        WHERE p.assigned_worker_id=? OR p.team_leader_id=? 
        ORDER BY p.created_at DESC
    """, (user_id, user_id)).fetchall()]
    notifications = [dict(r) for r in db.execute(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 20", (user_id,)).fetchall()]
    audits = [dict(r) for r in db.execute(
        "SELECT a.*, c.business_name FROM seo_audits a LEFT JOIN clients c ON a.client_id=c.id ORDER BY a.created_at DESC LIMIT 10").fetchall()]
    
    total = len(my_tasks)
    completed = sum(1 for t in my_tasks if t["status"] == "completed")
    
    return {
        "my_tasks": my_tasks, "my_projects": my_projects, "notifications": notifications, "audits": audits,
        "stats": {
            "total_tasks": total, "completed_tasks": completed, "pending_tasks": total - completed,
            "completion_pct": round(completed/total*100) if total else 0,
            "active_projects": sum(1 for p in my_projects if p["status"] == "in_progress"),
        }
    }

def _get_sales_data(db, user_id):
    leads = [dict(r) for r in db.execute("""
        SELECT * FROM sales_leads ORDER BY created_at DESC
    """).fetchall()]
    recent_clients = [dict(r) for r in db.execute(
        "SELECT * FROM clients ORDER BY created_at DESC LIMIT 10").fetchall()]
    
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
        SELECT sp.*, c.business_name FROM social_posts sp 
        LEFT JOIN clients c ON sp.client_id=c.id 
        ORDER BY sp.created_at DESC LIMIT 50
    """).fetchall()]
    clients = [dict(r) for r in db.execute(
        "SELECT * FROM clients WHERE status='active' ORDER BY business_name").fetchall()]
    
    return {
        "posts": posts, "clients": clients,
        "stats": {
            "total_posts": len(posts),
            "scheduled": sum(1 for p in posts if p["status"] == "scheduled"),
            "published": sum(1 for p in posts if p["status"] == "published"),
            "drafts": sum(1 for p in posts if p["status"] == "draft"),
        }
    }

def _get_finance_data(db):
    payments = [dict(r) for r in db.execute("""
        SELECT pay.*, c.business_name FROM payments pay 
        LEFT JOIN clients c ON pay.client_id=c.id ORDER BY pay.created_at DESC
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
    db.commit()
    client_id = c.lastrowid
    db.close()
    return {"id": client_id, "message": "Client created"}

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
    # Notify worker
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
    # Update project progress
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
        db.execute("""INSERT INTO users (username, password_hash, full_name, email, role, rank, salary)
                      VALUES (?,?,?,?,?,?,?)""",
                   (data["username"], pw_hash, data["full_name"], data.get("email"),
                    data["role"], data.get("rank", "junior"), data.get("salary", 0)))
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
    c.execute("""INSERT INTO seo_audits (client_id, website_url, status, ai_provider, created_by)
                 VALUES (?,?,?,?,?)""",
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

# Chat API for website chatbot
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
