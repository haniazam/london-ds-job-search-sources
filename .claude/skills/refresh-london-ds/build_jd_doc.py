#!/usr/bin/env python3
"""Build the plain-text JD doc -> /tmp/ldn_ds_jds.txt

Reads /tmp/ldn_ds_active.csv (from refresh_roles.py), fetches each active role's
job description + requirements, trims boilerplate, and writes a NO-MARKDOWN plain
text document grouped by company. Greenhouse/Ashby/Amazon via official JSON APIs;
all other hosts via Playwright. The assistant then uploads /tmp/ldn_ds_jds.txt to
the Drive folder as a Google Doc (text/plain). See SKILL.md.
"""
import csv, json, re, html, sys, urllib.request
from urllib.parse import urlparse

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
CAP = 800   # per-role body cap (keeps the whole doc uploadable in one shot)

def get(url, t=25):
    r = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(r, timeout=t) as f:
        return f.read().decode("utf-8", "replace")

def strip(s):
    s = html.unescape(s)                      # unescape FIRST (Greenhouse escapes its HTML)
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?i)<li[^>]*>", "- ", s); s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|ul|ol)>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s); s = html.unescape(s).replace("&nbsp;", " ")
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s).replace("**", "").replace("`", "")  # de-markdown
    s = re.sub(r"[ \t]+\n", "\n", s); s = re.sub(r"\n[ \t]+", "\n", s); s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

STRONG = ["Description & Requirements", "About the Role", "About the role", "\nThe Role\n",
          "\nThe role\n", "Role Responsibilities", "\nResponsibilities\n", "What You'll Do",
          "What you'll be doing", "What you'll be working on", "Your future role", "Purpose of Role",
          "Key responsibilities", "Minimum qualifications", "In this role, you", "\nThe Team\n",
          "About the Team", "About the team", "\nThe mission", "About us\n"]
END = ["Why should you apply", "What's in it for you", "Our benefits", "Our global benefits",
       "Benefits\n", "We are an equal", "Equal Opportunity", "Equal opportunity", "QRT is an equal",
       "Important notice for candidates", "Inclusion, Work-Life", "Compensation, Benefits",
       "Get what you need to succeed", "About OpenAI\n", "Accommodations", "Learn about life at Spotify",
       "Apply Now\n", "Job Application Checklist", "Still Exploring", "Similar jobs", "Quick clicks",
       "The Trade Desk does not accept", "Discover our values", "P72 Careers", "\nHow we hire\n",
       "Share this", "Amazon is an equal"]

def clean(body, cap=CAP):
    if not body or body.startswith("[fetch") or body.startswith("[no "):
        return body or "[no description captured]"
    cand = [body.find(m) for m in STRONG]; cand = [i for i in cand if i != -1]
    if cand: body = body[min(cand):].lstrip("\n")
    e = len(body)
    for m in END:
        i = body.find(m)
        if i != -1 and i >= 200 and i < e: e = i
    body = body[:e].rstrip()
    if len(body) > cap: body = body[:cap].rstrip() + " [trimmed; see Apply link for full JD]"
    return body.strip()

# pretty display names for greenhouse tokens etc.
PRETTY = {"deepmind": "Google DeepMind", "monzo": "Monzo", "mangroup": "Man Group",
          "gocardless": "GoCardless", "dunnhumby": "dunnhumby", "wayve": "Wayve",
          "datadog": "Datadog", "thetradedesk": "The Trade Desk", "openai": "OpenAI",
          "quberesearchandtechnologies": "Qube RT", "palantir": "Palantir"}

# ---------------- read active roles ----------------
rows = list(csv.reader(open("/tmp/ldn_ds_active.csv")))
roles = []  # (company, role, level, location, url)
for r in rows[1:]:
    if len(r) < 6 or r[5] != "Active": continue
    roles.append((PRETTY.get(r[0], r[0]), r[1], r[2], r[3], r[4]))

# ---------------- Amazon JD map (search.json) ----------------
amap = {}
for q in ["data scientist", "applied scientist"]:
    try:
        d = json.loads(get(f"https://www.amazon.jobs/en/search.json?base_query={q.replace(' ','%20')}"
                           f"&loc_query=London&country=GBR&result_limit=100"))
        for job in d.get("jobs", []):
            m = re.search(r"/jobs/(\d+)", job.get("job_path", ""))
            if m: amap[m.group(1)] = job
    except Exception as e:
        print("[amazon feed]", type(e).__name__, file=sys.stderr)

def gh_board_id(url):
    m = re.search(r"greenhouse\.io/([^/]+)/jobs/(\d+)", url)
    if m: return m.group(1), m.group(2)
    m = re.search(r"gh_jid=(\d+)", url)
    if m:
        host = urlparse(url).netloc
        board = {"www.dunnhumby.com": "dunnhumby", "wayve.firststage.co": "wayve",
                 "careers.datadoghq.com": "datadog"}.get(host)
        return board, m.group(1)
    return None, None

# ---------------- fetch bodies ----------------
results = {}   # url -> body
spa = []       # (url,) needing browser
ashby_cache = {}
for comp, role, lvl, loc, url in roles:
    try:
        if "greenhouse.io" in url or "gh_jid=" in url:
            board, jid = gh_board_id(url)
            if board and jid:
                d = json.loads(get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{jid}"))
                results[url] = clean(strip(d.get("content", ""))); continue
        if "ashbyhq.com" in url:
            org = urlparse(url).path.strip("/").split("/")[0]
            if org not in ashby_cache:
                ashby_cache[org] = json.loads(get(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true")).get("jobs", [])
            jid = url.rstrip("/").split("/")[-1]
            body = ""
            for j in ashby_cache[org]:
                if j.get("id") == jid: body = strip(j.get("descriptionHtml") or ""); break
            results[url] = clean(body) or "[no description captured]"; continue
        if "amazon.jobs" in url:
            m = re.search(r"/jobs/(\d+)", url); job = amap.get(m.group(1)) if m else None
            if job:
                desc = clean(strip(job.get("description", "")), 650)
                bq = strip(job.get("basic_qualifications", "")); pq = strip(job.get("preferred_qualifications", ""))
                for mk in ["Amazon is an equal", "Our inclusive culture", "Protecting your privacy"]:
                    i = pq.find(mk)
                    if i != -1: pq = pq[:i].rstrip()
                results[url] = (desc + "\n\nBasic Qualifications\n" + bq[:550] +
                                "\n\nPreferred Qualifications\n" + pq[:450]).strip()
            else:
                results[url] = "[not in amazon.jobs feed — see Apply link]"
            continue
        spa.append(url)
    except Exception as e:
        results[url] = f"[fetch error: {type(e).__name__}]"

# ---------------- SPA bodies via Playwright ----------------
if spa:
    try:
        from playwright.sync_api import sync_playwright
        SEL = {"www.lifeatspotify.com": "main, .job-details, article",
               "bloomberg.avature.net": "#content, main, .jobDescription, .description",
               "faculty.ai": "main, article, .job", "careers.point72.com": "main, #content, article",
               "careers.tiktok.com": "main, .position-detail, article, #root",
               "www.gresearch.com": "main, article, .vacancy",
               "jobs.careers.microsoft.com": "main, div[role='main']",
               "www.google.com": "div.KwJkGe, main, c-wiz"}
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
            ctx = b.new_context(ignore_https_errors=True, locale="en-GB", user_agent=UA["User-Agent"])
            pg = ctx.new_page()
            for url in spa:
                try:
                    pg.goto(url, wait_until="domcontentloaded", timeout=45000)
                    try: pg.wait_for_load_state("networkidle", timeout=8000)
                    except Exception: pass
                    pg.wait_for_timeout(2500)
                    sel = SEL.get(urlparse(url).netloc, "main, article")
                    body = ""
                    el = pg.query_selector(sel.split(",")[0].strip())
                    if el and len(el.inner_text().strip()) > 250: body = strip(el.inner_html())
                    if not body: body = strip(pg.content())
                    results[url] = clean(body)
                except Exception as e:
                    results[url] = f"[fetch error: {type(e).__name__}]"
            b.close()
    except ImportError:
        for url in spa: results[url] = "[Playwright not installed — see Apply link]"

# ---------------- write plain text ----------------
order = ["OpenAI", "Google DeepMind", "Google", "Microsoft", "Spotify", "Monzo", "Man Group",
         "Point72", "Qube RT", "G-Research", "Bloomberg", "Amazon", "The Trade Desk", "TikTok",
         "Datadog", "GoCardless", "dunnhumby", "Faculty AI", "Wayve"]
roles.sort(key=lambda r: (order.index(r[0]) if r[0] in order else 99,
                          0 if r[2] == "Senior+" else 1, r[1]))
reg = sum(1 for r in roles if r[2] == "Regular/Mid")
out = ["LONDON DS — ACTIVE ROLE JOB DESCRIPTIONS & REQUIREMENTS",
       f"{len(roles)} active London (or London-eligible) Data Science roles across "
       f"{len({r[0] for r in roles})} companies ({reg} regular/mid, {len(roles)-reg} senior+).",
       "Sources: Greenhouse / Ashby / Amazon official job APIs; other sites via headless browser.",
       "Each entry is trimmed to role, responsibilities and requirements — open the Apply link for the full posting."]
cur = None
for comp, role, lvl, loc, url in roles:
    if comp != cur:
        out += ["", "", "=" * 60, "   " + comp.upper(), "=" * 60]; cur = comp
    out += ["", "-" * 60, role, f"Level: {lvl}    Location: {loc}", f"Apply: {url}", "-" * 60, ""]
    out.append(results.get(url, "[no description captured]"))
text = "\n".join(out)
open("/tmp/ldn_ds_jds.txt", "w").write(text)
print(f"WROTE /tmp/ldn_ds_jds.txt : {len(roles)} roles, {len(text.encode())} bytes, "
      f"{len(re.findall(r'[#*`]', text))} stray md chars (C#/footnote ok).")
print("NEXT: assistant reads the file and uploads it to Drive folder "
      "1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI as text/plain (Google Doc). See SKILL.md.")
