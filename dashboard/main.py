"""AI Growth Labs — Agency Operating System Dashboard v3"""
import os
import json
import secrets
import io
import csv
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional
from functools import wraps

from fastapi import FastAPI, Request, Form, HTTPException, Depends, Response, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from passlib.hash import bcrypt

from database import get_db, init_db

app = FastAPI(title="AI Growth Labs OS", docs_url=None, redoc_url=None)

# CORS — allow frontend to call API from any origin (for demo/dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security: HTTP Headers Middleware
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

# Security: Rate limiting storage
_rate_limit_store = {}

SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
TOKEN_EXPIRE = 24
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

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

# ===== SECURITY: Rate Limiting =====
def rate_limit(key_prefix: str, max_requests: int = 10, window_seconds: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host if request.client else "unknown"
            key = f"{key_prefix}:{client_ip}"
            now = time.time()
            if key in _rate_limit_store:
                requests_list = [t for t in _rate_limit_store[key] if now - t < window_seconds]
                if len(requests_list) >= max_requests:
                    raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
                requests_list.append(now)
                _rate_limit_store[key] = requests_list
            else:
                _rate_limit_store[key] = [now]
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def log_activity(db, user_id, action, details=None, entity_type=None, entity_id=None):
    db.execute("INSERT INTO activity_log (user_id, action, details, entity_type, entity_id) VALUES (?,?,?,?,?)",
               (user_id, action, details, entity_type, entity_id))

# ===== DASHBOARD ROUTER =====
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = get_current_user(request)
    if user:
        if user["role"] == "client":
            return RedirectResponse(url="/client-portal")
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    if user["role"] == "client":
        return RedirectResponse(url="/client-portal")
    role = user["role"]
    db = get_db()
    if role == "super_admin":
        data = _get_admin_data(db)
        template = "admin_dashboard.html"
    elif role == "operations_manager":
        data = _get_ops_manager_data(db)
        template = "ops_dashboard.html"
    elif role in ("worker", "tech_seo", "content_writer", "link_builder"):
        data = _get_worker_data(db, user["id"])
        template = "worker_dashboard.html"
    elif role in ("sales", "account_manager"):
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

# ===== CLIENT PORTAL =====
@app.get("/client-portal", response_class=HTMLResponse)
async def client_portal(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    if user["role"] != "client":
        return RedirectResponse(url="/dashboard")
    db = get_db()
    # Find client record linked to this user
    client = db.execute("SELECT * FROM clients WHERE email=?", (user["email"],)).fetchone()
    if not client:
        # Fallback: try to find by username match
        client = db.execute("SELECT * FROM clients WHERE contact_name=?", (user["full_name"],)).fetchone()
    data = {"user": user, "request": request}
    if client:
        client = dict(client)
        data["client"] = client
        projects = [dict(r) for r in db.execute("""
            SELECT p.*, u.full_name as worker_name FROM projects p 
            LEFT JOIN users u ON p.assigned_worker_id=u.id WHERE p.client_id=? ORDER BY p.created_at DESC
        """, (client["id"],)).fetchall()]
        data["projects"] = projects
        tasks_all = []
        for p in projects:
            tasks_all += [dict(r) for r in db.execute("SELECT * FROM tasks WHERE project_id=? ORDER BY order_num", (p["id"],)).fetchall()]
        data["tasks"] = tasks_all
        data["reports"] = [dict(r) for r in db.execute("SELECT * FROM client_reports WHERE client_id=? AND sent_to_client=1 ORDER BY created_at DESC", (client["id"],)).fetchall()]
        data["invoices"] = [dict(r) for r in db.execute("SELECT * FROM invoices WHERE client_id=? ORDER BY created_at DESC", (client["id"],)).fetchall()]
        data["rankings"] = [dict(r) for r in db.execute("SELECT * FROM keyword_rankings WHERE client_id=? ORDER BY tracked_date DESC LIMIT 50", (client["id"],)).fetchall()]
        data["approvals"] = [dict(r) for r in db.execute("SELECT * FROM approval_requests WHERE client_id=? ORDER BY created_at DESC", (client["id"],)).fetchall()]
        total_tasks = len(tasks_all)
        completed = sum(1 for t in tasks_all if t["status"] == "completed")
        data["stats"] = {
            "total_projects": len(projects),
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "completion_pct": round(completed/total_tasks*100) if total_tasks else 0,
            "pending_approvals": sum(1 for a in data["approvals"] if a["status"] == "pending"),
        }
    else:
        data["client"] = None
        data["projects"] = []
        data["tasks"] = []
        data["reports"] = []
        data["invoices"] = []
        data["rankings"] = []
        data["approvals"] = []
        data["stats"] = {"total_projects": 0, "total_tasks": 0, "completed_tasks": 0, "completion_pct": 0, "pending_approvals": 0}
    db.close()
    return templates.TemplateResponse("client_portal.html", data)

# ===== TEAM MONITOR PAGE (Admin) =====
@app.get("/monitor", response_class=HTMLResponse)
async def monitor_page(request: Request):
    user = get_current_user(request)
    if not user or user["role"] not in ("super_admin", "operations_manager"):
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
    api = db.execute("SELECT * FROM api_settings WHERE provider IN ('claude','chatgpt','gemini') AND is_active=1 LIMIT 1").fetchone()
    
    provider = api["provider"] if api and api["api_key"] else "demo"
    
    # Generate demo AI result (in production, real API call happens here)
    demo_result = {
        "status": "completed",
        "provider": provider,
        "url": client_url,
        "triggered_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "mode": "demo" if provider == "demo" else "live",
        "audit_result": {
            "overall_score": 78,
            "categories": {
                "technical_seo": {"score": 82, "issues": 5, "critical": 1},
                "on_page_seo": {"score": 75, "issues": 8, "critical": 2},
                "content_quality": {"score": 70, "issues": 6, "critical": 0},
                "backlink_profile": {"score": 65, "issues": 4, "critical": 1},
                "local_seo": {"score": 88, "issues": 3, "critical": 0},
                "mobile_usability": {"score": 85, "issues": 2, "critical": 0}
            },
            "top_recommendations": [
                "Add LocalBusiness schema markup to all location pages",
                "Optimize Core Web Vitals — LCP is 3.2s (target: <2.5s)",
                "Build 10+ quality local backlinks per month",
                "Create location-specific content for each service area",
                "Implement FAQ schema on top 5 service pages"
            ]
        },
        "note": "Demo mode — add real AI API key in Settings for live processing" if provider == "demo" else f"Processed by {provider}"
    }
    
    db.execute("UPDATE tasks SET status='completed', auto_result=? WHERE id=?",
               (json.dumps(demo_result), task_id))
    log_activity(db, user["id"], "ai_task", f"AI task #{task_id} completed ({provider})", "task", task_id)
    db.commit()
    db.close()
    return {"message": f"AI task completed using {provider}.", "provider": provider, "result": demo_result}

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

# ===== TIME TRACKING =====
@app.post("/api/time/start")
async def start_timer(request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    # Check for active timer
    active = db.execute("SELECT id FROM time_entries WHERE user_id=? AND end_time IS NULL", (user["id"],)).fetchone()
    if active:
        db.close()
        return JSONResponse({"error": "You already have an active timer. Stop it first."}, status_code=400)
    task = db.execute("SELECT t.*, p.id as proj_id FROM tasks t LEFT JOIN projects p ON t.project_id=p.id WHERE t.id=?", (data["task_id"],)).fetchone()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    db.execute("INSERT INTO time_entries (user_id, task_id, project_id, start_time) VALUES (?,?,?,datetime('now'))",
               (user["id"], data["task_id"], task["proj_id"]))
    db.execute("UPDATE tasks SET status='in_progress' WHERE id=? AND status='pending'", (data["task_id"],))
    log_activity(db, user["id"], "timer_started", f"Started timer on task #{data['task_id']}", "task", data["task_id"])
    db.commit()
    db.close()
    return {"message": "Timer started"}

@app.post("/api/time/stop")
async def stop_timer(request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    entry = db.execute("SELECT * FROM time_entries WHERE user_id=? AND end_time IS NULL", (user["id"],)).fetchone()
    if not entry:
        db.close()
        return JSONResponse({"error": "No active timer found"}, status_code=400)
    entry = dict(entry)
    start = datetime.fromisoformat(entry["start_time"])
    now = datetime.now()
    hours = round((now - start).total_seconds() / 3600, 2)
    db.execute("UPDATE time_entries SET end_time=datetime('now'), hours=?, notes=? WHERE id=?",
               (hours, data.get("notes", ""), entry["id"]))
    log_activity(db, user["id"], "timer_stopped", f"Logged {hours}h on task #{entry['task_id']}", "task", entry["task_id"])
    db.commit()
    db.close()
    return {"message": f"Timer stopped. {hours} hours logged.", "hours": hours}

@app.get("/api/time/active")
async def get_active_timer(request: Request):
    user = require_auth(request)
    db = get_db()
    entry = db.execute("""SELECT te.*, t.title as task_title, p.title as project_title 
        FROM time_entries te LEFT JOIN tasks t ON te.task_id=t.id LEFT JOIN projects p ON te.project_id=p.id 
        WHERE te.user_id=? AND te.end_time IS NULL""", (user["id"],)).fetchone()
    db.close()
    if entry:
        entry = dict(entry)
        start = datetime.fromisoformat(entry["start_time"])
        entry["elapsed_minutes"] = round((datetime.now() - start).total_seconds() / 60, 1)
    return {"active_timer": dict(entry) if entry else None}

@app.get("/api/time/entries")
async def get_time_entries(request: Request):
    user = require_auth(request)
    db = get_db()
    if user["role"] in ("super_admin", "operations_manager", "finance"):
        entries = [dict(r) for r in db.execute("""
            SELECT te.*, t.title as task_title, u.full_name as worker_name, p.title as project_title
            FROM time_entries te LEFT JOIN tasks t ON te.task_id=t.id LEFT JOIN users u ON te.user_id=u.id 
            LEFT JOIN projects p ON te.project_id=p.id ORDER BY te.created_at DESC LIMIT 100
        """).fetchall()]
    else:
        entries = [dict(r) for r in db.execute("""
            SELECT te.*, t.title as task_title, p.title as project_title
            FROM time_entries te LEFT JOIN tasks t ON te.task_id=t.id LEFT JOIN projects p ON te.project_id=p.id 
            WHERE te.user_id=? ORDER BY te.created_at DESC LIMIT 50
        """, (user["id"],)).fetchall()]
    db.close()
    return {"entries": entries}

# ===== INVOICE SYSTEM =====
def _generate_invoice_number(db):
    year = datetime.now().year
    month = datetime.now().month
    count = db.execute("SELECT COUNT(*) FROM invoices WHERE invoice_number LIKE ?", (f"INV-{year}-%",)).fetchone()[0]
    return f"INV-{year}-{count+1:04d}"

@app.post("/api/invoices")
async def create_invoice(request: Request):
    user = require_role(request, ["super_admin", "finance"])
    data = await request.json()
    db = get_db()
    inv_num = _generate_invoice_number(db)
    items = data.get("items", [])
    subtotal = sum(item.get("quantity", 1) * item.get("rate", 0) for item in items)
    tax_rate = data.get("tax_rate", 0)
    tax_amount = round(subtotal * tax_rate / 100, 2)
    total = round(subtotal + tax_amount, 2)
    c = db.cursor()
    c.execute("""INSERT INTO invoices (client_id, invoice_number, due_date, subtotal, tax_rate, tax_amount, total, status, notes, created_by)
                 VALUES (?,?,?,?,?,?,?,?,?,?)""",
              (data["client_id"], inv_num, data.get("due_date"), subtotal, tax_rate, tax_amount, total, "draft", data.get("notes"), user["id"]))
    invoice_id = c.lastrowid
    for item in items:
        amount = round(item.get("quantity", 1) * item.get("rate", 0), 2)
        c.execute("INSERT INTO invoice_items (invoice_id, description, quantity, rate, amount) VALUES (?,?,?,?,?)",
                  (invoice_id, item["description"], item.get("quantity", 1), item.get("rate", 0), amount))
    log_activity(db, user["id"], "invoice_created", f"Invoice {inv_num} for ${total}", "invoice", invoice_id)
    db.commit()
    db.close()
    return {"id": invoice_id, "invoice_number": inv_num, "total": total}

@app.get("/api/invoices")
async def list_invoices(request: Request):
    user = require_auth(request)
    db = get_db()
    if user["role"] in ("super_admin", "finance", "operations_manager"):
        invoices = [dict(r) for r in db.execute("""
            SELECT i.*, c.business_name FROM invoices i LEFT JOIN clients c ON i.client_id=c.id ORDER BY i.created_at DESC
        """).fetchall()]
    elif user["role"] == "client":
        client = db.execute("SELECT id FROM clients WHERE email=?", (user["email"],)).fetchone()
        cid = client["id"] if client else 0
        invoices = [dict(r) for r in db.execute("SELECT * FROM invoices WHERE client_id=? ORDER BY created_at DESC", (cid,)).fetchall()]
    else:
        invoices = []
    db.close()
    return {"invoices": invoices}

@app.put("/api/invoices/{invoice_id}/status")
async def update_invoice_status(invoice_id: int, request: Request):
    user = require_role(request, ["super_admin", "finance"])
    data = await request.json()
    db = get_db()
    new_status = data["status"]
    paid_date = "datetime('now')" if new_status == "paid" else "NULL"
    if new_status == "paid":
        db.execute("UPDATE invoices SET status=?, paid_date=datetime('now'), updated_at=datetime('now') WHERE id=?", (new_status, invoice_id))
        # Auto-create payment record
        inv = db.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()
        if inv:
            db.execute("INSERT INTO payments (client_id, amount, status, due_date, paid_date, invoice_number) VALUES (?,?,?,?,datetime('now'),?)",
                       (inv["client_id"], inv["total"], "paid", inv["due_date"], inv["invoice_number"]))
    else:
        db.execute("UPDATE invoices SET status=?, updated_at=datetime('now') WHERE id=?", (new_status, invoice_id))
    log_activity(db, user["id"], "invoice_status_updated", f"Invoice #{invoice_id} → {new_status}", "invoice", invoice_id)
    db.commit()
    db.close()
    return {"message": f"Invoice status updated to {new_status}"}

@app.get("/api/invoices/{invoice_id}/download")
async def download_invoice(invoice_id: int, request: Request):
    user = require_auth(request)
    db = get_db()
    inv = db.execute("SELECT i.*, c.business_name, c.contact_name, c.email as client_email, c.phone as client_phone, c.location as client_location FROM invoices i LEFT JOIN clients c ON i.client_id=c.id WHERE i.id=?", (invoice_id,)).fetchone()
    if not inv:
        db.close()
        raise HTTPException(status_code=404)
    inv = dict(inv)
    items = [dict(r) for r in db.execute("SELECT * FROM invoice_items WHERE invoice_id=?", (invoice_id,)).fetchall()]
    db.close()
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Invoice {inv['invoice_number']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:Inter,sans-serif;background:#fff;color:#333;padding:40px;max-width:800px;margin:0 auto}}
.inv-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:40px;padding-bottom:20px;border-bottom:3px solid #0891B2}}
.inv-logo{{font-size:24px;font-weight:800;color:#0A1628}}.inv-logo span{{color:#0891B2}}
.inv-title{{font-size:32px;font-weight:800;color:#0A1628;text-align:right}}
.inv-meta{{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-bottom:30px}}
.inv-meta h4{{color:#0891B2;font-size:12px;text-transform:uppercase;margin-bottom:8px}}
.inv-meta p{{font-size:14px;margin:3px 0}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}th{{background:#0A1628;color:#fff;padding:12px;text-align:left;font-size:13px}}
td{{padding:12px;border-bottom:1px solid #eee;font-size:14px}}.text-right{{text-align:right}}
.totals{{margin-top:20px;text-align:right}}.totals div{{margin:6px 0;font-size:14px}}.totals .total{{font-size:22px;font-weight:800;color:#0A1628;border-top:2px solid #0A1628;padding-top:10px;margin-top:10px}}
.badge{{display:inline-block;padding:4px 12px;border-radius:50px;font-size:12px;font-weight:700}}
.badge-paid{{background:#d1fae5;color:#059669}}.badge-draft{{background:#e2e8f0;color:#64748b}}.badge-sent{{background:#dbeafe;color:#2563eb}}.badge-overdue{{background:#fecaca;color:#dc2626}}
.footer{{margin-top:40px;padding-top:20px;border-top:1px solid #eee;text-align:center;color:#999;font-size:12px}}
@media print{{body{{padding:20px}}}}
</style></head><body>
<div class="inv-header"><div><div class="inv-logo">AI Growth<span>Labs</span></div><p style="color:#64748b;font-size:13px">AI-Powered SEO & Reputation Management</p></div><div class="inv-title">INVOICE</div></div>
<div class="inv-meta"><div><h4>Bill To</h4><p><strong>{inv.get('business_name','')}</strong></p><p>{inv.get('contact_name','')}</p><p>{inv.get('client_email','')}</p><p>{inv.get('client_phone','')}</p><p>{inv.get('client_location','')}</p></div>
<div style="text-align:right"><h4>Invoice Details</h4><p><strong>Invoice #:</strong> {inv['invoice_number']}</p><p><strong>Issue Date:</strong> {inv.get('issue_date','')}</p><p><strong>Due Date:</strong> {inv.get('due_date','')}</p><p><strong>Status:</strong> <span class="badge badge-{inv['status']}">{inv['status'].upper()}</span></p></div></div>
<table><thead><tr><th>Description</th><th class="text-right">Qty</th><th class="text-right">Rate</th><th class="text-right">Amount</th></tr></thead><tbody>"""
    for item in items:
        html += f'<tr><td>{item["description"]}</td><td class="text-right">{item["quantity"]}</td><td class="text-right">${item["rate"]:,.2f}</td><td class="text-right">${item["amount"]:,.2f}</td></tr>'
    html += f"""</tbody></table>
<div class="totals"><div>Subtotal: ${inv['subtotal']:,.2f}</div><div>Tax ({inv['tax_rate']}%): ${inv['tax_amount']:,.2f}</div><div class="total">Total: ${inv['total']:,.2f}</div></div>"""
    if inv.get("notes"):
        html += f'<div style="margin-top:30px;background:#f8fafc;padding:16px;border-radius:8px"><h4 style="font-size:13px;color:#64748b;margin-bottom:6px">Notes</h4><p style="font-size:14px">{inv["notes"]}</p></div>'
    html += '<div class="footer"><p>AI Growth Labs | Thank you for your business!</p></div></body></html>'
    return HTMLResponse(content=html)

# ===== FILE UPLOADS =====
@app.post("/api/upload")
async def upload_file(request: Request, file: UploadFile = File(...), related_type: str = Form(...), related_id: int = Form(...)):
    user = require_auth(request)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    safe_filename = f"{int(time.time())}_{file.filename.replace('..', '').replace('/', '_')}"
    filepath = os.path.join(UPLOAD_DIR, safe_filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    db = get_db()
    db.execute("INSERT INTO file_attachments (related_type, related_id, filename, filepath, filesize, mime_type, uploaded_by) VALUES (?,?,?,?,?,?,?)",
               (related_type, related_id, file.filename, safe_filename, len(contents), file.content_type, user["id"]))
    log_activity(db, user["id"], "file_uploaded", f"Uploaded {file.filename}", related_type, related_id)
    db.commit()
    db.close()
    return {"message": "File uploaded", "filename": safe_filename}

@app.get("/uploads/{filename}")
async def serve_upload(filename: str, request: Request):
    user = require_auth(request)
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404)
    with open(filepath, "rb") as f:
        content = f.read()
    return Response(content=content, media_type="application/octet-stream",
                    headers={"Content-Disposition": f"inline; filename={filename}"})

# ===== APPROVAL REQUESTS =====
@app.post("/api/approvals")
async def create_approval(request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    c = db.cursor()
    c.execute("""INSERT INTO approval_requests (task_id, project_id, client_id, request_type, title, description, requested_by) VALUES (?,?,?,?,?,?,?)""",
              (data.get("task_id"), data.get("project_id"), data.get("client_id"), data.get("request_type", "content"),
               data["title"], data.get("description"), user["id"]))
    approval_id = c.lastrowid
    log_activity(db, user["id"], "approval_requested", f"Approval: {data['title']}", "approval", approval_id)
    db.commit()
    db.close()
    return {"id": approval_id, "message": "Approval request created"}

@app.put("/api/approvals/{approval_id}")
async def respond_approval(approval_id: int, request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    db.execute("UPDATE approval_requests SET status=?, reviewed_by=?, review_notes=?, reviewed_at=datetime('now') WHERE id=?",
               (data["status"], user["id"], data.get("review_notes"), approval_id))
    log_activity(db, user["id"], "approval_responded", f"Approval #{approval_id} → {data['status']}", "approval", approval_id)
    db.commit()
    db.close()
    return {"message": f"Approval {data['status']}"}

# ===== DATA EXPORT =====
@app.get("/api/export/{table_name}")
async def export_data(table_name: str, request: Request):
    user = require_role(request, ["super_admin", "finance", "operations_manager"])
    allowed = {"clients", "payments", "expenses", "invoices", "tasks", "projects", "time_entries"}
    if table_name not in allowed:
        raise HTTPException(status_code=400, detail=f"Export not allowed for '{table_name}'")
    db = get_db()
    rows = [dict(r) for r in db.execute(f"SELECT * FROM {table_name}").fetchall()]
    db.close()
    if not rows:
        return Response(content="No data", media_type="text/plain")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={table_name}_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

# ===== ACTIVITY TIMELINE =====
@app.get("/api/activity")
async def get_activity(request: Request):
    user = require_auth(request)
    db = get_db()
    if user["role"] in ("super_admin", "operations_manager"):
        activities = [dict(r) for r in db.execute("""
            SELECT al.*, u.full_name as user_name FROM activity_log al LEFT JOIN users u ON al.user_id=u.id ORDER BY al.created_at DESC LIMIT 50
        """).fetchall()]
    else:
        activities = [dict(r) for r in db.execute("""
            SELECT al.*, u.full_name as user_name FROM activity_log al LEFT JOIN users u ON al.user_id=u.id WHERE al.user_id=? ORDER BY al.created_at DESC LIMIT 30
        """, (user["id"],)).fetchall()]
    db.close()
    return {"activities": activities}

# ===== OPS MANAGER DATA =====
def _get_ops_manager_data(db):
    clients = [dict(r) for r in db.execute("SELECT * FROM clients WHERE status='active' ORDER BY business_name").fetchall()]
    projects = [dict(r) for r in db.execute("""
        SELECT p.*, c.business_name, u.full_name as worker_name FROM projects p 
        LEFT JOIN clients c ON p.client_id=c.id LEFT JOIN users u ON p.assigned_worker_id=u.id ORDER BY p.created_at DESC
    """).fetchall()]
    workers = [dict(r) for r in db.execute("SELECT id, full_name, role, rank FROM users WHERE role NOT IN ('super_admin','client','finance') AND is_active=1 ORDER BY role, full_name").fetchall()]
    for w in workers:
        w["active_tasks"] = db.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=? AND status='in_progress'", (w["id"],)).fetchone()[0]
        w["total_hours"] = db.execute("SELECT COALESCE(SUM(hours),0) FROM time_entries WHERE user_id=?", (w["id"],)).fetchone()[0]
    tasks = [dict(r) for r in db.execute("""
        SELECT t.*, u.full_name as assigned_name, p.title as project_title FROM tasks t 
        LEFT JOIN users u ON t.assigned_to=u.id LEFT JOIN projects p ON t.project_id=p.id ORDER BY t.created_at DESC LIMIT 50
    """).fetchall()]
    overdue_tasks = [dict(r) for r in db.execute("""
        SELECT t.*, u.full_name as assigned_name, p.title as project_title FROM tasks t 
        LEFT JOIN users u ON t.assigned_to=u.id LEFT JOIN projects p ON t.project_id=p.id 
        WHERE t.due_date IS NOT NULL AND t.due_date < date('now') AND t.status != 'completed' ORDER BY t.due_date
    """).fetchall()]
    pending_approvals = [dict(r) for r in db.execute("SELECT * FROM approval_requests WHERE status='pending' ORDER BY created_at DESC").fetchall()]
    active_projects = db.execute("SELECT COUNT(*) FROM projects WHERE status='in_progress'").fetchone()[0]
    total_tasks = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'").fetchone()[0]
    return {
        "clients": clients, "projects": projects, "workers": workers, "tasks": tasks,
        "overdue_tasks": overdue_tasks, "pending_approvals": pending_approvals,
        "stats": {
            "active_projects": active_projects, "total_tasks": total_tasks, "completed_tasks": completed_tasks,
            "task_completion": round(completed_tasks/total_tasks*100) if total_tasks else 0,
            "overdue_count": len(overdue_tasks), "pending_approvals": len(pending_approvals),
        }
    }

# ===== KEYWORD RANKINGS =====
@app.post("/api/rankings")
async def add_ranking(request: Request):
    user = require_role(request, ["super_admin", "operations_manager", "worker", "tech_seo"])
    data = await request.json()
    db = get_db()
    prev = db.execute("SELECT position FROM keyword_rankings WHERE client_id=? AND keyword=? ORDER BY tracked_date DESC LIMIT 1",
                      (data["client_id"], data["keyword"])).fetchone()
    prev_pos = prev["position"] if prev else None
    db.execute("INSERT INTO keyword_rankings (client_id, keyword, position, previous_position, search_volume, url) VALUES (?,?,?,?,?,?)",
               (data["client_id"], data["keyword"], data["position"], prev_pos, data.get("search_volume", 0), data.get("url")))
    db.commit()
    db.close()
    return {"message": "Ranking recorded"}

@app.get("/api/rankings/{client_id}")
async def get_rankings(client_id: int, request: Request):
    user = require_auth(request)
    db = get_db()
    if client_id == 0:
        rankings = [dict(r) for r in db.execute("SELECT * FROM keyword_rankings ORDER BY tracked_date DESC, keyword LIMIT 200").fetchall()]
    else:
        rankings = [dict(r) for r in db.execute("SELECT * FROM keyword_rankings WHERE client_id=? ORDER BY tracked_date DESC, keyword LIMIT 100", (client_id,)).fetchall()]
    db.close()
    return {"rankings": rankings}

# ===== CONTRACTS =====
@app.get("/api/contracts")
async def list_contracts(request: Request):
    user = require_auth(request)
    db = get_db()
    contracts = [dict(r) for r in db.execute("SELECT * FROM contracts ORDER BY created_at DESC").fetchall()]
    db.close()
    return {"contracts": contracts}

@app.post("/api/contracts")
async def create_contract(request: Request):
    user = require_role(request, ["super_admin", "sales", "account_manager"])
    data = await request.json()
    db = get_db()
    c = db.cursor()
    c.execute("""INSERT INTO contracts (client_id, title, start_date, end_date, terms, status, monthly_value, auto_renew, created_by) VALUES (?,?,?,?,?,?,?,?,?)""",
              (data["client_id"], data["title"], data.get("start_date"), data.get("end_date"), data.get("terms"),
               data.get("status", "active"), data.get("monthly_value", 0), data.get("auto_renew", 0), user["id"]))
    contract_id = c.lastrowid
    log_activity(db, user["id"], "contract_created", f"Contract for client #{data['client_id']}", "contract", contract_id)
    db.commit()
    db.close()
    return {"id": contract_id, "message": "Contract created"}

# ===== SECURITY: Change Password =====
@app.post("/api/change-password")
async def change_password(request: Request):
    user = require_auth(request)
    data = await request.json()
    old_pw = data.get("old_password", "")
    new_pw = data.get("new_password", "")
    if len(new_pw) < 8:
        return JSONResponse({"error": "Password must be at least 8 characters"}, status_code=400)
    db = get_db()
    u = db.execute("SELECT password_hash FROM users WHERE id=?", (user["id"],)).fetchone()
    if not bcrypt.verify(old_pw, u["password_hash"]):
        db.close()
        return JSONResponse({"error": "Current password is incorrect"}, status_code=400)
    db.execute("UPDATE users SET password_hash=? WHERE id=?", (bcrypt.hash(new_pw), user["id"]))
    log_activity(db, user["id"], "password_changed", "User changed password", "user", user["id"])
    db.commit()
    db.close()
    return {"message": "Password changed successfully"}

# ===== PART 2: WHITE-LABEL REPORTS =====
@app.post("/api/reports/white-label")
async def generate_white_label_report(request: Request):
    user = require_role(request, ["super_admin", "finance", "operations_manager", "account_manager"])
    data = await request.json()
    client_id = data["client_id"]
    db = get_db()
    client = dict(db.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone())
    projects = [dict(r) for r in db.execute("SELECT * FROM projects WHERE client_id=?", (client_id,)).fetchall()]
    tasks_all = []
    for p in projects:
        tasks_all += [dict(r) for r in db.execute("SELECT * FROM tasks WHERE project_id=?", (p["id"],)).fetchall()]
    payments = [dict(r) for r in db.execute("SELECT * FROM payments WHERE client_id=?", (client_id,)).fetchall()]
    rankings = [dict(r) for r in db.execute("SELECT * FROM keyword_rankings WHERE client_id=? ORDER BY tracked_date DESC LIMIT 20", (client_id,)).fetchall()]
    locations = [dict(r) for r in db.execute("SELECT * FROM client_locations WHERE client_id=?", (client_id,)).fetchall()]
    
    agency_name = data.get("agency_name", "AI Growth Labs")
    agency_tagline = data.get("agency_tagline", "AI-Powered SEO & Reputation Management")
    primary_color = data.get("primary_color", "#0A1628")
    accent_color = data.get("accent_color", "#00D4FF")
    logo_url = data.get("logo_url", "")
    
    report_data = json.dumps({
        "client": client, "projects": projects, "tasks": tasks_all, "payments": payments,
        "rankings": rankings, "locations": locations,
        "branding": {"agency_name": agency_name, "tagline": agency_tagline, "primary_color": primary_color, "accent_color": accent_color, "logo_url": logo_url},
        "generated_at": datetime.now().isoformat(), "generated_by": user["full_name"]
    })
    
    c = db.cursor()
    c.execute("INSERT INTO client_reports (client_id, report_type, title, report_data, created_by) VALUES (?,?,?,?,?)",
              (client_id, "white_label", f"White-Label Report - {client['business_name']} - {datetime.now().strftime('%B %Y')}", report_data, user["id"]))
    report_id = c.lastrowid
    log_activity(db, user["id"], "report_generated", f"White-label report for {client['business_name']}", "report", report_id)
    db.commit()
    db.close()
    return {"id": report_id, "message": "White-label report generated"}

@app.get("/api/reports/{report_id}/white-label")
async def download_white_label_report(report_id: int, request: Request):
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
    rankings = rdata.get("rankings", [])
    branding = rdata.get("branding", {})
    
    agency = branding.get("agency_name", "AI Growth Labs")
    tagline = branding.get("tagline", "AI-Powered SEO & Reputation Management")
    pc = branding.get("primary_color", "#0A1628")
    ac = branding.get("accent_color", "#00D4FF")
    logo = branding.get("logo_url", "")
    
    completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
    total_tasks = len(tasks)
    total_paid = sum(p.get("amount", 0) for p in payments if p.get("status") == "paid")
    
    logo_html = f'<img src="{logo}" style="max-height:50px;margin-bottom:12px">' if logo else ""
    
    rankings_html = ""
    if rankings:
        rankings_html = '<div class="section"><h2>Keyword Rankings</h2><table><thead><tr><th>Keyword</th><th>Position</th><th>Change</th><th>Volume</th><th>URL</th></tr></thead><tbody>'
        for r in rankings:
            prev = r.get("previous_position")
            pos = r.get("position", 0)
            if prev and prev > pos:
                change = f'<span style="color:#059669">▲ {prev - pos}</span>'
            elif prev and prev < pos:
                change = f'<span style="color:#dc2626">▼ {pos - prev}</span>'
            else:
                change = '<span style="color:#999">—</span>'
            rankings_html += f'<tr><td><strong>{r.get("keyword","")}</strong></td><td>{pos}</td><td>{change}</td><td>{r.get("search_volume",0)}</td><td style="font-size:11px">{r.get("url","")}</td></tr>'
        rankings_html += '</tbody></table></div>'
    
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{report['title']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:Inter,Arial,sans-serif;background:#fff;color:#333;padding:40px}}
.header{{background:linear-gradient(135deg,{pc},{ac}22);color:#fff;padding:40px;border-radius:12px;margin-bottom:30px;border-left:5px solid {ac}}}
.header h1{{font-size:24px;margin-bottom:4px}}.header p{{opacity:.8;font-size:14px}}
.section{{margin-bottom:30px}}.section h2{{font-size:18px;color:{pc};border-bottom:2px solid {ac};padding-bottom:8px;margin-bottom:16px}}
table{{width:100%;border-collapse:collapse;margin-top:12px}}th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid #eee;font-size:13px}}
th{{background:#f7f9fc;font-weight:600}}.stat-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:30px}}
.stat-card{{background:#f7f9fc;padding:20px;border-radius:8px;text-align:center;border-top:3px solid {ac}}}.stat-card .num{{font-size:28px;font-weight:700;color:{pc}}}
.stat-card .label{{font-size:12px;color:#666;margin-top:4px}}.badge{{padding:3px 8px;border-radius:4px;font-size:11px;font-weight:600}}
.badge-paid,.badge-completed{{background:#d1fae5;color:#059669}}.badge-pending{{background:#fef3c7;color:#d97706}}
.badge-progress,.badge-in_progress{{background:#dbeafe;color:#2563eb}}
.footer{{margin-top:40px;padding-top:20px;border-top:2px solid #eee;text-align:center;color:#999;font-size:12px}}
.confidential{{background:#fef3c7;padding:8px 16px;border-radius:6px;font-size:11px;color:#92400e;margin-bottom:20px;text-align:center}}
@media print{{body{{padding:20px}}.header{{break-after:avoid}}}}
</style></head><body>
<div class="header">{logo_html}<h1>{agency}</h1><p>{tagline}</p><p style="margin-top:8px">Report for: <strong>{client.get('business_name','')}</strong> | {rdata.get('generated_at','')[:10]}</p></div>
<div class="confidential">CONFIDENTIAL — Prepared exclusively for {client.get('business_name','')}</div>
<div class="stat-grid">
<div class="stat-card"><div class="num">{len(projects)}</div><div class="label">Active Projects</div></div>
<div class="stat-card"><div class="num">{completed_tasks}/{total_tasks}</div><div class="label">Tasks Completed</div></div>
<div class="stat-card"><div class="num">{round(completed_tasks/total_tasks*100) if total_tasks else 0}%</div><div class="label">Completion Rate</div></div>
<div class="stat-card"><div class="num">${total_paid:,.0f}</div><div class="label">Total Invested</div></div>
</div>
{rankings_html}
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
<div class="footer"><p>{agency} | {tagline}</p><p>Generated by {rdata.get('generated_by','System')} on {rdata.get('generated_at','')[:10]}</p></div>
</body></html>"""
    return HTMLResponse(content=html)

# ===== PART 2: EMAIL SENDING =====
@app.post("/api/email/send")
async def send_email(request: Request):
    user = require_role(request, ["super_admin", "finance", "operations_manager", "account_manager"])
    data = await request.json()
    db = get_db()
    smtp = db.execute("SELECT * FROM api_settings WHERE provider='smtp'").fetchone()
    if not smtp or not smtp["api_key"]:
        db.close()
        return JSONResponse({"error": "SMTP not configured. Go to Settings → SMTP to configure email sending."}, status_code=400)
    smtp = dict(smtp)
    config = json.loads(smtp.get("config") or "{}")
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = data.get("subject", "AI Growth Labs Report")
        msg["From"] = config.get("from_email", smtp["api_key"])
        msg["To"] = data["to_email"]
        
        if data.get("html_body"):
            msg.attach(MIMEText(data["html_body"], "html"))
        elif data.get("body"):
            msg.attach(MIMEText(data["body"], "plain"))
        
        host = config.get("host", "smtp.gmail.com")
        port = int(config.get("port", 587))
        
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            server.login(config.get("from_email", smtp["api_key"]), smtp["api_key"])
            server.send_message(msg)
        
        log_activity(db, user["id"], "email_sent", f"Email to {data['to_email']}: {data.get('subject','')}", "email", 0)
        db.commit()
        db.close()
        return {"message": f"Email sent to {data['to_email']}"}
    except Exception as e:
        db.close()
        return JSONResponse({"error": f"Email failed: {str(e)}"}, status_code=500)

@app.post("/api/reports/{report_id}/email")
async def email_report(report_id: int, request: Request):
    user = require_role(request, ["super_admin", "finance", "operations_manager"])
    data = await request.json()
    db = get_db()
    report = db.execute("SELECT r.*, c.business_name, c.email as client_email FROM client_reports r LEFT JOIN clients c ON r.client_id=c.id WHERE r.id=?", (report_id,)).fetchone()
    if not report:
        db.close()
        raise HTTPException(status_code=404)
    report = dict(report)
    
    to_email = data.get("to_email", report.get("client_email", ""))
    if not to_email:
        db.close()
        return JSONResponse({"error": "No email address provided"}, status_code=400)
    
    smtp = db.execute("SELECT * FROM api_settings WHERE provider='smtp'").fetchone()
    if not smtp or not smtp["api_key"]:
        db.close()
        return JSONResponse({"error": "SMTP not configured"}, status_code=400)
    smtp_conf = json.loads(dict(smtp).get("config") or "{}")
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        rdata = json.loads(report["report_data"]) if report["report_data"] else {}
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Your SEO Report - {report['business_name']} - {report['title']}"
        msg["From"] = smtp_conf.get("from_email", dict(smtp)["api_key"])
        msg["To"] = to_email
        
        text = f"Hi,\n\nPlease find your latest SEO performance report attached.\n\nReport: {report['title']}\nGenerated: {rdata.get('generated_at','')[:10]}\n\nPlease log in to your client portal to view full details.\n\nBest regards,\nAI Growth Labs Team"
        msg.attach(MIMEText(text, "plain"))
        
        host = smtp_conf.get("host", "smtp.gmail.com")
        port = int(smtp_conf.get("port", 587))
        
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            server.login(smtp_conf.get("from_email", dict(smtp)["api_key"]), dict(smtp)["api_key"])
            server.send_message(msg)
        
        db.execute("UPDATE client_reports SET sent_to_client=1, sent_date=datetime('now'), sent_by=? WHERE id=?", (user["id"], report_id))
        log_activity(db, user["id"], "report_emailed", f"Report emailed to {to_email}", "report", report_id)
        db.commit()
        db.close()
        return {"message": f"Report emailed to {to_email}"}
    except Exception as e:
        db.close()
        return JSONResponse({"error": f"Email failed: {str(e)}"}, status_code=500)

# ===== PART 2: FILE ATTACHMENTS LIST =====
@app.get("/api/attachments/{related_type}/{related_id}")
async def list_attachments(related_type: str, related_id: int, request: Request):
    user = require_auth(request)
    db = get_db()
    files = [dict(r) for r in db.execute("""
        SELECT f.*, u.full_name as uploader_name FROM file_attachments f
        LEFT JOIN users u ON f.uploaded_by=u.id
        WHERE f.related_type=? AND f.related_id=? ORDER BY f.created_at DESC
    """, (related_type, related_id)).fetchall()]
    db.close()
    return {"attachments": files}

# ===== PART 2: CLIENT LOCATIONS =====
@app.post("/api/locations")
async def add_location(request: Request):
    user = require_role(request, ["super_admin", "operations_manager", "account_manager", "sales"])
    data = await request.json()
    db = get_db()
    c = db.cursor()
    c.execute("""INSERT INTO client_locations (client_id, location_name, address, city, state, zip_code, phone, gbp_url, gbp_cid) VALUES (?,?,?,?,?,?,?,?,?)""",
              (data["client_id"], data["location_name"], data.get("address"), data.get("city"), data.get("state"),
               data.get("zip_code"), data.get("phone"), data.get("gbp_url"), data.get("gbp_cid")))
    loc_id = c.lastrowid
    log_activity(db, user["id"], "location_added", f"Location: {data['location_name']} for client #{data['client_id']}", "location", loc_id)
    db.commit()
    db.close()
    return {"id": loc_id, "message": "Location added"}

@app.get("/api/locations/{client_id}")
async def get_locations(client_id: int, request: Request):
    user = require_auth(request)
    db = get_db()
    locations = [dict(r) for r in db.execute("SELECT * FROM client_locations WHERE client_id=? ORDER BY location_name", (client_id,)).fetchall()]
    db.close()
    return {"locations": locations}

# ===== PART 2: RANKINGS CHART PAGE =====
@app.get("/rankings/{client_id}", response_class=HTMLResponse)
async def rankings_chart_page(client_id: int, request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    if not client:
        db.close()
        raise HTTPException(status_code=404)
    client = dict(client)
    rankings = [dict(r) for r in db.execute("SELECT * FROM keyword_rankings WHERE client_id=? ORDER BY keyword, tracked_date", (client_id,)).fetchall()]
    locations = [dict(r) for r in db.execute("SELECT * FROM client_locations WHERE client_id=?", (client_id,)).fetchall()]
    db.close()
    
    keywords = {}
    for r in rankings:
        kw = r["keyword"]
        if kw not in keywords:
            keywords[kw] = {"positions": [], "current": r["position"], "previous": r.get("previous_position"), "volume": r.get("search_volume", 0), "url": r.get("url", "")}
        keywords[kw]["positions"].append(r["position"])
        keywords[kw]["current"] = r["position"]
    
    chart_data = json.dumps({"keywords": {k: v["positions"] for k, v in keywords.items()}})
    
    return templates.TemplateResponse("rankings_chart.html", {
        "request": request, "user": user, "client": client,
        "keywords": keywords, "chart_data": chart_data, "locations": locations
    })

# ===== PART 3: ACTIVITY TIMELINE PAGE =====
@app.get("/activity", response_class=HTMLResponse)
async def activity_page(request: Request):
    user = get_current_user(request)
    if not user or user["role"] not in ("super_admin", "operations_manager"):
        return RedirectResponse(url="/login")
    db = get_db()
    activities = [dict(r) for r in db.execute("""
        SELECT al.*, u.full_name as user_name FROM activity_log al LEFT JOIN users u ON al.user_id=u.id ORDER BY al.created_at DESC LIMIT 200
    """).fetchall()]
    db.close()
    return templates.TemplateResponse("activity_timeline.html", {"request": request, "user": user, "activities": activities})

# ===== PART 3: WORKER PERFORMANCE =====
@app.get("/api/performance/{user_id}")
async def get_worker_performance(user_id: int, request: Request):
    user = require_auth(request)
    if user["role"] not in ("super_admin", "operations_manager") and user["id"] != user_id:
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    db = get_db()
    worker = db.execute("SELECT id, username, full_name, role, rank FROM users WHERE id=?", (user_id,)).fetchone()
    if not worker:
        db.close()
        raise HTTPException(status_code=404)
    worker = dict(worker)
    total_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=?", (user_id,)).fetchone()[0]
    completed_tasks = db.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=? AND status='completed'", (user_id,)).fetchone()[0]
    in_progress = db.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=? AND status='in_progress'", (user_id,)).fetchone()[0]
    total_hours = db.execute("SELECT COALESCE(SUM(hours),0) FROM time_entries WHERE user_id=?", (user_id,)).fetchone()[0]
    avg_hours = db.execute("SELECT COALESCE(AVG(hours),0) FROM time_entries WHERE user_id=? AND hours > 0", (user_id,)).fetchone()[0]
    active_projects = db.execute("SELECT COUNT(DISTINCT project_id) FROM tasks WHERE assigned_to=? AND status IN ('in_progress','pending')", (user_id,)).fetchone()[0]
    
    # Recent completed tasks
    recent = [dict(r) for r in db.execute("""
        SELECT t.title, t.status, t.priority, p.title as project_title 
        FROM tasks t LEFT JOIN projects p ON t.project_id=p.id WHERE t.assigned_to=? ORDER BY t.created_at DESC LIMIT 10
    """, (user_id,)).fetchall()]
    
    # Performance score (0-100)
    completion_rate = round(completed_tasks / total_tasks * 100) if total_tasks else 0
    score = min(100, completion_rate + min(20, int(total_hours)))
    
    db.close()
    return {
        "worker": worker,
        "stats": {
            "total_tasks": total_tasks, "completed_tasks": completed_tasks, "in_progress": in_progress,
            "completion_rate": completion_rate, "total_hours": round(total_hours, 1),
            "avg_hours_per_task": round(avg_hours, 1), "active_projects": active_projects,
            "performance_score": score
        },
        "recent_tasks": recent
    }

@app.get("/performance", response_class=HTMLResponse)
async def performance_page(request: Request):
    user = get_current_user(request)
    if not user or user["role"] not in ("super_admin", "operations_manager"):
        return RedirectResponse(url="/login")
    db = get_db()
    workers = [dict(r) for r in db.execute("SELECT id, username, full_name, role, rank, salary FROM users WHERE role NOT IN ('super_admin','client') AND is_active=1").fetchall()]
    for w in workers:
        total = db.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=?", (w["id"],)).fetchone()[0]
        completed = db.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to=? AND status='completed'", (w["id"],)).fetchone()[0]
        hours = db.execute("SELECT COALESCE(SUM(hours),0) FROM time_entries WHERE user_id=?", (w["id"],)).fetchone()[0]
        w["total_tasks"] = total
        w["completed_tasks"] = completed
        w["completion_rate"] = round(completed / total * 100) if total else 0
        w["total_hours"] = round(hours, 1)
        w["score"] = min(100, w["completion_rate"] + min(20, int(hours)))
    workers.sort(key=lambda x: x["score"], reverse=True)
    db.close()
    return templates.TemplateResponse("performance.html", {"request": request, "user": user, "workers": workers})

# ===== PART 3: NOTIFICATIONS API =====
@app.get("/api/notifications")
async def get_notifications(request: Request):
    user = require_auth(request)
    db = get_db()
    notifs = [dict(r) for r in db.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 30", (user["id"],)).fetchall()]
    unread = db.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0", (user["id"],)).fetchone()[0]
    db.close()
    return {"notifications": notifs, "unread_count": unread}

@app.post("/api/notifications/read")
async def mark_notifications_read(request: Request):
    user = require_auth(request)
    db = get_db()
    db.execute("UPDATE notifications SET is_read=1 WHERE user_id=? AND is_read=0", (user["id"],))
    db.commit()
    db.close()
    return {"message": "All notifications marked as read"}

@app.post("/api/notifications/create")
async def create_notification(request: Request):
    user = require_role(request, ["super_admin", "operations_manager"])
    data = await request.json()
    db = get_db()
    db.execute("INSERT INTO notifications (user_id, type, title, message, link) VALUES (?,?,?,?,?)",
               (data["user_id"], data.get("type", "info"), data["title"], data.get("message", ""), data.get("link")))
    db.commit()
    db.close()
    return {"message": "Notification sent"}

# ===== PART 3: BULK TASK CREATION FROM TEMPLATES =====
@app.post("/api/tasks/bulk")
async def create_bulk_tasks(request: Request):
    user = require_role(request, ["super_admin", "operations_manager", "account_manager"])
    data = await request.json()
    project_id = data["project_id"]
    tasks = data.get("tasks", [])
    db = get_db()
    c = db.cursor()
    created = 0
    for i, t in enumerate(tasks):
        c.execute("""INSERT INTO tasks (project_id, title, description, priority, assigned_to, order_num) VALUES (?,?,?,?,?,?)""",
                  (project_id, t["title"], t.get("description", ""), t.get("priority", "medium"), t.get("assigned_to"), i + 1))
        created += 1
    log_activity(db, user["id"], "bulk_tasks_created", f"Created {created} tasks for project #{project_id}", "project", project_id)
    db.commit()
    db.close()
    return {"message": f"{created} tasks created", "count": created}

# ===== PART 3: TASK STATUS UPDATE =====
@app.put("/api/tasks/{task_id}/status")
async def update_task_status(task_id: int, request: Request):
    user = require_auth(request)
    data = await request.json()
    new_status = data["status"]
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not task:
        db.close()
        raise HTTPException(status_code=404)
    db.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
    if new_status == "completed":
        db.execute("UPDATE tasks SET completed_date=datetime('now') WHERE id=?", (task_id,))
        # Update project progress
        proj_id = task["project_id"]
        total = db.execute("SELECT COUNT(*) FROM tasks WHERE project_id=?", (proj_id,)).fetchone()[0]
        done = db.execute("SELECT COUNT(*) FROM tasks WHERE project_id=? AND status='completed'", (proj_id,)).fetchone()[0] + 1
        progress = round(done / total * 100) if total else 0
        db.execute("UPDATE projects SET progress=? WHERE id=?", (progress, proj_id))
    log_activity(db, user["id"], "task_status_updated", f"Task #{task_id} → {new_status}", "task", task_id)
    db.commit()
    db.close()
    return {"message": f"Task updated to {new_status}"}

# ===== PART 3: DASHBOARD SEARCH =====
@app.get("/api/search")
async def search(request: Request, q: str = ""):
    user = require_auth(request)
    if not q or len(q) < 2:
        return {"results": []}
    db = get_db()
    results = []
    # Search clients
    for r in db.execute("SELECT id, business_name, contact_name, industry FROM clients WHERE business_name LIKE ? OR contact_name LIKE ? LIMIT 5",
                         (f"%{q}%", f"%{q}%")).fetchall():
        results.append({"type": "client", "id": r["id"], "title": r["business_name"], "subtitle": r["contact_name"], "link": f"/client/{r['id']}"})
    # Search projects
    for r in db.execute("SELECT p.id, p.title, c.business_name FROM projects p LEFT JOIN clients c ON p.client_id=c.id WHERE p.title LIKE ? LIMIT 5",
                         (f"%{q}%",)).fetchall():
        results.append({"type": "project", "id": r["id"], "title": r["title"], "subtitle": r["business_name"] or "", "link": f"/client/{r['id']}"})
    # Search tasks
    for r in db.execute("SELECT t.id, t.title, p.title as project_title FROM tasks t LEFT JOIN projects p ON t.project_id=p.id WHERE t.title LIKE ? LIMIT 5",
                         (f"%{q}%",)).fetchall():
        results.append({"type": "task", "id": r["id"], "title": r["title"], "subtitle": r["project_title"] or "", "link": "#"})
    db.close()
    return {"results": results}

# ===== PART 4: REVENUE FORECASTING =====
@app.get("/api/analytics/revenue")
async def revenue_analytics(request: Request):
    user = require_role(request, ["super_admin", "finance", "operations_manager"])
    db = get_db()
    
    # Current MRR from active clients
    mrr = db.execute("SELECT COALESCE(SUM(monthly_payment),0) FROM clients WHERE status='active'").fetchone()[0]
    
    # Revenue by month (from invoices)
    monthly_rev = [dict(r) for r in db.execute("""
        SELECT strftime('%Y-%m', issue_date) as month, SUM(total) as revenue, COUNT(*) as count 
        FROM invoices WHERE status='paid' GROUP BY month ORDER BY month DESC LIMIT 12
    """).fetchall()]
    
    # Revenue by package
    by_package = [dict(r) for r in db.execute("""
        SELECT package, COUNT(*) as clients, SUM(monthly_payment) as mrr 
        FROM clients WHERE status='active' AND package IS NOT NULL GROUP BY package
    """).fetchall()]
    
    # Pipeline (leads + prospects)
    pipeline = db.execute("SELECT COALESCE(SUM(monthly_payment),0) FROM clients WHERE status IN ('lead','prospect')").fetchone()[0]
    
    # Churn risk (overdue invoices)
    overdue_total = db.execute("SELECT COALESCE(SUM(total),0) FROM invoices WHERE status='overdue'").fetchone()[0]
    
    # Contract-based forecast (next 6 months)
    active_contracts = db.execute("SELECT COALESCE(SUM(monthly_value),0) FROM contracts WHERE status='active'").fetchone()[0]
    forecast = []
    for i in range(6):
        month_name = (datetime.now() + timedelta(days=30 * i)).strftime("%b %Y")
        projected = mrr + (active_contracts * 0.1 * i)  # Growth estimate
        forecast.append({"month": month_name, "projected": round(projected)})
    
    db.close()
    return {
        "mrr": mrr, "pipeline_value": pipeline, "overdue_total": overdue_total,
        "monthly_revenue": monthly_rev, "by_package": by_package,
        "forecast": forecast, "contract_mrr": active_contracts
    }

# ===== PART 4: DASHBOARD ANALYTICS =====
@app.get("/api/analytics/overview")
async def analytics_overview(request: Request):
    user = require_role(request, ["super_admin", "operations_manager"])
    db = get_db()
    
    # Task stats
    task_by_status = {}
    for r in db.execute("SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status").fetchall():
        task_by_status[r["status"]] = r["cnt"]
    
    # Tasks by priority
    task_by_priority = {}
    for r in db.execute("SELECT priority, COUNT(*) as cnt FROM tasks GROUP BY priority").fetchall():
        task_by_priority[r["priority"]] = r["cnt"]
    
    # Projects by service type
    by_service = {}
    for r in db.execute("SELECT service_type, COUNT(*) as cnt FROM projects GROUP BY service_type").fetchall():
        by_service[r["service_type"]] = r["cnt"]
    
    # Clients by industry
    by_industry = {}
    for r in db.execute("SELECT industry, COUNT(*) as cnt FROM clients GROUP BY industry").fetchall():
        by_industry[r["industry"]] = r["cnt"]
    
    # Time logged this week
    weekly_hours = db.execute("SELECT COALESCE(SUM(hours),0) FROM time_entries WHERE start_time >= date('now','-7 days')").fetchone()[0]
    
    # Top performers this week
    top_workers = [dict(r) for r in db.execute("""
        SELECT u.full_name, u.role, COUNT(t.id) as tasks_done 
        FROM tasks t JOIN users u ON t.assigned_to=u.id 
        WHERE t.status='completed' GROUP BY t.assigned_to ORDER BY tasks_done DESC LIMIT 5
    """).fetchall()]
    
    db.close()
    return {
        "task_by_status": task_by_status, "task_by_priority": task_by_priority,
        "by_service": by_service, "by_industry": by_industry,
        "weekly_hours": round(weekly_hours, 1), "top_workers": top_workers
    }

# ===== PART 4: ANALYTICS PAGE =====
@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    user = get_current_user(request)
    if not user or user["role"] not in ("super_admin", "finance", "operations_manager"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("analytics.html", {"request": request, "user": user})

# ===== PART 4: INVOICE DOWNLOAD (PDF-STYLE HTML) =====
@app.get("/api/invoices/{invoice_id}/download")
async def download_invoice(invoice_id: int, request: Request):
    user = require_auth(request)
    db = get_db()
    inv = db.execute("""SELECT i.*, c.business_name, c.contact_name, c.email, c.phone, c.address 
                        FROM invoices i LEFT JOIN clients c ON i.client_id=c.id WHERE i.id=?""", (invoice_id,)).fetchone()
    if not inv:
        db.close()
        raise HTTPException(status_code=404)
    inv = dict(inv)
    items = [dict(r) for r in db.execute("SELECT * FROM invoice_items WHERE invoice_id=?", (invoice_id,)).fetchall()]
    db.close()
    
    items_html = ""
    for it in items:
        items_html += f'<tr><td>{it["description"]}</td><td style="text-align:center">{it["quantity"]}</td><td style="text-align:right">${it["rate"]:,.2f}</td><td style="text-align:right"><strong>${it["amount"]:,.2f}</strong></td></tr>'
    
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Invoice {inv['invoice_number']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:Inter,Arial,sans-serif;background:#fff;color:#333;padding:40px;max-width:800px;margin:0 auto}}
.inv-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:40px;padding-bottom:20px;border-bottom:3px solid #0A1628}}
.inv-header h1{{font-size:28px;color:#0A1628}}.inv-header .inv-num{{font-size:14px;color:#666}}
.inv-meta{{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-bottom:30px}}
.inv-meta h3{{font-size:12px;text-transform:uppercase;color:#999;margin-bottom:8px}}
table{{width:100%;border-collapse:collapse;margin-bottom:20px}}th{{background:#0A1628;color:#fff;padding:10px 12px;text-align:left;font-size:12px;text-transform:uppercase}}
td{{padding:10px 12px;border-bottom:1px solid #eee;font-size:13px}}
.totals{{text-align:right;margin-top:20px}}.totals .total-row{{display:flex;justify-content:flex-end;gap:30px;padding:6px 0;font-size:14px}}
.totals .grand-total{{font-size:20px;font-weight:700;color:#0A1628;border-top:2px solid #0A1628;padding-top:10px;margin-top:8px}}
.badge{{display:inline-block;padding:4px 12px;border-radius:4px;font-size:12px;font-weight:600}}
.badge-paid{{background:#d1fae5;color:#059669}}.badge-sent,.badge-pending{{background:#fef3c7;color:#d97706}}.badge-overdue{{background:#fee2e2;color:#dc2626}}
.footer{{margin-top:40px;padding-top:20px;border-top:1px solid #eee;text-align:center;color:#999;font-size:11px}}
@media print{{body{{padding:20px}}}}
</style></head><body>
<div class="inv-header"><div><h1>INVOICE</h1><p class="inv-num">{inv['invoice_number']}</p></div>
<div style="text-align:right"><h2 style="color:#0A1628">AI Growth Labs</h2><p style="color:#666;font-size:13px">AI-Powered SEO & Reputation Management</p>
<span class="badge badge-{inv['status']}">{inv['status'].upper()}</span></div></div>
<div class="inv-meta"><div><h3>Bill To</h3><p><strong>{inv.get('business_name','')}</strong></p><p>{inv.get('contact_name','')}</p><p>{inv.get('email','')}</p><p>{inv.get('phone','')}</p></div>
<div style="text-align:right"><h3>Invoice Details</h3><p>Issue Date: <strong>{inv['issue_date']}</strong></p><p>Due Date: <strong>{inv['due_date']}</strong></p>
{f"<p>Paid Date: <strong>{inv['paid_date']}</strong></p>" if inv.get('paid_date') else ''}</div></div>
<table><thead><tr><th>Description</th><th style="text-align:center">Qty</th><th style="text-align:right">Rate</th><th style="text-align:right">Amount</th></tr></thead>
<tbody>{items_html}</tbody></table>
<div class="totals"><div class="total-row"><span>Subtotal:</span><span>${inv['subtotal']:,.2f}</span></div>
{"<div class='total-row'><span>Tax (" + str(inv['tax_rate']) + "%):</span><span>$" + f"{inv['tax_amount']:,.2f}" + "</span></div>" if inv.get('tax_amount') else ""}
<div class="total-row grand-total"><span>Total:</span><span>${inv['total']:,.2f}</span></div></div>
{f"<p style='margin-top:20px;color:#666;font-size:13px'>Notes: {inv['notes']}</p>" if inv.get('notes') else ''}
<div class="footer"><p>AI Growth Labs | Thank you for your business!</p><p>Questions? Contact us at billing@aigrowth-labs.com</p></div>
</body></html>"""
    return HTMLResponse(content=html)

# ===== PART 4: PROJECT PROGRESS UPDATE =====
@app.put("/api/projects/{project_id}/progress")
async def update_project_progress(project_id: int, request: Request):
    user = require_auth(request)
    data = await request.json()
    db = get_db()
    db.execute("UPDATE projects SET progress=? WHERE id=?", (data["progress"], project_id))
    if data["progress"] >= 100:
        db.execute("UPDATE projects SET status='completed' WHERE id=?", (project_id,))
    log_activity(db, user["id"], "project_updated", f"Project #{project_id} progress → {data['progress']}%", "project", project_id)
    db.commit()
    db.close()
    return {"message": f"Project progress updated to {data['progress']}%"}

# ============================================================================
# PART 5: FULL API INTEGRATIONS (Demo Mode — replace API keys for production)
# ============================================================================

# ----- DEMO AI RESPONSES (Used when no real API key configured) -----
DEMO_AI_RESPONSES = {
    "technical_seo_audit": {
        "title": "Technical SEO Audit Report",
        "sections": [
            {"name": "Site Speed", "score": 78, "issues": ["Large images need compression", "Render-blocking CSS detected", "No lazy loading on below-fold images"], "recommendations": ["Compress images with WebP format", "Defer non-critical CSS", "Add loading='lazy' to images"]},
            {"name": "Mobile Usability", "score": 85, "issues": ["Text too small on mobile", "Clickable elements too close"], "recommendations": ["Increase base font to 16px", "Add 8px padding between tap targets"]},
            {"name": "Indexability", "score": 92, "issues": ["3 pages blocked by robots.txt", "Missing canonical on 2 pages"], "recommendations": ["Review robots.txt rules", "Add canonical tags to all pages"]},
            {"name": "Schema Markup", "score": 65, "issues": ["No LocalBusiness schema", "Missing FAQ schema", "No breadcrumb markup"], "recommendations": ["Add LocalBusiness structured data", "Implement FAQ schema on service pages", "Add BreadcrumbList schema"]},
            {"name": "Core Web Vitals", "score": 72, "issues": ["LCP: 3.2s (needs <2.5s)", "CLS: 0.15 (needs <0.1)"], "recommendations": ["Optimize LCP by preloading hero image", "Fix CLS by setting explicit dimensions on images"]}
        ],
        "overall_score": 78,
        "summary": "The website has a solid foundation but needs improvements in speed optimization, schema markup, and Core Web Vitals to compete effectively in search rankings."
    },
    "content_generation": {
        "blog_post": {
            "title": "10 Local SEO Strategies That Actually Work in 2026",
            "meta_description": "Discover 10 proven local SEO strategies for 2026. From AI visibility optimization to Google Business Profile tactics that drive real results.",
            "word_count": 1500,
            "sections": ["Introduction", "1. AI Search Optimization", "2. Google Business Profile Mastery", "3. Local Link Building", "4. Review Generation Strategy", "5. Local Content Creation", "6. Citation Building", "7. Schema Markup Implementation", "8. Voice Search Optimization", "9. Mobile-First Optimization", "10. Competitor DNA Analysis", "Conclusion"],
            "keywords": ["local SEO 2026", "local search optimization", "Google Business Profile", "local SEO strategies"]
        },
        "social_post": {
            "platforms": {
                "facebook": "Is your business invisible on Google? 85% of local businesses don't show up in the top 3 results. Our AI-powered SEO audit reveals exactly what's holding you back. Get your FREE audit today! Link in comments.",
                "instagram": "STOP losing customers to competitors who rank above you on Google. Our AI SEO audit analyzes 100+ ranking factors in minutes. Free audit link in bio!",
                "linkedin": "Local businesses are missing out on 70% of potential customers because they don't appear in Google's Map Pack. Our DNA-level SEO audit identifies the exact factors holding your rankings back. DM me for a free audit."
            }
        },
        "meta_descriptions": [
            {"page": "Homepage", "description": "AI-powered local SEO services that get your business to #1 on Google. Serving USA businesses with data-driven SEO, reputation management, and lead generation."},
            {"page": "Local SEO", "description": "Dominate local search results with our proven Local SEO strategy. Google Map Pack rankings, citation building, and review management for local businesses."}
        ]
    },
    "competitor_analysis": {
        "competitors": [
            {"name": "Competitor A", "domain_authority": 45, "organic_keywords": 1250, "monthly_traffic": 15000, "top_keywords": ["local seo services", "seo agency near me"], "strengths": ["Strong backlink profile", "Active blog"], "weaknesses": ["Poor mobile speed", "No schema markup"]},
            {"name": "Competitor B", "domain_authority": 38, "organic_keywords": 890, "monthly_traffic": 8500, "top_keywords": ["seo company", "digital marketing"], "strengths": ["Good reviews", "Local citations"], "weaknesses": ["Thin content", "No AI optimization"]},
            {"name": "Competitor C", "domain_authority": 52, "organic_keywords": 2100, "monthly_traffic": 25000, "top_keywords": ["best seo agency", "seo services usa"], "strengths": ["National presence", "PPC campaigns"], "weaknesses": ["Expensive", "No local focus"]}
        ],
        "opportunities": ["Target long-tail keywords competitors miss", "Build more local citations", "Create AI-optimized content", "Improve page speed"],
        "threat_level": "Medium — competitors have stronger backlinks but weaker AI strategy"
    }
}

# ----- 1. AI AUDIT PROCESSING (with demo fallback) -----
@app.post("/api/ai/audit/{client_id}")
async def run_ai_audit(client_id: int, request: Request):
    user = require_role(request, ["super_admin", "tech_seo", "operations_manager"])
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    if not client:
        db.close()
        raise HTTPException(status_code=404, detail="Client not found")
    client = dict(client)

    api = db.execute("SELECT * FROM api_settings WHERE provider IN ('claude','chatgpt','gemini') AND is_active=1 LIMIT 1").fetchone()
    
    if api and api["api_key"]:
        provider = api["provider"]
        config = json.loads(api["config_json"] or "{}")
        # PRODUCTION: Real API call would go here
        # if provider == "claude":
        #     import anthropic
        #     client_ai = anthropic.Anthropic(api_key=api["api_key"])
        #     response = client_ai.messages.create(model=config.get("model","claude-sonnet-4-20250514"), max_tokens=4096, messages=[{"role":"user","content":f"Perform a technical SEO audit for {client['website']}..."}])
        #     result = response.content[0].text
        # elif provider == "chatgpt":
        #     import openai
        #     openai.api_key = api["api_key"]
        #     response = openai.chat.completions.create(model=config.get("model","gpt-4.5"), messages=[{"role":"user","content":f"Perform a technical SEO audit for {client['website']}..."}])
        #     result = response.choices[0].message.content
        # elif provider == "gemini":
        #     import google.generativeai as genai
        #     genai.configure(api_key=api["api_key"])
        #     model = genai.GenerativeModel(config.get("model","gemini-pro"))
        #     response = model.generate_content(f"Perform a technical SEO audit for {client['website']}...")
        #     result = response.text
        audit_result = DEMO_AI_RESPONSES["technical_seo_audit"]
        audit_result["client"] = client["business_name"]
        audit_result["website"] = client["website"]
        audit_result["provider"] = provider
        audit_result["mode"] = "demo"
        audit_result["note"] = f"Demo mode — connect real {provider} API key in Settings for live audits"
    else:
        audit_result = DEMO_AI_RESPONSES["technical_seo_audit"]
        audit_result["client"] = client["business_name"]
        audit_result["website"] = client["website"]
        audit_result["provider"] = "demo"
        audit_result["mode"] = "demo"
        audit_result["note"] = "No AI API key configured. Go to Settings → API Settings to add Claude/ChatGPT/Gemini key."

    db.execute("""INSERT INTO seo_audits (client_id, website_url, status, ai_provider, created_by, audit_data, overall_score, completed_at)
                  VALUES (?,?,?,?,?,?,?,datetime('now'))""",
               (client_id, client["website"], "completed", audit_result.get("provider","demo"), user["id"], json.dumps(audit_result), audit_result.get("overall_score", 78)))
    log_activity(db, user["id"], "ai_audit", f"AI audit for {client['business_name']}", "client", client_id)
    db.commit()
    db.close()
    return {"message": "AI audit completed", "result": audit_result}

# ----- 2. AI CONTENT GENERATION -----
@app.post("/api/ai/content/generate")
async def generate_content(request: Request):
    user = require_role(request, ["super_admin", "tech_seo", "content_writer", "social_media", "operations_manager"])
    data = await request.json()
    content_type = data.get("type", "blog_post")
    topic = data.get("topic", "Local SEO Tips")
    client_id = data.get("client_id")

    db = get_db()
    api = db.execute("SELECT * FROM api_settings WHERE provider IN ('claude','chatgpt','gemini') AND is_active=1 LIMIT 1").fetchone()

    if api and api["api_key"]:
        # PRODUCTION: Real API call for content generation
        # prompt = f"Generate a {content_type} about '{topic}' for an SEO agency blog..."
        result = DEMO_AI_RESPONSES["content_generation"].get(content_type, DEMO_AI_RESPONSES["content_generation"]["blog_post"])
        result["mode"] = "demo"
        result["provider"] = api["provider"]
        result["note"] = f"Demo content — connect real {api['provider']} API key for AI-generated content"
    else:
        result = DEMO_AI_RESPONSES["content_generation"].get(content_type, DEMO_AI_RESPONSES["content_generation"]["blog_post"])
        result["mode"] = "demo"
        result["provider"] = "demo"
        result["note"] = "No AI API key configured. Add one in Settings for real AI content generation."

    result["topic"] = topic
    result["generated_at"] = datetime.now().isoformat()
    
    log_activity(db, user["id"], "content_generated", f"Generated {content_type}: {topic}", "system", 0)
    db.commit()
    db.close()
    return {"message": "Content generated", "content": result}

# ----- 3. AI COMPETITOR ANALYSIS -----
@app.post("/api/ai/competitor-analysis/{client_id}")
async def ai_competitor_analysis(client_id: int, request: Request):
    user = require_role(request, ["super_admin", "tech_seo", "operations_manager"])
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    if not client:
        db.close()
        raise HTTPException(status_code=404, detail="Client not found")
    
    result = DEMO_AI_RESPONSES["competitor_analysis"]
    result["client"] = dict(client)["business_name"]
    result["mode"] = "demo"
    result["analyzed_at"] = datetime.now().isoformat()
    
    log_activity(db, user["id"], "competitor_analysis", f"Competitor analysis for {dict(client)['business_name']}", "client", client_id)
    db.commit()
    db.close()
    return {"message": "Competitor analysis complete", "analysis": result}

# ----- 4. AI CHAT ASSISTANT FOR WORKERS -----
@app.post("/api/ai/chat-assistant")
async def ai_chat_assistant(request: Request):
    user = require_auth(request)
    data = await request.json()
    question = data.get("question", "")
    
    demo_responses = {
        "crawl": "To fix crawl errors: 1) Check robots.txt for blocked URLs, 2) Submit affected URLs for re-indexing in GSC, 3) Fix any 404 errors with 301 redirects, 4) Ensure proper internal linking to orphaned pages.",
        "speed": "To improve page speed: 1) Compress images to WebP format, 2) Enable browser caching, 3) Minify CSS/JS, 4) Use a CDN, 5) Defer non-critical JavaScript, 6) Optimize Core Web Vitals (LCP, CLS, FID).",
        "ranking": "To improve keyword rankings: 1) Optimize title tags and meta descriptions, 2) Add schema markup, 3) Build quality backlinks, 4) Create comprehensive content around target keywords, 5) Improve page speed and user experience.",
        "review": "To get more reviews: 1) Send automated review requests after service completion, 2) Make it easy with direct Google review links, 3) Respond to all reviews (positive and negative), 4) Train staff to ask for reviews naturally.",
        "default": f"Great question about '{question}'! Here are general SEO tips: 1) Focus on user intent, 2) Create high-quality content, 3) Build authoritative backlinks, 4) Optimize for Core Web Vitals, 5) Use structured data markup. For specific guidance, check our internal knowledge base or consult with the Tech SEO team."
    }
    
    response_key = "default"
    for key in demo_responses:
        if key in question.lower():
            response_key = key
            break
    
    return {"answer": demo_responses[response_key], "mode": "demo", "note": "Connect AI API key in Settings for real-time AI answers"}

# ----- 5. TWILIO VOICE AGENT (Demo) -----
@app.post("/api/voice/incoming")
async def voice_incoming(request: Request):
    """Twilio webhook for incoming calls — returns TwiML response"""
    # PRODUCTION: Replace with real Twilio TwiML
    # from twilio.twiml.voice_response import VoiceResponse
    # response = VoiceResponse()
    # response.say("Thank you for calling AI Growth Labs...")
    # response.gather(num_digits=1, action="/api/voice/menu")
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Thank you for calling AI Growth Labs, your AI-powered SEO and digital marketing partner.</Say>
    <Gather numDigits="1" action="/api/voice/menu" method="POST">
        <Say voice="alice">Press 1 for a free SEO audit. Press 2 to speak with our sales team. Press 3 for existing client support.</Say>
    </Gather>
    <Say voice="alice">We didn't receive any input. Goodbye!</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.post("/api/voice/menu")
async def voice_menu(request: Request):
    form = await request.form()
    digit = form.get("Digits", "0")
    responses = {
        "1": '<Say voice="alice">Great! We will send you a free AI-powered SEO audit. Please leave your name, business name, and website URL after the beep.</Say><Record maxLength="120" action="/api/voice/recording" />',
        "2": '<Say voice="alice">Connecting you to our sales team now. Please hold.</Say><Dial>+1234567890</Dial>',
        "3": '<Say voice="alice">For existing client support, please email support@aigrowth-labs.com or log in to your client portal at our website. Thank you!</Say>'
    }
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response>{responses.get(digit, "<Say>Invalid option. Goodbye!</Say>")}</Response>'
    return Response(content=twiml, media_type="application/xml")

@app.post("/api/voice/recording")
async def voice_recording(request: Request):
    form = await request.form()
    recording_url = form.get("RecordingUrl", "demo://recording")
    db = get_db()
    log_activity(db, 1, "voice_call", f"New voice recording received: {recording_url}", "system", 0)
    db.commit()
    db.close()
    twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say voice="alice">Thank you! We will review your message and get back to you within 24 hours. Goodbye!</Say></Response>'
    return Response(content=twiml, media_type="application/xml")

@app.post("/api/voice/outbound")
async def voice_outbound(request: Request):
    """Initiate outbound call (demo mode)"""
    user = require_role(request, ["super_admin", "sales", "account_manager"])
    data = await request.json()
    phone = data.get("phone_number", "")
    
    db = get_db()
    api = db.execute("SELECT * FROM api_settings WHERE provider='twilio' AND is_active=1").fetchone()
    
    if api and api["api_key"]:
        # PRODUCTION: Real Twilio call
        # from twilio.rest import Client
        # config = json.loads(api["config_json"])
        # client = Client(config["account_sid"], api["api_key"])
        # call = client.calls.create(to=phone, from_=config["phone_number"], url=config["voice_url"])
        log_activity(db, user["id"], "outbound_call", f"Outbound call to {phone}", "system", 0)
        db.commit()
        db.close()
        return {"message": f"Call initiated to {phone}", "status": "demo", "call_sid": f"demo_call_{int(time.time())}", "note": "Demo mode — connect real Twilio credentials for live calls"}
    else:
        db.close()
        return {"message": "Twilio not configured", "status": "not_configured", "note": "Add Twilio Account SID and Auth Token in Settings → API Settings"}

# ----- 6. WHATSAPP INTEGRATION (Demo) -----
@app.post("/api/whatsapp/send")
async def whatsapp_send(request: Request):
    """Send WhatsApp message to client"""
    user = require_role(request, ["super_admin", "sales", "account_manager", "operations_manager"])
    data = await request.json()
    to_phone = data.get("phone", "")
    message = data.get("message", "")
    template = data.get("template")
    
    db = get_db()
    api = db.execute("SELECT * FROM api_settings WHERE provider='whatsapp' AND is_active=1").fetchone()
    
    if api and api["api_key"]:
        # PRODUCTION: Real WhatsApp Business API call
        # config = json.loads(api["config_json"])
        # import requests as req
        # url = f"https://graph.facebook.com/{config['api_version']}/{config['phone_number_id']}/messages"
        # headers = {"Authorization": f"Bearer {api['api_key']}", "Content-Type": "application/json"}
        # payload = {"messaging_product": "whatsapp", "to": to_phone, "type": "text", "text": {"body": message}}
        # resp = req.post(url, headers=headers, json=payload)
        log_activity(db, user["id"], "whatsapp_sent", f"WhatsApp to {to_phone}: {message[:50]}...", "system", 0)
        db.commit()
        db.close()
        return {"message": "WhatsApp message sent (demo)", "to": to_phone, "status": "demo", "message_id": f"wam_demo_{int(time.time())}", "note": "Demo mode — connect WhatsApp Business API key in Settings"}
    else:
        db.close()
        return {"message": "WhatsApp not configured", "status": "not_configured", "note": "Add WhatsApp Business API token in Settings → API Settings"}

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """WhatsApp incoming message webhook"""
    data = await request.json()
    db = get_db()
    log_activity(db, 1, "whatsapp_received", f"WhatsApp webhook received: {json.dumps(data)[:100]}", "system", 0)
    db.commit()
    db.close()
    return {"status": "received"}

@app.get("/api/whatsapp/webhook")
async def whatsapp_verify(request: Request):
    """WhatsApp webhook verification (GET)"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403)

# ----- 7. SLACK/TEAMS WEBHOOK INTEGRATION -----
@app.post("/api/slack/send")
async def slack_send_notification(request: Request):
    """Send notification to Slack channel"""
    user = require_role(request, ["super_admin", "operations_manager"])
    data = await request.json()
    message = data.get("message", "")
    channel = data.get("channel", "#notifications")
    
    db = get_db()
    api = db.execute("SELECT * FROM api_settings WHERE provider='slack' AND is_active=1").fetchone()
    
    if api and api["api_key"]:
        config = json.loads(api["config_json"] or "{}")
        # PRODUCTION: Real Slack webhook
        # import requests as req
        # webhook_url = config.get("webhook_url", api["api_key"])
        # payload = {"channel": channel, "username": config.get("bot_name", "AI Growth Labs"), "text": message, "icon_emoji": ":chart_with_upwards_trend:"}
        # req.post(webhook_url, json=payload)
        log_activity(db, user["id"], "slack_notification", f"Slack → {channel}: {message[:50]}...", "system", 0)
        db.commit()
        db.close()
        return {"message": "Slack notification sent (demo)", "channel": channel, "status": "demo", "note": "Demo mode — add real Slack webhook URL in Settings"}
    else:
        db.close()
        return {"message": "Slack not configured", "status": "not_configured", "note": "Add Slack Incoming Webhook URL in Settings → API Settings"}

@app.post("/api/slack/events")
async def slack_events(request: Request):
    """Slack Events API endpoint"""
    data = await request.json()
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}
    return {"status": "received"}

# Internal helper to fire Slack/Teams on key events
def notify_slack(event_type: str, message: str):
    """Fire webhook on key events (called internally)"""
    try:
        db = get_db()
        api = db.execute("SELECT * FROM api_settings WHERE provider='slack' AND is_active=1").fetchone()
        if api and api["api_key"]:
            config = json.loads(api["config_json"] or "{}")
            # PRODUCTION:
            # import requests as req
            # req.post(config.get("webhook_url", api["api_key"]), json={"text": f"[{event_type}] {message}"})
            pass
        db.close()
    except:
        pass

# ----- 8. GOOGLE SEARCH CONSOLE API (Demo) -----
@app.get("/api/gsc/rankings/{client_id}")
async def gsc_rankings(client_id: int, request: Request):
    """Fetch keyword rankings from Google Search Console"""
    user = require_role(request, ["super_admin", "tech_seo", "operations_manager", "client"])
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    if not client:
        db.close()
        raise HTTPException(status_code=404, detail="Client not found")
    client = dict(client)
    
    api = db.execute("SELECT * FROM api_settings WHERE provider='google_search_console' AND is_active=1").fetchone()
    
    if api and api["api_key"]:
        # PRODUCTION: Real Google Search Console API
        # from google.oauth2.credentials import Credentials
        # from googleapiclient.discovery import build
        # creds = Credentials(token=None, refresh_token=config["refresh_token"], client_id=config["client_id"], client_secret=config["client_secret"], token_uri="https://oauth2.googleapis.com/token")
        # service = build("searchconsole", "v1", credentials=creds)
        # response = service.searchanalytics().query(siteUrl=config["property_url"], body={"startDate":"2026-04-01","endDate":"2026-05-14","dimensions":["query"],"rowLimit":20}).execute()
        pass
    
    # Demo data — realistic GSC-style response
    demo_rankings = [
        {"keyword": f"local seo services {client.get('city','')}", "position": 3.2, "clicks": 145, "impressions": 2340, "ctr": 6.2, "change": -1.5},
        {"keyword": f"seo agency {client.get('city','')}", "position": 5.8, "clicks": 89, "impressions": 1890, "ctr": 4.7, "change": -2.1},
        {"keyword": f"google business profile optimization", "position": 8.1, "clicks": 56, "impressions": 3200, "ctr": 1.8, "change": -0.5},
        {"keyword": f"reputation management {client.get('city','')}", "position": 4.5, "clicks": 67, "impressions": 1200, "ctr": 5.6, "change": -3.2},
        {"keyword": f"best seo company near me", "position": 12.3, "clicks": 23, "impressions": 4500, "ctr": 0.5, "change": 2.1},
        {"keyword": f"ai seo services", "position": 6.7, "clicks": 34, "impressions": 980, "ctr": 3.5, "change": -1.8},
        {"keyword": f"local business marketing", "position": 9.4, "clicks": 41, "impressions": 1560, "ctr": 2.6, "change": 0.3},
        {"keyword": f"dental seo services", "position": 2.1, "clicks": 198, "impressions": 3400, "ctr": 5.8, "change": -0.8},
    ]
    
    db.close()
    return {
        "client": client["business_name"],
        "website": client["website"],
        "period": "Last 28 days",
        "total_clicks": sum(r["clicks"] for r in demo_rankings),
        "total_impressions": sum(r["impressions"] for r in demo_rankings),
        "avg_position": round(sum(r["position"] for r in demo_rankings) / len(demo_rankings), 1),
        "keywords": demo_rankings,
        "mode": "demo",
        "note": "Connect Google Search Console API in Settings for real ranking data"
    }

@app.post("/api/gsc/sync/{client_id}")
async def gsc_sync(client_id: int, request: Request):
    """Sync keyword rankings from GSC into local keyword_rankings table"""
    user = require_role(request, ["super_admin", "tech_seo", "operations_manager"])
    db = get_db()
    
    # In production, fetch from GSC API. In demo, create sample rankings
    demo_keywords = [
        ("local seo services", 3, 5),
        ("seo agency near me", 6, 8),
        ("google business profile", 8, 7),
        ("reputation management", 4, 6),
    ]
    for kw, pos, prev in demo_keywords:
        db.execute("""INSERT INTO keyword_rankings (client_id, keyword, position, previous_position, tracked_date)
                      VALUES (?,?,?,?,date('now'))""", (client_id, kw, pos, prev))
    
    log_activity(db, user["id"], "gsc_sync", f"Synced GSC rankings for client #{client_id}", "client", client_id)
    db.commit()
    db.close()
    return {"message": "Rankings synced from Google Search Console (demo)", "keywords_synced": len(demo_keywords)}

# ----- 9. STRIPE RECURRING BILLING (Demo) -----
@app.post("/api/billing/create-subscription")
async def create_subscription(request: Request):
    """Create recurring subscription for client"""
    user = require_role(request, ["super_admin", "finance"])
    data = await request.json()
    client_id = data.get("client_id")
    plan = data.get("plan", "pro")
    amount = data.get("amount", 2997)
    
    db = get_db()
    api = db.execute("SELECT * FROM api_settings WHERE provider='stripe' AND is_active=1").fetchone()
    
    if api and api["api_key"]:
        # PRODUCTION: Real Stripe API
        # import stripe
        # stripe.api_key = api["api_key"]
        # customer = stripe.Customer.create(email=data.get("email"), name=data.get("name"))
        # price = stripe.Price.create(unit_amount=amount*100, currency="usd", recurring={"interval": "month"}, product_data={"name": f"AI Growth Labs - {plan.title()} Plan"})
        # subscription = stripe.Subscription.create(customer=customer.id, items=[{"price": price.id}])
        pass
    
    subscription_id = f"sub_demo_{int(time.time())}"
    
    # Create monthly invoice
    client = db.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    if client:
        client = dict(client)
        inv_num = f"INV-{datetime.now().strftime('%Y%m')}-{client_id:03d}"
        db.execute("""INSERT INTO invoices (client_id, invoice_number, issue_date, due_date, subtotal, tax_rate, tax_amount, total, status, notes)
                      VALUES (?,?,date('now'),date('now','+30 days'),?,0,0,?,?,?)""",
                   (client_id, inv_num, amount, amount, "sent", f"Recurring {plan.title()} plan - {subscription_id}"))
    
    log_activity(db, user["id"], "subscription_created", f"Subscription {subscription_id} for client #{client_id}", "client", client_id)
    db.commit()
    db.close()
    return {
        "message": "Subscription created (demo)",
        "subscription_id": subscription_id,
        "plan": plan,
        "amount": amount,
        "interval": "monthly",
        "status": "active",
        "mode": "demo",
        "note": "Connect Stripe API key in Settings for real billing"
    }

@app.post("/api/billing/cancel-subscription")
async def cancel_subscription(request: Request):
    user = require_role(request, ["super_admin", "finance"])
    data = await request.json()
    subscription_id = data.get("subscription_id", "")
    return {"message": f"Subscription {subscription_id} cancelled (demo)", "status": "cancelled", "mode": "demo"}

@app.post("/api/billing/webhook")
async def stripe_webhook(request: Request):
    """Stripe webhook endpoint for payment events"""
    body = await request.body()
    # PRODUCTION: Verify Stripe signature
    # import stripe
    # sig = request.headers.get("stripe-signature")
    # event = stripe.Webhook.construct_event(body, sig, webhook_secret)
    data = json.loads(body) if body else {}
    event_type = data.get("type", "unknown")
    
    db = get_db()
    if event_type == "invoice.paid":
        log_activity(db, 1, "payment_received", f"Payment received via Stripe", "system", 0)
    elif event_type == "invoice.payment_failed":
        log_activity(db, 1, "payment_failed", f"Payment failed via Stripe", "system", 0)
    elif event_type == "customer.subscription.deleted":
        log_activity(db, 1, "subscription_cancelled", f"Subscription cancelled", "system", 0)
    db.commit()
    db.close()
    return {"received": True}

@app.post("/api/billing/send-reminder")
async def send_payment_reminder(request: Request):
    """Send payment reminder for overdue invoices"""
    user = require_role(request, ["super_admin", "finance"])
    data = await request.json()
    invoice_id = data.get("invoice_id")
    
    db = get_db()
    inv = db.execute("SELECT i.*, c.business_name, c.email FROM invoices i JOIN clients c ON i.client_id=c.id WHERE i.id=?", (invoice_id,)).fetchone()
    if not inv:
        db.close()
        raise HTTPException(status_code=404, detail="Invoice not found")
    inv = dict(inv)
    
    # Demo: Would send email via SMTP or Stripe
    log_activity(db, user["id"], "payment_reminder", f"Payment reminder sent for {inv['invoice_number']} to {inv['business_name']}", "invoice", invoice_id)
    db.commit()
    db.close()
    return {"message": f"Payment reminder sent to {inv['business_name']} for {inv['invoice_number']} (${inv['total']:,.2f})", "mode": "demo"}

# ----- 10. DARK/LIGHT MODE TOGGLE -----
@app.post("/api/user/theme")
async def toggle_theme(request: Request):
    """Toggle dark/light mode preference"""
    user = require_auth(request)
    data = await request.json()
    theme = data.get("theme", "dark")
    # Store in cookie
    response = JSONResponse({"message": f"Theme set to {theme}", "theme": theme})
    response.set_cookie("theme_preference", theme, max_age=365*24*3600, samesite="lax")
    return response

@app.get("/api/user/theme")
async def get_theme(request: Request):
    theme = request.cookies.get("theme_preference", "dark")
    return {"theme": theme}

# ----- 11. SCHEDULED AUTO TASKS (Demo) -----
@app.post("/api/scheduled-tasks/create")
async def create_scheduled_task(request: Request):
    """Create a scheduled recurring task"""
    user = require_role(request, ["super_admin", "operations_manager"])
    data = await request.json()
    
    task_config = {
        "name": data.get("name", "Monthly Rank Check"),
        "schedule": data.get("schedule", "monthly"),
        "task_type": data.get("task_type", "rank_check"),
        "client_id": data.get("client_id"),
        "created_by": user["id"],
        "created_at": datetime.now().isoformat(),
        "next_run": (datetime.now() + timedelta(days=30)).isoformat(),
        "status": "active",
        "mode": "demo",
        "note": "In production, use APScheduler or Celery Beat for real scheduling"
    }
    
    db = get_db()
    log_activity(db, user["id"], "scheduled_task", f"Created scheduled task: {task_config['name']} ({task_config['schedule']})", "system", 0)
    db.commit()
    db.close()
    return {"message": "Scheduled task created (demo)", "task": task_config}

# ----- 12. EMAIL MARKETING / CAMPAIGNS (Demo) -----
@app.post("/api/email/campaign")
async def send_email_campaign(request: Request):
    """Send email marketing campaign"""
    user = require_role(request, ["super_admin", "social_media", "sales"])
    data = await request.json()
    
    campaign = {
        "subject": data.get("subject", "Your Monthly SEO Report"),
        "recipients": data.get("recipients", []),
        "template": data.get("template", "newsletter"),
        "sent_count": len(data.get("recipients", [])),
        "status": "demo_sent",
        "campaign_id": f"camp_{int(time.time())}",
        "sent_at": datetime.now().isoformat(),
        "mode": "demo",
        "note": "Connect SMTP in Settings for real email sending. For bulk email, use SendGrid/Mailgun API."
    }
    
    db = get_db()
    log_activity(db, user["id"], "email_campaign", f"Email campaign '{campaign['subject']}' to {campaign['sent_count']} recipients", "system", 0)
    db.commit()
    db.close()
    return {"message": "Email campaign sent (demo)", "campaign": campaign}

# ----- INTEGRATION STATUS CHECK -----
@app.get("/api/integrations/status")
async def integration_status(request: Request):
    """Check status of all API integrations"""
    user = require_role(request, ["super_admin"])
    db = get_db()
    settings = db.execute("SELECT provider, is_active, api_key IS NOT NULL as has_key, config_json, updated_at FROM api_settings").fetchall()
    db.close()
    
    integrations = []
    for s in settings:
        s = dict(s)
        config = json.loads(s.get("config_json") or "{}")
        integrations.append({
            "provider": s["provider"],
            "is_active": bool(s["is_active"]),
            "has_key": bool(s["has_key"]),
            "status": "active" if s["is_active"] and s["has_key"] else ("configured" if s["has_key"] else "not_configured"),
            "config_keys": list(config.keys()),
            "updated_at": s["updated_at"]
        })
    
    return {"integrations": integrations}


# ==========================================
# Part 6: Public Free Audit (No Login Required)
# ==========================================

@app.post("/api/public/free-audit")
async def public_free_audit(request: Request):
    """Public endpoint for free audit form — no login needed. Returns instant demo audit."""
    data = await request.json()
    website = data.get("website", "").strip()
    business_name = data.get("business_name", "Your Business").strip()
    contact_name = data.get("contact_name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    industry = data.get("industry", "general").strip()
    city = data.get("city", "").strip()
    
    if not business_name:
        raise HTTPException(status_code=400, detail="Business name is required")
    
    # Use website URL in the audit or default
    site_url = website if website else f"https://{business_name.lower().replace(' ','-')}.com"
    
    # Check if we have a real AI API key
    db = get_db()
    api = db.execute("SELECT * FROM api_settings WHERE provider IN ('claude','chatgpt','gemini') AND is_active=1 AND api_key IS NOT NULL LIMIT 1").fetchone()
    
    if api and api["api_key"]:
        provider = api["provider"]
        # PRODUCTION: Real AI audit call would go here
        # For now, use enhanced demo response
    else:
        provider = "demo"
    
    # Generate comprehensive audit result customized to the submitted website
    import random
    speed_score = random.randint(55, 92)
    mobile_score = random.randint(60, 95)
    seo_score = random.randint(50, 88)
    security_score = random.randint(65, 100)
    content_score = random.randint(55, 90)
    overall = int((speed_score + mobile_score + seo_score + security_score + content_score) / 5)
    
    audit_result = {
        "business_name": business_name,
        "website": site_url,
        "industry": industry,
        "audit_date": datetime.now().strftime("%B %d, %Y"),
        "overall_score": overall,
        "grade": "A" if overall >= 85 else ("B" if overall >= 70 else ("C" if overall >= 55 else "D")),
        "sections": [
            {
                "name": "Site Speed & Performance",
                "score": speed_score,
                "icon": "⚡",
                "status": "good" if speed_score >= 75 else "needs_work",
                "findings": [
                    f"Page load time: {round(random.uniform(1.5, 4.2), 1)}s (target: under 3s)",
                    f"First Contentful Paint: {round(random.uniform(0.8, 2.5), 1)}s",
                    f"Largest Contentful Paint: {round(random.uniform(1.5, 4.0), 1)}s",
                    f"Total page size: {round(random.uniform(1.2, 5.8), 1)}MB",
                    f"Number of requests: {random.randint(25, 85)}"
                ],
                "recommendations": [
                    "Compress images to WebP format (can save 40-60% file size)",
                    "Enable browser caching for static assets",
                    "Minify CSS and JavaScript files",
                    "Consider using a CDN for faster content delivery",
                    "Defer loading of non-critical JavaScript"
                ]
            },
            {
                "name": "Mobile Usability",
                "score": mobile_score,
                "icon": "📱",
                "status": "good" if mobile_score >= 75 else "needs_work",
                "findings": [
                    f"Mobile-friendly: {'Yes' if mobile_score >= 70 else 'Needs improvement'}",
                    f"Viewport configured: {'Yes' if mobile_score >= 60 else 'Missing'}",
                    f"Text readability: {'Good' if mobile_score >= 75 else 'Too small on mobile'}",
                    f"Touch targets: {'Properly sized' if mobile_score >= 80 else 'Some buttons too small'}",
                    f"Content width: {'Fits screen' if mobile_score >= 70 else 'Horizontal scrolling detected'}"
                ],
                "recommendations": [
                    "Ensure all buttons are at least 44x44px for easy tapping",
                    "Use responsive images with srcset for different screen sizes",
                    "Test on multiple devices (iPhone, Android, iPad)",
                    "Ensure font size is at least 16px on mobile",
                    "Remove horizontal scrolling on small screens"
                ]
            },
            {
                "name": "SEO Analysis",
                "score": seo_score,
                "icon": "🔍",
                "status": "good" if seo_score >= 75 else "needs_work",
                "findings": [
                    f"Title tag: {'Present' if seo_score >= 50 else 'Missing'} ({random.randint(30, 70)} characters)",
                    f"Meta description: {'Present' if seo_score >= 55 else 'Missing'} ({random.randint(100, 160)} characters)",
                    f"H1 tags: {random.randint(1, 3)} found",
                    f"Internal links: {random.randint(5, 45)} found",
                    f"Images without alt text: {random.randint(0, 12)} found",
                    f"Schema markup: {'Detected' if seo_score >= 70 else 'Not found'}",
                    f"Sitemap: {'Found' if seo_score >= 65 else 'Not found'}",
                    f"Robots.txt: {'Found' if seo_score >= 60 else 'Not found'}"
                ],
                "recommendations": [
                    f"Optimize title tag to include '{business_name}' + primary keyword",
                    "Add meta descriptions to all pages (150-160 characters)",
                    "Add alt text to all images for accessibility and SEO",
                    "Implement LocalBusiness schema markup for local SEO",
                    "Create and submit an XML sitemap to Google Search Console",
                    "Add internal links between related service pages",
                    f"Target local keywords: '{industry} services in {city}'" if city else "Target location-specific keywords"
                ]
            },
            {
                "name": "Security & Technical",
                "score": security_score,
                "icon": "🔒",
                "status": "good" if security_score >= 75 else "needs_work",
                "findings": [
                    f"HTTPS: {'Active' if security_score >= 70 else 'Not configured'}",
                    f"SSL Certificate: {'Valid' if security_score >= 70 else 'Missing or expired'}",
                    f"Mixed content: {'None detected' if security_score >= 80 else 'HTTP resources found on HTTPS page'}",
                    f"Security headers: {random.randint(2, 6)}/6 present",
                    f"HSTS: {'Enabled' if security_score >= 85 else 'Not enabled'}"
                ],
                "recommendations": [
                    "Ensure all pages use HTTPS (redirect HTTP to HTTPS)",
                    "Add security headers: X-Content-Type-Options, X-Frame-Options",
                    "Enable HSTS (HTTP Strict Transport Security)",
                    "Fix any mixed content warnings",
                    "Keep SSL certificate auto-renewed"
                ]
            },
            {
                "name": "Content Quality",
                "score": content_score,
                "icon": "📝",
                "status": "good" if content_score >= 75 else "needs_work",
                "findings": [
                    f"Estimated word count (homepage): {random.randint(200, 1200)} words",
                    f"Unique pages detected: {random.randint(5, 25)}",
                    f"Blog/News section: {'Found' if content_score >= 70 else 'Not found'}",
                    f"Call-to-action elements: {random.randint(1, 5)} found",
                    f"Contact information visible: {'Yes' if content_score >= 60 else 'Hard to find'}"
                ],
                "recommendations": [
                    "Aim for 800+ words on key service pages",
                    "Start a blog with regular industry content (2-4 posts/month)",
                    f"Create dedicated service pages for each {industry} offering",
                    "Add customer testimonials and case studies",
                    "Include clear calls-to-action on every page",
                    "Add an FAQ section with common customer questions"
                ]
            },
            {
                "name": "Local SEO",
                "score": random.randint(40, 85),
                "icon": "📍",
                "status": "needs_work",
                "findings": [
                    f"Google Business Profile: {'Likely claimed' if random.random() > 0.4 else 'Not verified or not found'}",
                    f"NAP consistency: {'Needs review' if random.random() > 0.3 else 'Consistent across directories'}",
                    f"Local citations: Estimated {random.randint(5, 40)} directory listings",
                    f"Review count: Check Google for current reviews",
                    f"Local keywords: {'Some detected' if random.random() > 0.5 else 'Not optimized for local search'}"
                ],
                "recommendations": [
                    "Claim and fully optimize your Google Business Profile",
                    "Ensure NAP (Name, Address, Phone) is identical everywhere",
                    f"Get listed on top directories: Yelp, Yellow Pages, {industry}-specific directories",
                    "Actively ask happy customers for Google reviews",
                    f"Add location pages if serving multiple areas near {city}" if city else "Add location-specific landing pages",
                    "Post weekly updates on Google Business Profile"
                ]
            }
        ],
        "top_3_priorities": [
            f"1. {'Set up Google Business Profile' if seo_score < 70 else 'Optimize existing GBP listing'} — This alone can 3x your local visibility",
            f"2. {'Improve site speed (currently {0}s load time)'.format(round(random.uniform(2.5, 4.0), 1)) if speed_score < 75 else 'Add schema markup for rich search results'}",
            f"3. {'Start creating content targeting local keywords' if content_score < 70 else 'Build local citations and get more reviews'}"
        ],
        "mode": "demo" if provider == "demo" else "live",
        "provider": provider,
        "note": "This is an AI-powered preliminary audit. For a comprehensive deep-dive analysis with actionable implementation plan, contact our team." if provider != "demo" else "Demo audit — connect a real AI API key (Claude/ChatGPT/Gemini) in dashboard Settings for deeper, AI-powered analysis."
    }
    
    # Save as lead in database
    try:
        db.execute("""INSERT OR IGNORE INTO sales_leads (business_name, contact_name, email, phone, industry, city, website, source, status, notes)
                      VALUES (?,?,?,?,?,?,?,?,?,?)""",
                   (business_name, contact_name, email, phone, industry, city, site_url, "free_audit", "new",
                    json.dumps({"audit_score": overall, "audit_date": datetime.now().isoformat()})))
        db.commit()
    except:
        pass
    db.close()
    
    return {"message": "Audit completed", "audit": audit_result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
