# API Integration Guide — AI Growth Labs OS

## Overview
The system uses **9 API integrations**. All work in **demo mode** without API keys (returns realistic mock data). Add real API keys to go live.

**Where to configure:** Dashboard → Login as Super Admin → `/settings`

---

## 1. AI Providers (Pick at least ONE)

### Claude (Anthropic)
| Field | Value |
|-------|-------|
| **Settings Location** | Dashboard → Settings → AI Providers → Claude Sonnet |
| **API Key Source** | https://console.anthropic.com/settings/keys |
| **Cost** | ~$3/MTok input, $15/MTok output |
| **Used For** | SEO audits, content generation, competitor analysis, AI chat assistant |
| **Code Location** | `dashboard/main.py` — search for `provider == "claude"` |
| **Production Code** | Uncomment `import anthropic` block in `/api/ai/audit/{client_id}` endpoint |

### ChatGPT (OpenAI)
| Field | Value |
|-------|-------|
| **Settings Location** | Dashboard → Settings → AI Providers → ChatGPT |
| **API Key Source** | https://platform.openai.com/api-keys |
| **Cost** | ~$2.50/MTok input, $10/MTok output (GPT-4.5) |
| **Used For** | Same as Claude — system auto-selects whichever is active |
| **Code Location** | `dashboard/main.py` — search for `provider == "chatgpt"` |
| **Production Code** | Uncomment `import openai` block |

### Google Gemini
| Field | Value |
|-------|-------|
| **Settings Location** | Dashboard → Settings → AI Providers → Google Gemini |
| **API Key Source** | https://aistudio.google.com/app/apikey |
| **Cost** | Free tier available, then ~$1.25/MTok |
| **Used For** | Same as Claude/ChatGPT |
| **Code Location** | `dashboard/main.py` — search for `provider == "gemini"` |
| **Production Code** | Uncomment `import google.generativeai` block |

**How to switch providers:** System uses first active provider. To switch, deactivate current and activate new one in Settings.

---

## 2. Communication Integrations

### SMTP (Email)
| Field | Value |
|-------|-------|
| **Settings Location** | Dashboard → Settings → Communication → Email (SMTP) |
| **Required Fields** | SMTP Password/App Password, From Email |
| **Gmail Setup** | Create App Password at https://myaccount.google.com/apppasswords |
| **Used For** | Email reports to clients, payment reminders, campaign emails |
| **Code Location** | `dashboard/main.py` — search for `smtp` |
| **Production Libraries** | `smtplib` (built-in Python) or `SendGrid`/`Mailgun` for bulk |

### Twilio (Voice/SMS)
| Field | Value |
|-------|-------|
| **Settings Location** | Dashboard → Settings → Communication → Twilio Voice/SMS |
| **Required Fields** | Auth Token, Account SID, Phone Number |
| **API Key Source** | https://console.twilio.com |
| **Cost** | $1/mo phone number + $0.0085/min voice + $0.0079/SMS |
| **Used For** | AI voice agent (IVR), outbound calls, SMS alerts, call recording |
| **Code Location** | `dashboard/main.py` — search for `twilio` |
| **Endpoints** | `/api/voice/incoming` (webhook), `/api/voice/menu`, `/api/voice/recording`, `/api/voice/outbound` |
| **Production Library** | `pip install twilio` → uncomment `from twilio.rest import Client` |
| **Twilio Setup** | Set voice webhook URL to `https://yourdomain.com/api/voice/incoming` in Twilio Console |

### WhatsApp Business
| Field | Value |
|-------|-------|
| **Settings Location** | Dashboard → Settings → Communication → WhatsApp Business |
| **Required Fields** | API Token, Phone Number ID |
| **API Key Source** | https://developers.facebook.com/apps → WhatsApp → API Setup |
| **Cost** | First 1000 conversations/mo free, then $0.005-0.08/conversation |
| **Used For** | Client updates, report sharing, appointment reminders |
| **Code Location** | `dashboard/main.py` — search for `whatsapp` |
| **Endpoints** | `/api/whatsapp/send`, `/api/whatsapp/webhook` (incoming) |
| **Webhook Setup** | Set webhook URL to `https://yourdomain.com/api/whatsapp/webhook` in Meta Developer Portal |

### Slack Notifications
| Field | Value |
|-------|-------|
| **Settings Location** | Dashboard → Settings → Communication → Slack Notifications |
| **Required Fields** | Bot Token or Incoming Webhook URL |
| **API Key Source** | https://api.slack.com/apps → Create App → Incoming Webhooks |
| **Cost** | Free |
| **Used For** | Team notifications (new leads, task completions, payments) |
| **Code Location** | `dashboard/main.py` — search for `slack` |
| **Endpoints** | `/api/slack/send`, `/api/slack/events` |

---

## 3. Billing & Analytics

### Stripe (Recurring Billing)
| Field | Value |
|-------|-------|
| **Settings Location** | Dashboard → Settings → Billing → Stripe Billing |
| **Required Fields** | Secret Key (sk_live_...), Publishable Key (pk_live_...), Webhook Secret (whsec_...) |
| **API Key Source** | https://dashboard.stripe.com/apikeys |
| **Cost** | 2.9% + $0.30 per transaction |
| **Used For** | Recurring subscriptions, auto-invoicing, payment processing |
| **Code Location** | `dashboard/main.py` — search for `stripe` |
| **Endpoints** | `/api/billing/create-subscription`, `/api/billing/cancel-subscription`, `/api/billing/webhook`, `/api/billing/send-reminder` |
| **Production Library** | `pip install stripe` → uncomment `import stripe` blocks |
| **Webhook Setup** | Add webhook endpoint `https://yourdomain.com/api/billing/webhook` in Stripe Dashboard → Developers → Webhooks |

### Google Search Console
| Field | Value |
|-------|-------|
| **Settings Location** | Dashboard → Settings → Analytics → Google Search Console |
| **Required Fields** | OAuth Refresh Token, Client ID, Client Secret, Property URL |
| **Setup Steps** | 1. Go to https://console.cloud.google.com/apis/credentials 2. Create OAuth 2.0 Client ID 3. Enable "Search Console API" 4. Get refresh token via OAuth flow |
| **Cost** | Free |
| **Used For** | Real keyword rankings, click data, impressions, CTR, position tracking |
| **Code Location** | `dashboard/main.py` — search for `google_search_console` |
| **Endpoints** | `/api/gsc/rankings/{client_id}`, `/api/gsc/sync/{client_id}` |
| **Production Library** | `pip install google-api-python-client google-auth` → uncomment `from googleapiclient.discovery import build` |

---

## 4. All API Endpoints (New)

| # | Endpoint | Method | Auth | Description |
|---|----------|--------|------|-------------|
| 1 | `/api/ai/audit/{client_id}` | POST | super_admin, tech_seo, ops_mgr | Run AI SEO audit |
| 2 | `/api/ai/content/generate` | POST | super_admin, tech_seo, content_writer, social_media, ops_mgr | Generate blog/social content |
| 3 | `/api/ai/competitor-analysis/{client_id}` | POST | super_admin, tech_seo, ops_mgr | AI competitor analysis |
| 4 | `/api/ai/chat-assistant` | POST | Any authenticated | AI Q&A for workers |
| 5 | `/api/voice/incoming` | POST | Public (Twilio webhook) | IVR voice agent |
| 6 | `/api/voice/menu` | POST | Public (Twilio webhook) | Voice menu handler |
| 7 | `/api/voice/recording` | POST | Public (Twilio webhook) | Recording handler |
| 8 | `/api/voice/outbound` | POST | super_admin, sales, account_mgr | Initiate outbound call |
| 9 | `/api/whatsapp/send` | POST | super_admin, sales, account_mgr, ops_mgr | Send WhatsApp message |
| 10 | `/api/whatsapp/webhook` | POST/GET | Public (Meta webhook) | Receive WhatsApp messages |
| 11 | `/api/slack/send` | POST | super_admin, ops_mgr | Send Slack notification |
| 12 | `/api/slack/events` | POST | Public (Slack Events API) | Slack event handler |
| 13 | `/api/gsc/rankings/{client_id}` | GET | super_admin, tech_seo, ops_mgr, client | Get GSC keyword data |
| 14 | `/api/gsc/sync/{client_id}` | POST | super_admin, tech_seo, ops_mgr | Sync GSC → local DB |
| 15 | `/api/billing/create-subscription` | POST | super_admin, finance | Create Stripe subscription |
| 16 | `/api/billing/cancel-subscription` | POST | super_admin, finance | Cancel subscription |
| 17 | `/api/billing/webhook` | POST | Public (Stripe webhook) | Stripe payment events |
| 18 | `/api/billing/send-reminder` | POST | super_admin, finance | Send payment reminder |
| 19 | `/api/user/theme` | POST/GET | Any authenticated | Dark/Light mode toggle |
| 20 | `/api/scheduled-tasks/create` | POST | super_admin, ops_mgr | Create scheduled task |
| 21 | `/api/email/campaign` | POST | super_admin, social_media, sales | Send email campaign |
| 22 | `/api/integrations/status` | GET | super_admin | Check all integration status |

---

## 5. Quick Production Setup

### Minimum viable setup (3 APIs):
1. **One AI Provider** (Claude recommended) — for SEO audits, content gen
2. **SMTP** (Gmail App Password) — for sending reports
3. **Stripe** — for billing clients

### Full production setup (all 9):
```bash
# Required pip packages for production
pip install anthropic openai google-generativeai  # AI providers
pip install twilio                                  # Voice/SMS
pip install stripe                                  # Billing
pip install google-api-python-client google-auth    # GSC
# SMTP & Slack use built-in Python libraries (smtplib, requests)
# WhatsApp uses Meta Graph API via requests
```

### Environment variables (optional alternative to Settings UI):
```bash
export CLAUDE_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="AI..."
export TWILIO_ACCOUNT_SID="AC..."
export TWILIO_AUTH_TOKEN="..."
export TWILIO_PHONE="+1..."
export STRIPE_SECRET_KEY="sk_live_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export WHATSAPP_TOKEN="EAA..."
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export GSC_CLIENT_ID="..."
export GSC_CLIENT_SECRET="..."
export GSC_REFRESH_TOKEN="..."
```

---

## 6. Code Locations Summary

| Integration | File | Line Search |
|-------------|------|-------------|
| AI Audit | `dashboard/main.py` | `@app.post("/api/ai/audit/` |
| AI Content | `dashboard/main.py` | `@app.post("/api/ai/content/generate")` |
| AI Competitor | `dashboard/main.py` | `@app.post("/api/ai/competitor-analysis/` |
| AI Chat | `dashboard/main.py` | `@app.post("/api/ai/chat-assistant")` |
| Twilio Voice | `dashboard/main.py` | `@app.post("/api/voice/` |
| WhatsApp | `dashboard/main.py` | `@app.post("/api/whatsapp/` |
| Slack | `dashboard/main.py` | `@app.post("/api/slack/` |
| Stripe | `dashboard/main.py` | `@app.post("/api/billing/` |
| GSC | `dashboard/main.py` | `@app.get("/api/gsc/` |
| Theme | `dashboard/main.py` | `@app.post("/api/user/theme")` |
| Settings UI | `dashboard/templates/settings.html` | Full file |
| DB Schema | `dashboard/database.py` | `api_settings` table |

**To switch from demo to production:** Search for `# PRODUCTION:` comments in `dashboard/main.py` — each integration has commented-out production code ready to uncomment.
