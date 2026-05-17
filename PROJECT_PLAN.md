# AI Growth Labs — Master Project Plan
## Step-by-Step Build Roadmap

**Repo:** `github.com/mariadomiguz-a11y/ai-growth-labs-final-3-update`  
**Branch:** `devin/1778433837-ai-seo-agency-website`  
**Last Updated:** May 2026  
**Live Frontend:** https://ai-growth-labs-part2-final-rdmstqlw.devinapps.com  

---

## HOW TO USE THIS FILE

If you're starting a new session, read this file first. It tells you:
1. What's already done
2. What needs to be done next
3. Exact file paths, naming conventions, and patterns to follow
4. Which phase to work on next

**Always update the STATUS column below after completing work.**

---

## COMPLETED WORK (DO NOT REDO)

### Already Built:
- [x] 10 service pages (local-seo, gbp, reputation, ai-seo, paid-ads, social-media, content-creation, video-seo, cro, ecommerce-seo)
- [x] 12 industry pages (dentists, lawyers, restaurants, plumbers, hvac, medical-spas, real-estate, gyms, auto-repair, electricians, roofing, pet-services)
- [x] 6 blog posts in `pages/blog/`
- [x] DNA-Level SEO Audit page with 12 pillars, PDF export, email report
- [x] Form validation (29 countries phone, disposable email blocking, rate limiting 3/day)
- [x] Floating CTA button on all pages
- [x] Video SEO pricing ($997, $1,997, $3,497)
- [x] Contact page with service dropdown + Book Strategy Call CTA
- [x] About page with LinkedIn skills section (27 skills + 6 service cards)
- [x] Schema markup (LocalBusiness) on all pages
- [x] OG tags, twitter cards, hreflang, canonical URLs on all pages
- [x] Breadcrumb schema on service/industry pages
- [x] sitemap.xml, robots.txt, 404.html
- [x] SEO audit of all 38 pages (0 critical issues)
- [x] FastAPI dashboard backend (99 endpoints, 27 tables)
- [x] Nav/footer consistent across all 38 pages
- [x] **PHASE 1 COMPLETE:** 15 new service pages with pricing tiers (Email Marketing, Web Design, GEO, Geofencing, Analytics, Lead Nurture, Programmatic Ads, Digital PR, Sales Enablement, UX/UI Design, Marketing Consulting, Brand Strategy, Influencer Marketing, Marketplace Marketing, Link Building)
- [x] Nav/footer updated on ALL 63+ pages with 25 services + 22 industries
- [x] Sitemap updated (62 URLs)
- [x] Contact page service dropdown updated (25 options)
- [x] **PHASE 2 COMPLETE:** 10 new industry pages (Cleaning, Movers, Insurance, Financial Advisors, Chiropractors, Landscaping, Photographers, Salons, Veterinarians, Construction)
- [x] Homepage industries grid updated (22 clickable cards)
- [x] Free-audit form industry dropdown updated (22 options)
- [x] **PHASE 3 COMPLETE:** All 25 service pages now have consistent Starter/Growth/Authority pricing tiers matching PROJECT_PLAN.md

### Key Files:
- **CSS:** `css/style.css` — all styles, CSS variables for colors
- **JS:** `js/main.js` — nav toggle, mobile menu
- **JS:** `js/form-validation.js` — phone/email/rate limiting validation (IIFE pattern)
- **Backend:** `dashboard/main.py` (2760 lines), `dashboard/database.py` (724 lines)
- **Templates:** `dashboard/templates/` (16 HTML templates)

### Conventions:
- Service pages: `pages/[service-name].html`
- Industry pages: `pages/seo-for-[industry].html`
- Blog posts: `pages/blog/[slug].html`
- All pages use `../css/style.css` and `../js/main.js` relative paths
- Blog pages use `../../css/style.css` (extra level)
- Nav has: Services dropdown (25 items), Industries dropdown (22 items), Case Studies, About, Blog, Contact, Free Audit button
- Footer has: Services links, Industries links, Company links, Social links
- Every page has: og:title, og:description, og:image, og:url, twitter:card, canonical, hreflang, LocalBusiness schema
- Phone placeholder: `+971 5X XXX XXXX` (UAE default)
- Color scheme: `--navy-900`, `--cyan`, `--white`, `--gray-300` CSS variables

---

## PHASE 1: NEW SERVICE PAGES (15 pages)
**Priority:** HIGH | **Estimated:** 6-7 hours | **Status:** COMPLETED (May 2026)

### What to do:
Create 15 new service pages following the EXACT pattern of existing service pages (e.g., `pages/video-seo.html`).

### Each page must include:
1. Same nav/header as all other pages
2. `<section class="page-hero">` with breadcrumb, H1, description, CTA button
3. 2 content sections (problem/solution with stats card)
4. Services grid (4-5 service cards with icons)
5. **Pricing section** with 3 tiers (Starter/Growth/Authority)
6. CTA section before footer
7. Same footer as all other pages
8. Floating CTA button
9. Full SEO meta tags (title, description, og tags, canonical, schema, hreflang)
10. Breadcrumb schema JSON-LD

### Pages to create:

| # | Page | File | Pricing (Starter/Growth/Authority) |
|---|---|---|---|
| 1 | Email Marketing | `pages/email-marketing.html` | $497 / $997 / $1,997 |
| 2 | Web Design & Development | `pages/web-design.html` | $2,997 / $5,997 / $9,997 (one-time) |
| 3 | GEO (AI Search Optimization) | `pages/geo-optimization.html` | $797 / $1,497 / $2,997 |
| 4 | Geofencing Marketing | `pages/geofencing.html` | $697 / $1,297 / $2,497 |
| 5 | Analytics & Reporting | `pages/analytics-reporting.html` | $397 / $797 / $1,497 |
| 6 | Lead Nurture / Automation | `pages/lead-nurture.html` | $597 / $1,197 / $2,297 |
| 7 | Programmatic Advertising | `pages/programmatic-ads.html` | $997 / $1,997 / $3,497 |
| 8 | Digital PR | `pages/digital-pr.html` | $797 / $1,497 / $2,997 |
| 9 | Sales Enablement | `pages/sales-enablement.html` | $697 / $1,297 / $2,497 |
| 10 | UX/UI Design | `pages/ux-design.html` | $1,497 / $2,997 / $5,997 (one-time) |
| 11 | Marketing Consulting | `pages/marketing-consulting.html` | $497 / $997 / $1,997 |
| 12 | Brand Strategy | `pages/brand-strategy.html` | $997 / $1,997 / $3,497 |
| 13 | Influencer Marketing | `pages/influencer-marketing.html` | $797 / $1,497 / $2,997 |
| 14 | Marketplace Marketing | `pages/marketplace-marketing.html` | $697 / $1,297 / $2,497 |
| 15 | Link Building | `pages/link-building.html` | $597 / $1,197 / $2,297 |

### After creating pages:
- [x] Update nav dropdown on ALL pages to include new services (use Python script)
- [x] Update footer service links on ALL pages
- [x] Update sitemap.xml with new URLs
- [x] Update contact.html service dropdown with 15 new options
- [ ] Run SEO audit on new pages

---

## PHASE 2: NEW INDUSTRY PAGES (10 pages)
**Priority:** HIGH | **Estimated:** 3-4 hours | **Status:** COMPLETED (May 2026)

### Pages to create:
Follow pattern of `pages/seo-for-dentists.html`.

| # | Industry | File |
|---|---|---|
| 1 | Home Cleaning | `pages/seo-for-cleaning.html` |
| 2 | Moving Companies | `pages/seo-for-movers.html` |
| 3 | Insurance Agents | `pages/seo-for-insurance.html` |
| 4 | Financial Advisors | `pages/seo-for-financial-advisors.html` |
| 5 | Chiropractors | `pages/seo-for-chiropractors.html` |
| 6 | Landscaping | `pages/seo-for-landscaping.html` |
| 7 | Photographers | `pages/seo-for-photographers.html` |
| 8 | Salons & Beauty | `pages/seo-for-salons.html` |
| 9 | Veterinarians | `pages/seo-for-veterinarians.html` |
| 10 | Construction | `pages/seo-for-construction.html` |

### After creating pages:
- [x] Update nav Industries dropdown on ALL pages (22 industries)
- [x] Update footer industry links on ALL pages
- [x] Update index.html industry cards (22 clickable cards)
- [x] Update sitemap.xml (62 total URLs)
- [x] Update free-audit.html industry dropdown
- [x] Schema serviceType includes all 25 services

---

## PHASE 3: PRICING TIERS ON ALL SERVICE PAGES
**Priority:** HIGH | **Estimated:** 6 hours | **Status:** COMPLETED (May 2026)

### What to do:
Add 3-tier pricing section to all 10 EXISTING service pages (new pages from Phase 1 already have pricing).

Use this HTML pattern:
```html
<section class="section section-light">
  <div class="container">
    <div class="text-center">
      <div class="section-title">Service Name <span class="highlight">Packages</span></div>
    </div>
    <div class="pricing-grid">
      <div class="pricing-card">...</div>
      <div class="pricing-card featured">...</div>
      <div class="pricing-card">...</div>
    </div>
  </div>
</section>
```

### Pricing for existing services:

| Service | Starter | Growth | Authority |
|---|---|---|---|
| Local SEO | $497/mo | $997/mo | $1,997/mo |
| GBP Optimization | $297/mo | $597/mo | $997/mo |
| Reputation Management | $497/mo | $997/mo | $1,997/mo |
| AI SEO Services | $797/mo | $1,497/mo | $2,997/mo |
| Paid Advertising | $997/mo + ad spend | $1,997/mo + ad spend | $3,497/mo + ad spend |
| Social Media | $497/mo | $997/mo | $1,997/mo |
| Content Creation | $597/mo | $1,197/mo | $2,297/mo |
| Video SEO | $997/mo | $1,997/mo | $3,497/mo | (ALREADY DONE)
| CRO | $597/mo | $1,197/mo | $2,297/mo |
| E-Commerce SEO | $797/mo | $1,497/mo | $2,997/mo |

---

## PHASE 4: WEBSITE-WIDE IMPROVEMENTS
**Priority:** HIGH | **Estimated:** 4-5 hours | **Status:** NOT STARTED

### Tasks:
1. [ ] Add phone number to header nav: `<a href="tel:+18005550199" class="nav-phone">📞 (800) 555-0199</a>`
2. [ ] Add testimonials section to index.html (3-4 client quotes with names/businesses)
3. [ ] Add trust badges section to index.html (Google Partner, Clutch rated, BBB, etc.)
4. [ ] Add social proof numbers to homepage hero ("500+ Businesses Served", "10,000+ Reviews Generated", "94% Client Retention")
5. [ ] Add FAQ section to each service page (5-7 questions per page with FAQ schema)
6. [ ] Add related services section at bottom of each service page
7. [ ] Add "Get Free Proposal" form as alternative CTA (not just audit)

---

## PHASE 5-6: BLOG POSTS (50 total)
**Priority:** MEDIUM | **Estimated:** 24-30 hours | **Status:** NOT STARTED

### Batch 1 (25 posts) — Phase 5:
Target keywords for each service. Each post: 1500+ words, internal links to service pages, proper SEO meta.

### Blog post topics:
1. How Email Marketing Increases Local Business Revenue
2. 10 Web Design Mistakes Killing Your Conversions
3. What is GEO? AI Search Optimization Explained
4. Geofencing Marketing for Local Businesses: Complete Guide
5. How to Track Marketing ROI: Analytics Guide
6. Lead Nurturing 101: Turn Leads into Customers
7. Programmatic Advertising vs Google Ads: Which is Better?
8. Digital PR Strategies for Local Businesses
9. Sales Enablement: How Marketing Supports Sales
10. UX Design Principles Every Small Business Website Needs
11. Local SEO Checklist 2026
12. Google Business Profile: Complete Setup Guide
13. How to Get More Google Reviews (Ethically)
14. AI SEO: How ChatGPT Changes Search
15. Facebook Ads vs Google Ads for Local Businesses
16. Social Media Content Calendar Template
17. Video SEO: How to Rank on YouTube
18. CRO Best Practices: Double Your Conversions
19. E-Commerce SEO Checklist
20. Brand Strategy Guide for Small Businesses
21. Influencer Marketing on a Budget
22. Amazon SEO: Product Listing Optimization
23. Link Building Strategies That Actually Work
24. Marketing Consulting: When to Hire an Agency
25. Marketing Automation Tools Comparison

### Batch 2 (25 posts) — Phase 6:
Industry-specific posts (one per industry) + additional service posts.

---

## PHASE 7: CASE STUDIES
**Priority:** MEDIUM | **Estimated:** 3-4 hours | **Status:** NOT STARTED

### Create 5 detailed case study pages:
| # | Case Study | Results to Show |
|---|---|---|
| 1 | Dental Practice: 300% more Google reviews | Before/after reviews, rankings |
| 2 | Law Firm: #1 on Google Maps | Traffic increase, lead gen |
| 3 | Restaurant: 250% more online orders | Revenue increase, foot traffic |
| 4 | HVAC Company: Dominating local search | Ranking keywords, calls |
| 5 | Med Spa: Social media to 50K followers | Engagement, bookings |

---

## PHASE 8: FREE TOOLS
**Priority:** MEDIUM | **Estimated:** 6-8 hours | **Status:** NOT STARTED

### Tools to build (all frontend, no backend needed):
1. **ROI Calculator** (`pages/tools/roi-calculator.html`) — Input ad spend, get estimated ROI
2. **Meta Tag Generator** (`pages/tools/meta-generator.html`) — Generate title/description tags
3. **Keyword Density Checker** (`pages/tools/keyword-checker.html`) — Paste text, get analysis
4. **Google Review Link Generator** (`pages/tools/review-link-generator.html`) — Generate direct review link

---

## PHASE 9: DASHBOARD — CLIENT PORTAL
**Priority:** LOW | **Estimated:** 10-14 hours | **Status:** NOT STARTED

### Tasks:
1. Build client-facing dashboard (separate from admin)
2. Client login with project overview
3. Report viewing (monthly SEO reports)
4. Invoice history
5. Task/ticket submission
6. Direct messaging to account manager

### Files to modify:
- `dashboard/main.py` — Add client portal routes
- `dashboard/database.py` — Add client access tables
- `dashboard/templates/client_portal.html` — Already exists, enhance

---

## PHASE 10: DASHBOARD — CRM & INTEGRATIONS
**Priority:** LOW | **Estimated:** 16-24 hours | **Status:** NOT STARTED

### Requires API keys:
- Twilio (call tracking) — `TWILIO_SID`, `TWILIO_TOKEN`
- Stripe (invoicing) — `STRIPE_SECRET_KEY`
- OpenAI (AI features) — `OPENAI_API_KEY`
- HubSpot or Salesforce (CRM) — OAuth credentials

---

## PHASE 11: AI VISIBILITY TRACKING
**Priority:** LOW | **Estimated:** 14-20 hours | **Status:** NOT STARTED

### Build tool to track:
- Brand mentions in ChatGPT, Copilot, Gemini
- AI Overview appearances
- Generative search visibility
- Competitor comparison

---

## PHASE 12: CITY-SPECIFIC LANDING PAGES
**Priority:** LOW | **Estimated:** 8-10 hours | **Status:** NOT STARTED

### Create pages like:
- `pages/cities/seo-dentists-new-york.html`
- `pages/cities/seo-plumbers-dallas.html`
- Use script to generate 50+ city × industry combinations

---

## QUICK REFERENCE — FILE NAMING

```
pages/
├── [service-name].html          # Service pages
├── seo-for-[industry].html      # Industry pages  
├── blog/
│   └── [slug].html              # Blog posts
├── tools/
│   └── [tool-name].html         # Free tools
├── cities/
│   └── seo-[industry]-[city].html  # City landing pages
├── case-studies/
│   └── [case-name].html         # Detailed case studies
```

---

## QUICK REFERENCE — TEMPLATE STRUCTURE

Every service/industry page follows this structure:
```
<!DOCTYPE html>
<html lang="en">
<head>
  [meta tags, canonical, og tags, schema, CSS link]
</head>
<body>
  <header> [nav with dropdowns] </header>
  <section class="page-hero"> [breadcrumb, H1, description, CTA] </section>
  <section class="section"> [content + stats card] </section>
  <section class="section section-light"> [services grid] </section>
  <section class="section"> [pricing grid - 3 tiers] </section>
  <section class="section section-light"> [process steps] </section>
  <section class="cta-section"> [final CTA] </section>
  <footer> [links grid + social] </footer>
  <a class="floating-cta"> [Free Audit button] </a>
  <script src="../js/main.js"></script>
</body>
</html>
```

---

*Last updated by: Devin Session effe7add916348fdba7bc832bc5db2d4*  
*Next session should start with: Phase 1 (New Service Pages)*
