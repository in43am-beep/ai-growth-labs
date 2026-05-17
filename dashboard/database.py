"""Database module using SQLite for the Agency OS v3 — Full Feature Implementation"""
import sqlite3
import json
import os
from datetime import datetime, timedelta
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
    
    # Users table — added 'client' and 'ops_manager' roles
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        role TEXT NOT NULL CHECK(role IN ('super_admin','worker','tech_seo','social_media','finance','sales','ops_manager','client')),
        rank TEXT DEFAULT 'junior',
        salary REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        linked_client_id INTEGER,
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
    
    # Client credentials table
    c.execute('''CREATE TABLE IF NOT EXISTS client_credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        credential_type TEXT NOT NULL CHECK(credential_type IN ('gsc','ga4','cms','gbp','ahrefs','semrush','social_fb','social_ig','social_tt','social_li','hosting','other')),
        label TEXT,
        username TEXT,
        password_enc TEXT,
        api_key TEXT,
        access_url TEXT,
        notes TEXT,
        added_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
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
        is_automated INTEGER DEFAULT 0,
        auto_result TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        title TEXT NOT NULL,
        message TEXT,
        type TEXT DEFAULT 'info' CHECK(type IN ('info','warning','success','task','urgent','chat_request','deadline')),
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
        report_data TEXT,
        overall_score INTEGER,
        status TEXT DEFAULT 'pending',
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
    
    # Payments table
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
    
    # Chat messages (website chatbot)
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
    
    # Team chat system
    c.execute('''CREATE TABLE IF NOT EXISTS team_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER REFERENCES users(id),
        to_user_id INTEGER REFERENCES users(id),
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Chat requests
    c.execute('''CREATE TABLE IF NOT EXISTS chat_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER REFERENCES users(id),
        to_user_id INTEGER REFERENCES users(id),
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected','ended')),
        created_at TEXT DEFAULT (datetime('now')),
        resolved_at TEXT
    )''')
    
    # Suggestions
    c.execute('''CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        project_id INTEGER REFERENCES projects(id),
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected','implemented')),
        admin_response TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # API Settings — added twilio
    c.execute('''CREATE TABLE IF NOT EXISTS api_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT UNIQUE NOT NULL CHECK(provider IN ('claude','chatgpt','gemini','twilio','smtp')),
        api_key TEXT,
        is_active INTEGER DEFAULT 0,
        config_json TEXT,
        updated_by INTEGER REFERENCES users(id),
        updated_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Client reports
    c.execute('''CREATE TABLE IF NOT EXISTS client_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        project_id INTEGER REFERENCES projects(id),
        report_type TEXT DEFAULT 'monthly' CHECK(report_type IN ('weekly','monthly','audit','custom')),
        title TEXT,
        report_data TEXT,
        pdf_path TEXT,
        sent_to_client INTEGER DEFAULT 0,
        sent_date TEXT,
        sent_by INTEGER REFERENCES users(id),
        created_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
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
    
    # Package task templates
    c.execute('''CREATE TABLE IF NOT EXISTS package_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        package TEXT NOT NULL CHECK(package IN ('Growth Starter','Growth Pro','Growth Elite')),
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        is_automated INTEGER DEFAULT 0,
        dna_prompt TEXT,
        order_num INTEGER DEFAULT 0
    )''')
    
    # =============== NEW TABLES (Expert Analysis Implementation) ===============
    
    # Time entries — start/stop timer on tasks
    c.execute('''CREATE TABLE IF NOT EXISTS time_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        task_id INTEGER REFERENCES tasks(id),
        project_id INTEGER REFERENCES projects(id),
        start_time TEXT NOT NULL,
        end_time TEXT,
        hours REAL DEFAULT 0,
        description TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Invoices — professional invoice generation
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        invoice_number TEXT UNIQUE,
        items TEXT,
        subtotal REAL DEFAULT 0,
        tax_rate REAL DEFAULT 0,
        tax_amount REAL DEFAULT 0,
        total REAL DEFAULT 0,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','sent','paid','overdue','cancelled')),
        due_date TEXT,
        paid_date TEXT,
        notes TEXT,
        created_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Keyword rankings — track keyword positions over time
    c.execute('''CREATE TABLE IF NOT EXISTS keyword_rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        keyword TEXT NOT NULL,
        position INTEGER,
        previous_position INTEGER,
        search_volume INTEGER DEFAULT 0,
        url TEXT,
        tracked_date TEXT DEFAULT (date('now')),
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Contracts — client agreements
    c.execute('''CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        title TEXT NOT NULL,
        terms TEXT,
        start_date TEXT,
        end_date TEXT,
        monthly_value REAL DEFAULT 0,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','sent','signed','active','expired','cancelled')),
        signed_date TEXT,
        created_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Client locations — multi-location support
    c.execute('''CREATE TABLE IF NOT EXISTS client_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        location_name TEXT NOT NULL,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        phone TEXT,
        gbp_url TEXT,
        is_primary INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # File attachments
    c.execute('''CREATE TABLE IF NOT EXISTS file_attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        mime_type TEXT,
        uploaded_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Generated content — AI content pipeline
    c.execute('''CREATE TABLE IF NOT EXISTS generated_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER REFERENCES clients(id),
        project_id INTEGER REFERENCES projects(id),
        content_type TEXT DEFAULT 'blog' CHECK(content_type IN ('blog','meta_title','meta_desc','social_post','landing_page','faq','schema','backlink_plan')),
        title TEXT,
        content TEXT,
        ai_provider TEXT,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','review','approved','published','rejected')),
        created_by INTEGER REFERENCES users(id),
        reviewed_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Scheduled tasks — recurring task support
    c.execute('''CREATE TABLE IF NOT EXISTS scheduled_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER REFERENCES projects(id),
        title TEXT NOT NULL,
        description TEXT,
        frequency TEXT DEFAULT 'weekly' CHECK(frequency IN ('daily','weekly','biweekly','monthly')),
        assigned_to INTEGER REFERENCES users(id),
        next_run TEXT,
        last_run TEXT,
        is_active INTEGER DEFAULT 1,
        created_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Knowledge base — internal wiki
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        category TEXT DEFAULT 'general',
        tags TEXT,
        created_by INTEGER REFERENCES users(id),
        updated_at TEXT DEFAULT (datetime('now')),
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Voice call logs — Twilio integration tracking
    c.execute('''CREATE TABLE IF NOT EXISTS voice_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        caller_number TEXT,
        agent_number TEXT,
        direction TEXT DEFAULT 'inbound' CHECK(direction IN ('inbound','outbound')),
        duration INTEGER DEFAULT 0,
        recording_url TEXT,
        transcript TEXT,
        status TEXT DEFAULT 'completed',
        notes TEXT,
        handled_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now'))
    )''')

    # Performance reviews — worker scoring
    c.execute('''CREATE TABLE IF NOT EXISTS performance_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        review_period TEXT,
        tasks_completed INTEGER DEFAULT 0,
        tasks_on_time INTEGER DEFAULT 0,
        on_time_pct REAL DEFAULT 0,
        quality_score REAL DEFAULT 0,
        overall_score REAL DEFAULT 0,
        reviewer_id INTEGER REFERENCES users(id),
        comments TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    
    # Create default super admin
    try:
        admin_hash = bcrypt.hash("admin123")
        c.execute('''INSERT OR IGNORE INTO users (username, password_hash, full_name, email, role, rank, salary) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  ('admin', admin_hash, 'Super Administrator', 'admin@aigrowth-labs.com', 'super_admin', 'director', 0))
    except Exception:
        pass
    
    _insert_demo_data(c)
    _insert_package_tasks(c)
    
    conn.commit()
    conn.close()

def _insert_package_tasks(c):
    """Insert DNA-level package task templates"""
    try:
        c.execute("SELECT COUNT(*) FROM package_tasks")
        if c.fetchone()[0] > 0:
            return
        
        starter_tasks = [
            ('Technical SEO', 'Site Speed Audit', 'Check Core Web Vitals: LCP, CLS, INP, TTFB', 1, 'Analyze website speed: Check LCP (should be <2.5s), CLS (<0.1), INP (<200ms), TTFB (<800ms). Test on Google PageSpeed Insights. Report all issues with fix priorities.'),
            ('Technical SEO', 'Mobile Responsiveness Check', 'Test mobile layout, tap targets, viewport', 1, 'Test mobile-friendliness: Check responsive design, tap target sizes (min 48x48px), viewport configuration, font readability. Screenshot issues.'),
            ('Technical SEO', 'Crawlability Audit', 'Check robots.txt, sitemap, crawl errors', 1, 'Audit crawlability: Review robots.txt rules, XML sitemap validity, check for orphan pages, broken links, redirect chains (max 2 hops). Report blocked resources.'),
            ('Technical SEO', 'SSL & Security Check', 'Verify HTTPS, mixed content, security headers', 1, 'Check security: Verify SSL certificate valid, no mixed content warnings, check security headers (HSTS, CSP, X-Frame-Options). Report vulnerabilities.'),
            ('On-Page SEO', 'Title Tag Optimization', 'Optimize all page title tags with target keywords', 0, None),
            ('On-Page SEO', 'Meta Description Optimization', 'Write CTR-optimized meta descriptions', 0, None),
            ('On-Page SEO', 'Header Structure (H1-H3)', 'Fix heading hierarchy, add keywords naturally', 0, None),
            ('On-Page SEO', 'Image Alt Text Audit', 'Check all images have descriptive alt text', 1, 'Scan all images on the website. Report images missing alt text, images with generic alt text ("image1.jpg"), oversized images (>200KB). Provide optimized alt text suggestions with target keywords.'),
            ('On-Page SEO', 'Schema Markup Setup', 'Add LocalBusiness, FAQ, Service schema', 0, None),
            ('Local SEO', 'GBP Profile Setup', 'Create/claim and optimize Google Business Profile', 0, None),
            ('Local SEO', 'NAP Consistency Check', 'Verify Name, Address, Phone across web', 1, 'Check NAP (Name, Address, Phone) consistency across top 20 directories. Report mismatches. Provide list of directories needing updates.'),
            ('Local SEO', 'Citation Building (20 dirs)', 'Submit to 20 core business directories', 0, None),
            ('Content', 'Blog Posts (4/month)', 'Create 4 SEO-optimized blog posts per month', 0, None),
            ('Reputation', 'Review Monitoring Setup', 'Set up Google review monitoring alerts', 0, None),
            ('Reporting', 'Monthly Report', 'Generate and send monthly progress report', 0, None),
        ]
        
        pro_tasks = starter_tasks + [
            ('AI SEO', 'Entity SEO Analysis', 'Map semantic entities for the business niche', 1, 'Analyze the business niche entities: Map primary entity, related entities, semantic relationships. Compare entity coverage vs top 3 competitors. Identify entity gaps. Create entity optimization roadmap.'),
            ('AI SEO', 'Search Intent Analysis', 'Classify all target keywords by search intent', 1, 'Classify target keywords: Informational, Commercial, Transactional, Navigational. Map content to intent. Identify intent mismatches. Recommend content restructuring.'),
            ('AI SEO', 'Competitor DNA Analysis', 'Deep analysis of top 5 competitors across 12 pillars', 1, 'Analyze top 5 competitors for this niche+location: Compare Technical SEO scores, Content depth, Backlink profiles, Entity coverage, Local signals, Social presence, Review counts, Page speed, Schema usage, Content freshness, Topical authority, UX signals. Generate competitive gap report with priority actions.'),
            ('AI SEO', 'NLP Content Optimization', 'Optimize content for semantic search and NLP', 1, 'Analyze content for NLP optimization: Check semantic keyword coverage, entity mentions, topic depth score, content helpfulness signals. Compare with top-ranking pages. Suggest semantic enrichments.'),
            ('On-Page SEO', 'Internal Linking Strategy', 'Build topical silo structure with contextual links', 0, None),
            ('Content', 'Blog Posts (8/month)', 'Create 8 SEO-optimized blog posts per month', 0, None),
            ('Content', 'Topical Authority Map', 'Create content cluster strategy for niche dominance', 1, 'Build topical authority map: Identify pillar topics, cluster subtopics, map content relationships. Create internal linking plan. Identify content gaps vs competitors.'),
            ('GBP', 'Weekly GBP Posts', 'Create and publish weekly Google Business posts', 0, None),
            ('GBP', 'Q&A Seeding', 'Seed relevant Q&A on Google Business Profile', 0, None),
            ('Reputation', 'Review Generation System', 'Set up automated review request system', 0, None),
            ('Social Media', 'Social Media Management (3)', 'Manage 3 social media platforms', 0, None),
            ('Ads', 'Google Ads Campaign Setup', 'Set up and optimize Google Ads campaigns', 0, None),
            ('Reporting', 'Bi-Weekly Strategy Calls', 'Schedule and conduct strategy calls', 0, None),
        ]
        
        elite_tasks = pro_tasks + [
            ('AI SEO', 'Full DNA-Level Audit', 'Complete 100+ factor audit across 12 DNA pillars', 1, 'Run complete DNA-level SEO audit covering all 12 pillars (100+ factors): Technical SEO, On-Page, Content, Entity SEO, Internal Linking, Off-Page, Local SEO, User Behavior, Conversion, Competitor DNA, Indexing, AI/Programmatic SEO. Score each pillar 0-10. Generate priority roadmap.'),
            ('AI SEO', 'Programmatic SEO Setup', 'Create scalable page templates for city/service combos', 1, 'Design programmatic SEO strategy: Identify scalable page patterns (city+service, service+niche). Create template structures. Plan internal linking between programmatic pages. Estimate traffic potential per template.'),
            ('AI SEO', 'Predictive SEO Analysis', 'Forecast ranking opportunities using AI trends', 1, 'Analyze search trends for the niche: Identify rising keywords, seasonal patterns, emerging topics. Predict ranking opportunities for next 90 days. Recommend content calendar based on trend predictions.'),
            ('Content', 'AI Content Engine (20+/mo)', 'Generate 20+ optimized content pieces monthly', 0, None),
            ('Content', 'Video Content Scripts', 'Create video scripts for YouTube/social platforms', 0, None),
            ('Reputation', 'Full Reputation Management', 'Complete reputation monitoring and response system', 0, None),
            ('Social Media', 'All Platform Management', 'Manage all social media platforms (6+)', 0, None),
            ('Ads', 'Facebook + Google Ads ($5K+)', 'Full ad management with $5K+ monthly budget', 0, None),
            ('Off-Page', 'Link Building Campaign', 'Strategic outreach for high-authority backlinks', 0, None),
            ('Off-Page', 'Backlink Structure File', 'Create detailed backlink acquisition plan document', 1, 'Generate backlink strategy: Identify 50+ link opportunities. Prioritize by DA, relevance, difficulty. Create outreach templates for each type.'),
            ('Reporting', 'Weekly Strategy Calls', 'Weekly client strategy calls with reports', 0, None),
        ]
        
        for cat, title, desc, auto, prompt in starter_tasks:
            c.execute('INSERT INTO package_tasks (package, category, title, description, is_automated, dna_prompt, order_num) VALUES (?,?,?,?,?,?,?)',
                      ('Growth Starter', cat, title, desc, auto, prompt, 0))
        
        for cat, title, desc, auto, prompt in pro_tasks:
            c.execute('INSERT INTO package_tasks (package, category, title, description, is_automated, dna_prompt, order_num) VALUES (?,?,?,?,?,?,?)',
                      ('Growth Pro', cat, title, desc, auto, prompt, 0))
        
        for cat, title, desc, auto, prompt in elite_tasks:
            c.execute('INSERT INTO package_tasks (package, category, title, description, is_automated, dna_prompt, order_num) VALUES (?,?,?,?,?,?,?)',
                      ('Growth Elite', cat, title, desc, auto, prompt, 0))
    except Exception as e:
        print(f"Package tasks error: {e}")

def _insert_demo_data(c):
    """Insert demo data for showcase"""
    try:
        c.execute("SELECT COUNT(*) FROM clients")
        if c.fetchone()[0] > 0:
            return
        
        # Demo workers — including ops_manager
        workers = [
            ('sarah_k', 'Sarah Kim', 'sarah@aigrowth-labs.com', 'tech_seo', 'senior', 5500),
            ('alex_r', 'Alex Rodriguez', 'alex@aigrowth-labs.com', 'tech_seo', 'lead', 7000),
            ('emily_p', 'Emily Parker', 'emily@aigrowth-labs.com', 'worker', 'senior', 5000),
            ('david_w', 'David Washington', 'david@aigrowth-labs.com', 'worker', 'mid', 4000),
            ('lisa_c', 'Lisa Chen', 'lisa@aigrowth-labs.com', 'sales', 'senior', 5500),
            ('marcus_j', 'Marcus Johnson', 'marcus@aigrowth-labs.com', 'social_media', 'mid', 4500),
            ('rachel_g', 'Rachel Green', 'rachel@aigrowth-labs.com', 'finance', 'senior', 5500),
            ('ops_mike', 'Michael Torres', 'mike@aigrowth-labs.com', 'ops_manager', 'lead', 6500),
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
        
        # Create client portal users for active clients
        for i, (biz, contact, email, phone, web, ind, loc, status, pkg, pmt) in enumerate(clients):
            if status == 'active':
                uname = f"client_{i+1}"
                c.execute('INSERT OR IGNORE INTO users (username, password_hash, full_name, email, role, rank, salary, linked_client_id) VALUES (?,?,?,?,?,?,?,?)',
                          (uname, pw, contact, email, 'client', 'client', 0, i+1))
        
        # Demo credentials
        creds = [
            (1, 'gsc', 'Google Search Console', 'robert@smilebright.com', None, None, 'https://search.google.com/search-console', 'Verified property'),
            (1, 'ga4', 'Google Analytics GA4', 'robert@smilebright.com', None, None, 'https://analytics.google.com', 'Property ID: 123456789'),
            (1, 'cms', 'WordPress Admin', 'admin', 'wp_pass_demo', None, 'https://smilebright-dental.com/wp-admin', 'WordPress 6.4'),
            (2, 'gsc', 'Google Search Console', 'sarah@martinezlegal.com', None, None, 'https://search.google.com/search-console', 'Verified'),
            (2, 'gbp', 'Google Business Profile', 'sarah@martinezlegal.com', None, None, 'https://business.google.com', 'Primary owner'),
        ]
        for cid, ctype, label, uname, pwd, akey, url, notes in creds:
            c.execute('INSERT INTO client_credentials (client_id, credential_type, label, username, password_enc, api_key, access_url, notes, added_by) VALUES (?,?,?,?,?,?,?,?,1)',
                      (cid, ctype, label, uname, pwd, akey, url, notes))
        
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
        
        # Demo tasks with due dates for deadline tracking
        tasks = [
            (1, 'Keyword Research', 'Research local dental keywords for Austin market', 'completed', 2, 'high', 1, '2026-05-01'),
            (1, 'GBP Optimization', 'Optimize Google Business Profile', 'completed', 2, 'high', 2, '2026-05-05'),
            (1, 'Citation Building', 'Build citations across 50+ directories', 'in_progress', 2, 'medium', 3, '2026-05-20'),
            (1, 'On-Page SEO', 'Optimize title tags, meta descriptions, schema', 'in_progress', 2, 'high', 4, '2026-05-15'),
            (1, 'Content Calendar', 'Create 3-month content calendar', 'pending', 4, 'medium', 5, '2026-05-25'),
            (1, 'Link Building', 'Outreach to local associations and blogs', 'pending', 2, 'medium', 6, '2026-06-01'),
            (2, 'Legal Keyword Analysis', 'Deep keyword research for PI terms in Dallas', 'completed', 3, 'urgent', 1, '2026-04-25'),
            (2, 'Technical SEO Audit', 'Complete technical audit', 'completed', 3, 'high', 2, '2026-04-30'),
            (2, 'Google Ads Setup', 'Set up search campaigns for PI keywords', 'in_progress', 6, 'urgent', 3, '2026-05-08'),
            (2, 'Landing Page Creation', 'Create conversion-optimized landing pages', 'in_progress', 4, 'high', 4, '2026-05-12'),
            (2, 'Content Strategy', 'Plan legal blog content for topical authority', 'pending', 4, 'medium', 5, '2026-05-30'),
        ]
        for pid, title, desc, status, assigned, prio, order, due in tasks:
            c.execute('INSERT INTO tasks (project_id, title, description, status, assigned_to, priority, order_num, due_date) VALUES (?,?,?,?,?,?,?,?)',
                      (pid, title, desc, status, assigned, prio, order, due))
        
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
        
        # Demo social posts
        social_posts = [
            (1, 'instagram', '5 Tips for Maintaining Your Smile Between Dental Visits', 'published', '2026-05-01', json.dumps({"likes": 142, "comments": 23, "shares": 18, "reach": 3200})),
            (1, 'facebook', 'Meet Dr. Chen - Your Austin Dental Expert', 'published', '2026-05-03', json.dumps({"likes": 89, "comments": 15, "shares": 12, "reach": 2100})),
            (3, 'instagram', 'Fresh pasta made daily at Bellas Italian!', 'published', '2026-05-02', json.dumps({"likes": 234, "comments": 45, "shares": 67, "reach": 5600})),
            (3, 'tiktok', 'Behind the scenes: Making our famous tiramisu', 'published', '2026-05-04', json.dumps({"likes": 1200, "comments": 89, "shares": 156, "reach": 15000})),
            (5, 'facebook', 'HVAC Maintenance Tips for Arizona Summer', 'scheduled', '2026-05-15', None),
        ]
        for cid, platform, content, status, date, engagement in social_posts:
            c.execute('INSERT INTO social_posts (client_id, platform, content, status, scheduled_date, engagement_data, created_by) VALUES (?,?,?,?,?,?,7)',
                      (cid, platform, content, status, date, engagement))
        
        # Demo suggestions
        suggestions = [
            (2, 1, 'Add FAQ Schema to dental pages', 'The SmileBright site could benefit from FAQ schema markup on service pages.', 'approved', 'Good suggestion, implement it.'),
            (3, 2, 'Consider video testimonials', 'Martinez Legal could get better conversion with video testimonials.', 'pending', None),
        ]
        for uid, pid, title, desc, status, response in suggestions:
            c.execute('INSERT INTO suggestions (user_id, project_id, title, description, status, admin_response) VALUES (?,?,?,?,?,?)',
                      (uid, pid, title, desc, status, response))
        
        # Demo API settings — include twilio
        api_settings = [
            ('claude', None, 0, json.dumps({"model": "claude-sonnet-4-20250514", "max_tokens": 4096})),
            ('chatgpt', None, 0, json.dumps({"model": "gpt-4.5", "max_tokens": 4096})),
            ('gemini', None, 0, json.dumps({"model": "gemini-pro", "max_tokens": 4096})),
            ('smtp', None, 0, json.dumps({"host": "smtp.gmail.com", "port": 587, "from_email": ""})),
            ('twilio', None, 0, json.dumps({"account_sid": "", "auth_token": "", "phone_number": ""})),
        ]
        for provider, key, active, config in api_settings:
            c.execute('INSERT OR IGNORE INTO api_settings (provider, api_key, is_active, config_json) VALUES (?,?,?,?)',
                      (provider, key, active, config))
        
        # Demo keyword rankings
        keywords = [
            (1, 'dentist austin tx', 8, 12, 2400, 'https://smilebright-dental.com'),
            (1, 'dental cleaning austin', 5, 9, 880, 'https://smilebright-dental.com/services/cleaning'),
            (1, 'emergency dentist austin', 15, 22, 1200, 'https://smilebright-dental.com/emergency'),
            (2, 'personal injury lawyer dallas', 12, 18, 5400, 'https://martinezlegal.com'),
            (2, 'car accident attorney dallas', 18, 25, 3200, 'https://martinezlegal.com/car-accident'),
            (5, 'hvac repair phoenix', 6, 11, 3800, 'https://phoenixhvacpro.com'),
            (5, 'ac installation phoenix az', 9, 14, 2200, 'https://phoenixhvacpro.com/ac-install'),
        ]
        for cid, kw, pos, prev, vol, url in keywords:
            c.execute('INSERT INTO keyword_rankings (client_id, keyword, position, previous_position, search_volume, url) VALUES (?,?,?,?,?,?)',
                      (cid, kw, pos, prev, vol, url))
        
        # Demo time entries
        time_data = [
            (2, 1, 1, '2026-05-05 09:00', '2026-05-05 11:30', 2.5, 'Keyword research for dental market'),
            (2, 2, 1, '2026-05-06 10:00', '2026-05-06 12:00', 2.0, 'GBP optimization setup'),
            (3, 7, 2, '2026-05-07 09:00', '2026-05-07 13:00', 4.0, 'Legal keyword deep analysis'),
            (4, 10, 2, '2026-05-08 14:00', '2026-05-08 17:00', 3.0, 'Landing page design'),
        ]
        for uid, tid, pid, start, end, hours, desc in time_data:
            c.execute('INSERT INTO time_entries (user_id, task_id, project_id, start_time, end_time, hours, description) VALUES (?,?,?,?,?,?,?)',
                      (uid, tid, pid, start, end, hours, desc))
        
        # Demo invoices
        invoices = [
            (1, 'INV-2026-001', json.dumps([{"desc": "Growth Pro - Monthly SEO", "qty": 1, "rate": 2997}]), 2997, 0, 0, 2997, 'paid', '2026-05-01', '2026-05-01'),
            (2, 'INV-2026-002', json.dumps([{"desc": "Growth Elite - Full Service", "qty": 1, "rate": 6997}]), 6997, 0, 0, 6997, 'paid', '2026-05-01', '2026-05-02'),
            (4, 'INV-2026-004', json.dumps([{"desc": "Growth Starter - Basic SEO", "qty": 1, "rate": 997}]), 997, 0, 0, 997, 'sent', '2026-05-15', None),
            (6, 'INV-2026-006', json.dumps([{"desc": "Growth Elite - Full Service", "qty": 1, "rate": 6997}]), 6997, 0, 0, 6997, 'overdue', '2026-04-15', None),
        ]
        for cid, inv_num, items, sub, tax_r, tax_a, total, status, due, paid in invoices:
            c.execute('INSERT INTO invoices (client_id, invoice_number, items, subtotal, tax_rate, tax_amount, total, status, due_date, paid_date, created_by) VALUES (?,?,?,?,?,?,?,?,?,?,1)',
                      (cid, inv_num, items, sub, tax_r, tax_a, total, status, due, paid))
        
        # Demo contracts
        contracts = [
            (1, 'SEO Service Agreement - SmileBright', 'Monthly SEO services including local SEO, content, GBP optimization', '2026-04-01', '2026-09-30', 2997, 'active', '2026-04-01'),
            (2, 'Full Service Agreement - Martinez Legal', 'Complete SEO + Ads + Content marketing', '2026-03-15', '2027-03-14', 6997, 'active', '2026-03-15'),
            (6, 'MedSpa Marketing Agreement', 'Full digital marketing package', '2026-01-01', '2026-12-31', 6997, 'active', '2026-01-01'),
        ]
        for cid, title, terms, start, end, val, status, signed in contracts:
            c.execute('INSERT INTO contracts (client_id, title, terms, start_date, end_date, monthly_value, status, signed_date, created_by) VALUES (?,?,?,?,?,?,?,?,1)',
                      (cid, title, terms, start, end, val, status, signed))
        
        # Demo client locations
        locations = [
            (1, 'SmileBright - Main Office', '123 Dental Ave', 'Austin', 'TX', '78701', '(512) 555-0101', 'https://g.co/smilebright', 1),
            (1, 'SmileBright - North Austin', '456 North Loop', 'Austin', 'TX', '78756', '(512) 555-0102', None, 0),
            (2, 'Martinez Legal - Downtown', '789 Commerce St', 'Dallas', 'TX', '75201', '(214) 555-0202', 'https://g.co/martinezlegal', 1),
        ]
        for cid, name, addr, city, state, zip_code, phone, gbp, primary in locations:
            c.execute('INSERT INTO client_locations (client_id, location_name, address, city, state, zip_code, phone, gbp_url, is_primary) VALUES (?,?,?,?,?,?,?,?,?)',
                      (cid, name, addr, city, state, zip_code, phone, gbp, primary))
        
        # Demo knowledge base
        kb_articles = [
            ('Local SEO Checklist', '1. Claim GBP listing\n2. Optimize NAP consistency\n3. Build citations\n4. Get reviews\n5. Local content\n6. Schema markup\n7. Internal linking', 'seo', 'local,gbp,citations'),
            ('Client Onboarding Process', '1. Sign agreement\n2. Collect credentials\n3. Run initial audit\n4. Create project plan\n5. Assign team\n6. Kickoff call\n7. Begin execution', 'process', 'onboarding,client'),
            ('Content Writing Guidelines', 'All content must be:\n- Original and unique\n- 1500+ words for blog posts\n- Include target keyword in title, H1, first paragraph\n- Use related entities naturally\n- Include internal links to 3+ relevant pages', 'content', 'writing,guidelines'),
        ]
        for title, content, cat, tags in kb_articles:
            c.execute('INSERT INTO knowledge_base (title, content, category, tags, created_by) VALUES (?,?,?,?,1)',
                      (title, content, cat, tags))
        
        # Demo activity log
        activities = [
            (1, 'Created client', 'Added SmileBright Dental as new client', 'client', 1),
            (2, 'Completed task', 'Finished keyword research for SmileBright', 'task', 1),
            (1, 'Generated report', 'Monthly report for Martinez Legal', 'report', 1),
            (6, 'Updated lead', 'Elite Fitness moved to proposal stage', 'lead', 2),
        ]
        for uid, action, details, etype, eid in activities:
            c.execute('INSERT INTO activity_log (user_id, action, details, entity_type, entity_id) VALUES (?,?,?,?,?)',
                      (uid, action, details, etype, eid))
        
    except Exception as e:
        print(f"Demo data error: {e}")

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
