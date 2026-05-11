#!/usr/bin/env python3
"""Generate all website pages for AI Growth Labs"""
import os

SITE = "/home/ubuntu/repos/ai-seo-agency/site/pages"

NAV = '''<nav class="nav" id="nav"><div class="nav-inner"><a href="../" class="nav-logo">AI Growth<span>Labs</span></a><button class="nav-mobile" id="navToggle" aria-label="Toggle navigation">☰</button><div class="nav-links" id="navLinks"><a href="../">Home</a><div class="nav-dropdown"><a class="dropdown-toggle">Services</a><div class="dropdown-menu"><a href="local-seo.html">Local SEO</a><a href="gbp-optimization.html">GBP Optimization</a><a href="reputation-management.html">Reputation Management</a><a href="ai-seo.html">AI SEO Services</a><a href="paid-advertising.html">Facebook &amp; Google Ads</a><a href="social-media.html">Social Media</a><a href="content-creation.html">Content Creation</a></div></div><div class="nav-dropdown"><a class="dropdown-toggle">Industries</a><div class="dropdown-menu"><a href="seo-for-dentists.html">Dentists</a><a href="seo-for-lawyers.html">Lawyers</a><a href="seo-for-restaurants.html">Restaurants</a><a href="seo-for-plumbers.html">Plumbers</a><a href="seo-for-hvac.html">HVAC</a><a href="seo-for-medical-spas.html">Medical Spas</a></div></div><a href="case-studies.html">Case Studies</a><a href="about.html">About</a><a href="blog.html">Blog</a><a href="contact.html">Contact</a><a href="free-audit.html" class="nav-cta">Free Audit →</a></div></div></nav>'''

FOOTER = '''<footer class="footer"><div class="container"><div class="footer-grid"><div class="footer-brand"><div class="logo">AI Growth<span>Labs</span></div><p>AI-powered SEO &amp; reputation management for USA businesses.</p></div><div class="footer-col"><h4>Services</h4><a href="local-seo.html">Local SEO</a><a href="gbp-optimization.html">GBP Optimization</a><a href="reputation-management.html">Reputation Management</a><a href="ai-seo.html">AI SEO</a><a href="paid-advertising.html">Paid Ads</a><a href="social-media.html">Social Media</a><a href="content-creation.html">Content Creation</a></div><div class="footer-col"><h4>Industries</h4><a href="seo-for-dentists.html">Dentists</a><a href="seo-for-lawyers.html">Lawyers</a><a href="seo-for-restaurants.html">Restaurants</a><a href="seo-for-plumbers.html">Plumbers</a><a href="seo-for-hvac.html">HVAC</a><a href="seo-for-medical-spas.html">Medical Spas</a></div><div class="footer-col"><h4>Company</h4><a href="about.html">About</a><a href="case-studies.html">Case Studies</a><a href="blog.html">Blog</a><a href="contact.html">Contact</a><a href="free-audit.html">Free Audit</a><a href="privacy-policy.html">Privacy</a><a href="terms.html">Terms</a></div></div><div class="footer-bottom"><span>© 2026 AI Growth Labs. All rights reserved.</span><span>🇺🇸 Serving USA businesses</span></div></div></footer>'''

CHATBOT = '''<div class="floating-cta"><a href="free-audit.html" class="float-btn float-audit">📊 Free Audit</a><button class="float-btn float-chat" id="chatToggle">💬 Chat</button></div>
<div class="chatbot-container" id="chatbot"><div class="chat-header"><div class="chat-header-info"><div class="chat-avatar">🤖</div><div><h4>AI Growth Assistant</h4><p>Online</p></div></div><button class="chat-close" id="chatClose">✕</button></div><div class="chat-messages" id="chatMessages"></div><div class="chat-input-area"><input type="text" class="chat-input" id="chatInput" placeholder="Type your message..."><button class="chat-send" id="chatSend">→</button></div></div>
<script src="../js/main.js"></script>'''

def page(title, desc, keywords, body):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | AI Growth Labs</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<link rel="stylesheet" href="../css/main.css">
</head>
<body>
{NAV}
{body}
{FOOTER}
{CHATBOT}
</body>
</html>'''

# ===== REPUTATION MANAGEMENT =====
pages = {}
pages["reputation-management.html"] = page(
    "Reputation Management Services — Review Generation & Monitoring",
    "Ethical reputation management services for USA businesses. Review generation, sentiment monitoring, and customer feedback automation.",
    "reputation management, review generation, online reviews, customer feedback, review monitoring",
    '''<section class="page-hero"><div class="container"><span class="section-badge">⭐ Reputation Management</span><h1>Build Trust With Ethical Reputation Management</h1><p>Generate real 5-star reviews, monitor your online reputation, and turn customer feedback into your strongest marketing asset.</p></div></section>
<section class="section section-darker"><div class="container"><div class="services-grid">
<div class="service-card"><div class="service-icon">📱</div><h3>Review Generation System</h3><p>Multi-channel review requests via SMS, email, and QR codes. Automated follow-ups with customizable templates that make it easy for happy customers to leave reviews on Google, Yelp, and Facebook.</p></div>
<div class="service-card"><div class="service-icon">🛡️</div><h3>Negative Review Response</h3><p>Our A.R.E.S. framework (Acknowledge, Respond, Explain, Solve) handles negative reviews professionally. We turn unhappy customers into advocates with proven response templates.</p></div>
<div class="service-card"><div class="service-icon">📊</div><h3>Sentiment Monitoring</h3><p>Real-time monitoring across Google, Yelp, Facebook, BBB, Trustpilot, and industry-specific platforms. Get alerts for new reviews and track sentiment trends over time.</p></div>
<div class="service-card"><div class="service-icon">🔄</div><h3>Review Response Management</h3><p>Professional, personalized responses to every review within 24 hours. Our team crafts responses that show you care about customer feedback and builds trust with prospects.</p></div>
<div class="service-card"><div class="service-icon">📈</div><h3>Reputation Analytics</h3><p>Monthly reports showing review volume, average rating, sentiment analysis, competitor comparison, and review source breakdown. Track your reputation growth with clear metrics.</p></div>
<div class="service-card"><div class="service-icon">🚫</div><h3>100% Ethical Approach</h3><p>We never buy fake reviews, incentivize reviews with discounts, or use review gating. Our approach follows all Google policies — building genuine trust through authentic customer experiences.</p></div>
</div></div></section>
<section class="section section-dark"><div class="container"><div class="text-center mb-40"><h2 class="section-title">Reputation Results</h2></div>
<div class="cases-grid">
<div class="case-card"><div class="case-top"><div class="case-industry">⭐ Review Growth</div><h3 class="case-title">Medical Spa — Los Angeles, CA</h3><p class="case-desc">From 23 reviews to 680+ reviews in 8 months with our ethical review generation system.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">680+</div><div class="lbl">Reviews</div></div><div class="case-metric"><div class="val">4.9★</div><div class="lbl">Avg Rating</div></div><div class="case-metric"><div class="val">156%</div><div class="lbl">More Bookings</div></div></div></div>
<div class="case-card"><div class="case-top"><div class="case-industry">⭐ Reputation Recovery</div><h3 class="case-title">Auto Dealer — Houston, TX</h3><p class="case-desc">Recovered from 3.1 to 4.7 star rating through strategic review management.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">3.1→4.7</div><div class="lbl">Rating</div></div><div class="case-metric"><div class="val">340+</div><div class="lbl">New Reviews</div></div><div class="case-metric"><div class="val">89%</div><div class="lbl">5-Star Rate</div></div></div></div>
</div></div></section>
<section class="cta-section"><div class="container"><h2>Start Building Your Reputation Today</h2><p>Free reputation audit shows your current review landscape and exactly what we can improve.</p><a href="free-audit.html" class="btn btn-white">Free Reputation Audit →</a></div></section>'''
)

# ===== AI SEO =====
pages["ai-seo.html"] = page(
    "AI SEO Services — Next-Generation Search Optimization",
    "AI-powered SEO services using entity optimization, semantic search, and machine learning. The future of search optimization for USA businesses.",
    "AI SEO services, artificial intelligence SEO, entity SEO, semantic SEO, AI search optimization",
    '''<section class="page-hero"><div class="container"><span class="section-badge">🤖 AI SEO Services</span><h1>Next-Generation AI-Powered SEO</h1><p>Go beyond traditional SEO. Our AI analyzes 100+ ranking factors across 12 DNA pillars to find optimization opportunities that human analysts miss.</p></div></section>
<section class="section section-darker"><div class="container"><div class="services-grid">
<div class="service-card"><div class="service-icon">🧬</div><h3>DNA-Level SEO Analysis</h3><p>Our AI analyzes your website across 12 DNA pillars and 100+ ranking factors — technical SEO, content quality, entity relationships, semantic coverage, user behavior, and competitor intelligence.</p></div>
<div class="service-card"><div class="service-icon">🔍</div><h3>Entity & Semantic SEO</h3><p>Build topical authority through entity optimization. We map your semantic graph, identify entity gaps, and create content that establishes your expertise in Google's Knowledge Graph.</p></div>
<div class="service-card"><div class="service-icon">🤖</div><h3>AI Visibility Optimization</h3><p>Get your business featured in AI search results — ChatGPT, Google Gemini, and Perplexity. We optimize your content for the new era of AI-powered search engines.</p></div>
<div class="service-card"><div class="service-icon">📊</div><h3>Predictive SEO Analytics</h3><p>Machine learning models predict ranking changes, traffic trends, and competitor movements before they happen — giving you a strategic advantage in your market.</p></div>
<div class="service-card"><div class="service-icon">✍️</div><h3>AI Content Generation</h3><p>AI-assisted content creation that maintains E-E-A-T quality standards. We generate, optimize, and publish topically relevant content at scale while maintaining your brand voice.</p></div>
<div class="service-card"><div class="service-icon">⚡</div><h3>Automated Optimization</h3><p>AI continuously monitors your site and automatically identifies technical issues, content gaps, and optimization opportunities — then provides actionable fix recommendations.</p></div>
</div></div></section>
<section class="section section-dark"><div class="container"><div class="text-center mb-40"><span class="section-badge">The 12 DNA Pillars</span><h2 class="section-title">What Our AI Analyzes</h2></div>
<div class="industries-grid" style="grid-template-columns:repeat(auto-fill,minmax(160px,1fr))">
<div class="industry-card"><div class="icon">⚙️</div><h4>Technical SEO</h4></div>
<div class="industry-card"><div class="icon">📄</div><h4>On-Page SEO</h4></div>
<div class="industry-card"><div class="icon">✍️</div><h4>Content SEO</h4></div>
<div class="industry-card"><div class="icon">🔗</div><h4>Entity SEO</h4></div>
<div class="industry-card"><div class="icon">🕸️</div><h4>Internal Linking</h4></div>
<div class="industry-card"><div class="icon">🌐</div><h4>Off-Page SEO</h4></div>
<div class="industry-card"><div class="icon">📍</div><h4>Local SEO</h4></div>
<div class="industry-card"><div class="icon">👤</div><h4>User Behavior</h4></div>
<div class="industry-card"><div class="icon">🎯</div><h4>Conversion DNA</h4></div>
<div class="industry-card"><div class="icon">🏆</div><h4>Competitor DNA</h4></div>
<div class="industry-card"><div class="icon">📑</div><h4>Indexing DNA</h4></div>
<div class="industry-card"><div class="icon">🤖</div><h4>AI/Programmatic</h4></div>
</div></div></section>
<section class="cta-section"><div class="container"><h2>Experience DNA-Level SEO</h2><p>Get your free AI-powered audit. See what 100+ ranking factors reveal about your website.</p><a href="free-audit.html" class="btn btn-white">Get AI SEO Audit →</a></div></section>'''
)

# ===== PAID ADVERTISING =====
pages["paid-advertising.html"] = page(
    "Facebook & Google Ads Management — Lead Generation Campaigns",
    "Expert Facebook & Google Ads management for USA local businesses. Lead generation, conversion campaigns, and retargeting with AI-optimized bidding.",
    "Google Ads management, Facebook Ads, PPC management, lead generation ads, local business advertising",
    '''<section class="page-hero"><div class="container"><span class="section-badge">📢 Paid Advertising</span><h1>Facebook & Google Ads That Generate Leads</h1><p>High-converting ad campaigns with precision targeting, AI-optimized bidding, and transparent reporting. Get more leads for less.</p></div></section>
<section class="section section-darker"><div class="container"><div class="services-grid">
<div class="service-card"><div class="service-icon">🔍</div><h3>Google Search Ads</h3><p>Capture high-intent searches with optimized Google Ads campaigns. We target buyers actively looking for your services with compelling ad copy and landing pages.</p></div>
<div class="service-card"><div class="service-icon">📱</div><h3>Facebook & Instagram Ads</h3><p>Social media advertising that reaches your ideal customers. Demographic targeting, lookalike audiences, and engaging ad creatives that drive leads and conversions.</p></div>
<div class="service-card"><div class="service-icon">🔄</div><h3>Retargeting Campaigns</h3><p>Stay top-of-mind with website visitors who didn't convert. Our retargeting campaigns across Google, Facebook, and Instagram bring back warm leads with personalized messaging.</p></div>
<div class="service-card"><div class="service-icon">🎯</div><h3>Landing Page Design</h3><p>High-converting landing pages designed for maximum lead capture. A/B tested headlines, forms, and CTAs that turn clicks into customers.</p></div>
<div class="service-card"><div class="service-icon">📊</div><h3>Campaign Analytics</h3><p>Real-time dashboard showing impressions, clicks, conversions, cost per lead, and ROI. Weekly optimization reports with actionable insights.</p></div>
<div class="service-card"><div class="service-icon">💰</div><h3>Budget Optimization</h3><p>AI-powered bid management that maximizes your ad spend. We continuously optimize campaigns to lower your cost per lead while increasing conversion volume.</p></div>
</div></div></section>
<section class="section section-dark"><div class="container"><div class="text-center mb-40"><h2 class="section-title">Advertising Results</h2></div>
<div class="cases-grid">
<div class="case-card"><div class="case-top"><div class="case-industry">📢 Google Ads</div><h3 class="case-title">Personal Injury Law — NYC</h3><p class="case-desc">Generated 85 qualified leads per month at $42 cost per lead with Google Ads.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">85</div><div class="lbl">Leads/Month</div></div><div class="case-metric"><div class="val">$42</div><div class="lbl">Cost/Lead</div></div><div class="case-metric"><div class="val">520%</div><div class="lbl">ROI</div></div></div></div>
<div class="case-card"><div class="case-top"><div class="case-industry">📢 Facebook Ads</div><h3 class="case-title">Medical Spa — Miami, FL</h3><p class="case-desc">Facebook Ads drove 340+ appointment bookings in the first 90 days.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">340+</div><div class="lbl">Bookings</div></div><div class="case-metric"><div class="val">$18</div><div class="lbl">Cost/Booking</div></div><div class="case-metric"><div class="val">8.2x</div><div class="lbl">ROAS</div></div></div></div>
</div></div></section>
<section class="cta-section"><div class="container"><h2>Start Getting More Leads Today</h2><p>Free ad account audit reveals wasted spend and untapped opportunities.</p><a href="free-audit.html" class="btn btn-white">Free Ads Audit →</a></div></section>'''
)

# ===== SOCIAL MEDIA =====
pages["social-media.html"] = page(
    "Social Media Management — Instagram, Facebook, TikTok, LinkedIn",
    "Complete social media management for USA businesses. Content creation, posting, engagement, and growth across all major platforms.",
    "social media management, Instagram management, Facebook management, TikTok marketing, social media agency",
    '''<section class="page-hero"><div class="container"><span class="section-badge">📱 Social Media</span><h1>Social Media Management That Grows Your Brand</h1><p>Complete social presence management across Instagram, Facebook, TikTok, and LinkedIn. Daily content, engagement, and strategic growth.</p></div></section>
<section class="section section-darker"><div class="container"><div class="services-grid">
<div class="service-card"><div class="service-icon">📸</div><h3>Instagram Management</h3><p>Feed posts, Stories, Reels, and engagement management. We create visually stunning content that builds your brand and drives followers to become customers.</p></div>
<div class="service-card"><div class="service-icon">👍</div><h3>Facebook Management</h3><p>Business page optimization, daily posts, community management, and event promotion. We keep your Facebook presence active and engaging.</p></div>
<div class="service-card"><div class="service-icon">🎵</div><h3>TikTok Marketing</h3><p>Short-form video content that captures attention and goes viral. We create trending content that puts your business in front of millions of potential customers.</p></div>
<div class="service-card"><div class="service-icon">💼</div><h3>LinkedIn Strategy</h3><p>B2B networking and thought leadership content. We position you as an industry expert with strategic posts, articles, and connection-building campaigns.</p></div>
<div class="service-card"><div class="service-icon">📅</div><h3>Content Calendar</h3><p>Strategic posting schedule optimized for maximum engagement. We batch-create 30 days of content in a single session — consistent, professional, and on-brand.</p></div>
<div class="service-card"><div class="service-icon">📊</div><h3>Growth Analytics</h3><p>Monthly reports showing follower growth, engagement rates, reach, and conversion metrics. We track what's working and optimize for continuous improvement.</p></div>
</div></div></section>
<section class="cta-section"><div class="container"><h2>Build Your Social Presence</h2><p>Free social media audit reveals your strengths, gaps, and opportunities for growth.</p><a href="free-audit.html" class="btn btn-white">Free Social Audit →</a></div></section>'''
)

# ===== CONTENT CREATION =====
pages["content-creation.html"] = page(
    "Content Creation Services — SEO Blogs, Social Media, Video Scripts",
    "Professional content creation for SEO, social media, and marketing. Blog posts, social content, video scripts, and AI-generated assets.",
    "content creation services, SEO blog writing, social media content, video scripts, content marketing agency",
    '''<section class="page-hero"><div class="container"><span class="section-badge">✍️ Content Creation</span><h1>Content That Ranks, Engages & Converts</h1><p>SEO-optimized blog posts, social media content, video scripts, and AI-powered assets that establish topical authority and drive traffic.</p></div></section>
<section class="section section-darker"><div class="container"><div class="services-grid">
<div class="service-card"><div class="service-icon">📝</div><h3>SEO Blog Posts</h3><p>Research-backed, long-form articles optimized for target keywords. We cover every content pillar in your niche to build topical authority and drive organic traffic.</p></div>
<div class="service-card"><div class="service-icon">📱</div><h3>Social Media Content</h3><p>Platform-specific content for Instagram, Facebook, TikTok, and LinkedIn. Captions, graphics, Reels, and Stories designed for maximum engagement.</p></div>
<div class="service-card"><div class="service-icon">🎬</div><h3>Video Scripts</h3><p>Engaging video scripts for YouTube, TikTok, and Instagram Reels. From educational content to testimonial scripts — optimized for retention and conversion.</p></div>
<div class="service-card"><div class="service-icon">🤖</div><h3>AI-Powered Content</h3><p>Leverage AI tools for content ideation, drafting, and optimization while maintaining human quality standards and E-E-A-T compliance.</p></div>
<div class="service-card"><div class="service-icon">📧</div><h3>Email Campaigns</h3><p>Nurturing email sequences, promotional campaigns, and newsletter content that keeps your audience engaged and drives repeat business.</p></div>
<div class="service-card"><div class="service-icon">🎨</div><h3>Visual Content</h3><p>Infographics, custom graphics, branded templates, and visual assets that make your content stand out across all platforms.</p></div>
</div></div></section>
<section class="cta-section"><div class="container"><h2>Content That Drives Results</h2><p>Free content audit reveals gaps in your content strategy and opportunities for growth.</p><a href="free-audit.html" class="btn btn-white">Free Content Audit →</a></div></section>'''
)

# ===== NICHE PAGES =====
niches = [
    {
        "file": "seo-for-dentists.html",
        "title": "SEO for Dentists — Get More Patients Online",
        "desc": "Specialized SEO services for dental practices. Get found on Google, attract new patients, and grow your dental practice with AI-powered marketing.",
        "keywords": "SEO for dentists, dental SEO, dental marketing, dentist Google ranking, dental practice marketing",
        "icon": "🦷", "name": "Dentists", "industry": "Dental",
        "h1": "SEO for Dentists — Get More Patients From Google",
        "sub": "Specialized dental SEO that puts your practice at the top of Google when patients search for a dentist in your area.",
        "challenges": [
            ("High competition in local search", "Dental practices face intense local competition. Our DNA-level analysis identifies exactly where your competitors are strong and where you can outperform them."),
            ("Getting quality patient reviews", "We implement ethical review generation systems using SMS + email campaigns that make it effortless for satisfied patients to share their experience."),
            ("Standing out from corporate dental chains", "We highlight what makes your practice unique — your expertise, personal care, and patient stories — through compelling content and social proof."),
        ],
        "stats": [("340%", "Traffic Increase"), ("47", "New Patients/Mo"), ("#1", "Map Pack Position")],
        "case": "SmileBright Dental went from page 5 to Map Pack #1 in Austin, TX — generating 47 new patient appointments every month."
    },
    {
        "file": "seo-for-lawyers.html",
        "title": "SEO for Lawyers — Get More Legal Clients Online",
        "desc": "Specialized SEO for law firms and attorneys. Rank higher on Google, generate qualified leads, and grow your legal practice.",
        "keywords": "SEO for lawyers, law firm SEO, attorney marketing, legal SEO services, lawyer Google ranking",
        "icon": "⚖️", "name": "Lawyers", "industry": "Legal",
        "h1": "SEO for Lawyers — Generate More Qualified Leads",
        "sub": "Dominate legal search results in your practice area. Get found by potential clients searching for an attorney right when they need one.",
        "challenges": [
            ("Extremely competitive keywords", "Legal keywords are among the most expensive and competitive. Our AI identifies long-tail and localized opportunities that deliver high-intent leads at lower cost."),
            ("Building authority and trust", "We create authoritative legal content, earn quality backlinks from legal directories, and build your E-E-A-T signals to establish credibility with Google and potential clients."),
            ("Converting website visitors to consultations", "Our conversion optimization includes compelling CTAs, live chat integration, click-to-call buttons, and free consultation offers that turn visitors into leads."),
        ],
        "stats": [("520%", "ROI"), ("85", "Leads/Month"), ("$42", "Cost Per Lead")],
        "case": "Martinez Legal increased qualified leads from 12 to 85 per month in Dallas, TX — achieving 520% ROI on their marketing investment."
    },
    {
        "file": "seo-for-restaurants.html",
        "title": "SEO for Restaurants — Get More Diners & Reservations",
        "desc": "Restaurant SEO services that drive more reservations and foot traffic. Google Maps optimization, review management, and social media marketing.",
        "keywords": "SEO for restaurants, restaurant marketing, restaurant Google Maps, restaurant reviews, food business SEO",
        "icon": "🍽️", "name": "Restaurants", "industry": "Restaurant",
        "h1": "SEO for Restaurants — Fill Every Table, Every Night",
        "sub": "Get your restaurant to the top of Google Maps and local search. More visibility means more reservations, deliveries, and walk-ins.",
        "challenges": [
            ("Standing out in a crowded market", "Every neighborhood has dozens of restaurants. We optimize your Google Maps listing, menu items, and location pages to ensure you appear first when diners are hungry."),
            ("Managing online reviews", "Reviews make or break restaurants. Our review management system generates authentic positive reviews while professionally handling any negative feedback."),
            ("Building social media presence", "Food is visual. We create mouth-watering social content across Instagram, TikTok, and Facebook that drives engagement and foot traffic."),
        ],
        "stats": [("200%", "More Reservations"), ("890", "New Reviews"), ("$45K", "Revenue/Mo Added")],
        "case": "Bella's Italian in Chicago went from 45 to 890 reviews and doubled their monthly revenue through our GBP + social media strategy."
    },
    {
        "file": "seo-for-plumbers.html",
        "title": "SEO for Plumbers — Get More Service Calls",
        "desc": "Plumber SEO services that generate emergency and scheduled service calls. Dominate Google Maps and local search in your service area.",
        "keywords": "SEO for plumbers, plumber marketing, plumbing SEO, plumber Google ranking, plumbing company marketing",
        "icon": "🔧", "name": "Plumbers", "industry": "Plumbing",
        "h1": "SEO for Plumbers — More Calls, More Jobs, More Revenue",
        "sub": "When someone has a plumbing emergency, they search Google. Make sure your plumbing company appears first with our proven local SEO strategy.",
        "challenges": [
            ("Capturing emergency searches", "Plumbing emergencies need immediate response. We optimize for 'emergency plumber near me' and similar high-intent keywords that drive immediate calls."),
            ("Covering your entire service area", "We create location-specific landing pages for every city and neighborhood you serve, ensuring you rank for local searches across your entire service area."),
            ("Building trust before the first call", "Verified reviews, professional Google listing, and an authoritative website give potential customers the confidence to call you instead of a competitor."),
        ],
        "stats": [("450%", "More Calls"), ("#2", "Map Pack"), ("$85K", "Revenue/Month")],
        "case": "Dallas Plumbing Co. went from 30 to 120+ service calls per month through our local SEO and GBP optimization strategy."
    },
    {
        "file": "seo-for-hvac.html",
        "title": "SEO for HVAC Companies — Generate More Service Leads",
        "desc": "HVAC SEO services that drive installation and repair leads year-round. Local SEO, Google Ads, and reputation management for HVAC companies.",
        "keywords": "HVAC SEO, HVAC marketing, air conditioning SEO, heating company SEO, HVAC lead generation",
        "icon": "❄️", "name": "HVAC", "industry": "HVAC",
        "h1": "SEO for HVAC Companies — Year-Round Lead Generation",
        "sub": "Stay booked all year with our seasonal HVAC marketing strategy. From AC installations to furnace repairs, we keep your phone ringing.",
        "challenges": [
            ("Seasonal demand fluctuations", "HVAC is seasonal. Our strategy includes seasonal keyword targeting, pre-season content campaigns, and maintenance plan promotions that smooth out demand throughout the year."),
            ("High-cost emergency leads", "Emergency HVAC calls are expensive but profitable. We optimize for emergency keywords and set up Google Ads campaigns that capture these high-value searches cost-effectively."),
            ("Competing with national brands", "Local HVAC companies compete with Carrier, Trane, and national franchises. We highlight your local expertise, response time, and personalized service to win local customers."),
        ],
        "stats": [("380%", "More Leads"), ("#1", "Map Pack"), ("$120K", "Revenue/Mo")],
        "case": "Phoenix HVAC Pro went from 25 leads/month to 120+ leads/month with our combined SEO + Google Ads strategy."
    },
    {
        "file": "seo-for-medical-spas.html",
        "title": "SEO for Medical Spas — Attract More Patients",
        "desc": "Medical spa SEO and marketing services. Drive more Botox, filler, and aesthetic treatment bookings with Google visibility and social media.",
        "keywords": "medical spa SEO, medspa marketing, aesthetic clinic SEO, Botox marketing, medical spa advertising",
        "icon": "💆", "name": "Medical Spas", "industry": "Medical Spa",
        "h1": "SEO for Medical Spas — Book More Aesthetic Treatments",
        "sub": "Attract patients searching for Botox, fillers, laser treatments, and aesthetic services. Our marketing drives consultations and bookings.",
        "challenges": [
            ("Competing in a premium market", "Medical spa patients research extensively. We create authoritative content about procedures, before/after galleries, and provider credentials that build confidence."),
            ("HIPAA-compliant marketing", "Healthcare marketing has strict regulations. We ensure all marketing materials comply with HIPAA, FTC guidelines, and state medical advertising laws."),
            ("Building Instagram presence", "Medical spa results are visual. We manage your Instagram with professional before/after content, Reels, and Stories that showcase your work and attract new patients."),
        ],
        "stats": [("290%", "More Bookings"), ("680+", "Reviews"), ("4.9★", "Avg Rating")],
        "case": "LA MedSpa went from 23 to 680+ reviews and increased bookings by 290% through our comprehensive digital marketing strategy."
    }
]

for n in niches:
    challenges_html = ""
    for title, desc in n["challenges"]:
        challenges_html += f'<div class="service-card"><div class="service-icon">{n["icon"]}</div><h3>{title}</h3><p>{desc}</p></div>'
    
    stats_html = ""
    for val, lbl in n["stats"]:
        stats_html += f'<div class="case-metric"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>'
    
    pages[n["file"]] = page(n["title"], n["desc"], n["keywords"],
        f'''<section class="page-hero"><div class="container"><span class="section-badge">{n["icon"]} {n["name"]}</span><h1>{n["h1"]}</h1><p>{n["sub"]}</p></div></section>
<section class="section section-darker"><div class="container"><div class="text-center mb-40"><span class="section-badge">Common Challenges</span><h2 class="section-title">Why {n["name"]} Need Specialized SEO</h2></div><div class="services-grid">{challenges_html}</div></div></section>
<section class="section section-dark"><div class="container"><div class="text-center mb-40"><h2 class="section-title">{n["industry"]} SEO Results</h2></div>
<div class="case-card" style="max-width:600px;margin:0 auto"><div class="case-top"><div class="case-industry">{n["icon"]} Success Story</div><h3 class="case-title">{n["case"]}</h3></div><div class="case-metrics">{stats_html}</div></div>
</div></section>
<section class="section section-darker"><div class="container"><div class="text-center mb-40"><h2 class="section-title">Our {n["name"]} SEO Services Include</h2></div>
<div class="services-grid" style="grid-template-columns:repeat(auto-fill,minmax(240px,1fr))">
<div class="service-card" style="text-align:center"><div class="service-icon" style="margin:0 auto 12px">📍</div><h3>Local SEO</h3><p>Dominate local search results in your service area.</p></div>
<div class="service-card" style="text-align:center"><div class="service-icon" style="margin:0 auto 12px">🏢</div><h3>GBP Optimization</h3><p>Complete Google Business Profile optimization.</p></div>
<div class="service-card" style="text-align:center"><div class="service-icon" style="margin:0 auto 12px">⭐</div><h3>Review Generation</h3><p>Ethical review generation and management.</p></div>
<div class="service-card" style="text-align:center"><div class="service-icon" style="margin:0 auto 12px">✍️</div><h3>Content Strategy</h3><p>Industry-specific content that ranks and converts.</p></div>
</div></div></section>
<section class="cta-section"><div class="container"><h2>Ready to Grow Your {n["industry"]} Business?</h2><p>Get your free {n["industry"].lower()} SEO audit and see exactly how we can help you get more customers.</p><a href="free-audit.html" class="btn btn-white">Free {n["industry"]} SEO Audit →</a></div></section>'''
    )

# ===== ABOUT PAGE =====
pages["about.html"] = page(
    "About AI Growth Labs — Our Team & Mission",
    "Meet the AI Growth Labs team. Learn about our mission to help USA local businesses grow through AI-powered SEO and digital marketing.",
    "about AI Growth Labs, SEO agency team, digital marketing experts, USA SEO company",
    '''<section class="page-hero"><div class="container"><span class="section-badge">About Us</span><h1>AI-Powered Growth for USA Local Businesses</h1><p>We combine cutting-edge AI technology with proven SEO strategies to help local businesses dominate their market.</p></div></section>
<section class="section section-darker"><div class="container">
<div style="max-width:800px;margin:0 auto">
<h2 class="section-title mb-24">Our Mission</h2>
<p style="font-size:1.1rem;line-height:1.8;color:#CBD5E1;margin-bottom:32px">At AI Growth Labs, we believe every local business deserves access to enterprise-level SEO intelligence. Our DNA-level analysis goes deeper than any traditional SEO audit — examining 100+ ranking factors across 12 pillars to find opportunities that others miss.</p>
<p style="font-size:1.1rem;line-height:1.8;color:#CBD5E1;margin-bottom:32px">Founded in 2024, we've helped over 500 USA local businesses increase their Google visibility, generate more reviews, and grow their customer base. Our month-to-month contracts and transparent reporting ensure we earn your trust every single month.</p>
<h2 class="section-title mb-24" style="margin-top:60px">Why Choose Us</h2>
<div class="services-grid" style="grid-template-columns:repeat(auto-fill,minmax(240px,1fr))">
<div class="service-card" style="text-align:center"><div class="service-icon" style="margin:0 auto 12px">🤖</div><h3>AI-Powered Analysis</h3><p>Our AI analyzes 100+ SEO factors that human analysts miss.</p></div>
<div class="service-card" style="text-align:center"><div class="service-icon" style="margin:0 auto 12px">🇺🇸</div><h3>100% USA-Based</h3><p>Our entire team is based in the United States.</p></div>
<div class="service-card" style="text-align:center"><div class="service-icon" style="margin:0 auto 12px">📊</div><h3>Transparent Reporting</h3><p>Monthly reports with clear metrics and honest results.</p></div>
<div class="service-card" style="text-align:center"><div class="service-icon" style="margin:0 auto 12px">🤝</div><h3>No Long-Term Contracts</h3><p>Month-to-month. We earn your business every month.</p></div>
</div>
</div>
</div></section>
<section class="section section-dark"><div class="container"><div class="text-center mb-40"><span class="section-badge">Our Team</span><h2 class="section-title">Meet the Experts Behind Your Growth</h2><p class="section-sub">A team of SEO specialists, AI engineers, and marketing strategists dedicated to your success.</p></div>
<div class="team-grid">
<div class="team-card"><div class="team-avatar">JM</div><h4>James Mitchell</h4><div class="role">CEO & Founder</div><p>15+ years in digital marketing. Former head of SEO at a Fortune 500 company. Passionate about bringing enterprise strategies to local businesses.</p><div class="team-social"><a href="#" title="LinkedIn">in</a></div></div>
<div class="team-card"><div class="team-avatar">SK</div><h4>Sarah Kim</h4><div class="role">Head of SEO</div><p>Google certified. Managed SEO for 300+ local businesses. Specialist in local SEO, GBP optimization, and technical audits.</p><div class="team-social"><a href="#" title="LinkedIn">in</a></div></div>
<div class="team-card"><div class="team-avatar">AR</div><h4>Alex Rodriguez</h4><div class="role">AI & Technology Lead</div><p>ML engineer with expertise in NLP and search algorithms. Built our proprietary DNA-level analysis engine.</p><div class="team-social"><a href="#" title="LinkedIn">in</a></div></div>
<div class="team-card"><div class="team-avatar">EP</div><h4>Emily Parker</h4><div class="role">Head of Content</div><p>Published author and content strategist. Leads our team of writers in creating content that ranks and converts.</p><div class="team-social"><a href="#" title="LinkedIn">in</a></div></div>
<div class="team-card"><div class="team-avatar">DW</div><h4>David Washington</h4><div class="role">Reputation Manager</div><p>10+ years in reputation management. Developed our ethical review generation system used by 500+ businesses.</p><div class="team-social"><a href="#" title="LinkedIn">in</a></div></div>
<div class="team-card"><div class="team-avatar">LC</div><h4>Lisa Chen</h4><div class="role">Paid Ads Director</div><p>Google Ads certified. Manages $2M+ in ad spend. Specializes in high-ROI campaigns for local service businesses.</p><div class="team-social"><a href="#" title="LinkedIn">in</a></div></div>
<div class="team-card"><div class="team-avatar">MJ</div><h4>Marcus Johnson</h4><div class="role">Social Media Lead</div><p>Former social media manager for national brands. Now focuses on helping local businesses build authentic social presence.</p><div class="team-social"><a href="#" title="LinkedIn">in</a></div></div>
<div class="team-card"><div class="team-avatar">RG</div><h4>Rachel Green</h4><div class="role">Client Success Director</div><p>Ensures every client achieves their growth goals. 97% client retention rate under her leadership.</p><div class="team-social"><a href="#" title="LinkedIn">in</a></div></div>
</div>
</div></section>
<section class="cta-section"><div class="container"><h2>Ready to Work With Our Team?</h2><p>Book a free strategy call and see how our experts can help grow your business.</p><a href="free-audit.html" class="btn btn-white">Get Your Free Audit →</a></div></section>'''
)

# ===== CONTACT PAGE =====
pages["contact.html"] = page(
    "Contact AI Growth Labs — Get Your Free Strategy Call",
    "Contact AI Growth Labs for a free SEO strategy call. Reach our team for questions about local SEO, reputation management, and digital marketing.",
    "contact AI Growth Labs, free SEO consultation, SEO strategy call, digital marketing inquiry",
    '''<section class="page-hero"><div class="container"><span class="section-badge">📞 Contact Us</span><h1>Let's Grow Your Business Together</h1><p>Ready to dominate your local market? Get in touch for a free strategy call — no pressure, just actionable advice.</p></div></section>
<section class="section section-darker"><div class="container">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:start">
<div>
<h2 class="section-title mb-24">Get In Touch</h2>
<p style="color:#94A3B8;margin-bottom:32px;line-height:1.7">Fill out the form and our team will get back to you within 2 hours during business hours. Or call us directly for an immediate consultation.</p>
<div style="margin-bottom:24px"><div style="display:flex;align-items:center;gap:12px;margin-bottom:16px"><span style="font-size:1.5rem">📞</span><div><div style="color:#F1F5F9;font-weight:600">Call Us</div><div style="color:#22D3EE">(800) 555-0199</div></div></div></div>
<div style="margin-bottom:24px"><div style="display:flex;align-items:center;gap:12px;margin-bottom:16px"><span style="font-size:1.5rem">📧</span><div><div style="color:#F1F5F9;font-weight:600">Email</div><div style="color:#22D3EE">hello@aigrowth-labs.com</div></div></div></div>
<div style="margin-bottom:24px"><div style="display:flex;align-items:center;gap:12px;margin-bottom:16px"><span style="font-size:1.5rem">🕐</span><div><div style="color:#F1F5F9;font-weight:600">Business Hours</div><div style="color:#94A3B8">Mon-Fri: 8AM - 6PM EST</div></div></div></div>
<div><div style="display:flex;align-items:center;gap:12px"><span style="font-size:1.5rem">🇺🇸</span><div><div style="color:#F1F5F9;font-weight:600">Location</div><div style="color:#94A3B8">Serving all 50 states</div></div></div></div>
</div>
<div style="background:#0F172A;border:1px solid #1E3A5F;border-radius:16px;padding:36px">
<h3 style="color:#F1F5F9;font-size:1.2rem;font-weight:700;margin-bottom:24px">Send Us a Message</h3>
<form id="contactForm">
<div class="form-grid">
<div class="form-group"><label>First Name *</label><input type="text" required placeholder="John"></div>
<div class="form-group"><label>Last Name *</label><input type="text" required placeholder="Smith"></div>
<div class="form-group"><label>Email *</label><input type="email" required placeholder="john@business.com"></div>
<div class="form-group"><label>Phone</label><input type="tel" placeholder="(555) 555-5555"></div>
<div class="form-group full"><label>Website URL</label><input type="url" placeholder="https://yourbusiness.com"></div>
<div class="form-group full"><label>What service are you interested in?</label>
<select><option value="">Select a service...</option><option>Local SEO</option><option>GBP Optimization</option><option>Reputation Management</option><option>AI SEO Services</option><option>Facebook & Google Ads</option><option>Social Media Management</option><option>Content Creation</option><option>Full Growth Package</option><option>Not sure — need advice</option></select></div>
<div class="form-group full"><label>Tell us about your business</label><textarea placeholder="What are your goals? What challenges are you facing?"></textarea></div>
</div>
<button type="submit" class="form-submit">Send Message →</button>
</form>
</div>
</div>
</div></section>
<section class="cta-section"><div class="container"><h2>Prefer a Quick Chat?</h2><p>Click the chat button in the corner to speak with our AI assistant instantly. Or call (800) 555-0199 for immediate help.</p><a href="free-audit.html" class="btn btn-white">Get Free Audit Instead →</a></div></section>'''
)

# ===== CASE STUDIES =====
pages["case-studies.html"] = page(
    "Case Studies — Real Results for Real Businesses",
    "See real SEO results from AI Growth Labs clients. Case studies showing traffic increases, lead generation, and revenue growth for USA local businesses.",
    "SEO case studies, local business results, SEO success stories, digital marketing results",
    '''<section class="page-hero"><div class="container"><span class="section-badge">📊 Case Studies</span><h1>Real Results for Real Businesses</h1><p>See how we've helped USA local businesses increase visibility, generate leads, and grow revenue with our AI-powered approach.</p></div></section>
<section class="section section-darker"><div class="container"><div class="cases-grid">
<div class="case-card"><div class="case-top"><div class="case-industry">🦷 Dental</div><h3 class="case-title">SmileBright Dental — Austin, TX</h3><p class="case-desc">From invisible on Google to Map Pack #1. Generated 47 new patient appointments per month through Local SEO and GBP optimization.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">340%</div><div class="lbl">Traffic</div></div><div class="case-metric"><div class="val">47</div><div class="lbl">Patients/Mo</div></div><div class="case-metric"><div class="val">4.9★</div><div class="lbl">Rating</div></div></div></div>
<div class="case-card"><div class="case-top"><div class="case-industry">⚖️ Legal</div><h3 class="case-title">Martinez Legal — Dallas, TX</h3><p class="case-desc">Personal injury law firm increased qualified leads by 608% using our combined SEO + Google Ads strategy with AI-optimized landing pages.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">520%</div><div class="lbl">ROI</div></div><div class="case-metric"><div class="val">85</div><div class="lbl">Leads/Mo</div></div><div class="case-metric"><div class="val">$42</div><div class="lbl">Cost/Lead</div></div></div></div>
<div class="case-card"><div class="case-top"><div class="case-industry">🍽️ Restaurant</div><h3 class="case-title">Bella's Italian — Chicago, IL</h3><p class="case-desc">Doubled monthly revenue through GBP optimization, review management, and Instagram strategy. From 45 to 890 Google reviews.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">200%</div><div class="lbl">Revenue</div></div><div class="case-metric"><div class="val">890</div><div class="lbl">Reviews</div></div><div class="case-metric"><div class="val">$45K</div><div class="lbl">Revenue Added</div></div></div></div>
<div class="case-card"><div class="case-top"><div class="case-industry">🔧 Plumbing</div><h3 class="case-title">Precision Plumbing — Dallas, TX</h3><p class="case-desc">Emergency plumber went from 30 to 120+ service calls per month by dominating "plumber near me" searches across their entire service area.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">450%</div><div class="lbl">Calls</div></div><div class="case-metric"><div class="val">#2</div><div class="lbl">Map Pack</div></div><div class="case-metric"><div class="val">$85K</div><div class="lbl">Revenue/Mo</div></div></div></div>
<div class="case-card"><div class="case-top"><div class="case-industry">❄️ HVAC</div><h3 class="case-title">Phoenix HVAC Pro — Phoenix, AZ</h3><p class="case-desc">Year-round lead generation strategy eliminated seasonal dips. Now generating 120+ leads per month across AC and heating services.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">380%</div><div class="lbl">More Leads</div></div><div class="case-metric"><div class="val">#1</div><div class="lbl">Map Pack</div></div><div class="case-metric"><div class="val">$120K</div><div class="lbl">Revenue/Mo</div></div></div></div>
<div class="case-card"><div class="case-top"><div class="case-industry">💆 Medical Spa</div><h3 class="case-title">Glow Aesthetics — Los Angeles, CA</h3><p class="case-desc">From 23 reviews to 680+ with our ethical review system. Increased bookings by 290% through SEO + Instagram marketing.</p></div><div class="case-metrics"><div class="case-metric"><div class="val">290%</div><div class="lbl">Bookings</div></div><div class="case-metric"><div class="val">680+</div><div class="lbl">Reviews</div></div><div class="case-metric"><div class="val">4.9★</div><div class="lbl">Rating</div></div></div></div>
</div></div></section>
<section class="cta-section"><div class="container"><h2>Your Success Story Starts Here</h2><p>Get your free DNA-level audit and see what's possible for your business.</p><a href="free-audit.html" class="btn btn-white">Start My Free Audit →</a></div></section>'''
)

# ===== BLOG =====
pages["blog.html"] = page(
    "Blog — SEO Tips, Digital Marketing Insights & Growth Strategies",
    "Expert SEO tips, local marketing strategies, and digital growth insights from AI Growth Labs. Learn how to rank higher and grow your business.",
    "SEO blog, digital marketing tips, local SEO strategies, Google ranking tips, business growth blog",
    '''<section class="page-hero"><div class="container"><span class="section-badge">📝 Blog</span><h1>SEO Tips & Growth Strategies</h1><p>Expert insights, actionable tips, and proven strategies to help your business grow online.</p></div></section>
<section class="section section-darker"><div class="container"><div class="services-grid">
<a href="#" class="service-card"><div class="service-icon">🦷</div><h3>How Dentists Can Rank #1 on Google Maps in 2026</h3><p>Complete guide for dental practices looking to dominate local search. Step-by-step GBP optimization, review strategy, and local SEO tactics.</p><span class="link">Read Article →</span></a>
<a href="#" class="service-card"><div class="service-icon">🍽️</div><h3>Best Local SEO Strategies for Restaurants in 2026</h3><p>Everything restaurant owners need to know about getting found on Google. From menu optimization to Instagram marketing that drives foot traffic.</p><span class="link">Read Article →</span></a>
<a href="#" class="service-card"><div class="service-icon">⚖️</div><h3>How Lawyers Get Leads From Google — Complete Guide</h3><p>Legal marketing strategies that generate qualified consultations. SEO, Google Ads, and content marketing for law firms.</p><span class="link">Read Article →</span></a>
<a href="#" class="service-card"><div class="service-icon">🏢</div><h3>GBP Optimization Guide 2026 — Rank Higher on Maps</h3><p>The definitive guide to Google Business Profile optimization. Every field, every feature, every strategy to maximize your map pack visibility.</p><span class="link">Read Article →</span></a>
<a href="#" class="service-card"><div class="service-icon">⭐</div><h3>Ethical Review Generation — Get More 5-Star Reviews</h3><p>How to generate authentic customer reviews without violating Google's policies. SMS, email, and QR code strategies that work.</p><span class="link">Read Article →</span></a>
<a href="#" class="service-card"><div class="service-icon">🤖</div><h3>AI SEO in 2026 — What Local Businesses Need to Know</h3><p>How AI is changing search engine optimization. Entity SEO, semantic search, and AI visibility optimization explained for business owners.</p><span class="link">Read Article →</span></a>
</div></div></section>'''
)

# ===== FREE AUDIT =====
pages["free-audit.html"] = page(
    "Free DNA-Level SEO Audit — 100+ Ranking Factors Analyzed",
    "Get your free DNA-level SEO audit. We analyze 100+ ranking factors across 12 pillars and deliver a detailed report with actionable recommendations.",
    "free SEO audit, website audit, SEO analysis, free website review, SEO report",
    '''<section class="page-hero"><div class="container"><span class="section-badge">📊 Free SEO Audit</span><h1>Free DNA-Level SEO Audit</h1><p>We analyze your website across 100+ ranking factors and 12 DNA pillars. Get a detailed report with actionable recommendations — completely free.</p></div></section>
<section class="section section-darker"><div class="container">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:start">
<div>
<h2 class="section-title mb-24">What You'll Get</h2>
<div class="services-grid" style="grid-template-columns:1fr">
<div class="service-card"><div style="display:flex;gap:16px;align-items:start"><div class="service-icon" style="flex-shrink:0">⚙️</div><div><h3>Technical SEO Analysis</h3><p>Crawlability, indexability, site speed, mobile optimization, security, and structured data assessment.</p></div></div></div>
<div class="service-card"><div style="display:flex;gap:16px;align-items:start"><div class="service-icon" style="flex-shrink:0">📄</div><div><h3>Content & On-Page Review</h3><p>Title tags, meta descriptions, heading structure, keyword optimization, content quality, and UX signals.</p></div></div></div>
<div class="service-card"><div style="display:flex;gap:16px;align-items:start"><div class="service-icon" style="flex-shrink:0">📍</div><div><h3>Local SEO Assessment</h3><p>Google Business Profile, NAP consistency, local citations, geo relevance, and review analysis.</p></div></div></div>
<div class="service-card"><div style="display:flex;gap:16px;align-items:start"><div class="service-icon" style="flex-shrink:0">🏆</div><div><h3>Competitor Comparison</h3><p>How you stack up against your top local competitors across authority, content, and visibility.</p></div></div></div>
<div class="service-card"><div style="display:flex;gap:16px;align-items:start"><div class="service-icon" style="flex-shrink:0">🎯</div><div><h3>90-Day Action Plan</h3><p>Prioritized recommendations with quick wins, medium-term goals, and long-term strategy.</p></div></div></div>
</div>
</div>
<div style="background:#0F172A;border:1px solid #1E3A5F;border-radius:16px;padding:36px">
<h3 style="color:#F1F5F9;font-size:1.2rem;font-weight:700;margin-bottom:8px">Get Your Free Audit</h3>
<p style="color:#94A3B8;font-size:.88rem;margin-bottom:24px">Fill out the form below and we'll deliver your detailed audit report within 24 hours.</p>
<form id="auditForm">
<div class="form-group"><label>Business Name *</label><input type="text" required placeholder="Your Business Name"></div>
<div class="form-group"><label>Website URL *</label><input type="url" required placeholder="https://yourbusiness.com"></div>
<div class="form-grid">
<div class="form-group"><label>Your Name *</label><input type="text" required placeholder="John Smith"></div>
<div class="form-group"><label>Email *</label><input type="email" required placeholder="john@business.com"></div>
</div>
<div class="form-group"><label>Phone</label><input type="tel" placeholder="(555) 555-5555"></div>
<div class="form-group"><label>Industry</label>
<select><option value="">Select your industry...</option><option>Dentist</option><option>Lawyer</option><option>Restaurant</option><option>Plumber</option><option>HVAC</option><option>Medical Spa</option><option>Real Estate</option><option>Contractor</option><option>Auto Services</option><option>Other</option></select></div>
<div class="form-group"><label>What's your biggest challenge?</label><textarea placeholder="Tell us about your current marketing challenges..." rows="3"></textarea></div>
<button type="submit" class="form-submit">Get My Free Audit →</button>
<p style="color:#64748B;font-size:.78rem;margin-top:12px;text-align:center">No credit card required. No obligation. Just actionable insights.</p>
</form>
</div>
</div>
</div></section>'''
)

# ===== LEGAL PAGES =====
pages["privacy-policy.html"] = page(
    "Privacy Policy",
    "AI Growth Labs privacy policy. Learn how we collect, use, and protect your personal information.",
    "privacy policy, data protection, personal information",
    '''<section class="page-hero"><div class="container"><h1>Privacy Policy</h1><p>Last updated: January 2026</p></div></section>
<section class="section section-darker"><div class="container"><div style="max-width:800px;margin:0 auto;color:#CBD5E1;line-height:1.8">
<h2 style="color:#F1F5F9;margin:32px 0 16px">Information We Collect</h2><p>We collect information you provide directly: name, email, phone number, website URL, and business details when you submit forms, request audits, or contact us. We also collect usage data through cookies and analytics tools including pages visited, time on site, and referral source.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">How We Use Your Information</h2><p>We use your information to: provide our SEO and marketing services, send you audit reports and recommendations, communicate about your account, improve our services, and send relevant marketing communications (with your consent).</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Information Sharing</h2><p>We do not sell your personal information. We may share information with: service providers who assist in delivering our services, analytics partners, and when required by law.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Data Security</h2><p>We implement industry-standard security measures to protect your information including encryption, secure servers, and access controls.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Your Rights</h2><p>You have the right to access, correct, or delete your personal information. Contact us at privacy@aigrowth-labs.com for any data requests.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Contact</h2><p>For privacy-related questions: privacy@aigrowth-labs.com</p>
</div></div></section>'''
)

pages["terms.html"] = page(
    "Terms & Conditions",
    "AI Growth Labs terms and conditions of service. Read our service agreement, payment terms, and policies.",
    "terms and conditions, service agreement, terms of service",
    '''<section class="page-hero"><div class="container"><h1>Terms & Conditions</h1><p>Last updated: January 2026</p></div></section>
<section class="section section-darker"><div class="container"><div style="max-width:800px;margin:0 auto;color:#CBD5E1;line-height:1.8">
<h2 style="color:#F1F5F9;margin:32px 0 16px">Service Agreement</h2><p>By engaging AI Growth Labs for SEO and digital marketing services, you agree to these terms. Our services are provided on a month-to-month basis unless otherwise specified in a custom agreement.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Payment Terms</h2><p>Services are billed monthly in advance. Payment is due upon receipt of invoice. We accept major credit cards and bank transfers. Late payments may result in service suspension after 15 days notice.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">No Guarantees</h2><p>While we use proven strategies and best practices, we cannot guarantee specific search engine rankings. SEO results depend on many factors including competition, industry, and search engine algorithms. We guarantee transparent work, regular reporting, and adherence to Google's guidelines.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Cancellation</h2><p>Either party may cancel services with 30 days written notice. We recommend a minimum 3-6 month engagement for meaningful SEO results, but you are never locked into a long-term contract.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Ethical Standards</h2><p>We adhere to Google's Webmaster Guidelines and never engage in black-hat SEO practices. We do not buy fake reviews, use spam backlinks, or make guarantees about #1 rankings.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Contact</h2><p>For questions about these terms: legal@aigrowth-labs.com</p>
</div></div></section>'''
)

pages["disclaimer.html"] = page(
    "Disclaimer",
    "AI Growth Labs disclaimer. Important information about our SEO services, results, and claims.",
    "disclaimer, SEO disclaimer, results disclaimer",
    '''<section class="page-hero"><div class="container"><h1>Disclaimer</h1><p>Last updated: January 2026</p></div></section>
<section class="section section-darker"><div class="container"><div style="max-width:800px;margin:0 auto;color:#CBD5E1;line-height:1.8">
<h2 style="color:#F1F5F9;margin:32px 0 16px">Results Disclaimer</h2><p>The results and statistics mentioned on our website, case studies, and marketing materials are based on actual client results. However, individual results may vary. Past performance does not guarantee future results. SEO timelines, ranking improvements, and lead generation outcomes depend on many factors including competition, industry, location, and search engine algorithm updates.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">No Ranking Guarantees</h2><p>AI Growth Labs does not guarantee #1 rankings on Google or any search engine. No ethical SEO company can make such guarantees. We guarantee our work ethic, transparency, and commitment to using best practices.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Third-Party Tools</h2><p>We use various third-party tools and platforms in delivering our services. We are not responsible for changes to third-party tools, APIs, or platforms that may affect service delivery.</p>
<h2 style="color:#F1F5F9;margin:32px 0 16px">Professional Advice</h2><p>Content on our website is for informational purposes and should not be considered professional business, legal, or financial advice.</p>
</div></div></section>'''
)

# Write all pages
for filename, content in pages.items():
    filepath = os.path.join(SITE, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Created: {filename}")

print(f"\nTotal pages created: {len(pages)}")
