# AI Growth Labs — AI-Powered Local SEO Agency Website

> Full-stack digital marketing agency website with static frontend (38+ pages) and FastAPI backend dashboard.

**Live Site:** https://ai-growth-labs-part2-final-rdmstqlw.devinapps.com  
**Branch:** `devin/1778433837-ai-seo-agency-website`

---

## Quick Start

### Frontend
```bash
python -m http.server 8080
# Visit http://localhost:8080
```

### Backend Dashboard
```bash
cd dashboard
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## What's Built

| Category | Count | Details |
|---|---|---|
| **Service Pages** | 10 | Local SEO, GBP, Reputation, AI SEO, Paid Ads, Social Media, Content, Video SEO, CRO, E-Commerce SEO |
| **Industry Pages** | 12 | Dentists, Lawyers, Restaurants, Plumbers, HVAC, Med Spas, Real Estate, Gyms, Auto Repair, Electricians, Roofing, Pet Services |
| **Blog Posts** | 6 | 1500+ words each with internal links |
| **Dashboard Endpoints** | 99 | Full CRUD for clients, projects, tasks, invoices, rankings, reviews, analytics |
| **Database Tables** | 27 | Users, clients, projects, tasks, invoices, rankings, reviews, etc. |
| **API Integrations** | 9 | OpenAI, Claude, Gemini, Stripe, Twilio, Google APIs, SendGrid |

### Key Features
- **DNA-Level SEO Audit** — 12-pillar analysis with visual scoring, PDF export, email reports
- **Form Security** — Phone validation (28 countries), disposable email blocking, rate limiting (3/day)
- **Full SEO** — Schema markup, OG tags, canonical URLs, sitemap, robots.txt, breadcrumbs
- **Floating CTA** — "Free Audit →" button on every page
- **Responsive Design** — Mobile-first CSS with dark navy/cyan theme

---

## Documentation

| File | Purpose |
|---|---|
| [`PROJECT_TREE.md`](PROJECT_TREE.md) | Complete file tree + code documentation (start here) |
| [`PROJECT_PLAN.md`](PROJECT_PLAN.md) | Step-by-step build roadmap (12 phases) |
| [`FEASIBILITY_REPORT.md`](FEASIBILITY_REPORT.md) | Feasibility analysis for all planned additions |
| [`SEO_AUDIT_REPORT.md`](SEO_AUDIT_REPORT.md) | SEO audit results (38 pages) |
| [`API_GUIDE.md`](API_GUIDE.md) | Backend API documentation |
| [`PROGRESS_LOG.md`](PROGRESS_LOG.md) | Work completion log |

---

## For AI Agents / New Sessions

If you're an AI agent starting a new session on this project:

1. **Read `PROJECT_TREE.md` first** — Understand the full project structure
2. **Read `PROJECT_PLAN.md`** — See what's done and what's next
3. **Check `FEASIBILITY_REPORT.md`** — Time estimates and dependencies
4. **Use `neworigin` remote** for git push (NOT `origin`)
5. **Branch:** `devin/1778433837-ai-seo-agency-website`

### Key conventions:
- Service pages: `pages/[service-name].html`
- Industry pages: `pages/seo-for-[industry].html`
- Blog posts: `pages/blog/[slug].html`
- CSS vars: `--navy-900`, `--cyan`, `--white`, `--gray-300`
- Phone default: `+971 5X XXX XXXX` (UAE)
- Do NOT modify `js/form-validation.js` without understanding the validation system

---

## Tech Stack

HTML5 | CSS3 | JavaScript | Python 3.11 | FastAPI | SQLAlchemy | SQLite | bcrypt | JWT | Jinja2

---

*Last updated: May 2026*
