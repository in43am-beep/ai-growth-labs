# AI Growth Labs — Complete Data Tree

## Project Structure

```
ai-growth-labs/
├── index.html                          # Main homepage
├── css/style.css                       # Frontend styles (Navy + Cyan theme)
├── js/main.js                          # Frontend interactions
├── pages/                              # 16 static HTML pages
│   ├── about.html
│   ├── ai-seo.html
│   ├── blog.html
│   ├── case-studies.html
│   ├── contact.html
│   ├── content-creation.html
│   ├── disclaimer.html
│   ├── free-audit.html
│   ├── gbp-optimization.html
│   ├── local-seo.html
│   ├── paid-advertising.html
│   ├── privacy-policy.html
│   ├── reputation-management.html
│   ├── seo-for-dentists.html
│   ├── seo-for-lawyers.html
│   ├── seo-for-plumbers.html
│   ├── seo-for-restaurants.html
│   ├── social-media.html
│   └── terms.html
├── templates/                          # 16 agency strategy templates
│   ├── ai-seo-agency-os.html
│   ├── client-proposal.html
│   ├── client-reporting.html
│   ├── competitor-styles.html
│   ├── discovery-call.html
│   ├── dna-audit-prompt-level1.html
│   ├── dna-audit-prompt-level2.html
│   ├── index.html
│   ├── kickoff-call.html
│   ├── onboarding-form.html
│   ├── pro-tips-working-patterns.html
│   ├── service-ai-seo.html
│   ├── service-content-creation.html
│   ├── service-gbp-optimization.html
│   ├── service-paid-ads.html
│   ├── service-reputation-management.html
│   └── service-social-media.html
├── dashboard/                          # Backend Application (FastAPI)
│   ├── main.py                         # FastAPI app (75 endpoints, 1900+ lines)
│   ├── database.py                     # SQLite DB init + demo data (720+ lines)
│   ├── static/css/dashboard.css        # Dashboard styles
│   ├── uploads/                        # File upload directory (10MB max)
│   └── templates/                      # 14 Jinja2 HTML templates
│       ├── login.html                  # Auth page (11 demo users)
│       ├── admin_dashboard.html        # Super Admin (full control)
│       ├── worker_dashboard.html       # Workers (time tracking, tasks)
│       ├── client_portal.html          # Client-only view
│       ├── client_detail.html          # Client management page
│       ├── ops_dashboard.html          # Operations Manager
│       ├── finance_dashboard.html      # Finance & Invoicing
│       ├── sales_dashboard.html        # Sales & Leads
│       ├── social_dashboard.html       # Social Media
│       ├── analytics.html              # Revenue & Analytics charts
│       ├── activity_timeline.html      # Audit log timeline
│       ├── performance.html            # Worker performance leaderboard
│       ├── rankings_chart.html         # Keyword ranking Chart.js
│       ├── settings.html               # API & SMTP settings
│       ├── monitor.html                # Team monitor
│       └── team_chat.html              # Internal team chat
├── COMPLETE_STRATEGY.md                # Competitor DNA analysis
├── COMPLETE_EXECUTION_GUIDE.md         # Service delivery guide
├── DEPLOYMENT_GUIDE.md                 # cPanel/VPS deployment
└── DATA_TREE.md                        # This file
```

---

## Database Schema (22 Tables)

### Core Tables

#### `users` (11 demo users)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| username | TEXT NOT NULL | Login username |
| password_hash | TEXT NOT NULL | bcrypt hashed password |
| full_name | TEXT NOT NULL | Display name |
| email | TEXT | Email address |
| role | TEXT NOT NULL | One of 11 roles (see below) |
| rank | TEXT | junior/mid/senior |
| salary | REAL | Monthly salary |
| is_active | INTEGER | 1=active, 0=disabled |
| created_at | TEXT | Timestamp |
| last_login | TEXT | Last login timestamp |

**11 User Roles:**
1. `super_admin` — Full system access
2. `tech_seo` — SEO audit & technical work
3. `content_writer` — Content creation tasks
4. `link_builder` — Link building campaigns
5. `social_media` — Social media management
6. `finance` — Invoicing, payments, expenses
7. `sales` — Lead management, proposals
8. `account_manager` — Client relationship management
9. `operations_manager` — Team oversight, approvals
10. `client` — Client portal access only
11. `worker` — General worker (tasks, time tracking)

#### `clients` (7 demo clients)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| business_name | TEXT NOT NULL | Company name |
| contact_name | TEXT | Primary contact |
| email | TEXT | Contact email |
| phone | TEXT | Phone number |
| website | TEXT | Website URL |
| industry | TEXT | Business industry |
| location | TEXT | City/State |
| status | TEXT | active/inactive/lead/prospect |
| package | TEXT | Service package name |
| monthly_payment | REAL | Monthly fee |
| source | TEXT | Lead source |

#### `projects` (6 demo projects)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| client_id | INTEGER FK → clients | Client reference |
| title | TEXT NOT NULL | Project name |
| service_type | TEXT | local_seo/gbp/reputation/etc |
| status | TEXT | active/completed/paused |
| priority | TEXT | high/medium/low |
| assigned_worker_id | INTEGER FK → users | Assigned worker |
| progress | INTEGER | 0-100% |
| start_date / due_date | TEXT | Date range |

#### `tasks` (11 demo tasks)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK → projects | Parent project |
| title | TEXT NOT NULL | Task name |
| status | TEXT | pending/in_progress/completed/blocked |
| assigned_to | INTEGER FK → users | Worker |
| priority | TEXT | high/medium/low/urgent |
| due_date | TEXT | Deadline |
| is_automated | INTEGER | AI-automated flag |

### Financial Tables

#### `invoices` (5 demo invoices)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| client_id | INTEGER FK → clients | Client reference |
| invoice_number | TEXT NOT NULL UNIQUE | e.g. INV-2025-001 |
| issue_date | TEXT | Issue date |
| due_date | TEXT | Payment deadline |
| subtotal | REAL | Before tax |
| tax_rate | REAL | Tax percentage |
| tax_amount | REAL | Tax dollar amount |
| total | REAL | Final amount |
| status | TEXT | draft/sent/paid/overdue |

#### `invoice_items` (5 demo items)
| Column | Type | Description |
|--------|------|-------------|
| invoice_id | INTEGER FK → invoices | Parent invoice |
| description | TEXT NOT NULL | Line item desc |
| quantity | REAL | Units |
| rate | REAL | Per-unit price |
| amount | REAL | Line total |

#### `payments` (6 demo payments)
| Column | Type | Description |
|--------|------|-------------|
| client_id | INTEGER FK → clients | Client reference |
| amount | REAL NOT NULL | Payment amount |
| status | TEXT | paid/pending/overdue |

#### `expenses` (6 demo expenses)
| Column | Type | Description |
|--------|------|-------------|
| category | TEXT NOT NULL | tool/marketing/salary/office |
| amount | REAL NOT NULL | Expense amount |

#### `contracts` (3 demo contracts)
| Column | Type | Description |
|--------|------|-------------|
| client_id | INTEGER FK → clients | Client reference |
| title | TEXT NOT NULL | Contract name |
| start_date / end_date | TEXT | Contract period |
| monthly_value | REAL | Monthly contract value |
| status | TEXT | active/expired/pending |
| auto_renew | INTEGER | Auto-renewal flag |

### SEO & Marketing Tables

#### `keyword_rankings` (9 demo entries)
| Column | Type | Description |
|--------|------|-------------|
| client_id | INTEGER FK → clients | Client reference |
| keyword | TEXT NOT NULL | Target keyword |
| position | INTEGER | Current ranking |
| previous_position | INTEGER | Previous ranking |
| search_volume | INTEGER | Monthly search volume |
| url | TEXT | Ranking URL |
| tracked_date | TEXT | Date tracked |

#### `seo_audits`
| Column | Type | Description |
|--------|------|-------------|
| client_id | INTEGER FK → clients | Client reference |
| website_url | TEXT NOT NULL | Audited URL |
| audit_data | TEXT | JSON audit results |
| overall_score | INTEGER | 0-100 score |
| ai_provider | TEXT | claude/chatgpt/gemini |

#### `social_posts` (5 demo posts)
| Column | Type | Description |
|--------|------|-------------|
| client_id | INTEGER FK → clients | Client reference |
| platform | TEXT NOT NULL | facebook/instagram/linkedin/twitter/google |
| content | TEXT | Post content |
| status | TEXT | draft/scheduled/published |
| engagement_data | TEXT | JSON engagement metrics |

### Operations Tables

#### `time_entries`
| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER FK → users | Worker |
| task_id | INTEGER FK → tasks | Task being timed |
| project_id | INTEGER FK → projects | Project reference |
| start_time | TEXT NOT NULL | Timer start |
| end_time | TEXT | Timer stop |
| hours | REAL | Calculated duration |

#### `client_locations` (5 demo locations)
| Column | Type | Description |
|--------|------|-------------|
| client_id | INTEGER FK → clients | Client reference |
| location_name | TEXT NOT NULL | Office/branch name |
| address | TEXT | Street address |
| city / state / zip_code | TEXT | Location details |
| phone | TEXT | Location phone |
| gbp_url | TEXT | Google Business Profile URL |

#### `file_attachments`
| Column | Type | Description |
|--------|------|-------------|
| related_type | TEXT NOT NULL | client/task/report/invoice |
| related_id | INTEGER NOT NULL | Related entity ID |
| filename | TEXT NOT NULL | Original filename |
| filepath | TEXT NOT NULL | Server file path |
| filesize | INTEGER | Size in bytes |
| mime_type | TEXT | MIME type |

#### `approval_requests`
| Column | Type | Description |
|--------|------|-------------|
| task_id / project_id / client_id | INTEGER FK | Related entity |
| request_type | TEXT | content/budget/deliverable/access |
| status | TEXT | pending/approved/rejected |
| requested_by / reviewed_by | INTEGER FK → users | Participants |

### System Tables

#### `notifications` (4 demo notifications)
| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER FK → users | Recipient |
| title | TEXT NOT NULL | Notification title |
| type | TEXT | info/warning/success/task/urgent |
| is_read | INTEGER | Read status |

#### `activity_log`
| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER FK → users | Actor |
| action | TEXT NOT NULL | Action type |
| details | TEXT | Description |
| entity_type | TEXT | client/task/project/etc |
| entity_id | INTEGER | Related entity ID |

#### `api_settings` (4 entries: Claude, ChatGPT, Gemini, SMTP)
| Column | Type | Description |
|--------|------|-------------|
| provider | TEXT NOT NULL | claude/chatgpt/gemini/smtp |
| api_key | TEXT | Encrypted API key |
| is_active | INTEGER | Active status |
| config_json | TEXT | JSON configuration |

#### `client_reports`
| Column | Type | Description |
|--------|------|-------------|
| client_id | INTEGER FK → clients | Client reference |
| report_type | TEXT | weekly/monthly/audit/custom/white_label |
| report_data | TEXT | JSON report data |
| sent_to_client | INTEGER | Email sent flag |

#### Other Tables
- `chat_messages` — Live chat conversations
- `chat_requests` — Team chat requests
- `team_chats` — Internal team messages
- `suggestions` — Worker suggestions (2 demo)
- `sales_leads` — CRM leads (3 demo)
- `client_credentials` — Stored credentials vault (5 demo)
- `package_tasks` — Service package task templates (82 demo)

---

## API Endpoints (75 total)

### Authentication
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/login` | Login page | Public |
| POST | `/login` | Authenticate user | Public |
| GET | `/logout` | Clear session | Auth |
| POST | `/api/password/change` | Change password | Auth |

### Dashboards (Pages)
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/dashboard` | Role-based dashboard | Auth |
| GET | `/client/{id}` | Client detail page | Auth |
| GET | `/settings` | API settings page | Super Admin |
| GET | `/monitor` | Team monitor page | Auth |
| GET | `/team-chat` | Team chat page | Auth |
| GET | `/analytics` | Analytics dashboard | Super Admin, Finance, Ops |
| GET | `/activity` | Activity timeline page | Super Admin, Ops |
| GET | `/performance` | Performance leaderboard | Super Admin, Ops |
| GET | `/rankings/{client_id}` | Rankings chart page | Auth |

### Client Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/clients` | Add new client | Super Admin |
| GET | `/api/clients/stats` | Dashboard statistics | Auth |
| POST | `/api/locations` | Add client location | Auth |
| GET | `/api/locations/{client_id}` | Get client locations | Auth |

### Project & Task Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/projects` | Create project | Super Admin |
| PUT | `/api/projects/{id}/progress` | Update project progress | Auth |
| POST | `/api/tasks` | Create task | Auth |
| PUT | `/api/tasks/{id}/status` | Update task status | Auth |
| POST | `/api/tasks/bulk` | Create multiple tasks | Super Admin, Ops, AM |

### Time Tracking
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/time/start` | Start timer | Auth |
| POST | `/api/time/stop` | Stop timer | Auth |
| GET | `/api/time/active` | Get active timer | Auth |

### Invoicing
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/invoices` | Create invoice | Super Admin, Finance |
| GET | `/api/invoices` | List invoices | Super Admin, Finance |
| PUT | `/api/invoices/{id}/status` | Update invoice status | Super Admin, Finance |
| GET | `/api/invoices/{id}/download` | Download printable HTML | Auth |

### Reports & Analytics
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/reports/white-label` | Generate white-label report | Super Admin, Finance, Ops, AM |
| GET | `/api/reports/{id}/white-label` | Download branded report | Auth |
| POST | `/api/reports/{id}/email` | Email report to client | Super Admin, Finance, Ops, AM |
| GET | `/api/analytics/revenue` | Revenue forecasting data | Super Admin, Finance, Ops |
| GET | `/api/analytics/overview` | Dashboard analytics data | Super Admin, Ops |

### Rankings & SEO
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/rankings` | Add keyword ranking | Auth |
| GET | `/api/rankings/{client_id}` | Get client rankings | Auth |
| POST | `/api/audit` | Run SEO audit | Auth |

### Communication
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/email/send` | Send email via SMTP | Super Admin, Finance, Ops, AM |
| GET | `/api/notifications` | Get user notifications | Auth |
| POST | `/api/notifications/read` | Mark all read | Auth |
| POST | `/api/notifications/create` | Send notification | Super Admin, Ops |

### Data Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/export/{table_name}` | Export table to CSV | Super Admin, Finance |
| GET | `/api/search?q=...` | Global search | Auth |
| POST | `/api/upload` | Upload file (10MB max) | Auth |
| GET | `/api/attachments/{type}/{id}` | List file attachments | Auth |

### Workers & Performance
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/performance/{user_id}` | Worker performance stats | Super Admin, Ops, Self |
| GET | `/api/activity` | Activity log data | Auth |
| POST | `/api/workers` | Add new worker | Super Admin |

### Approvals & Contracts
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/approvals` | Create approval request | Auth |
| PUT | `/api/approvals/{id}` | Approve/reject | Super Admin, Ops |
| GET | `/api/contracts` | List contracts | Super Admin, Finance, Ops |

---

## Security Features

| Feature | Implementation |
|---------|---------------|
| Password Hashing | bcrypt via passlib |
| Authentication | JWT tokens (python-jose) with 24hr expiry |
| Rate Limiting | IP-based (5 failed logins per 5 minutes) |
| Role-Based Access | 11 roles with endpoint-level enforcement |
| Security Headers | X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy |
| SQL Injection Prevention | Parameterized queries throughout |
| File Upload Validation | MIME type check, 10MB max, safe filename |
| Activity Logging | All actions logged with user, timestamp, entity |
| Session Management | HTTP-only cookies with JWT |
| API Docs Disabled | `docs_url=None, redoc_url=None` |

---

## Demo Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | super_admin |
| sarah_k | password123 | tech_seo |
| content_anna | password123 | content_writer |
| link_mike | password123 | link_builder |
| social_emma | password123 | social_media |
| rachel_g | password123 | finance |
| sales_john | password123 | sales |
| am_lisa | password123 | account_manager |
| ops_manager | password123 | operations_manager |
| client_chen | password123 | client |
| worker_ali | password123 | worker |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12 + FastAPI |
| Database | SQLite3 |
| Templates | Jinja2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Charts | Chart.js |
| Styling | Custom CSS (Navy/Cyan theme) |
| Server | Uvicorn |
| Frontend | Static HTML/CSS/JS |
