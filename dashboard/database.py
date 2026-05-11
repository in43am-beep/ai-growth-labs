"""Database module using SQLite for the Agency OS"""
import sqlite3
import json
import os
from datetime import datetime
from passlib.hash import bcrypt

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "agency.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Users table with role-based access
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        role TEXT NOT NULL CHECK(role IN ('super_admin','worker','tech_seo','social_media','finance','sales')),
        rank TEXT DEFAULT 'junior',
        salary REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        last_login TEXT
    )''')
    
    # Clients table
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name TEXT NOT NULL,
        contact_name TEXT,
        email TEXT,
        phone TEXT,
        website TEXT,
        industry TEXT,
        location TEXT,
        status TEXT DEFAULT 'lead' CHECK(status IN ('lead','prospect','active','completed','churned')),
        package TEXT,
        monthly_payment REAL DEFAULT 0,
        notes TEXT,
        source TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        title TEXT NOT NULL,
        description TEXT,
        service_type TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','in_progress','review','completed','paused')),
        priority TEXT DEFAULT 'medium' CHECK(priority IN ('low','medium','high','urgent')),
        assigned_worker_id INTEGER REFERENCES users(id),
        team_leader_id INTEGER REFERENCES users(id),
        progress INTEGER DEFAULT 0,
        start_date TEXT,
        due_date TEXT,
        completed_date TEXT,
        upsell_opportunities TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Tasks table
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER REFERENCES projects(id),
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','in_progress','completed','blocked')),
        assigned_to INTEGER REFERENCES users(id),
        priority TEXT DEFAULT 'medium',
        due_date TEXT,
        completed_date TEXT,
        order_num INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        title TEXT NOT NULL,
        message TEXT,
        type TEXT DEFAULT 'info' CHECK(type IN ('info','warning','success','task','urgent')),
        is_read INTEGER DEFAULT 0,
        link TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # SEO Audits table
    c.execute('''CREATE TABLE IF NOT EXISTS seo_audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        website_url TEXT NOT NULL,
        audit_data TEXT,
        overall_score INTEGER,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','processing','completed','failed')),
        report_pdf_path TEXT,
        ai_provider TEXT,
        created_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now')),
        completed_at TEXT
    )''')
    
    # Expenses table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL CHECK(category IN ('salary','tools','marketing','office','other')),
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT DEFAULT (date('now')),
        approved_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Payments table (client payments)
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','paid','overdue','refunded')),
        due_date TEXT,
        paid_date TEXT,
        invoice_number TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Sales leads table
    c.execute('''CREATE TABLE IF NOT EXISTS sales_leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name TEXT NOT NULL,
        contact_name TEXT,
        email TEXT,
        phone TEXT,
        website TEXT,
        industry TEXT,
        location TEXT,
        source TEXT CHECK(source IN ('google_search','google_maps','linkedin','facebook','apify','referral','website','other')),
        status TEXT DEFAULT 'new' CHECK(status IN ('new','contacted','qualified','proposal_sent','negotiating','won','lost')),
        assigned_to INTEGER REFERENCES users(id),
        proposal_data TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Social media posts table
    c.execute('''CREATE TABLE IF NOT EXISTS social_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        platform TEXT NOT NULL CHECK(platform IN ('facebook','instagram','tiktok','linkedin','twitter','pinterest','youtube')),
        content TEXT,
        media_url TEXT,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','scheduled','published','failed')),
        scheduled_date TEXT,
        published_date TEXT,
        engagement_data TEXT,
        created_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Chat messages (from website chatbot)
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        visitor_name TEXT,
        visitor_email TEXT,
        visitor_phone TEXT,
        business_name TEXT,
        industry TEXT,
        location TEXT,
        website_url TEXT,
        messages TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active','converted','closed')),
        assigned_to INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Activity log
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        action TEXT NOT NULL,
        details TEXT,
        entity_type TEXT,
        entity_id INTEGER,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Create default super admin user
    try:
        admin_hash = bcrypt.hash("admin123")
        c.execute('''INSERT OR IGNORE INTO users (username, password_hash, full_name, email, role, rank, salary) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  ('admin', admin_hash, 'Super Administrator', 'admin@aigrowth-labs.com', 'super_admin', 'director', 0))
    except Exception:
        pass
    
    # Insert demo data
    _insert_demo_data(c)
    
    conn.commit()
    conn.close()

def _insert_demo_data(c):
    """Insert demo data for showcase"""
    try:
        # Check if demo data already exists
        c.execute("SELECT COUNT(*) FROM clients")
        if c.fetchone()[0] > 0:
            return
        
        # Demo workers
        workers = [
            ('sarah_k', 'Sarah Kim', 'sarah@aigrowth-labs.com', 'tech_seo', 'senior', 5500),
            ('alex_r', 'Alex Rodriguez', 'alex@aigrowth-labs.com', 'tech_seo', 'lead', 7000),
            ('emily_p', 'Emily Parker', 'emily@aigrowth-labs.com', 'worker', 'senior', 5000),
            ('david_w', 'David Washington', 'david@aigrowth-labs.com', 'worker', 'mid', 4000),
            ('lisa_c', 'Lisa Chen', 'lisa@aigrowth-labs.com', 'sales', 'senior', 5500),
            ('marcus_j', 'Marcus Johnson', 'marcus@aigrowth-labs.com', 'social_media', 'mid', 4500),
            ('rachel_g', 'Rachel Green', 'rachel@aigrowth-labs.com', 'finance', 'senior', 5500),
        ]
        pw = bcrypt.hash("password123")
        for uname, name, email, role, rank, salary in workers:
            c.execute('INSERT OR IGNORE INTO users (username, password_hash, full_name, email, role, rank, salary) VALUES (?,?,?,?,?,?,?)',
                      (uname, pw, name, email, role, rank, salary))
        
        # Demo clients
        clients = [
            ('SmileBright Dental', 'Dr. Robert Chen', 'robert@smilebright.com', '(512) 555-0101', 'https://smilebright-dental.com', 'Dentist', 'Austin, TX', 'active', 'Growth Pro', 2997),
            ('Martinez Legal', 'Sarah Martinez', 'sarah@martinezlegal.com', '(214) 555-0202', 'https://martinezlegal.com', 'Lawyer', 'Dallas, TX', 'active', 'Growth Elite', 6997),
            ("Bella's Italian", 'Marco Bellini', 'marco@bellasitalian.com', '(312) 555-0303', 'https://bellasitalian.com', 'Restaurant', 'Chicago, IL', 'active', 'Growth Pro', 2997),
            ('Precision Plumbing', 'Mike Johnson', 'mike@precisionplumb.com', '(214) 555-0404', 'https://precisionplumbing.com', 'Plumber', 'Dallas, TX', 'active', 'Growth Starter', 997),
            ('Phoenix HVAC Pro', 'Tom Williams', 'tom@phoenixhvac.com', '(602) 555-0505', 'https://phoenixhvacpro.com', 'HVAC', 'Phoenix, AZ', 'active', 'Growth Pro', 2997),
            ('Glow Aesthetics', 'Dr. Amy Lee', 'amy@glowmed.com', '(310) 555-0606', 'https://glowaesthetics.com', 'Medical Spa', 'Los Angeles, CA', 'active', 'Growth Elite', 6997),
            ('Quick Fix Auto', 'James Brown', 'james@quickfix.com', '(713) 555-0707', 'https://quickfixauto.com', 'Auto Services', 'Houston, TX', 'prospect', None, 0),
        ]
        for biz, contact, email, phone, web, ind, loc, status, pkg, pmt in clients:
            c.execute('INSERT INTO clients (business_name, contact_name, email, phone, website, industry, location, status, package, monthly_payment) VALUES (?,?,?,?,?,?,?,?,?,?)',
                      (biz, contact, email, phone, web, ind, loc, status, pkg, pmt))
        
        # Demo projects
        projects = [
            (1, 'Local SEO Campaign', 'Complete local SEO optimization for SmileBright Dental', 'Local SEO', 'in_progress', 'high', 2, 3, 68),
            (2, 'SEO + Ads Campaign', 'Full SEO and Google Ads management for Martinez Legal', 'AI SEO', 'in_progress', 'urgent', 3, 3, 45),
            (3, 'GBP + Social Media', 'GBP optimization and social media management for Bellas', 'GBP Optimization', 'in_progress', 'medium', 7, 2, 82),
            (4, 'Local SEO Starter', 'Basic local SEO setup for Precision Plumbing', 'Local SEO', 'in_progress', 'medium', 4, 2, 35),
            (5, 'HVAC Growth Campaign', 'Full marketing campaign for Phoenix HVAC Pro', 'AI SEO', 'in_progress', 'high', 2, 3, 55),
            (6, 'MedSpa Marketing', 'Complete digital marketing for Glow Aesthetics', 'Content Creation', 'in_progress', 'high', 5, 2, 72),
        ]
        for cid, title, desc, stype, status, prio, worker, leader, prog in projects:
            c.execute('INSERT INTO projects (client_id, title, description, service_type, status, priority, assigned_worker_id, team_leader_id, progress) VALUES (?,?,?,?,?,?,?,?,?)',
                      (cid, title, desc, stype, status, prio, worker, leader, prog))
        
        # Demo tasks
        tasks = [
            (1, 'Keyword Research', 'Research local dental keywords for Austin market', 'completed', 2, 'high', 1),
            (1, 'GBP Optimization', 'Optimize Google Business Profile - categories, description, photos', 'completed', 2, 'high', 2),
            (1, 'Citation Building', 'Build citations across 50+ directories', 'in_progress', 2, 'medium', 3),
            (1, 'On-Page SEO', 'Optimize title tags, meta descriptions, schema markup', 'in_progress', 2, 'high', 4),
            (1, 'Content Calendar', 'Create 3-month content calendar for dental blog', 'pending', 4, 'medium', 5),
            (1, 'Link Building', 'Outreach to local dental associations and health blogs', 'pending', 2, 'medium', 6),
            (2, 'Legal Keyword Analysis', 'Deep keyword research for personal injury terms in Dallas', 'completed', 3, 'urgent', 1),
            (2, 'Technical SEO Audit', 'Complete technical audit of martinezlegal.com', 'completed', 3, 'high', 2),
            (2, 'Google Ads Setup', 'Set up search campaigns for PI keywords', 'in_progress', 6, 'urgent', 3),
            (2, 'Landing Page Creation', 'Create conversion-optimized landing pages', 'in_progress', 4, 'high', 4),
            (2, 'Content Strategy', 'Plan legal blog content for topical authority', 'pending', 4, 'medium', 5),
        ]
        for pid, title, desc, status, assigned, prio, order in tasks:
            c.execute('INSERT INTO tasks (project_id, title, description, status, assigned_to, priority, order_num) VALUES (?,?,?,?,?,?,?)',
                      (pid, title, desc, status, assigned, prio, order))
        
        # Demo notifications
        notifs = [
            (2, 'New Task Assigned', 'You have been assigned: Citation Building for SmileBright Dental', 'task'),
            (3, 'Project Update', 'Martinez Legal project reached 45% completion', 'info'),
            (2, 'Urgent: Client Call', 'Dr. Chen requested a call about ranking progress', 'urgent'),
            (7, 'New Social Post', 'Instagram post for Bellas Italian is ready for review', 'info'),
        ]
        for uid, title, msg, ntype in notifs:
            c.execute('INSERT INTO notifications (user_id, title, message, type) VALUES (?,?,?,?)',
                      (uid, title, msg, ntype))
        
        # Demo payments
        payments = [
            (1, 2997, 'paid', '2026-05-01', '2026-05-01', 'INV-2026-001'),
            (2, 6997, 'paid', '2026-05-01', '2026-05-02', 'INV-2026-002'),
            (3, 2997, 'paid', '2026-05-01', '2026-05-01', 'INV-2026-003'),
            (4, 997, 'pending', '2026-05-15', None, 'INV-2026-004'),
            (5, 2997, 'paid', '2026-05-01', '2026-05-03', 'INV-2026-005'),
            (6, 6997, 'overdue', '2026-04-15', None, 'INV-2026-006'),
        ]
        for cid, amt, status, due, paid, inv in payments:
            c.execute('INSERT INTO payments (client_id, amount, status, due_date, paid_date, invoice_number) VALUES (?,?,?,?,?,?)',
                      (cid, amt, status, due, paid, inv))
        
        # Demo expenses
        expenses = [
            ('salary', 'Staff Salaries - May 2026', 37000, '2026-05-01'),
            ('tools', 'Semrush Pro - Monthly', 229, '2026-05-01'),
            ('tools', 'Ahrefs Standard - Monthly', 199, '2026-05-01'),
            ('tools', 'Canva Pro Team - Monthly', 120, '2026-05-01'),
            ('marketing', 'Google Ads - Agency Account', 500, '2026-05-05'),
            ('office', 'Cloud Hosting - Monthly', 89, '2026-05-01'),
        ]
        for cat, desc, amt, date in expenses:
            c.execute('INSERT INTO expenses (category, description, amount, date) VALUES (?,?,?,?)',
                      (cat, desc, amt, date))
        
        # Demo sales leads
        leads = [
            ('Green Valley Landscaping', 'Mike Peters', 'mike@greenvalley.com', '(480) 555-0801', 'https://greenvalleyland.com', 'Landscaping', 'Scottsdale, AZ', 'google_maps', 'contacted'),
            ('Elite Fitness Studio', 'Jessica Lane', 'jess@elitefitness.com', '(305) 555-0802', 'https://elitefitness.com', 'Fitness', 'Miami, FL', 'linkedin', 'proposal_sent'),
            ('Classic Car Wash', 'Robert Taylor', 'rob@classicwash.com', '(817) 555-0803', 'https://classiccarwash.com', 'Auto Services', 'Fort Worth, TX', 'google_search', 'new'),
        ]
        for biz, contact, email, phone, web, ind, loc, src, status in leads:
            c.execute('INSERT INTO sales_leads (business_name, contact_name, email, phone, website, industry, location, source, status, assigned_to) VALUES (?,?,?,?,?,?,?,?,?,?)',
                      (biz, contact, email, phone, web, ind, loc, src, status, 6))
        
    except Exception as e:
        print(f"Demo data error: {e}")

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
