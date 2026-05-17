"""Real SEO DNA Audit Engine — Crawls and analyzes websites for 100+ SEO factors."""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
import re
import time
import ssl
import socket

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 15


def run_audit(url: str) -> dict:
    if not url.startswith("http"):
        url = "https://" + url
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path.split("/")[0]
    base_url = f"{parsed.scheme}://{domain}"

    result = {
        "url": url,
        "domain": domain,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "overall_score": 0,
        "maturity_level": "",
        "pillars": {},
        "quick_wins": [],
        "critical_issues": [],
        "warnings": [],
        "passed": [],
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        html = resp.text
        soup = BeautifulSoup(html, "lxml")
        load_time = resp.elapsed.total_seconds()
    except Exception as e:
        result["error"] = f"Could not fetch website: {str(e)}"
        result["overall_score"] = 0
        result["maturity_level"] = "Unable to Audit"
        return result

    scores = {}

    # 1. TECHNICAL SEO DNA
    tech = _audit_technical(url, base_url, domain, resp, soup, html, load_time, result)
    scores["technical"] = tech

    # 2. ON-PAGE SEO DNA
    onpage = _audit_onpage(soup, html, url, result)
    scores["onpage"] = onpage

    # 3. CONTENT SEO DNA
    content = _audit_content(soup, html, result)
    scores["content"] = content

    # 4. ENTITY SEO DNA
    entity = _audit_entity(soup, html, result)
    scores["entity"] = entity

    # 5. INTERNAL LINKING DNA
    linking = _audit_linking(soup, base_url, url, result)
    scores["linking"] = linking

    # 6. STRUCTURED DATA / SCHEMA DNA
    schema = _audit_schema(soup, html, result)
    scores["schema"] = schema

    # 7. IMAGE & MEDIA DNA
    media = _audit_media(soup, base_url, result)
    scores["media"] = media

    # 8. SOCIAL MEDIA DNA
    social = _audit_social(soup, html, domain, result)
    scores["social"] = social

    # 9. SECURITY DNA
    security = _audit_security(url, domain, resp, result)
    scores["security"] = security

    # 10. MOBILE & UX DNA
    mobile = _audit_mobile(soup, html, result)
    scores["mobile"] = mobile

    # 11. INDEXABILITY DNA
    indexability = _audit_indexability(base_url, soup, html, resp, result)
    scores["indexability"] = indexability

    # 12. PERFORMANCE DNA
    perf = _audit_performance(resp, html, soup, load_time, result)
    scores["performance"] = perf

    # Calculate overall
    pillar_scores = list(scores.values())
    overall = round(sum(pillar_scores) / len(pillar_scores)) if pillar_scores else 0
    result["overall_score"] = overall
    result["pillar_scores"] = scores

    if overall >= 85:
        result["maturity_level"] = "DNA Level (Advanced)"
    elif overall >= 70:
        result["maturity_level"] = "Advanced"
    elif overall >= 50:
        result["maturity_level"] = "Intermediate"
    elif overall >= 30:
        result["maturity_level"] = "Basic"
    else:
        result["maturity_level"] = "Critical — Needs Immediate Attention"

    return result


def _audit_technical(url, base_url, domain, resp, soup, html, load_time, result):
    score = 100
    pillar = {"name": "Technical SEO", "checks": []}

    # HTTPS check
    if url.startswith("https"):
        pillar["checks"].append({"factor": "HTTPS/SSL", "status": "pass", "detail": "Site uses HTTPS"})
        result["passed"].append("HTTPS/SSL is enabled")
    else:
        pillar["checks"].append({"factor": "HTTPS/SSL", "status": "fail", "detail": "Site does NOT use HTTPS"})
        result["critical_issues"].append("Site is not using HTTPS — Critical security and ranking issue")
        score -= 20

    # Response code
    if resp.status_code == 200:
        pillar["checks"].append({"factor": "HTTP Status", "status": "pass", "detail": f"Status: {resp.status_code}"})
    else:
        pillar["checks"].append({"factor": "HTTP Status", "status": "warn", "detail": f"Status: {resp.status_code}"})
        result["warnings"].append(f"HTTP status code: {resp.status_code}")
        score -= 10

    # Load time
    if load_time < 1.0:
        pillar["checks"].append({"factor": "Server Response", "status": "pass", "detail": f"TTFB: {load_time:.2f}s — Excellent"})
        result["passed"].append(f"Fast server response: {load_time:.2f}s")
    elif load_time < 3.0:
        pillar["checks"].append({"factor": "Server Response", "status": "warn", "detail": f"TTFB: {load_time:.2f}s — Needs improvement"})
        result["warnings"].append(f"Server response time is {load_time:.2f}s — should be under 1s")
        score -= 10
    else:
        pillar["checks"].append({"factor": "Server Response", "status": "fail", "detail": f"TTFB: {load_time:.2f}s — Slow"})
        result["critical_issues"].append(f"Very slow server response: {load_time:.2f}s")
        score -= 20

    # Redirect chain
    if len(resp.history) > 2:
        pillar["checks"].append({"factor": "Redirect Chain", "status": "fail", "detail": f"{len(resp.history)} redirects detected"})
        result["warnings"].append(f"Redirect chain detected: {len(resp.history)} hops")
        score -= 10
    elif len(resp.history) > 0:
        pillar["checks"].append({"factor": "Redirect Chain", "status": "warn", "detail": f"{len(resp.history)} redirect(s)"})
    else:
        pillar["checks"].append({"factor": "Redirect Chain", "status": "pass", "detail": "No redirects"})

    # Robots.txt
    try:
        robots_resp = requests.get(f"{base_url}/robots.txt", headers=HEADERS, timeout=5)
        if robots_resp.status_code == 200 and len(robots_resp.text) > 10:
            pillar["checks"].append({"factor": "robots.txt", "status": "pass", "detail": "Found and valid"})
            result["passed"].append("robots.txt is present")
            if "Disallow: /" in robots_resp.text and "Allow:" not in robots_resp.text:
                pillar["checks"].append({"factor": "robots.txt Blocking", "status": "fail", "detail": "Site may be blocking all crawlers"})
                result["critical_issues"].append("robots.txt may be blocking search engines")
                score -= 20
        else:
            pillar["checks"].append({"factor": "robots.txt", "status": "warn", "detail": "Not found or empty"})
            result["warnings"].append("robots.txt is missing or empty")
            score -= 5
    except Exception:
        pillar["checks"].append({"factor": "robots.txt", "status": "warn", "detail": "Could not check"})

    # Sitemap
    try:
        sm_resp = requests.get(f"{base_url}/sitemap.xml", headers=HEADERS, timeout=5)
        if sm_resp.status_code == 200 and ("urlset" in sm_resp.text or "sitemapindex" in sm_resp.text):
            urls_count = sm_resp.text.count("<loc>")
            pillar["checks"].append({"factor": "Sitemap", "status": "pass", "detail": f"Found with ~{urls_count} URLs"})
            result["passed"].append(f"XML Sitemap found with ~{urls_count} URLs")
        else:
            pillar["checks"].append({"factor": "Sitemap", "status": "warn", "detail": "Not found at /sitemap.xml"})
            result["warnings"].append("XML Sitemap not found — add sitemap.xml for better indexing")
            result["quick_wins"].append("Create and submit an XML sitemap")
            score -= 10
    except Exception:
        pillar["checks"].append({"factor": "Sitemap", "status": "warn", "detail": "Could not check"})

    # Doctype
    if "<!DOCTYPE" in html[:100].upper() or "<!doctype" in html[:100]:
        pillar["checks"].append({"factor": "DOCTYPE", "status": "pass", "detail": "HTML5 DOCTYPE present"})
    else:
        pillar["checks"].append({"factor": "DOCTYPE", "status": "warn", "detail": "DOCTYPE missing"})
        score -= 5

    # Language attribute
    html_tag = soup.find("html")
    if html_tag and html_tag.get("lang"):
        pillar["checks"].append({"factor": "Language", "status": "pass", "detail": f"lang=\"{html_tag['lang']}\""})
    else:
        pillar["checks"].append({"factor": "Language", "status": "warn", "detail": "No lang attribute on <html>"})
        result["quick_wins"].append("Add lang attribute to <html> tag")
        score -= 5

    # Canonical
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        pillar["checks"].append({"factor": "Canonical URL", "status": "pass", "detail": canonical["href"]})
        result["passed"].append("Canonical URL is set")
    else:
        pillar["checks"].append({"factor": "Canonical URL", "status": "warn", "detail": "No canonical tag found"})
        result["warnings"].append("Missing canonical URL — risk of duplicate content issues")
        result["quick_wins"].append("Add canonical URL tag")
        score -= 10

    result["pillars"]["technical"] = pillar
    return max(0, min(100, score))


def _audit_onpage(soup, html, url, result):
    score = 100
    pillar = {"name": "On-Page SEO", "checks": []}

    # Title tag
    title = soup.find("title")
    if title and title.string:
        title_text = title.string.strip()
        title_len = len(title_text)
        if 30 <= title_len <= 65:
            pillar["checks"].append({"factor": "Title Tag", "status": "pass", "detail": f"\"{title_text}\" ({title_len} chars)"})
            result["passed"].append(f"Title tag is optimized: {title_len} chars")
        elif title_len > 65:
            pillar["checks"].append({"factor": "Title Tag", "status": "warn", "detail": f"\"{title_text[:60]}...\" ({title_len} chars — too long)"})
            result["warnings"].append(f"Title tag too long ({title_len} chars) — keep under 65")
            score -= 5
        elif title_len < 30:
            pillar["checks"].append({"factor": "Title Tag", "status": "warn", "detail": f"\"{title_text}\" ({title_len} chars — too short)"})
            result["warnings"].append(f"Title tag too short ({title_len} chars) — aim for 30-65")
            score -= 5
    else:
        pillar["checks"].append({"factor": "Title Tag", "status": "fail", "detail": "MISSING — Critical for SEO"})
        result["critical_issues"].append("Title tag is missing — This is critical for rankings")
        score -= 25

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        desc = meta_desc["content"].strip()
        desc_len = len(desc)
        if 120 <= desc_len <= 160:
            pillar["checks"].append({"factor": "Meta Description", "status": "pass", "detail": f"\"{desc[:80]}...\" ({desc_len} chars)"})
            result["passed"].append(f"Meta description is optimized: {desc_len} chars")
        elif desc_len > 160:
            pillar["checks"].append({"factor": "Meta Description", "status": "warn", "detail": f"({desc_len} chars — too long, will be truncated)"})
            result["warnings"].append(f"Meta description too long ({desc_len} chars) — keep under 160")
            score -= 5
        else:
            pillar["checks"].append({"factor": "Meta Description", "status": "warn", "detail": f"({desc_len} chars — too short)"})
            result["warnings"].append(f"Meta description too short ({desc_len} chars)")
            score -= 5
    else:
        pillar["checks"].append({"factor": "Meta Description", "status": "fail", "detail": "MISSING — Affects CTR"})
        result["critical_issues"].append("Meta description is missing — hurts click-through rates")
        result["quick_wins"].append("Add meta description with target keyword and CTA")
        score -= 15

    # H1 tag
    h1s = soup.find_all("h1")
    if len(h1s) == 1:
        h1_text = h1s[0].get_text(strip=True)
        pillar["checks"].append({"factor": "H1 Tag", "status": "pass", "detail": f"\"{h1_text[:80]}\" — Single H1 found"})
        result["passed"].append("Single H1 tag present")
    elif len(h1s) == 0:
        pillar["checks"].append({"factor": "H1 Tag", "status": "fail", "detail": "No H1 tag found"})
        result["critical_issues"].append("No H1 tag — Search engines need this for page topic")
        score -= 15
    else:
        pillar["checks"].append({"factor": "H1 Tag", "status": "warn", "detail": f"Multiple H1 tags found ({len(h1s)})"})
        result["warnings"].append(f"Multiple H1 tags ({len(h1s)}) — use only one per page")
        score -= 5

    # H2-H6 structure
    headings = {}
    for level in range(2, 7):
        tags = soup.find_all(f"h{level}")
        if tags:
            headings[f"H{level}"] = len(tags)
    if headings:
        detail = ", ".join(f"{k}: {v}" for k, v in headings.items())
        pillar["checks"].append({"factor": "Heading Structure", "status": "pass", "detail": detail})
        result["passed"].append(f"Heading hierarchy present: {detail}")
    else:
        pillar["checks"].append({"factor": "Heading Structure", "status": "warn", "detail": "No H2-H6 tags found"})
        result["warnings"].append("No subheadings (H2-H6) — add for better content structure")
        score -= 10

    # Meta viewport
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if viewport:
        pillar["checks"].append({"factor": "Viewport Meta", "status": "pass", "detail": "Mobile viewport configured"})
    else:
        pillar["checks"].append({"factor": "Viewport Meta", "status": "fail", "detail": "No viewport meta — not mobile friendly"})
        result["critical_issues"].append("No viewport meta tag — site is not mobile-optimized")
        score -= 15

    # Open Graph tags
    og_tags = soup.find_all("meta", property=re.compile(r"^og:"))
    if len(og_tags) >= 3:
        pillar["checks"].append({"factor": "Open Graph", "status": "pass", "detail": f"{len(og_tags)} OG tags found"})
        result["passed"].append(f"Open Graph tags present ({len(og_tags)} tags)")
    elif og_tags:
        pillar["checks"].append({"factor": "Open Graph", "status": "warn", "detail": f"Only {len(og_tags)} OG tag(s) — add more"})
        score -= 5
    else:
        pillar["checks"].append({"factor": "Open Graph", "status": "warn", "detail": "No Open Graph tags — affects social sharing"})
        result["quick_wins"].append("Add Open Graph tags for better social media sharing")
        score -= 10

    # Twitter cards
    twitter_tags = soup.find_all("meta", attrs={"name": re.compile(r"^twitter:")})
    if twitter_tags:
        pillar["checks"].append({"factor": "Twitter Cards", "status": "pass", "detail": f"{len(twitter_tags)} Twitter card tags"})
    else:
        pillar["checks"].append({"factor": "Twitter Cards", "status": "warn", "detail": "No Twitter Card tags"})
        score -= 3

    # Favicon
    favicon = soup.find("link", rel=re.compile(r"icon", re.I))
    if favicon:
        pillar["checks"].append({"factor": "Favicon", "status": "pass", "detail": "Favicon found"})
    else:
        pillar["checks"].append({"factor": "Favicon", "status": "warn", "detail": "No favicon detected"})
        result["quick_wins"].append("Add favicon for branding")
        score -= 3

    result["pillars"]["onpage"] = pillar
    return max(0, min(100, score))


def _audit_content(soup, html, result):
    score = 100
    pillar = {"name": "Content Quality", "checks": []}

    # Word count
    body = soup.find("body")
    text = body.get_text(separator=" ", strip=True) if body else ""
    words = len(text.split())
    if words >= 1500:
        pillar["checks"].append({"factor": "Word Count", "status": "pass", "detail": f"{words} words — Strong content depth"})
        result["passed"].append(f"Strong content depth: {words} words")
    elif words >= 500:
        pillar["checks"].append({"factor": "Word Count", "status": "warn", "detail": f"{words} words — Consider adding more"})
        result["warnings"].append(f"Content is {words} words — aim for 1500+ for ranking")
        score -= 10
    elif words >= 100:
        pillar["checks"].append({"factor": "Word Count", "status": "warn", "detail": f"{words} words — Thin content"})
        result["warnings"].append(f"Thin content ({words} words) — Google may not rank this")
        score -= 20
    else:
        pillar["checks"].append({"factor": "Word Count", "status": "fail", "detail": f"Only {words} words — Very thin"})
        result["critical_issues"].append(f"Very thin content ({words} words) — needs significant content")
        score -= 30

    # Paragraphs
    paragraphs = soup.find_all("p")
    p_with_text = [p for p in paragraphs if len(p.get_text(strip=True)) > 20]
    if len(p_with_text) >= 5:
        pillar["checks"].append({"factor": "Paragraphs", "status": "pass", "detail": f"{len(p_with_text)} content paragraphs"})
    else:
        pillar["checks"].append({"factor": "Paragraphs", "status": "warn", "detail": f"Only {len(p_with_text)} paragraphs"})
        score -= 5

    # Lists (ul/ol)
    lists = soup.find_all(["ul", "ol"])
    content_lists = [l for l in lists if l.find("li")]
    if content_lists:
        pillar["checks"].append({"factor": "Lists", "status": "pass", "detail": f"{len(content_lists)} lists found — good for readability"})
    else:
        pillar["checks"].append({"factor": "Lists", "status": "warn", "detail": "No lists — add for better readability"})
        result["quick_wins"].append("Add bullet/numbered lists for better readability and featured snippets")
        score -= 5

    # Bold/Strong emphasis
    strong_tags = soup.find_all(["strong", "b"])
    if strong_tags:
        pillar["checks"].append({"factor": "Emphasis", "status": "pass", "detail": f"{len(strong_tags)} bold/strong elements"})
    else:
        pillar["checks"].append({"factor": "Emphasis", "status": "warn", "detail": "No bold text for keyword emphasis"})
        score -= 3

    result["pillars"]["content"] = pillar
    return max(0, min(100, score))


def _audit_entity(soup, html, result):
    score = 70  # Start lower as entity SEO is hard to detect externally
    pillar = {"name": "Entity SEO", "checks": []}

    body = soup.find("body")
    text = body.get_text(separator=" ", strip=True).lower() if body else ""
    words = text.split()
    word_count = len(words)

    # Unique entities (simple word frequency analysis)
    word_freq = {}
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "as", "it", "this", "that", "they", "we", "you", "our", "your", "can", "will", "has", "have", "had", "do", "does", "not", "no", "all", "more", "about", "up"}
    for w in words:
        clean = re.sub(r'[^a-z]', '', w)
        if len(clean) > 3 and clean not in stopwords:
            word_freq[clean] = word_freq.get(clean, 0) + 1

    top_entities = sorted(word_freq.items(), key=lambda x: -x[1])[:20]
    if top_entities:
        entity_list = ", ".join(f"{e[0]} ({e[1]}x)" for e in top_entities[:10])
        pillar["checks"].append({"factor": "Top Entities", "status": "info", "detail": entity_list})

    unique_topics = len([w for w, c in word_freq.items() if c >= 2])
    if unique_topics >= 30:
        pillar["checks"].append({"factor": "Semantic Depth", "status": "pass", "detail": f"{unique_topics} unique topic terms"})
        score += 15
    elif unique_topics >= 15:
        pillar["checks"].append({"factor": "Semantic Depth", "status": "warn", "detail": f"{unique_topics} unique terms — could be deeper"})
        score += 5
    else:
        pillar["checks"].append({"factor": "Semantic Depth", "status": "warn", "detail": f"Only {unique_topics} unique terms — thin semantic coverage"})
        result["warnings"].append("Low semantic depth — add more related topic terms")

    result["pillars"]["entity"] = pillar
    return max(0, min(100, score))


def _audit_linking(soup, base_url, url, result):
    score = 100
    pillar = {"name": "Internal Linking", "checks": []}
    parsed_base = urlparse(base_url)

    all_links = soup.find_all("a", href=True)
    internal_links = []
    external_links = []
    broken_anchors = []

    for link in all_links:
        href = link["href"]
        if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
            if href == "#":
                broken_anchors.append(href)
            continue
        full_url = urljoin(url, href)
        parsed = urlparse(full_url)
        if parsed.netloc == parsed_base.netloc:
            anchor = link.get_text(strip=True)
            internal_links.append({"url": full_url, "anchor": anchor})
        else:
            external_links.append({"url": full_url, "anchor": link.get_text(strip=True)})

    # Internal links count
    if len(internal_links) >= 10:
        pillar["checks"].append({"factor": "Internal Links", "status": "pass", "detail": f"{len(internal_links)} internal links — Good"})
        result["passed"].append(f"{len(internal_links)} internal links found")
    elif len(internal_links) >= 3:
        pillar["checks"].append({"factor": "Internal Links", "status": "warn", "detail": f"Only {len(internal_links)} internal links"})
        result["warnings"].append(f"Only {len(internal_links)} internal links — add more for better SEO")
        score -= 15
    else:
        pillar["checks"].append({"factor": "Internal Links", "status": "fail", "detail": f"Only {len(internal_links)} internal links — Critical"})
        result["critical_issues"].append("Very few internal links — major SEO weakness")
        result["quick_wins"].append("Add contextual internal links to related pages")
        score -= 25

    # External links
    if external_links:
        pillar["checks"].append({"factor": "External Links", "status": "pass", "detail": f"{len(external_links)} external links"})
    else:
        pillar["checks"].append({"factor": "External Links", "status": "warn", "detail": "No external links — consider linking to authoritative sources"})
        score -= 5

    # Broken anchor links
    if broken_anchors:
        pillar["checks"].append({"factor": "Empty Anchors", "status": "warn", "detail": f"{len(broken_anchors)} empty # links"})
        score -= 3

    # Nofollow check
    nofollow_count = sum(1 for link in all_links if "nofollow" in (link.get("rel") or []))
    if nofollow_count:
        pillar["checks"].append({"factor": "Nofollow Links", "status": "info", "detail": f"{nofollow_count} nofollow links"})

    result["pillars"]["linking"] = pillar
    return max(0, min(100, score))


def _audit_schema(soup, html, result):
    score = 100
    pillar = {"name": "Structured Data", "checks": []}

    # JSON-LD schema
    schemas = soup.find_all("script", type="application/ld+json")
    schema_types = []
    if schemas:
        for s in schemas:
            try:
                data = json.loads(s.string)
                if isinstance(data, dict):
                    schema_types.append(data.get("@type", "Unknown"))
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            schema_types.append(item.get("@type", "Unknown"))
            except Exception:
                pass
        if schema_types:
            pillar["checks"].append({"factor": "JSON-LD Schema", "status": "pass", "detail": f"Found: {', '.join(schema_types)}"})
            result["passed"].append(f"Structured data found: {', '.join(schema_types)}")
        else:
            pillar["checks"].append({"factor": "JSON-LD Schema", "status": "warn", "detail": "JSON-LD script found but could not parse types"})
            score -= 10
    else:
        pillar["checks"].append({"factor": "JSON-LD Schema", "status": "fail", "detail": "No JSON-LD structured data found"})
        result["critical_issues"].append("No structured data (Schema.org) — missing rich results opportunity")
        result["quick_wins"].append("Add JSON-LD structured data (LocalBusiness, FAQ, Service, etc.)")
        score -= 30

    # Microdata
    microdata = soup.find_all(attrs={"itemtype": True})
    if microdata:
        types = [m["itemtype"].split("/")[-1] for m in microdata]
        pillar["checks"].append({"factor": "Microdata", "status": "pass", "detail": f"Found: {', '.join(types[:5])}"})
    else:
        pillar["checks"].append({"factor": "Microdata", "status": "info", "detail": "No microdata (JSON-LD is preferred)"})

    # Check for specific recommended schemas
    recommended = ["LocalBusiness", "Organization", "WebSite", "FAQPage", "Service", "BreadcrumbList"]
    missing = [r for r in recommended if r not in schema_types]
    if missing and schema_types:
        pillar["checks"].append({"factor": "Recommended Schemas", "status": "warn", "detail": f"Consider adding: {', '.join(missing[:4])}"})
        result["quick_wins"].append(f"Add schema types: {', '.join(missing[:3])}")
        score -= 5

    result["pillars"]["schema"] = pillar
    return max(0, min(100, score))


def _audit_media(soup, base_url, result):
    score = 100
    pillar = {"name": "Images & Media", "checks": []}

    images = soup.find_all("img")
    total_images = len(images)
    images_with_alt = [img for img in images if img.get("alt") and len(img["alt"].strip()) > 0]
    images_without_alt = total_images - len(images_with_alt)
    lazy_loaded = [img for img in images if img.get("loading") == "lazy"]

    pillar["checks"].append({"factor": "Total Images", "status": "info", "detail": f"{total_images} images found"})

    if total_images == 0:
        pillar["checks"].append({"factor": "Images", "status": "warn", "detail": "No images — add visual content"})
        result["warnings"].append("No images on page — add relevant images for engagement")
        score -= 10
    else:
        # Alt text
        alt_pct = round(len(images_with_alt) / total_images * 100) if total_images else 0
        if images_without_alt == 0:
            pillar["checks"].append({"factor": "Alt Text", "status": "pass", "detail": f"All {total_images} images have alt text"})
            result["passed"].append("All images have alt text")
        elif alt_pct >= 80:
            pillar["checks"].append({"factor": "Alt Text", "status": "warn", "detail": f"{images_without_alt} images missing alt text ({alt_pct}% have it)"})
            result["warnings"].append(f"{images_without_alt} images missing alt text")
            score -= 5
        else:
            pillar["checks"].append({"factor": "Alt Text", "status": "fail", "detail": f"{images_without_alt}/{total_images} images missing alt text ({alt_pct}% coverage)"})
            result["critical_issues"].append(f"{images_without_alt} images missing alt text — hurts accessibility and SEO")
            result["quick_wins"].append("Add descriptive alt text to all images")
            score -= 15

        # Lazy loading
        if lazy_loaded:
            pillar["checks"].append({"factor": "Lazy Loading", "status": "pass", "detail": f"{len(lazy_loaded)} images use lazy loading"})
        else:
            pillar["checks"].append({"factor": "Lazy Loading", "status": "warn", "detail": "No lazy loading — add loading=\"lazy\" to below-fold images"})
            result["quick_wins"].append("Add lazy loading to images for faster page speed")
            score -= 5

        # Check for large images (by looking at src attributes)
        svg_imgs = [img for img in images if img.get("src", "").endswith(".svg")]
        webp_imgs = [img for img in images if img.get("src", "").endswith(".webp")]
        if webp_imgs:
            pillar["checks"].append({"factor": "WebP Format", "status": "pass", "detail": f"{len(webp_imgs)} images use WebP — Good"})
        else:
            pillar["checks"].append({"factor": "WebP Format", "status": "warn", "detail": "No WebP images — consider converting for speed"})
            score -= 5

    # Videos
    videos = soup.find_all(["video", "iframe"])
    youtube_embeds = [v for v in videos if v.name == "iframe" and "youtube" in (v.get("src") or "")]
    if videos:
        pillar["checks"].append({"factor": "Video Content", "status": "pass", "detail": f"{len(videos)} video elements found"})
    if youtube_embeds:
        pillar["checks"].append({"factor": "YouTube Embeds", "status": "pass", "detail": f"{len(youtube_embeds)} YouTube videos"})

    result["pillars"]["media"] = pillar
    return max(0, min(100, score))


def _audit_social(soup, html, domain, result):
    score = 50  # Start at 50 since social signals are estimated
    pillar = {"name": "Social Media Presence", "checks": []}
    html_lower = html.lower()

    platforms = {
        "Facebook": ["facebook.com/", "fb.com/"],
        "Instagram": ["instagram.com/"],
        "Twitter/X": ["twitter.com/", "x.com/"],
        "LinkedIn": ["linkedin.com/"],
        "YouTube": ["youtube.com/", "youtu.be/"],
        "TikTok": ["tiktok.com/"],
        "Pinterest": ["pinterest.com/"],
    }

    found_platforms = []
    missing_platforms = []

    for platform, patterns in platforms.items():
        found = False
        for pattern in patterns:
            links = soup.find_all("a", href=re.compile(re.escape(pattern), re.I))
            if links:
                url_found = links[0]["href"]
                pillar["checks"].append({"factor": platform, "status": "pass", "detail": f"Link found: {url_found[:60]}"})
                found_platforms.append(platform)
                found = True
                score += 7
                break
        if not found:
            if pattern.replace("/", "") in html_lower:
                pillar["checks"].append({"factor": platform, "status": "warn", "detail": "Mentioned but no direct link"})
                score += 3
            else:
                missing_platforms.append(platform)

    if missing_platforms:
        pillar["checks"].append({"factor": "Missing Platforms", "status": "warn", "detail": f"Not found: {', '.join(missing_platforms)}"})
        if len(missing_platforms) > 4:
            result["warnings"].append(f"Missing social profiles: {', '.join(missing_platforms)}")
            result["quick_wins"].append("Add social media profile links to website footer")

    if found_platforms:
        result["passed"].append(f"Social profiles linked: {', '.join(found_platforms)}")

    result["pillars"]["social"] = pillar
    return max(0, min(100, score))


def _audit_security(url, domain, resp, result):
    score = 100
    pillar = {"name": "Security", "checks": []}

    # HTTPS
    if url.startswith("https"):
        pillar["checks"].append({"factor": "HTTPS", "status": "pass", "detail": "Secure connection"})
    else:
        pillar["checks"].append({"factor": "HTTPS", "status": "fail", "detail": "Not using HTTPS"})
        score -= 30

    # Security headers
    headers = resp.headers
    security_headers = {
        "Strict-Transport-Security": "HSTS",
        "X-Content-Type-Options": "Content-Type Options",
        "X-Frame-Options": "Frame Protection",
        "X-XSS-Protection": "XSS Protection",
        "Content-Security-Policy": "CSP",
    }
    found_headers = 0
    for header, name in security_headers.items():
        if header in headers:
            pillar["checks"].append({"factor": name, "status": "pass", "detail": f"{header} is set"})
            found_headers += 1
        else:
            pillar["checks"].append({"factor": name, "status": "warn", "detail": f"{header} missing"})
            score -= 5

    if found_headers >= 3:
        result["passed"].append(f"{found_headers}/5 security headers present")
    elif found_headers == 0:
        result["warnings"].append("No security headers found — add HSTS, CSP, X-Frame-Options")

    result["pillars"]["security"] = pillar
    return max(0, min(100, score))


def _audit_mobile(soup, html, result):
    score = 100
    pillar = {"name": "Mobile & UX", "checks": []}

    # Viewport
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if viewport:
        content = viewport.get("content", "")
        if "width=device-width" in content:
            pillar["checks"].append({"factor": "Viewport", "status": "pass", "detail": "Responsive viewport configured"})
            result["passed"].append("Mobile-responsive viewport set")
        else:
            pillar["checks"].append({"factor": "Viewport", "status": "warn", "detail": "Viewport set but may not be responsive"})
            score -= 10
    else:
        pillar["checks"].append({"factor": "Viewport", "status": "fail", "detail": "No viewport — not mobile friendly"})
        result["critical_issues"].append("No viewport meta tag — site is NOT mobile-friendly")
        score -= 30

    # Media queries in inline styles
    styles = soup.find_all("style")
    has_media_query = any("@media" in (s.string or "") for s in styles)
    # Also check for responsive CSS classes
    responsive_classes = ["container", "row", "col-", "flex", "grid", "responsive", "mobile"]
    has_responsive = any(cls in html.lower() for cls in responsive_classes)

    if has_media_query or has_responsive:
        pillar["checks"].append({"factor": "Responsive Design", "status": "pass", "detail": "Responsive CSS detected"})
    else:
        pillar["checks"].append({"factor": "Responsive Design", "status": "warn", "detail": "No responsive CSS detected"})
        score -= 10

    # Touch-friendly (check for small font sizes or small tap targets)
    small_font_count = len(re.findall(r'font-size:\s*(8|9|10)px', html))
    if small_font_count > 5:
        pillar["checks"].append({"factor": "Font Size", "status": "warn", "detail": f"{small_font_count} very small font sizes detected"})
        result["warnings"].append("Small font sizes detected — may be hard to read on mobile")
        score -= 5
    else:
        pillar["checks"].append({"factor": "Font Size", "status": "pass", "detail": "Font sizes appear adequate"})

    # Check for horizontal scroll indicators
    fixed_width = len(re.findall(r'width:\s*\d{4,}px', html))
    if fixed_width > 2:
        pillar["checks"].append({"factor": "Fixed Widths", "status": "warn", "detail": f"{fixed_width} large fixed widths — may cause horizontal scroll"})
        score -= 10

    result["pillars"]["mobile"] = pillar
    return max(0, min(100, score))


def _audit_indexability(base_url, soup, html, resp, result):
    score = 100
    pillar = {"name": "Indexability", "checks": []}

    # Meta robots
    meta_robots = soup.find("meta", attrs={"name": "robots"})
    if meta_robots:
        content = meta_robots.get("content", "").lower()
        if "noindex" in content:
            pillar["checks"].append({"factor": "Meta Robots", "status": "fail", "detail": f"NOINDEX detected: {content}"})
            result["critical_issues"].append("Page has NOINDEX — Google will NOT index this page")
            score -= 40
        elif "nofollow" in content:
            pillar["checks"].append({"factor": "Meta Robots", "status": "warn", "detail": f"NOFOLLOW detected: {content}"})
            result["warnings"].append("Page has NOFOLLOW — links will not pass authority")
            score -= 15
        else:
            pillar["checks"].append({"factor": "Meta Robots", "status": "pass", "detail": f"Robots: {content}"})
    else:
        pillar["checks"].append({"factor": "Meta Robots", "status": "pass", "detail": "No restrictive meta robots — page is indexable"})

    # X-Robots-Tag header
    x_robots = resp.headers.get("X-Robots-Tag", "")
    if "noindex" in x_robots.lower():
        pillar["checks"].append({"factor": "X-Robots-Tag", "status": "fail", "detail": f"Header: {x_robots}"})
        result["critical_issues"].append("X-Robots-Tag header has NOINDEX")
        score -= 30
    elif x_robots:
        pillar["checks"].append({"factor": "X-Robots-Tag", "status": "info", "detail": f"Header: {x_robots}"})

    # Canonical
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        pillar["checks"].append({"factor": "Canonical", "status": "pass", "detail": f"Set to: {canonical['href'][:80]}"})
    else:
        pillar["checks"].append({"factor": "Canonical", "status": "warn", "detail": "No canonical — risk of duplicate content"})
        score -= 10

    result["pillars"]["indexability"] = pillar
    return max(0, min(100, score))


def _audit_performance(resp, html, soup, load_time, result):
    score = 100
    pillar = {"name": "Performance", "checks": []}

    # HTML size
    html_size_kb = len(html.encode("utf-8")) / 1024
    if html_size_kb < 100:
        pillar["checks"].append({"factor": "HTML Size", "status": "pass", "detail": f"{html_size_kb:.0f} KB — Lightweight"})
    elif html_size_kb < 300:
        pillar["checks"].append({"factor": "HTML Size", "status": "warn", "detail": f"{html_size_kb:.0f} KB — Consider optimizing"})
        score -= 5
    else:
        pillar["checks"].append({"factor": "HTML Size", "status": "fail", "detail": f"{html_size_kb:.0f} KB — Too large"})
        result["warnings"].append(f"HTML is {html_size_kb:.0f} KB — optimize for speed")
        score -= 15

    # Inline scripts and styles
    scripts = soup.find_all("script")
    inline_scripts = [s for s in scripts if not s.get("src")]
    external_scripts = [s for s in scripts if s.get("src")]
    styles = soup.find_all("link", rel="stylesheet")
    inline_styles = soup.find_all("style")

    pillar["checks"].append({"factor": "External Scripts", "status": "info", "detail": f"{len(external_scripts)} external JS files"})
    pillar["checks"].append({"factor": "External Styles", "status": "info", "detail": f"{len(styles)} CSS files"})

    if len(external_scripts) > 15:
        pillar["checks"].append({"factor": "JS Count", "status": "warn", "detail": f"{len(external_scripts)} scripts — consider bundling"})
        result["warnings"].append(f"Too many scripts ({len(external_scripts)}) — bundle to reduce HTTP requests")
        score -= 10

    if len(inline_scripts) > 10:
        pillar["checks"].append({"factor": "Inline Scripts", "status": "warn", "detail": f"{len(inline_scripts)} inline scripts"})
        score -= 5

    # Render-blocking
    render_blocking = [s for s in scripts if not s.get("async") and not s.get("defer") and s.get("src")]
    if render_blocking:
        pillar["checks"].append({"factor": "Render Blocking", "status": "warn", "detail": f"{len(render_blocking)} render-blocking scripts"})
        result["quick_wins"].append("Add async/defer to non-critical scripts")
        score -= 5
    else:
        pillar["checks"].append({"factor": "Render Blocking", "status": "pass", "detail": "No render-blocking scripts detected"})

    # Server response
    if load_time < 0.5:
        pillar["checks"].append({"factor": "TTFB", "status": "pass", "detail": f"{load_time:.2f}s — Excellent"})
    elif load_time < 1.5:
        pillar["checks"].append({"factor": "TTFB", "status": "pass", "detail": f"{load_time:.2f}s — Good"})
    elif load_time < 3:
        pillar["checks"].append({"factor": "TTFB", "status": "warn", "detail": f"{load_time:.2f}s — Slow"})
        score -= 10
    else:
        pillar["checks"].append({"factor": "TTFB", "status": "fail", "detail": f"{load_time:.2f}s — Very slow"})
        score -= 20

    # Compression
    encoding = resp.headers.get("Content-Encoding", "")
    if encoding:
        pillar["checks"].append({"factor": "Compression", "status": "pass", "detail": f"Using {encoding}"})
        result["passed"].append(f"Compression enabled: {encoding}")
    else:
        pillar["checks"].append({"factor": "Compression", "status": "warn", "detail": "No compression detected (gzip/br)"})
        result["quick_wins"].append("Enable gzip/brotli compression")
        score -= 10

    result["pillars"]["performance"] = pillar
    return max(0, min(100, score))
