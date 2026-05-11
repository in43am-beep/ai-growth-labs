"""Generate all dashboard templates for Agency OS v2"""
import os

TMPL_DIR = os.path.join(os.path.dirname(__file__), "templates")

# Common header/sidebar that all templates share
def base_start(title, role_label, sidebar_items):
    sidebar_html = ""
    for icon, label, href, active in sidebar_items:
        cls = ' class="active"' if active else ''
        sidebar_html += f'<a href="{href}"{cls}>{icon}{label}</a>\n'
    
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} — AI Growth Labs OS</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/dashboard.css"></head><body>
<aside class="sidebar"><div class="sidebar-brand">AI Growth<span>Labs</span></div>
<nav><div class="nav-section">Main</div>{sidebar_html}</nav>
<div class="sidebar-user"><div class="user-avatar">{{{{ user.full_name[:2]|upper }}}}</div>
<div><strong>{{{{ user.full_name }}}}</strong><small>{role_label}</small></div></div></aside>
<main class="main">'''

def base_end():
    return '</main></body></html>'

# ===== ADMIN DASHBOARD =====
def gen_admin():
    sidebar = [
        ('📊', 'Dashboard', '/dashboard', True),
        ('👥', 'Clients', '#clients-section', False),
        ('📋', 'Projects', '#projects-section', False),
        ('✅', 'Tasks', '#tasks-section', False),
        ('👷', 'Workers', '#workers-section', False),
        ('💰', 'Payments', '#payments-section', False),
        ('🔍', 'SEO Audit', '#audit-section', False),
        ('📡', 'Team Monitor', '/monitor', False),
        ('💬', 'Team Chat', '/team-chat', False),
        ('⚙️', 'API Settings', '/settings', False),
    ]
    return base_start('Super Admin', '{{ user.role }}', sidebar) + '''
<div class="header-bar"><h1>Super Admin Dashboard</h1><span>Agency Operating System — Complete Overview</span>
<div class="header-actions">
<button class="btn btn-primary" onclick="openModal('addClientModal')">+ Add Client</button>
<button class="btn btn-secondary" onclick="openModal('addProjectModal')">+ New Project</button>
<button class="btn btn-secondary" onclick="openModal('addWorkerModal')">+ Add Worker</button>
{% if unread_chats > 0 %}<a href="/team-chat" class="btn btn-warning">💬 {{ unread_chats }} New Messages</a>{% endif %}
{% if chat_requests|length > 0 %}<a href="/monitor" class="btn btn-warning">🔔 {{ chat_requests|length }} Chat Requests</a>{% endif %}
<a href="/logout" class="btn btn-outline">Logout</a></div></div>

<div class="stats-grid">
<div class="stat-card"><div class="stat-label">Monthly Revenue</div><div class="stat-value cyan">${{ "{:,.0f}".format(stats.monthly_recurring) }}</div><div class="stat-sub">Active MRR</div></div>
<div class="stat-card"><div class="stat-label">Total Collected</div><div class="stat-value green">${{ "{:,.0f}".format(stats.total_revenue) }}</div><div class="stat-sub">All time payments</div></div>
<div class="stat-card"><div class="stat-label">Pending Revenue</div><div class="stat-value orange">${{ "{:,.0f}".format(stats.pending_revenue) }}</div><div class="stat-sub">Outstanding payments</div></div>
<div class="stat-card"><div class="stat-label">Active Clients</div><div class="stat-value">{{ stats.active_clients }}</div><div class="stat-sub">Currently active</div></div>
<div class="stat-card"><div class="stat-label">Active Projects</div><div class="stat-value">{{ stats.active_projects }}</div><div class="stat-sub">In progress</div></div>
<div class="stat-card"><div class="stat-label">Task Completion</div><div class="stat-value">{{ stats.task_completion }}%</div><div class="stat-sub">{{ stats.completed_tasks }}/{{ stats.total_tasks }} tasks</div></div>
</div>

{% if suggestions|length > 0 %}
<div class="card" id="suggestions-section"><h3>💡 Team Suggestions</h3>
<table><thead><tr><th>From</th><th>Project</th><th>Suggestion</th><th>Status</th><th>Action</th></tr></thead><tbody>
{% for s in suggestions %}
<tr><td>{{ s.author_name }}</td><td>{{ s.project_title or '-' }}</td><td><strong>{{ s.title }}</strong><br><small>{{ s.description[:80] }}...</small></td>
<td><span class="badge badge-{{ s.status }}">{{ s.status }}</span></td>
<td>{% if s.status == 'pending' %}<button class="btn btn-sm btn-primary" onclick="updateSuggestion({{ s.id }}, 'approved')">Approve</button>
<button class="btn btn-sm btn-danger" onclick="updateSuggestion({{ s.id }}, 'rejected')">Reject</button>{% else %}{{ s.admin_response or '-' }}{% endif %}</td></tr>
{% endfor %}</tbody></table></div>
{% endif %}

<div class="card" id="projects-section"><h3>📋 All Projects</h3>
<table><thead><tr><th>Client</th><th>Project</th><th>Service</th><th>Worker</th><th>Team Lead</th><th>Progress</th><th>Priority</th><th>Status</th><th>Upsell</th></tr></thead><tbody>
{% for p in projects %}
<tr><td><a href="/client/{{ p.client_id }}">{{ p.business_name }}</a></td><td>{{ p.title }}</td><td>{{ p.service_type }}</td><td>{{ p.worker_name }}</td><td>{{ p.leader_name }}</td>
<td><div class="progress-bar"><div class="progress-fill" style="width:{{ p.progress }}%"></div></div>{{ p.progress }}%</td>
<td><span class="badge badge-{{ p.priority }}">{{ p.priority }}</span></td><td><span class="badge badge-active">{{ p.status }}</span></td><td>—</td></tr>
{% endfor %}</tbody></table></div>

<div class="card" id="clients-section"><h3>👥 All Clients</h3>
<table><thead><tr><th>Business</th><th>Contact</th><th>Industry</th><th>Location</th><th>Package</th><th>Payment</th><th>Status</th><th>Details</th></tr></thead><tbody>
{% for c in clients %}
<tr><td><strong>{{ c.business_name }}</strong><br><small>{{ c.website }}</small></td><td>{{ c.contact_name }}<br><small>{{ c.email }}</small></td>
<td>{{ c.industry }}</td><td>{{ c.location }}</td><td>{{ c.package or '-' }}</td>
<td>{% if c.monthly_payment %}${{ "{:,.0f}".format(c.monthly_payment) }}/mo{% else %}-{% endif %}</td>
<td><span class="badge badge-{{ c.status }}">{{ c.status }}</span></td>
<td><a href="/client/{{ c.id }}" class="btn btn-sm btn-primary">View</a></td></tr>
{% endfor %}</tbody></table></div>

<div class="card" id="workers-section"><h3>👷 Team Members</h3>
<table><thead><tr><th>Name</th><th>Role</th><th>Rank</th><th>Salary</th><th>Status</th></tr></thead><tbody>
{% for w in workers %}
<tr><td><strong>{{ w.full_name }}</strong><br><small>@{{ w.username }}</small></td><td>{{ w.role|replace('_',' ')|title }}</td><td>{{ w.rank }}</td>
<td>${{ "{:,.0f}".format(w.salary) }}</td><td><span class="badge badge-active">Active</span></td></tr>
{% endfor %}</tbody></table></div>

<div class="card" id="tasks-section"><h3>✅ Recent Tasks</h3>
<table><thead><tr><th>Task</th><th>Project</th><th>Assigned</th><th>Priority</th><th>Status</th></tr></thead><tbody>
{% for t in tasks %}
<tr><td>{{ t.title }}</td><td>{{ t.project_title }}</td><td>{{ t.assigned_name }}</td>
<td><span class="badge badge-{{ t.priority }}">{{ t.priority }}</span></td>
<td><span class="badge badge-{{ t.status|replace(' ','_') }}">{{ t.status }}</span></td></tr>
{% endfor %}</tbody></table></div>

<div class="card" id="payments-section"><h3>💰 Payment Records</h3>
<table><thead><tr><th>Invoice</th><th>Client</th><th>Amount</th><th>Due Date</th><th>Paid Date</th><th>Status</th><th>Report</th></tr></thead><tbody>
{% for p in payments %}
<tr><td>{{ p.invoice_number }}</td><td>{{ p.business_name }}</td><td><strong>${{ "{:,.0f}".format(p.amount) }}</strong></td>
<td>{{ p.due_date }}</td><td>{{ p.paid_date or '-' }}</td>
<td><span class="badge badge-{{ p.status }}">{{ p.status }}</span></td>
<td><button class="btn btn-sm btn-primary" onclick="generateReport({{ p.client_id }})">📄 Generate</button></td></tr>
{% endfor %}</tbody></table></div>

<div class="card" id="audit-section"><h3>🔍 Run SEO DNA Audit</h3>
<p>Paste a client's website URL and select an AI provider to run a complete DNA-level audit.</p>
<div class="form-row"><input type="url" id="auditUrl" placeholder="https://clientwebsite.com" class="form-input">
<select id="auditProvider" class="form-select"><option value="claude">Claude Sonnet</option><option value="chatgpt">ChatGPT 4.5</option><option value="gemini">Google Gemini</option></select>
<button class="btn btn-primary" onclick="runAudit()">Run Audit →</button></div>
<p class="text-muted">Note: AI API key must be configured in <a href="/settings">Settings</a> for audits to process.</p></div>

<!-- Add Client Modal -->
<div class="modal-overlay" id="addClientModal"><div class="modal"><div class="modal-header"><h3>Add New Client</h3><button onclick="closeModal('addClientModal')" class="modal-close">×</button></div>
<div class="modal-body"><input id="nc_business" placeholder="Business Name" class="form-input"><input id="nc_contact" placeholder="Contact Name" class="form-input">
<input id="nc_email" placeholder="Email" class="form-input"><input id="nc_phone" placeholder="Phone" class="form-input">
<input id="nc_website" placeholder="Website URL" class="form-input"><input id="nc_industry" placeholder="Industry" class="form-input">
<input id="nc_location" placeholder="Location (City, ST)" class="form-input">
<select id="nc_package" class="form-select"><option value="">Select Package</option><option value="Growth Starter">Growth Starter - $997/mo</option><option value="Growth Pro">Growth Pro - $2,997/mo</option><option value="Growth Elite">Growth Elite - $6,997/mo</option></select>
<select id="nc_status" class="form-select"><option value="lead">Lead</option><option value="prospect">Prospect</option><option value="active">Active</option></select>
<button class="btn btn-primary btn-full" onclick="addClient()">Add Client</button></div></div></div>

<!-- Add Project Modal -->
<div class="modal-overlay" id="addProjectModal"><div class="modal"><div class="modal-header"><h3>New Project</h3><button onclick="closeModal('addProjectModal')" class="modal-close">×</button></div>
<div class="modal-body"><select id="np_client" class="form-select">{% for c in clients %}<option value="{{ c.id }}">{{ c.business_name }}</option>{% endfor %}</select>
<input id="np_title" placeholder="Project Title" class="form-input"><textarea id="np_desc" placeholder="Description" class="form-input"></textarea>
<select id="np_service" class="form-select"><option>Local SEO</option><option>AI SEO</option><option>GBP Optimization</option><option>Reputation Management</option><option>Content Creation</option><option>Social Media</option><option>Paid Advertising</option></select>
<select id="np_worker" class="form-select">{% for w in workers %}<option value="{{ w.id }}">{{ w.full_name }} ({{ w.role }})</option>{% endfor %}</select>
<button class="btn btn-primary btn-full" onclick="addProject()">Create Project</button></div></div></div>

<!-- Add Worker Modal -->
<div class="modal-overlay" id="addWorkerModal"><div class="modal"><div class="modal-header"><h3>Add Worker</h3><button onclick="closeModal('addWorkerModal')" class="modal-close">×</button></div>
<div class="modal-body"><input id="nw_username" placeholder="Username" class="form-input"><input id="nw_name" placeholder="Full Name" class="form-input">
<input id="nw_email" placeholder="Email" class="form-input"><input id="nw_password" placeholder="Password" class="form-input" type="password">
<select id="nw_role" class="form-select"><option value="worker">Worker</option><option value="tech_seo">Tech SEO</option><option value="sales">Sales</option><option value="social_media">Social Media</option><option value="finance">Finance</option></select>
<select id="nw_rank" class="form-select"><option value="junior">Junior</option><option value="mid">Mid</option><option value="senior">Senior</option><option value="lead">Lead</option></select>
<input id="nw_salary" placeholder="Monthly Salary" type="number" class="form-input">
<button class="btn btn-primary btn-full" onclick="addWorker()">Add Worker</button></div></div></div>

<script>
function openModal(id){document.getElementById(id).classList.add('show')}
function closeModal(id){document.getElementById(id).classList.remove('show')}
function api(url,data){return fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json())}
function apiPut(url,data){return fetch(url,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json())}

function addClient(){
    const pkg=document.getElementById('nc_package').value;
    const pmts={'Growth Starter':997,'Growth Pro':2997,'Growth Elite':6997};
    api('/api/clients',{business_name:document.getElementById('nc_business').value,contact_name:document.getElementById('nc_contact').value,
        email:document.getElementById('nc_email').value,phone:document.getElementById('nc_phone').value,website:document.getElementById('nc_website').value,
        industry:document.getElementById('nc_industry').value,location:document.getElementById('nc_location').value,
        package:pkg,monthly_payment:pmts[pkg]||0,status:document.getElementById('nc_status').value}).then(()=>location.reload())}

function addProject(){api('/api/projects',{client_id:parseInt(document.getElementById('np_client').value),title:document.getElementById('np_title').value,
    description:document.getElementById('np_desc').value,service_type:document.getElementById('np_service').value,
    assigned_worker_id:parseInt(document.getElementById('np_worker').value)}).then(()=>location.reload())}

function addWorker(){api('/api/users',{username:document.getElementById('nw_username').value,full_name:document.getElementById('nw_name').value,
    email:document.getElementById('nw_email').value,password:document.getElementById('nw_password').value,
    role:document.getElementById('nw_role').value,rank:document.getElementById('nw_rank').value,
    salary:parseFloat(document.getElementById('nw_salary').value)||0}).then(()=>location.reload())}

function runAudit(){api('/api/audit',{website_url:document.getElementById('auditUrl').value,ai_provider:document.getElementById('auditProvider').value})
    .then(r=>{alert(r.message||r.error);location.reload()})}

function generateReport(clientId){api('/api/reports/generate',{client_id:clientId,report_type:'monthly'})
    .then(r=>{if(r.id){window.open('/api/reports/'+r.id+'/download','_blank')}else{alert(r.error||'Error')}})}

function updateSuggestion(id,status){apiPut('/api/suggestions/'+id,{status:status,admin_response:status=='approved'?'Approved by admin':'Rejected'}).then(()=>location.reload())}
</script>
''' + base_end()

# ===== WORKER DASHBOARD =====
def gen_worker():
    sidebar = [
        ('📊', 'Dashboard', '/dashboard', True),
        ('✅', 'My Tasks', '#tasks-section', False),
        ('📋', 'My Projects', '#projects-section', False),
        ('🔔', 'Notifications', '#notif-section', False),
        ('🔍', 'SEO Audit', '#audit-section', False),
        ('💡', 'Suggestions', '#suggestions-section', False),
        ('💬', 'Team Chat', '/team-chat', False),
    ]
    return base_start('Worker Dashboard', '{{ user.role|replace("_"," ")|title }}', sidebar) + '''
<div class="header-bar"><h1>{{ user.full_name }} — Dashboard</h1><span>{{ user.role|replace('_',' ')|title }} | {{ user.rank|title }}</span>
<div class="header-actions">
{% if unread_chats > 0 %}<a href="/team-chat" class="btn btn-warning">💬 {{ unread_chats }} New Messages</a>{% endif %}
<button class="btn btn-secondary" onclick="openModal('addSuggestionModal')">💡 Add Suggestion</button>
<a href="/logout" class="btn btn-outline">Logout</a></div></div>

<div class="stats-grid">
<div class="stat-card"><div class="stat-label">Total Tasks</div><div class="stat-value">{{ stats.total_tasks }}</div></div>
<div class="stat-card"><div class="stat-label">Completed</div><div class="stat-value green">{{ stats.completed_tasks }}</div></div>
<div class="stat-card"><div class="stat-label">Pending</div><div class="stat-value orange">{{ stats.pending_tasks }}</div></div>
<div class="stat-card"><div class="stat-label">Completion Rate</div><div class="stat-value cyan">{{ stats.completion_pct }}%</div></div>
<div class="stat-card"><div class="stat-label">Active Projects</div><div class="stat-value">{{ stats.active_projects }}</div></div>
</div>

<div class="card" id="tasks-section"><h3>✅ My Tasks — Kanban Board</h3>
<div class="kanban-board">
<div class="kanban-col"><h4>⏳ Pending</h4>
{% for t in my_tasks if t.status == 'pending' %}
<div class="kanban-card"><div class="kanban-card-header"><span class="badge badge-{{ t.priority }}">{{ t.priority }}</span>
{% if t.is_automated %}<span class="badge badge-auto">🤖 Auto</span>{% endif %}</div>
<h5>{{ t.title }}</h5><small>{{ t.business_name }} — {{ t.project_title }}</small>
<div class="kanban-actions">
<button class="btn btn-sm btn-primary" onclick="moveTask({{ t.id }},'in_progress')">Start →</button>
{% if t.is_automated %}<button class="btn btn-sm btn-warning" onclick="runAutoTask({{ t.id }})">🤖 Run AI</button>{% endif %}
</div></div>{% endfor %}</div>
<div class="kanban-col"><h4>🔄 In Progress</h4>
{% for t in my_tasks if t.status == 'in_progress' %}
<div class="kanban-card active"><div class="kanban-card-header"><span class="badge badge-{{ t.priority }}">{{ t.priority }}</span></div>
<h5>{{ t.title }}</h5><small>{{ t.business_name }} — {{ t.project_title }}</small>
<div class="kanban-actions"><button class="btn btn-sm btn-warning" onclick="moveTask({{ t.id }},'blocked')">Block</button>
<button class="btn btn-sm btn-success" onclick="moveTask({{ t.id }},'completed')">Complete ✓</button></div></div>{% endfor %}</div>
<div class="kanban-col"><h4>🚫 Blocked</h4>
{% for t in my_tasks if t.status == 'blocked' %}
<div class="kanban-card blocked"><div class="kanban-card-header"><span class="badge badge-urgent">blocked</span></div>
<h5>{{ t.title }}</h5><small>{{ t.business_name }} — {{ t.project_title }}</small>
<div class="kanban-actions"><button class="btn btn-sm btn-primary" onclick="moveTask({{ t.id }},'in_progress')">Resume →</button></div></div>{% endfor %}</div>
<div class="kanban-col"><h4>✅ Completed</h4>
{% for t in my_tasks if t.status == 'completed' %}
<div class="kanban-card completed"><h5>{{ t.title }}</h5><small>{{ t.business_name }} — {{ t.project_title }}</small></div>{% endfor %}</div>
</div></div>

<div class="card" id="projects-section"><h3>📋 My Projects</h3>
<div class="project-grid">{% for p in my_projects %}
<div class="project-card"><div class="project-header"><h4>{{ p.business_name }}</h4><span class="badge badge-{{ p.status|replace(' ','_') }}">{{ p.status }}</span></div>
<p>{{ p.title }}</p><small>{{ p.industry }} | {{ p.location }} | Package: {{ p.package or 'N/A' }}</small>
<div class="progress-bar"><div class="progress-fill" style="width:{{ p.progress }}%"></div></div><span>{{ p.progress }}% Complete</span>
<div style="margin-top:8px"><a href="/client/{{ p.client_id }}" class="btn btn-sm btn-primary">View Client Details</a></div>
</div>{% endfor %}</div></div>

<div class="card" id="notif-section"><h3>🔔 Notifications</h3>
{% for n in notifications %}
<div class="notif-item {{ 'unread' if not n.is_read else '' }}"><span class="badge badge-{{ n.type }}">{{ n.type }}</span>
<strong>{{ n.title }}</strong> — {{ n.message }} <small>{{ n.created_at }}</small>
{% if not n.is_read %}<button class="btn btn-sm" onclick="markRead({{ n.id }})">Mark Read</button>{% endif %}</div>
{% endfor %}</div>

<div class="card" id="suggestions-section"><h3>💡 My Suggestions</h3>
<table><thead><tr><th>Suggestion</th><th>Project</th><th>Status</th><th>Admin Response</th></tr></thead><tbody>
{% for s in suggestions %}
<tr><td><strong>{{ s.title }}</strong><br><small>{{ s.description[:100] }}</small></td><td>{{ s.project_title or '-' }}</td>
<td><span class="badge badge-{{ s.status }}">{{ s.status }}</span></td><td>{{ s.admin_response or 'Waiting...' }}</td></tr>
{% endfor %}</tbody></table></div>

<div class="card" id="audit-section"><h3>🔍 SEO DNA Audit Tool</h3>
<p>Run a DNA-level audit on any client website. Results are auto-generated using AI.</p>
<div class="form-row"><input type="url" id="auditUrl" placeholder="https://clientwebsite.com" class="form-input">
<select id="auditProvider" class="form-select"><option value="claude">Claude Sonnet</option><option value="chatgpt">ChatGPT 4.5</option><option value="gemini">Google Gemini</option></select>
<button class="btn btn-primary" onclick="runAudit()">Run Audit →</button></div>
{% if audits|length > 0 %}<h4 style="margin-top:16px">Recent Audits</h4>
<table><thead><tr><th>Client</th><th>URL</th><th>Provider</th><th>Score</th><th>Status</th><th>Date</th></tr></thead><tbody>
{% for a in audits %}<tr><td>{{ a.business_name or '-' }}</td><td>{{ a.website_url }}</td><td>{{ a.ai_provider }}</td>
<td>{{ a.overall_score or '-' }}/100</td><td><span class="badge badge-{{ a.status }}">{{ a.status }}</span></td><td>{{ a.created_at }}</td></tr>{% endfor %}</tbody></table>{% endif %}</div>

<!-- Add Suggestion Modal -->
<div class="modal-overlay" id="addSuggestionModal"><div class="modal"><div class="modal-header"><h3>💡 Submit Suggestion</h3><button onclick="closeModal('addSuggestionModal')" class="modal-close">×</button></div>
<div class="modal-body">
<select id="sg_project" class="form-select"><option value="">General Suggestion</option>{% for p in my_projects %}<option value="{{ p.id }}">{{ p.title }} ({{ p.business_name }})</option>{% endfor %}</select>
<input id="sg_title" placeholder="Suggestion Title" class="form-input">
<textarea id="sg_desc" placeholder="Describe your suggestion in detail..." class="form-input" rows="4"></textarea>
<button class="btn btn-primary btn-full" onclick="addSuggestion()">Submit Suggestion</button></div></div></div>

<script>
function openModal(id){document.getElementById(id).classList.add('show')}
function closeModal(id){document.getElementById(id).classList.remove('show')}
function api(url,data){return fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json())}
function moveTask(id,status){fetch('/api/tasks/'+id+'/status',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:status})}).then(()=>location.reload())}
function runAutoTask(id){api('/api/tasks/'+id+'/run-auto',{}).then(r=>{alert(r.message||r.error)})}
function markRead(id){api('/api/notifications/'+id+'/read',{}).then(()=>location.reload())}
function runAudit(){api('/api/audit',{website_url:document.getElementById('auditUrl').value,ai_provider:document.getElementById('auditProvider').value}).then(r=>{alert(r.message||r.error)})}
function addSuggestion(){api('/api/suggestions',{project_id:document.getElementById('sg_project').value||null,title:document.getElementById('sg_title').value,description:document.getElementById('sg_desc').value}).then(()=>{closeModal('addSuggestionModal');location.reload()})}
</script>
''' + base_end()

# ===== SALES DASHBOARD =====
def gen_sales():
    sidebar = [
        ('📊', 'Dashboard', '/dashboard', True),
        ('🎯', 'Leads', '#leads-section', False),
        ('📧', 'Lead Tools', '#tools-section', False),
        ('📝', 'Proposals', '#proposal-section', False),
        ('👥', 'Clients', '#clients-section', False),
        ('💬', 'Team Chat', '/team-chat', False),
    ]
    return base_start('Sales Dashboard', 'Sales Agent', sidebar) + '''
<div class="header-bar"><h1>Sales Dashboard</h1><span>Lead Pipeline & Conversion Tracking</span>
<div class="header-actions"><button class="btn btn-primary" onclick="openModal('addLeadModal')">+ New Lead</button>
<a href="/logout" class="btn btn-outline">Logout</a></div></div>

<div class="stats-grid">
<div class="stat-card"><div class="stat-label">Total Leads</div><div class="stat-value">{{ stats.total_leads }}</div></div>
<div class="stat-card"><div class="stat-label">New Leads</div><div class="stat-value cyan">{{ stats.new_leads }}</div></div>
<div class="stat-card"><div class="stat-label">Proposals Sent</div><div class="stat-value orange">{{ stats.proposals_sent }}</div></div>
<div class="stat-card"><div class="stat-label">Won Deals</div><div class="stat-value green">{{ stats.won_leads }}</div></div>
<div class="stat-card"><div class="stat-label">Conversion Rate</div><div class="stat-value">{{ stats.conversion_rate }}%</div></div>
</div>

<div class="card" id="leads-section"><h3>🎯 Lead Pipeline</h3>
<div class="kanban-board" style="grid-template-columns:repeat(6,1fr)">
{% set stages = [('new','🆕 New'),('contacted','📞 Contacted'),('qualified','✅ Qualified'),('proposal_sent','📝 Proposal'),('negotiating','🤝 Negotiating'),('won','🏆 Won')] %}
{% for stage_key, stage_label in stages %}
<div class="kanban-col"><h4>{{ stage_label }}</h4>
{% for l in leads if l.status == stage_key %}
<div class="kanban-card"><h5>{{ l.business_name }}</h5><small>{{ l.contact_name }}<br>{{ l.industry }} — {{ l.location }}</small>
<div class="kanban-actions">
{% if stage_key != 'won' %}<select onchange="moveLead({{ l.id }},this.value)" class="form-select form-select-sm">
<option value="">Move to...</option><option value="contacted">Contacted</option><option value="qualified">Qualified</option>
<option value="proposal_sent">Proposal</option><option value="negotiating">Negotiating</option><option value="won">Won</option>
<option value="lost">Lost</option></select>{% endif %}</div></div>{% endfor %}</div>
{% endfor %}</div></div>

<div class="card" id="tools-section"><h3>📧 Lead Collection Tools</h3>
<div class="tools-grid">
<div class="tool-card"><h4>🔍 Google Search</h4><p>Find businesses via Google search queries</p><button class="btn btn-primary" disabled>Coming Soon</button></div>
<div class="tool-card"><h4>📍 Google Maps</h4><p>Scrape local business listings from Maps</p><button class="btn btn-primary" disabled>Coming Soon</button></div>
<div class="tool-card"><h4>💼 LinkedIn</h4><p>Find business owners on LinkedIn</p><button class="btn btn-primary" disabled>Coming Soon</button></div>
<div class="tool-card"><h4>📱 Social Media</h4><p>Discover businesses on Facebook/Instagram</p><button class="btn btn-primary" disabled>Coming Soon</button></div>
</div></div>

<div class="card" id="clients-section"><h3>👥 Recent Clients</h3>
<table><thead><tr><th>Business</th><th>Contact</th><th>Package</th><th>Status</th><th>Details</th></tr></thead><tbody>
{% for c in recent_clients %}
<tr><td>{{ c.business_name }}</td><td>{{ c.contact_name }}</td><td>{{ c.package or '-' }}</td>
<td><span class="badge badge-{{ c.status }}">{{ c.status }}</span></td>
<td><a href="/client/{{ c.id }}" class="btn btn-sm btn-primary">View</a></td></tr>
{% endfor %}</tbody></table></div>

<!-- Add Lead Modal -->
<div class="modal-overlay" id="addLeadModal"><div class="modal"><div class="modal-header"><h3>Add New Lead</h3><button onclick="closeModal('addLeadModal')" class="modal-close">×</button></div>
<div class="modal-body"><input id="nl_business" placeholder="Business Name" class="form-input"><input id="nl_contact" placeholder="Contact Name" class="form-input">
<input id="nl_email" placeholder="Email" class="form-input"><input id="nl_phone" placeholder="Phone" class="form-input">
<input id="nl_website" placeholder="Website" class="form-input"><input id="nl_industry" placeholder="Industry" class="form-input">
<input id="nl_location" placeholder="Location" class="form-input">
<select id="nl_source" class="form-select"><option value="google_search">Google Search</option><option value="google_maps">Google Maps</option><option value="linkedin">LinkedIn</option><option value="facebook">Facebook</option><option value="referral">Referral</option><option value="website">Website</option><option value="other">Other</option></select>
<button class="btn btn-primary btn-full" onclick="addLead()">Add Lead</button></div></div></div>

<script>
function openModal(id){document.getElementById(id).classList.add('show')}
function closeModal(id){document.getElementById(id).classList.remove('show')}
function api(url,data){return fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).then(r=>r.json())}
function addLead(){api('/api/leads',{business_name:document.getElementById('nl_business').value,contact_name:document.getElementById('nl_contact').value,
    email:document.getElementById('nl_email').value,phone:document.getElementById('nl_phone').value,website:document.getElementById('nl_website').value,
    industry:document.getElementById('nl_industry').value,location:document.getElementById('nl_location').value,
    source:document.getElementById('nl_source').value}).then(()=>location.reload())}
function moveLead(id,status){if(!status)return;fetch('/api/leads/'+id+'/status',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:status})}).then(()=>location.reload())}
</script>
''' + base_end()

# ===== SOCIAL MEDIA DASHBOARD =====
def gen_social():
    sidebar = [
        ('📊', 'Dashboard', '/dashboard', True),
        ('📱', 'Client Accounts', '#accounts-section', False),
        ('📝', 'Posts', '#posts-section', False),
        ('📈', 'Analytics', '#analytics-section', False),
        ('💡', 'Suggestions', '#suggestions-section', False),
        ('💬', 'Team Chat', '/team-chat', False),
    ]
    return base_start('Social Media', 'Social Media Manager', sidebar) + '''
<div class="header-bar"><h1>Social Media Dashboard</h1><span>Content Creation, Scheduling & Analytics</span>
<div class="header-actions"><button class="btn btn-primary" onclick="openModal('addPostModal')">+ Create Post</button>
<a href="/logout" class="btn btn-outline">Logout</a></div></div>

<div class="stats-grid">
<div class="stat-card"><div class="stat-label">Total Posts</div><div class="stat-value">{{ stats.total_posts }}</div></div>
<div class="stat-card"><div class="stat-label">Published</div><div class="stat-value green">{{ stats.published }}</div></div>
<div class="stat-card"><div class="stat-label">Scheduled</div><div class="stat-value cyan">{{ stats.scheduled }}</div></div>
<div class="stat-card"><div class="stat-label">Drafts</div><div class="stat-value orange">{{ stats.drafts }}</div></div>
<div class="stat-card"><div class="stat-label">Total Likes</div><div class="stat-value">{{ "{:,}".format(stats.total_likes) }}</div></div>
<div class="stat-card"><div class="stat-label">Total Reach</div><div class="stat-value cyan">{{ "{:,}".format(stats.total_reach) }}</div></div>
</div>

<div class="card" id="analytics-section"><h3>📈 Engagement Analytics</h3>
<div class="stats-grid">
<div class="stat-card"><div class="stat-value green">{{ "{:,}".format(stats.total_likes) }}</div><div class="stat-sub">Total Likes</div></div>
<div class="stat-card"><div class="stat-value cyan">{{ "{:,}".format(stats.total_comments) }}</div><div class="stat-sub">Total Comments</div></div>
<div class="stat-card"><div class="stat-value orange">{{ "{:,}".format(stats.total_shares) }}</div><div class="stat-sub">Total Shares</div></div>
<div class="stat-card"><div class="stat-value">{{ "{:,}".format(stats.total_reach) }}</div><div class="stat-sub">Total Reach</div></div>
</div></div>

<div class="card" id="accounts-section"><h3>📱 Client Social Accounts</h3>
<div class="project-grid">{% for c in clients %}
<div class="project-card"><h4>{{ c.business_name }}</h4><small>{{ c.industry }} | {{ c.location }}</small>
<div style="margin-top:8px">
<span class="badge badge-active">FB</span> <span class="badge badge-active">IG</span> <span class="badge badge-active">TT</span>
</div><a href="/client/{{ c.id }}" class="btn btn-sm btn-primary" style="margin-top:8px">Manage</a></div>{% endfor %}</div></div>

<div class="card" id="posts-section"><h3>📝 All Posts</h3>
<table><thead><tr><th>Client</th><th>Platform</th><th>Content</th><th>Status</th><th>Engagement</th><th>Date</th></tr></thead><tbody>
{% for p in posts %}{% set eng = {} %}
<tr><td>{{ p.business_name }}</td><td><span class="badge badge-active">{{ p.platform }}</span></td>
<td>{{ p.content[:60] }}...</td><td><span class="badge badge-{{ p.status }}">{{ p.status }}</span></td>
<td>{% if p.engagement_data %}{{ p.engagement_data }}{% else %}-{% endif %}</td><td>{{ p.scheduled_date or p.created_at }}</td></tr>
{% endfor %}</tbody></table></div>

<div class="card"><h3>🤖 AI Content Generator</h3>
<div class="tools-grid">
<div class="tool-card"><h4>💬 Engagement</h4><p>Questions, polls, tips</p></div>
<div class="tool-card"><h4>📚 Educational</h4><p>How-to, tips, guides</p></div>
<div class="tool-card"><h4>⭐ Testimonials</h4><p>Client success stories</p></div>
<div class="tool-card"><h4>🎯 Promotional</h4><p>Offers, deals, CTAs</p></div>
<div class="tool-card"><h4>📊 Statistics</h4><p>Industry facts, data</p></div>
<div class="tool-card"><h4>🎬 Video Script</h4><p>Short-form video scripts</p></div>
</div></div>

<!-- Create Post Modal -->
<div class="modal-overlay" id="addPostModal"><div class="modal"><div class="modal-header"><h3>Create Post</h3><button onclick="closeModal('addPostModal')" class="modal-close">×</button></div>
<div class="modal-body">
<select id="sp_client" class="form-select">{% for c in clients %}<option value="{{ c.id }}">{{ c.business_name }}</option>{% endfor %}</select>
<select id="sp_platform" class="form-select"><option value="facebook">Facebook</option><option value="instagram">Instagram</option><option value="tiktok">TikTok</option><option value="linkedin">LinkedIn</option><option value="twitter">Twitter</option><option value="pinterest">Pinterest</option></select>
<textarea id="sp_content" placeholder="Post content..." class="form-input" rows="4"></textarea>
<input id="sp_date" type="datetime-local" class="form-input">
<select id="sp_status" class="form-select"><option value="draft">Draft</option><option value="scheduled">Scheduled</option><option value="published">Published</option></select>
<button class="btn btn-primary btn-full" onclick="addPost()">Create Post</button></div></div></div>

<script>
function openModal(id){document.getElementById(id).classList.add('show')}
function closeModal(id){document.getElementById(id).classList.remove('show')}
function addPost(){fetch('/api/social-posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
    client_id:parseInt(document.getElementById('sp_client').value),platform:document.getElementById('sp_platform').value,
    content:document.getElementById('sp_content').value,status:document.getElementById('sp_status').value,
    scheduled_date:document.getElementById('sp_date').value})}).then(()=>location.reload())}
</script>
''' + base_end()

# ===== FINANCE DASHBOARD =====
def gen_finance():
    sidebar = [
        ('📊', 'Dashboard', '/dashboard', True),
        ('💰', 'Payments', '#payments-section', False),
        ('📋', 'Expenses', '#expenses-section', False),
        ('👷', 'Salaries', '#salaries-section', False),
        ('📄', 'Reports', '#reports-section', False),
        ('💬', 'Team Chat', '/team-chat', False),
    ]
    return base_start('Finance', 'Finance & Accounts', sidebar) + '''
<div class="header-bar"><h1>Finance Dashboard</h1><span>Payment Tracking, Expenses & P&L</span>
<div class="header-actions"><button class="btn btn-primary" onclick="openModal('addExpenseModal')">+ Add Expense</button>
<a href="/logout" class="btn btn-outline">Logout</a></div></div>

<div class="stats-grid">
<div class="stat-card"><div class="stat-label">Total Income</div><div class="stat-value green">${{ "{:,.0f}".format(stats.total_income) }}</div></div>
<div class="stat-card"><div class="stat-label">Total Expenses</div><div class="stat-value orange">${{ "{:,.0f}".format(stats.total_expenses) }}</div></div>
<div class="stat-card"><div class="stat-label">Net Profit</div><div class="stat-value cyan">${{ "{:,.0f}".format(stats.net_profit) }}</div></div>
<div class="stat-card"><div class="stat-label">Pending Payments</div><div class="stat-value orange">${{ "{:,.0f}".format(stats.pending_payments) }}</div></div>
<div class="stat-card"><div class="stat-label">Staff Salaries</div><div class="stat-value">${{ "{:,.0f}".format(stats.total_salaries) }}/mo</div></div>
<div class="stat-card"><div class="stat-label">Tools Cost</div><div class="stat-value">${{ "{:,.0f}".format(stats.tools_cost) }}/mo</div></div>
</div>

<div class="card" id="payments-section"><h3>💰 Client Payments</h3>
<table><thead><tr><th>Invoice</th><th>Client</th><th>Amount</th><th>Due Date</th><th>Paid Date</th><th>Status</th><th>Report</th></tr></thead><tbody>
{% for p in payments %}
<tr><td>{{ p.invoice_number }}</td><td>{{ p.business_name }}</td><td><strong>${{ "{:,.0f}".format(p.amount) }}</strong></td>
<td>{{ p.due_date }}</td><td>{{ p.paid_date or '-' }}</td>
<td><span class="badge badge-{{ p.status }}">{{ p.status }}</span></td>
<td><button class="btn btn-sm btn-primary" onclick="generateReport({{ p.client_id }})">📄 Report</button></td></tr>
{% endfor %}</tbody></table></div>

<div class="card" id="expenses-section"><h3>📋 Expenses</h3>
<table><thead><tr><th>Category</th><th>Description</th><th>Amount</th><th>Date</th></tr></thead><tbody>
{% for e in expenses %}
<tr><td><span class="badge badge-{{ e.category }}">{{ e.category }}</span></td><td>{{ e.description }}</td>
<td><strong>${{ "{:,.0f}".format(e.amount) }}</strong></td><td>{{ e.date }}</td></tr>
{% endfor %}</tbody></table></div>

<div class="card" id="salaries-section"><h3>👷 Staff Salaries</h3>
<table><thead><tr><th>Name</th><th>Role</th><th>Rank</th><th>Monthly Salary</th></tr></thead><tbody>
{% for w in workers %}
<tr><td>{{ w.full_name }}</td><td>{{ w.role|replace('_',' ')|title }}</td><td>{{ w.rank }}</td><td><strong>${{ "{:,.0f}".format(w.salary) }}</strong></td></tr>
{% endfor %}
<tr style="border-top:2px solid #00D4FF"><td colspan="3"><strong>Total Monthly Payroll</strong></td><td><strong>${{ "{:,.0f}".format(stats.total_salaries) }}</strong></td></tr>
</tbody></table></div>

<!-- Add Expense Modal -->
<div class="modal-overlay" id="addExpenseModal"><div class="modal"><div class="modal-header"><h3>Add Expense</h3><button onclick="closeModal('addExpenseModal')" class="modal-close">×</button></div>
<div class="modal-body">
<select id="ex_cat" class="form-select"><option value="tools">Tools</option><option value="marketing">Marketing</option><option value="office">Office</option><option value="salary">Salary</option><option value="other">Other</option></select>
<input id="ex_desc" placeholder="Description" class="form-input"><input id="ex_amount" placeholder="Amount" type="number" class="form-input">
<input id="ex_date" type="date" class="form-input">
<button class="btn btn-primary btn-full" onclick="addExpense()">Add Expense</button></div></div></div>

<script>
function openModal(id){document.getElementById(id).classList.add('show')}
function closeModal(id){document.getElementById(id).classList.remove('show')}
function addExpense(){fetch('/api/expenses',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
    category:document.getElementById('ex_cat').value,description:document.getElementById('ex_desc').value,
    amount:parseFloat(document.getElementById('ex_amount').value),date:document.getElementById('ex_date').value})}).then(()=>location.reload())}
function generateReport(clientId){fetch('/api/reports/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({client_id:clientId,report_type:'monthly'})})
    .then(r=>r.json()).then(r=>{if(r.id){window.open('/api/reports/'+r.id+'/download','_blank')}else{alert(r.error||'Error')}})}
</script>
''' + base_end()

# ===== SETTINGS PAGE =====
def gen_settings():
    sidebar = [
        ('📊', 'Dashboard', '/dashboard', False),
        ('⚙️', 'API Settings', '/settings', True),
        ('📡', 'Team Monitor', '/monitor', False),
        ('💬', 'Team Chat', '/team-chat', False),
    ]
    return base_start('Settings', 'Super Admin', sidebar) + '''
<div class="header-bar"><h1>⚙️ API Settings</h1><span>Configure AI providers and integrations</span>
<div class="header-actions"><a href="/dashboard" class="btn btn-outline">← Back to Dashboard</a></div></div>

<div class="settings-grid">
{% for s in api_settings %}
<div class="card setting-card"><h3>
{% if s.provider == 'claude' %}🟣 Claude Sonnet{% elif s.provider == 'chatgpt' %}🟢 ChatGPT{% elif s.provider == 'gemini' %}🔵 Google Gemini{% elif s.provider == 'smtp' %}📧 Email (SMTP){% else %}🔧 {{ s.provider }}{% endif %}
</h3>
<div class="setting-status">Status: {% if s.is_active %}<span class="badge badge-active">Active</span>{% else %}<span class="badge badge-pending">Not Configured</span>{% endif %}</div>
<input id="api_key_{{ s.provider }}" type="password" value="{{ s.api_key or '' }}" placeholder="Paste API Key here..." class="form-input">
<button class="btn btn-primary btn-full" onclick="saveApiKey('{{ s.provider }}')">Save & Activate</button>
</div>
{% endfor %}
</div>

<div class="card"><h3>📋 How It Works</h3>
<div class="info-grid">
<div class="info-item"><h4>1. Paste API Key</h4><p>Get your API key from Claude, ChatGPT, or Gemini and paste it above.</p></div>
<div class="info-item"><h4>2. System Activates</h4><p>Once saved, the AI provider becomes available for all automated tasks.</p></div>
<div class="info-item"><h4>3. Auto DNA Audits</h4><p>Workers can run automated SEO audits using the configured AI provider.</p></div>
<div class="info-item"><h4>4. Task Automation</h4><p>Tasks marked as "automated" will use AI to analyze and generate results.</p></div>
</div></div>

<script>
function saveApiKey(provider){
    const key=document.getElementById('api_key_'+provider).value;
    fetch('/api/settings/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({provider:provider,api_key:key})})
    .then(r=>r.json()).then(r=>{alert(r.message||r.error);location.reload()})}
</script>
''' + base_end()

# ===== TEAM MONITOR PAGE =====
def gen_monitor():
    sidebar = [
        ('📊', 'Dashboard', '/dashboard', False),
        ('📡', 'Team Monitor', '/monitor', True),
        ('💬', 'Team Chat', '/team-chat', False),
        ('⚙️', 'Settings', '/settings', False),
    ]
    return base_start('Team Monitor', 'Super Admin', sidebar) + '''
<div class="header-bar"><h1>📡 Team Monitor</h1><span>One-click view of all team activity</span>
<div class="header-actions"><a href="/dashboard" class="btn btn-outline">← Back to Dashboard</a></div></div>

{% if chat_requests|length > 0 %}
<div class="card"><h3>🔔 Pending Chat Requests</h3>
{% for cr in chat_requests %}
<div class="notif-item"><strong>{{ cr.from_name }}</strong> wants to chat <small>{{ cr.created_at }}</small>
<button class="btn btn-sm btn-primary" onclick="handleChatReq({{ cr.id }},'approved')">Approve</button>
<button class="btn btn-sm btn-danger" onclick="handleChatReq({{ cr.id }},'rejected')">Reject</button></div>
{% endfor %}</div>{% endif %}

{% if suggestions|length > 0 %}
<div class="card"><h3>💡 Team Suggestions</h3>
<table><thead><tr><th>From</th><th>Project</th><th>Suggestion</th><th>Status</th><th>Action</th></tr></thead><tbody>
{% for s in suggestions %}
<tr><td>{{ s.author_name }}</td><td>{{ s.project_title or '-' }}</td><td><strong>{{ s.title }}</strong></td>
<td><span class="badge badge-{{ s.status }}">{{ s.status }}</span></td>
<td>{% if s.status == 'pending' %}<button class="btn btn-sm btn-primary" onclick="handleSugg({{ s.id }},'approved')">Approve</button>
<button class="btn btn-sm btn-danger" onclick="handleSugg({{ s.id }},'rejected')">Reject</button>{% else %}Done{% endif %}</td></tr>
{% endfor %}</tbody></table></div>{% endif %}

<div class="card"><h3>👷 Team Activity Overview</h3>
<div class="monitor-grid">
{% for w in workers %}
<div class="monitor-card">
<div class="monitor-header"><div class="user-avatar">{{ w.full_name[:2]|upper }}</div>
<div><strong>{{ w.full_name }}</strong><br><small>{{ w.role|replace('_',' ')|title }} | {{ w.rank }}</small></div></div>
<div class="monitor-stats">
<div class="mini-stat"><span class="mini-num green">{{ w.active_tasks }}</span><span>Active</span></div>
<div class="mini-stat"><span class="mini-num orange">{{ w.pending_tasks }}</span><span>Pending</span></div>
<div class="mini-stat"><span class="mini-num cyan">{{ w.completed_tasks }}</span><span>Done</span></div>
<div class="mini-stat"><span class="mini-num">{{ w.total_tasks }}</span><span>Total</span></div>
</div>
{% if w.projects %}
<div class="monitor-projects"><h5>Projects:</h5>
{% for p in w.projects %}
<div class="mini-project"><span>{{ p.business_name }} — {{ p.title }}</span>
<div class="progress-bar"><div class="progress-fill" style="width:{{ p.progress }}%"></div></div><small>{{ p.progress }}%</small></div>
{% endfor %}</div>{% endif %}
<div style="margin-top:8px"><a href="/team-chat" class="btn btn-sm btn-primary">💬 Chat</a></div>
</div>
{% endfor %}
</div></div>

<script>
function handleChatReq(id,status){fetch('/api/chat-request/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:status})}).then(()=>location.reload())}
function handleSugg(id,status){fetch('/api/suggestions/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:status,admin_response:status=='approved'?'Approved':'Rejected'})}).then(()=>location.reload())}
</script>
''' + base_end()

# ===== TEAM CHAT PAGE =====
def gen_team_chat():
    sidebar = [
        ('📊', 'Dashboard', '/dashboard', False),
        ('💬', 'Team Chat', '/team-chat', True),
    ]
    return base_start('Team Chat', '{{ user.role|replace("_"," ")|title }}', sidebar) + '''
<div class="header-bar"><h1>💬 Team Chat</h1><span>Real-time messaging with team members</span>
<div class="header-actions"><a href="/dashboard" class="btn btn-outline">← Back to Dashboard</a></div></div>

<div class="chat-layout">
<div class="chat-sidebar">
<h4>Team Members</h4>
{% for m in team_members %}
<div class="chat-member" onclick="openChat({{ m.id }},'{{ m.full_name }}')">
<div class="user-avatar small">{{ m.full_name[:2]|upper }}</div>
<div><strong>{{ m.full_name }}</strong><br><small>{{ m.role|replace('_',' ')|title }}</small></div>
</div>{% endfor %}
{% if user.role != 'super_admin' %}
<div style="margin-top:16px;padding:12px">
<h4>Request Chat</h4><p style="font-size:12px;color:#94A3B8">Request approval from Super Admin to start a chat session.</p>
<select id="chat_request_to" class="form-select">{% for m in team_members %}<option value="{{ m.id }}">{{ m.full_name }}</option>{% endfor %}</select>
<button class="btn btn-primary btn-full" onclick="requestChat()" style="margin-top:8px">Send Request</button>
</div>{% endif %}
</div>
<div class="chat-main">
<div class="chat-header" id="chatHeader"><h4>Select a team member to chat</h4></div>
<div class="chat-messages" id="chatMessages"><div class="chat-empty">Select a team member from the left panel to start chatting.</div></div>
<div class="chat-input" id="chatInput" style="display:none">
<input type="text" id="msgInput" placeholder="Type your message..." class="form-input" onkeypress="if(event.key==='Enter')sendMsg()">
<button class="btn btn-primary" onclick="sendMsg()">Send</button>
</div></div></div>

<script>
let currentChatUser=null;
function openChat(userId,name){
    currentChatUser=userId;
    document.getElementById('chatHeader').innerHTML='<h4>Chat with '+name+'</h4>';
    document.getElementById('chatInput').style.display='flex';
    loadMessages(userId);
}
function loadMessages(userId){
    fetch('/api/chat-messages/'+userId).then(r=>r.json()).then(data=>{
        const container=document.getElementById('chatMessages');
        if(!data.messages||data.messages.length===0){container.innerHTML='<div class="chat-empty">No messages yet. Start the conversation!</div>';return}
        container.innerHTML=data.messages.map(m=>'<div class="chat-msg '+(m.from_user_id=={{ user.id }}?'sent':'received')+'"><strong>'+m.sender_name+'</strong><p>'+m.message+'</p><small>'+m.created_at+'</small></div>').join('');
        container.scrollTop=container.scrollHeight;
    });
}
function sendMsg(){
    const msg=document.getElementById('msgInput').value;
    if(!msg||!currentChatUser)return;
    fetch('/api/chat-messages',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({to_user_id:currentChatUser,message:msg})})
    .then(()=>{document.getElementById('msgInput').value='';loadMessages(currentChatUser)});
}
function requestChat(){
    const toId=document.getElementById('chat_request_to').value;
    fetch('/api/chat-request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({to_user_id:parseInt(toId)})})
    .then(r=>r.json()).then(r=>alert(r.message));
}
{% if approved_chats|length > 0 %}document.addEventListener('DOMContentLoaded',function(){
    // Auto-refresh messages every 5 seconds
    setInterval(function(){if(currentChatUser)loadMessages(currentChatUser)},5000);
});{% endif %}
</script>
''' + base_end()

# ===== CLIENT DETAIL PAGE =====
def gen_client_detail():
    sidebar = [
        ('📊', 'Dashboard', '/dashboard', False),
        ('👤', 'Client', '#', True),
    ]
    return base_start('Client Detail', '{{ user.role|replace("_"," ")|title }}', sidebar) + '''
<div class="header-bar"><h1>{{ client.business_name }}</h1><span>{{ client.industry }} | {{ client.location }} | {{ client.package or 'No Package' }}</span>
<div class="header-actions"><a href="/dashboard" class="btn btn-outline">← Back</a>
<button class="btn btn-primary" onclick="generateReport({{ client.id }})">📄 Generate Report</button>
{% if user.role in ('super_admin','finance') %}<button class="btn btn-secondary" onclick="sendReport()">📧 Send Report to Client</button>{% endif %}
</div></div>

<div class="stats-grid">
<div class="stat-card"><div class="stat-label">Package</div><div class="stat-value">{{ client.package or 'None' }}</div></div>
<div class="stat-card"><div class="stat-label">Monthly</div><div class="stat-value cyan">${{ "{:,.0f}".format(client.monthly_payment) }}</div></div>
<div class="stat-card"><div class="stat-label">Status</div><div class="stat-value"><span class="badge badge-{{ client.status }}">{{ client.status }}</span></div></div>
<div class="stat-card"><div class="stat-label">Projects</div><div class="stat-value">{{ projects|length }}</div></div>
</div>

<div class="card"><h3>📞 Contact Information</h3>
<div class="info-grid">
<div class="info-item"><strong>Contact:</strong> {{ client.contact_name }}</div>
<div class="info-item"><strong>Email:</strong> {{ client.email }}</div>
<div class="info-item"><strong>Phone:</strong> {{ client.phone }}</div>
<div class="info-item"><strong>Website:</strong> <a href="{{ client.website }}" target="_blank">{{ client.website }}</a></div>
</div></div>

{% if credentials|length > 0 %}
<div class="card"><h3>🔐 Client Credentials</h3>
<table><thead><tr><th>Type</th><th>Label</th><th>Username</th><th>Access URL</th><th>Notes</th></tr></thead><tbody>
{% for cr in credentials %}
<tr><td><span class="badge badge-active">{{ cr.credential_type|upper }}</span></td><td>{{ cr.label }}</td>
<td>{{ cr.username or '-' }}</td><td>{% if cr.access_url %}<a href="{{ cr.access_url }}" target="_blank">{{ cr.access_url[:40] }}...</a>{% else %}-{% endif %}</td>
<td>{{ cr.notes or '-' }}</td></tr>
{% endfor %}</tbody></table>
<button class="btn btn-secondary" onclick="openModal('addCredModal')" style="margin-top:12px">+ Add Credential</button></div>
{% else %}
<div class="card"><h3>🔐 Client Credentials</h3><p>No credentials added yet.</p>
<button class="btn btn-secondary" onclick="openModal('addCredModal')">+ Add Credential</button></div>
{% endif %}

{% if package_tasks|length > 0 %}
<div class="card"><h3>📋 Package Tasks ({{ client.package }})</h3>
<p>DNA-level tasks auto-generated based on the selected package.</p>
<table><thead><tr><th>Category</th><th>Task</th><th>Description</th><th>Type</th></tr></thead><tbody>
{% for pt in package_tasks %}
<tr><td><span class="badge badge-active">{{ pt.category }}</span></td><td>{{ pt.title }}</td>
<td>{{ pt.description[:80] }}</td><td>{% if pt.is_automated %}<span class="badge badge-auto">🤖 Auto</span>{% else %}<span class="badge badge-pending">Manual</span>{% endif %}</td></tr>
{% endfor %}</tbody></table></div>
{% endif %}

{% for p in projects %}
<div class="card"><h3>📋 {{ p.title }} <span class="badge badge-{{ p.status|replace(' ','_') }}">{{ p.status }}</span></h3>
<div class="progress-bar"><div class="progress-fill" style="width:{{ p.progress }}%"></div></div><span>{{ p.progress }}% Complete | Worker: {{ p.worker_name or 'Unassigned' }} | Lead: {{ p.leader_name or '-' }}</span>
{% if tasks_by_project.get(p.id) %}
<table style="margin-top:12px"><thead><tr><th>Task</th><th>Assigned To</th><th>Priority</th><th>Status</th><th>Auto</th></tr></thead><tbody>
{% for t in tasks_by_project[p.id] %}
<tr><td>{{ t.title }}</td><td>{{ t.assigned_name or '-' }}</td><td><span class="badge badge-{{ t.priority }}">{{ t.priority }}</span></td>
<td><span class="badge badge-{{ t.status|replace(' ','_') }}">{{ t.status }}</span></td>
<td>{% if t.is_automated %}<span class="badge badge-auto">🤖</span>{% else %}-{% endif %}</td></tr>
{% endfor %}</tbody></table>{% endif %}</div>
{% endfor %}

{% if reports|length > 0 %}
<div class="card"><h3>📄 Generated Reports</h3>
<table><thead><tr><th>Title</th><th>Type</th><th>Created</th><th>Sent</th><th>Action</th></tr></thead><tbody>
{% for r in reports %}
<tr><td>{{ r.title }}</td><td>{{ r.report_type }}</td><td>{{ r.created_at }}</td>
<td>{% if r.sent_to_client %}<span class="badge badge-active">Sent {{ r.sent_date }}</span>{% else %}<span class="badge badge-pending">Not sent</span>{% endif %}</td>
<td><a href="/api/reports/{{ r.id }}/download" target="_blank" class="btn btn-sm btn-primary">📄 View</a>
{% if not r.sent_to_client and user.role in ('super_admin','finance') %}<button class="btn btn-sm btn-secondary" onclick="markSent({{ r.id }})">📧 Mark Sent</button>{% endif %}</td></tr>
{% endfor %}</tbody></table></div>{% endif %}

{% if payments|length > 0 %}
<div class="card"><h3>💰 Payment History</h3>
<table><thead><tr><th>Invoice</th><th>Amount</th><th>Due</th><th>Paid</th><th>Status</th></tr></thead><tbody>
{% for p in payments %}
<tr><td>{{ p.invoice_number }}</td><td><strong>${{ "{:,.0f}".format(p.amount) }}</strong></td><td>{{ p.due_date }}</td>
<td>{{ p.paid_date or '-' }}</td><td><span class="badge badge-{{ p.status }}">{{ p.status }}</span></td></tr>
{% endfor %}</tbody></table></div>{% endif %}

<!-- Add Credential Modal -->
<div class="modal-overlay" id="addCredModal"><div class="modal"><div class="modal-header"><h3>Add Credential</h3><button onclick="closeModal('addCredModal')" class="modal-close">×</button></div>
<div class="modal-body">
<select id="cred_type" class="form-select"><option value="gsc">Google Search Console</option><option value="ga4">Google Analytics GA4</option><option value="cms">CMS/WordPress</option><option value="gbp">Google Business Profile</option><option value="social_fb">Facebook</option><option value="social_ig">Instagram</option><option value="social_tt">TikTok</option><option value="social_li">LinkedIn</option><option value="hosting">Hosting/Server</option><option value="ahrefs">Ahrefs</option><option value="semrush">Semrush</option><option value="other">Other</option></select>
<input id="cred_label" placeholder="Label (e.g. WordPress Admin)" class="form-input">
<input id="cred_user" placeholder="Username/Email" class="form-input">
<input id="cred_pass" placeholder="Password" type="password" class="form-input">
<input id="cred_url" placeholder="Access URL" class="form-input">
<textarea id="cred_notes" placeholder="Notes..." class="form-input"></textarea>
<button class="btn btn-primary btn-full" onclick="addCred()">Save Credential</button></div></div></div>

<script>
function openModal(id){document.getElementById(id).classList.add('show')}
function closeModal(id){document.getElementById(id).classList.remove('show')}
function addCred(){fetch('/api/client-credentials',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
    client_id:{{ client.id }},credential_type:document.getElementById('cred_type').value,label:document.getElementById('cred_label').value,
    username:document.getElementById('cred_user').value,password_enc:document.getElementById('cred_pass').value,
    access_url:document.getElementById('cred_url').value,notes:document.getElementById('cred_notes').value})}).then(()=>location.reload())}
function generateReport(clientId){fetch('/api/reports/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({client_id:clientId,report_type:'monthly'})})
    .then(r=>r.json()).then(r=>{if(r.id){window.open('/api/reports/'+r.id+'/download','_blank')}else{alert(r.error||'Error')}})}
function markSent(reportId){fetch('/api/reports/'+reportId+'/send',{method:'POST'}).then(()=>location.reload())}
function sendReport(){generateReport({{ client.id }})}
</script>
''' + base_end()

# ===== GENERATE ALL =====
if __name__ == "__main__":
    templates_map = {
        "admin_dashboard.html": gen_admin(),
        "worker_dashboard.html": gen_worker(),
        "sales_dashboard.html": gen_sales(),
        "social_dashboard.html": gen_social(),
        "finance_dashboard.html": gen_finance(),
        "settings.html": gen_settings(),
        "monitor.html": gen_monitor(),
        "team_chat.html": gen_team_chat(),
        "client_detail.html": gen_client_detail(),
    }
    
    for fname, content in templates_map.items():
        path = os.path.join(TMPL_DIR, fname)
        with open(path, 'w') as f:
            f.write(content)
        print(f"Generated: {fname} ({len(content)} chars)")
    
    print(f"\nDone! Generated {len(templates_map)} templates.")
