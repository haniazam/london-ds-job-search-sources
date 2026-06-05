#!/usr/bin/env python3
"""Refresh the London DS active-roles list -> /tmp/ldn_ds_active.csv

Enumerates company ATS boards (Greenhouse/Lever/Ashby/Amazon/Workday via urllib)
and the JS career sites (Spotify/TikTok/Microsoft/Point72/Google/Bloomberg/
Faculty/Revolut/Citadel/G-Research via Playwright). Classifies each role's level,
keeps only active London (or London-eligible) Data-Science-family roles with a
unique job-post URL, and writes a combined CSV: active rows first, then companies
with no active London DS role.

Run in a Full-network session. For the JS sites: pip install playwright &&
python -m playwright install chromium  (script still works for the ATS backbone
if Playwright is missing — it just skips the browser companies).

See SKILL.md for endpoints, gotchas and the upload step (assistant action).
"""
import csv, json, re, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
DS = re.compile(r"data scien|applied scien|data analyst|decision scien|machine learning|"
                r"\bml scien|research scien|economist|\bquant", re.I)
LON = re.compile(r"london|united kingdom|\buk\b|england", re.I)
SENIOR = re.compile(r"senior|staff|lead|principal|head|director|manager|\bsr\.?\b|distinguished", re.I)
EXCLUDE = re.compile(r"intern|graduate|apprentice|placement|industrial year|working student", re.I)

def level(t): return "Senior+" if SENIOR.search(t) else "Regular/Mid"

def get(url, t=20, post=None):
    data = json.dumps(post).encode() if post is not None else None
    hdr = dict(UA)
    if post is not None: hdr["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, headers=hdr)
    with urllib.request.urlopen(r, timeout=t) as f:
        return f.read().decode("utf-8", "replace")

active = []   # (company, role, level, location, url)
norole = []   # (company, reason)

# ---------------- Greenhouse ----------------
GREENHOUSE = ["deepmind", "monzo", "mangroup", "gocardless", "dunnhumby",
              "quberesearchandtechnologies", "wayve", "datadog", "thetradedesk",
              # big-tech boards that historically return 0 London DS (catch new):
              "databricks", "cloudflare", "braze", "amplitude", "figma",
              "mongodb", "elasticsearch", "unity3d", "catonetworks", "polyai",
              "truelayer", "anthropic", "hubspotjobs", "stripe"]
for tok in GREENHOUSE:
    try:
        d = json.loads(get(f"https://boards-api.greenhouse.io/v1/boards/{tok}/jobs?content=false"))
    except Exception as e:
        print(f"[gh] {tok}: {type(e).__name__}", file=sys.stderr); continue
    hits = []
    for j in d.get("jobs", []):
        t = j.get("title", ""); loc = (j.get("location") or {}).get("name", "")
        if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
            hits.append((t, loc, j.get("absolute_url")))
    if hits:
        for t, loc, u in hits: active.append((tok, t, level(t), loc, u))
    print(f"[gh] {tok}: {len(d.get('jobs',[]))} jobs, {len(hits)} London DS", file=sys.stderr)

# ---------------- Ashby ----------------
for org in ["openai"]:
    try:
        d = json.loads(get(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true"))
        for j in d.get("jobs", []):
            t = j.get("title", ""); loc = j.get("location", "")
            if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
                active.append((org, t, level(t), loc, j.get("jobUrl")))
    except Exception as e:
        print(f"[ashby] {org}: {type(e).__name__}", file=sys.stderr)

# ---------------- Lever ----------------
for org in ["palantir"]:
    try:
        d = json.loads(get(f"https://api.lever.co/v0/postings/{org}?mode=json"))
        for j in d:
            t = j.get("text", ""); loc = (j.get("categories") or {}).get("location", "") or ""
            if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
                active.append((org, t, level(t), loc, j.get("hostedUrl")))
    except Exception as e:
        print(f"[lever] {org}: {type(e).__name__}", file=sys.stderr)

# ---------------- Amazon ----------------
seen = set()
for q in ["data scientist", "applied scientist"]:
    try:
        d = json.loads(get(f"https://www.amazon.jobs/en/search.json?base_query={q.replace(' ','%20')}"
                           f"&loc_query=London&country=GBR&result_limit=100"))
        for job in d.get("jobs", []):
            t = job.get("title", ""); loc = job.get("normalized_location", "")
            if not (re.search(r"data scientist|applied scientist", t, re.I) and "london" in loc.lower()):
                continue
            if EXCLUDE.search(t) or job.get("is_intern"): continue
            m = re.search(r"/jobs/(\d+)", job.get("job_path", ""))
            jid = m.group(1) if m else t
            if jid in seen: continue
            seen.add(jid)
            active.append(("Amazon", t, level(t), "London", f"https://www.amazon.jobs{job.get('job_path')}"))
    except Exception as e:
        print(f"[amazon] {q}: {type(e).__name__}", file=sys.stderr)

# ---------------- Workday CXS (mostly 0 London DS; re-check) ----------------
WORKDAY = {
    "NVIDIA": "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs",
    "Salesforce": "https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/External_Career_Site/jobs",
    "Mastercard": "https://mastercard.wd1.myworkdayjobs.com/wday/cxs/mastercard/CorporateCareers/jobs",
}
for name, url in WORKDAY.items():
    try:
        d = json.loads(get(url, post={"appliedFacets": {}, "limit": 20, "offset": 0,
                                      "searchText": "data scientist London"}))
        for j in d.get("jobPostings", []):
            t = j.get("title", ""); loc = j.get("locationsText", "")
            if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
                active.append((name, t, level(t), loc, "(Workday — see careers site)"))
    except Exception as e:
        print(f"[workday] {name}: {type(e).__name__}", file=sys.stderr)

# ---------------- JS sites via Playwright (optional) ----------------
try:
    from playwright.sync_api import sync_playwright
    HAVE_PW = True
except ImportError:
    HAVE_PW = False
    print("[spa] Playwright not installed — skipping JS sites. "
          "Run: pip install playwright && python -m playwright install chromium", file=sys.stderr)

def spa_refresh():
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        ctx = b.new_context(ignore_https_errors=True, locale="en-GB", user_agent=UA["User-Agent"])
        pg = ctx.new_page()
        def goto(url, wait=2500):
            pg.goto(url, wait_until="domcontentloaded", timeout=45000)
            try: pg.wait_for_load_state("networkidle", timeout=8000)
            except Exception: pass
            pg.wait_for_timeout(wait)

        # Spotify
        try:
            caps = []
            pg.on("response", lambda r: caps.append(r.text()) if "animal/v1/job/search" in r.url else None)
            goto("https://www.lifeatspotify.com/jobs?q=data%20scientist&l=london", 3000)
            for body in caps:
                try: d = json.loads(body)
                except Exception: continue
                def walk(o):
                    if isinstance(o, dict):
                        if o.get("sub_category", {}).get("slug") == "data-science" and "id" in o:
                            locs = [l.get("slug") for l in o.get("locations", [])]
                            if "london" in locs and not EXCLUDE.search(o.get("text", "")):
                                t = re.sub(r"&amp;", "&", o["text"])
                                out.append(("Spotify", t, level(t), "London",
                                            f"https://www.lifeatspotify.com/jobs/{o['id']}"))
                        for v in o.values(): walk(v)
                    elif isinstance(o, list):
                        for v in o: walk(v)
                walk(d)
        except Exception as e: print("[spa] spotify", type(e).__name__, file=sys.stderr)

        # G-Research (individual vacancy pages)
        try:
            goto("https://www.gresearch.com/vacancies/", 3000)
            hrefs = set()
            for a in pg.query_selector_all("a[href*='/vacancies/']"):
                h = a.get_attribute("href") or ""
                m = re.search(r"/vacancies/([a-z0-9][a-z0-9\-]+)/", h)
                if m and m.group(1) not in ("page",):
                    slug = m.group(1)
                    if re.search(r"data-scien|machine-learning|nlp|natural-language|decision", slug):
                        out.append(("G-Research", slug.replace("-", " ").title(), "Regular/Mid",
                                    "London", f"https://www.gresearch.com{h if h.startswith('/') else '/vacancies/'+slug+'/'}"))
        except Exception as e: print("[spa] gresearch", type(e).__name__, file=sys.stderr)

        # Bloomberg avature
        try:
            goto("https://bloomberg.avature.net/careers/SearchJobs/data%20scientist", 3000)
            for a in pg.query_selector_all("a[href*='/careers/JobDetail/']"):
                h = a.get_attribute("href") or ""; t = (a.inner_text() or "").strip()
                if re.search(r"data scientist", t, re.I) and "london" in (pg.content().lower()):
                    if "london" in t.lower() or "Economics" in t:
                        url = h if h.startswith("http") else "https://bloomberg.avature.net" + h
                        out.append(("Bloomberg", t[:60], level(t), "London (verify)", url))
        except Exception as e: print("[spa] bloomberg", type(e).__name__, file=sys.stderr)

        # Microsoft Eightfold (in-browser)
        try:
            goto("https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=data%20scientist&num=50&start=0", 2000)
            d = json.loads(pg.inner_text("body"))
            def walk(o):
                if isinstance(o, dict):
                    t = o.get("name") or o.get("title")
                    if isinstance(t, str) and DS.search(t):
                        loc = str(o.get("location") or o.get("locations") or "")
                        idv = o.get("display_job_id") or o.get("id") or ""
                        if LON.search(loc) and not EXCLUDE.search(t):
                            out.append(("Microsoft", t, level(t), "London",
                                        f"https://jobs.careers.microsoft.com/global/en/job/{idv}"))
                    for v in o.values(): walk(v)
                elif isinstance(o, list):
                    for v in o: walk(v)
            walk(d)
        except Exception as e: print("[spa] microsoft", type(e).__name__, file=sys.stderr)

        # Point72 CSOD
        try:
            goto("https://careers.point72.com/?s=data+scientist", 3000)
            for _ in range(6): pg.mouse.wheel(0, 3000); pg.wait_for_timeout(400)
            seen2 = set()
            for a in pg.query_selector_all("a[href*='/CSJobDetail']"):
                h = a.get_attribute("href") or ""; t = (a.inner_text() or "").strip()[:60]
                if re.search(r"data scientist", t, re.I) and "london" in h.lower() + t.lower():
                    if h in seen2: continue
                    seen2.add(h)
                    url = h if h.startswith("http") else "https://careers.point72.com" + h
                    out.append(("Point72", t, level(t), "London (multi)", url))
        except Exception as e: print("[spa] point72", type(e).__name__, file=sys.stderr)

        # TikTok
        try:
            caps = []
            pg.on("response", lambda r: caps.append(r.text()) if ("lifeattiktok.com/api" in r.url and "job/posts" in r.url) else None)
            goto("https://lifeattiktok.com/search?keyword=data%20scientist&location=London", 4000)
            for body in caps:
                try: d = json.loads(body)
                except Exception: continue
                def walk(o):
                    if isinstance(o, dict):
                        t = o.get("title", "")
                        if isinstance(t, str) and re.search(r"data scientist", t, re.I):
                            jid = o.get("id") or o.get("job_id")
                            blob = json.dumps(o).lower()
                            if "london" in blob and not EXCLUDE.search(t):
                                out.append(("TikTok", t, level(t), "London",
                                            f"https://careers.tiktok.com/position/{jid}/detail"))
                        for v in o.values(): walk(v)
                    elif isinstance(o, list):
                        for v in o: walk(v)
                walk(d)
        except Exception as e: print("[spa] tiktok", type(e).__name__, file=sys.stderr)

        b.close()
    # dedupe
    uniq = {}
    for r in out: uniq[r[4]] = r
    return list(uniq.values())

if HAVE_PW:
    try:
        active += spa_refresh()
    except Exception as e:
        print("[spa] failed:", type(e).__name__, e, file=sys.stderr)

# ---------------- companies known to have NO active London DS (documented) ----------------
NO_ROLE = [
    ("Revolut", "DS roles exist but EU/remote, not London"),
    ("Stripe", "No London DS at any level (Greenhouse board)"),
    ("Citadel Securities", "Perennial talent-pool EOI only; no live London DS"),
    ("Mastercard", "Only a US Director DS (verify Workday)"),
    ("Apple", "No London DS in jobs.apple.com search"),
    ("ServiceNow", "No London DS (SmartRecruiters)"),
    ("Atlassian", "No London DS (careers/listings endpoint)"),
    ("Netflix", "No London DS (analyst near-miss only)"),
    ("Palantir", "No London DS (Lever)"),
    ("NVIDIA", "No London DS (Workday) — verify"),
    ("Salesforce", "No London DS (Workday) — verify"),
    ("Snap", "Contentful SPA — not queryable; check manually"),
    ("QuantumBlack (McKinsey)", "Akamai-blocked (503) — check manually"),
    ("American Express", "Eightfold ATS — not fully verified"),
    ("Confluent/Checkout.com/Quantexa/Miro/Canva", "No public ATS board found — not verified"),
]
have = {a[0].lower() for a in active}
for c, reason in NO_ROLE:
    if c.lower() not in have:
        norole.append((c, reason))

# ---------------- write CSV ----------------
order = ["openai", "deepmind", "Microsoft", "Spotify", "monzo", "mangroup",
         "Point72", "quberesearchandtechnologies", "G-Research", "Bloomberg",
         "Amazon", "thetradedesk", "TikTok", "datadog", "gocardless", "dunnhumby",
         "wayve"]
def okey(r):
    c = r[0]
    return (order.index(c) if c in order else 99, 0 if r[2] == "Senior+" else 1, r[1])
active.sort(key=okey)
reg = sum(1 for r in active if r[2] == "Regular/Mid")
with open("/tmp/ldn_ds_active.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Company", "Role", "Level", "Location", "Apply URL (unique active post)", "Status", "Notes"])
    for c, role, lv, loc, url in active:
        w.writerow([c, role, lv, loc, url, "Active", ""])
    w.writerow(["", "", "", "", "", "", ""])
    w.writerow(["— COMPANIES WITH NO ACTIVE LONDON DS ROLE —", "", "", "", "", "", ""])
    for c, reason in norole:
        w.writerow([c, "—", "—", "—", "", "No active London DS role", reason])
print(f"\nWROTE /tmp/ldn_ds_active.csv : {len(active)} active roles "
      f"({reg} regular/mid, {len(active)-reg} senior+) across "
      f"{len({a[0] for a in active})} companies; {len(norole)} no-role companies.")
print("NEXT: build_jd_doc.py, then assistant uploads both files to Drive folder "
      "1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI (see SKILL.md).")
