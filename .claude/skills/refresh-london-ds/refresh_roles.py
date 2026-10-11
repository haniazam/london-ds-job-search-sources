#!/usr/bin/env python3
"""Refresh the London DS active-roles list -> /tmp/ldn_ds_active.csv

Enumerates company ATS boards (Greenhouse/Lever/Ashby/Amazon/Workday via urllib),
Google careers (server-rendered results HTML via urllib — no browser), and the
JS career sites (Spotify/TikTok/Microsoft/Point72/Bloomberg/Faculty/Revolut/
Citadel/G-Research via Playwright). Classifies each role's level,
keeps only active London (or London-eligible) Data-Science-family roles with a
unique job-post URL, and writes a combined CSV: active rows first, then companies
with no active London DS role.

Run in a Full-network session. For the JS sites: pip install playwright &&
python -m playwright install chromium  (script still works for the ATS backbone
if Playwright is missing — it just skips the browser companies).

See SKILL.md for endpoints, gotchas and the upload step (assistant action).
"""
import csv, html, json, os, re, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from role_taxonomy import classify as role_type, COLLECT as DS   # core-role classifier (see role_taxonomy.py)

# Board registry: every ATS token lives in boards.json next to this script (see SKILL.md
# "Discovery" for how tokens are harvested). Edit the JSON, not the lists below.
REG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "boards.json")))

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
LON = re.compile(r"london|canary wharf|united kingdom|\buk\b|england", re.I)   # Workday sites label offices (Barclays: "Canary Wharf, 1 Churchill Place")
SENIOR = re.compile(r"senior|staff|lead|principal|head|director|manager|\bsr\.?\b|distinguished|vice president|\bvp\b|\bavp\b|executive director", re.I)
EXCLUDE = re.compile(r"intern|graduate|apprentice|placement|industrial year|working student|fixed.?term|\bFTC\b|\bcontract\b|fractional|part.?time", re.I)

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
GREENHOUSE = REG["greenhouse"]
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
for org in REG["ashby"]:
    try:
        d = json.loads(get(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true"))
        for j in d.get("jobs", []):
            t = j.get("title", ""); loc = j.get("location", "")
            sec = [x.get("location", "") for x in j.get("secondaryLocations", [])]
            if DS.search(t) and (LON.search(loc) or any(LON.search(x) for x in sec)) and not EXCLUDE.search(t):
                shown = loc if LON.search(loc) else f"{loc} (+London)"
                active.append((org, t, level(t), shown, j.get("jobUrl")))
    except Exception as e:
        print(f"[ashby] {org}: {type(e).__name__}", file=sys.stderr)

# ---------------- Lever ----------------
for org in REG["lever"]:
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
WORKDAY = REG["workday"]
for name, url in WORKDAY.items():
    try:
        d = json.loads(get(url, post={"appliedFacets": {}, "limit": 20, "offset": 0,
                                      "searchText": "data scientist London"}))
        for j in d.get("jobPostings", []):
            t = j.get("title", ""); loc = j.get("locationsText", "")
            if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
                host = url.split("/wday/")[0]; site = url.rstrip("/").rsplit("/", 2)[-2]
                active.append((name, t, level(t), loc, f"{host}/en-US/{site}{j.get('externalPath', '')}"))
    except Exception as e:
        print(f"[workday] {name}: {type(e).__name__}", file=sys.stderr)

# ---------------- Workable (widget API; rate-limits hard -> pace calls) ----------------
UNVERIFIED = {}   # platform -> [board tokens] the run could not read (rate-limited / gated); the Sheet carries their rows forward as unverified
wk_strikes = 0    # consecutive accounts lost to 429 -> after 2, one un-slept attempt each (bounds the pass at ~2 min, not ~40)
for acct in REG.get("workable", []):
    tries = 1 if wk_strikes >= 2 else 3
    for attempt in range(tries):
        try:
            d = json.loads(get(f"https://apply.workable.com/api/v1/widget/accounts/{acct}?details=false")); break
        except Exception as e:
            d = None
            if "429" in str(e):
                if attempt < tries - 1: time.sleep(15 * (attempt + 1))
                continue
            print(f"[workable] {acct}: {type(e).__name__}", file=sys.stderr); break
    if not d:
        wk_strikes += 1
        print(f"[workable] {acct}: rate-limited (429) — rows carried forward as unverified", file=sys.stderr)
        UNVERIFIED.setdefault("workable", []).append(acct); continue
    wk_strikes = 0
    hits = 0
    for j in d.get("jobs", []):
        t = j.get("title", ""); loc = f"{j.get('city','')}, {j.get('country','')} {'remote' if j.get('remote') else ''}"
        if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
            hits += 1; active.append((acct, t, level(t), loc.strip(), j.get("url") or j.get("shortlink")))
    print(f"[workable] {acct}: {len(d.get('jobs', []))} jobs, {hits} London DS", file=sys.stderr)
    time.sleep(6)

# ---------------- SmartRecruiters (public postings API; some companies gate it -> 0) ----------------
for cid in REG.get("smartrecruiters", []):
    try:
        d = json.loads(get(f"https://api.smartrecruiters.com/v1/companies/{cid}/postings?limit=100"))
    except Exception as e:
        print(f"[smartrecruiters] {cid}: {type(e).__name__}", file=sys.stderr); continue
    hits = 0
    for j in d.get("content", []):
        t = j.get("name", ""); L = j.get("location") or {}
        loc = f"{L.get('city','')}, {L.get('country','')} {'remote' if L.get('remote') else ''}"
        if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
            hits += 1; active.append((cid, t, level(t), loc.strip(), f"https://jobs.smartrecruiters.com/{cid}/{j.get('id')}"))
    print(f"[smartrecruiters] {cid}: {len(d.get('content', []))} postings, {hits} London DS", file=sys.stderr)

# ---------------- Pinpoint (postings.json) ----------------
for acct in REG.get("pinpoint", []):
    try:
        d = json.loads(get(f"https://{acct}.pinpointhq.com/postings.json"))
    except Exception as e:
        print(f"[pinpoint] {acct}: {type(e).__name__}", file=sys.stderr); continue
    items = d.get("data", d) if isinstance(d, dict) else d; hits = 0
    for j in items:
        t = j.get("title", ""); loc = json.dumps(j.get("location", "")) + " " + json.dumps(j.get("workplace_type", ""))
        if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
            hits += 1; active.append((acct, t, level(t), "London", j.get("url") or f"https://{acct}.pinpointhq.com/postings/{j.get('id')}"))
    print(f"[pinpoint] {acct}: {len(items)} postings, {hits} London DS", file=sys.stderr)

# ---------------- Recruitee (offers API) ----------------
for co in REG.get("recruitee", []):
    try:
        d = json.loads(get(f"https://{co}.recruitee.com/api/offers/"))
    except Exception as e:
        print(f"[recruitee] {co}: {type(e).__name__}", file=sys.stderr); continue
    hits = 0
    for j in d.get("offers", []):
        t = j.get("title", ""); loc = f"{j.get('city','')} {j.get('country','')} {j.get('location','')}"
        if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
            hits += 1; active.append((co, t, level(t), loc.strip(), j.get("careers_url")))
    print(f"[recruitee] {co}: {len(d.get('offers', []))} offers, {hits} London DS", file=sys.stderr)

# ---------------- Teamtailor (public JSON Feed at /jobs.json; locations in the schema.org jobposting) ----------------
for co in REG.get("teamtailor", []):
    try:
        d = json.loads(get(f"https://{co}.teamtailor.com/jobs.json"))
    except Exception as e:
        print(f"[teamtailor] {co}: {type(e).__name__}", file=sys.stderr); continue
    hits = 0
    for j in d.get("items", []):
        t = j.get("title", "")
        places = (j.get("_jobposting") or {}).get("jobLocation") or []
        loc = ", ".join(sorted({(pl.get("address") or {}).get("addressLocality", "") for pl in places} - {""})) or "Remote"
        if DS.search(t) and LON.search(loc) and not EXCLUDE.search(t):
            hits += 1; active.append((co, t, level(t), loc, j.get("url")))
    print(f"[teamtailor] {co}: {len(d.get('items', []))} jobs, {hits} London DS", file=sys.stderr)

# ---------------- Oracle HCM Cloud (public recruitingCEJobRequisitions finder; JPMorgan, BNY) ----------------
NEAR = re.compile(r"london|remote", re.I)          # these sites list every UK office; "United Kingdom" alone is not London-eligible
for name, site in REG.get("oraclehcm", {}).items():
    if name.startswith("_"): continue
    host, num = site["host"], site.get("site", "CX_1001"); hits = 0; total = 0; offset = 0
    try:
        while True:
            q = urllib.parse.quote(f'findReqs;siteNumber={num},keyword="data scientist",limit=100,offset={offset},sortBy=POSTING_DATES_DESC')
            d = json.loads(get(f"https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.secondaryLocations&finder={q}", 30))
            it = (d.get("items") or [{}])[0]; reqs = it.get("requisitionList", []); total = it.get("TotalJobsCount", len(reqs))
            for j in reqs:
                t = j.get("Title", ""); loc = "; ".join([j.get("PrimaryLocation", "")] + [x.get("Name", "") for x in j.get("secondaryLocations", []) if isinstance(x, dict)])
                if DS.search(t) and NEAR.search(loc) and not EXCLUDE.search(t):
                    hits += 1; active.append((name, t, level(t), loc.title(), f"https://{host}/hcmUI/CandidateExperience/en/sites/{num}/job/{j.get('Id')}"))
            offset += len(reqs)
            if not reqs or offset >= total or offset >= 500: break
        print(f"[oraclehcm] {name}: {total} requisitions, {hits} London DS", file=sys.stderr)
    except Exception as e:
        print(f"[oraclehcm] {name}: {type(e).__name__}", file=sys.stderr)

# ---------------- SAP SuccessFactors career sites (server-rendered /search/ page; Fitch) ----------------
for name, base in REG.get("successfactors", {}).items():
    if name.startswith("_"): continue
    try:
        page = get(f"{base.rstrip('/')}/search/?q=data+scientist", 30)
    except Exception as e:
        print(f"[successfactors] {name}: {type(e).__name__}", file=sys.stderr); continue
    rows = re.findall(r'<a class="jobTitle-link" href="([^"]+)">([^<]+)</a>.*?<span class="jobLocation">\s*([^<]+?)\s*</span>', page, re.S); hits = 0
    for path, t, loc in rows:
        t = html.unescape(t).strip(); loc = html.unescape(loc).strip()
        if DS.search(t) and NEAR.search(loc) and not EXCLUDE.search(t):
            hits += 1; active.append((name, t, level(t), loc, base.rstrip("/") + html.unescape(path)))
    print(f"[successfactors] {name}: {len(rows)} results, {hits} London DS", file=sys.stderr)

# ---------------- Apple (jobs.apple.com search API, GBR filter) ----------------
if "apple" in REG:
    try:
        hits = 0; pg = 1; total = 0
        while True:
            d = json.loads(get("https://jobs.apple.com/api/v1/search", 30, post={"query": REG["apple"].get("query", "data scientist"), "filters": {"locations": ["postLocation-GBR"]}, "page": pg, "locale": "en-gb",
                                                                              "sort": "newest", "format": {"longDate": "MMMM D, YYYY", "mediumDate": "MMM D, YYYY"}})).get("res", {})
            rs = d.get("searchResults", []); total = d.get("totalRecords", 0)
            for j in rs:
                t = j.get("postingTitle", ""); loc = ", ".join(l.get("name", "") for l in j.get("locations", []))
                if DS.search(t) and NEAR.search(loc) and not EXCLUDE.search(t):
                    hits += 1; active.append(("Apple", t, level(t), loc, f"https://jobs.apple.com/en-gb/details/{j.get('positionId')}/{j.get('transformedPostingTitle')}"))
            if len(rs) < 20 or pg >= 5: break
            pg += 1
        print(f"[apple] {total} GBR results, {hits} London DS", file=sys.stderr)
    except Exception as e:
        print(f"[apple] {type(e).__name__}", file=sys.stderr)

# ---------------- JS sites via Playwright (optional) ----------------
try:
    from playwright.sync_api import sync_playwright
    HAVE_PW = True
except ImportError:
    HAVE_PW = False
    print("[spa] Playwright not installed — skipping JS sites. "
          "Run: pip install playwright && python -m playwright install chromium", file=sys.stderr)
    # the Sheet must carry these sites' rows forward as unverified, never close them (build_sheet_rows.py reads this)
    UNVERIFIED["spa"] = ["www.lifeatspotify", "www.gresearch", "bloomberg.avature", "jobs.careers.microsoft", "careers.point72", "careers.tiktok"]

def spa_refresh():
    out = []
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        except Exception:
            # pip's playwright may want a newer Chromium than the pre-installed one
            # (PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers); fall back to that binary
            # instead of failing the whole JS-site pass.
            import glob
            exe = (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") or [None])[0]
            if not exe: raise
            b = p.chromium.launch(headless=True, executable_path=exe, args=["--ignore-certificate-errors"])
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

# ---------------- Google careers (server-rendered HTML; no Playwright needed) ----------------
# Google's careers SPA hydrates from server HTML that embeds each posting as
# `jobs/results/<id>-<slug>`. We pull DS-titled London posts straight from that
# HTML with urllib — no browser — which closes a long-standing blind spot where
# the Playwright path claimed Google but never actually fetched it (so live DS
# roles like "Staff Product Data Scientist, Google Shopping" were silently missed).
# DeepMind is already covered via its Greenhouse board (GREENHOUSE token "deepmind").
def google_refresh():
    out, seen = [], set()
    base = "https://www.google.com/about/careers/applications/jobs/results/"
    try:
        html = get(base + "?location=London%2C%20UK&q=data%20scientist", t=25)
    except Exception as e:
        print("[google]", type(e).__name__, file=sys.stderr); return out
    for m in re.finditer(r"jobs/results/(\d+)-([a-z0-9-]+)", html):
        jid, slug = m.group(1), m.group(2)
        if jid in seen: continue
        if not re.search(r"data-scientist|data-science|quantitative-analyst", slug): continue
        if re.search(r"research-(scientist|engineer)|software-engineer", slug): continue
        if EXCLUDE.search(slug): continue
        seen.add(jid)
        title = re.sub(r"\s+", " ", slug.replace("-", " ")).strip().title()
        out.append(("Google", title, level(title), "London (verify)", base + jid + "-" + slug))
    print(f"[google] {len(seen)} London DS post(s)", file=sys.stderr)
    return out

try:
    active += google_refresh()
except Exception as e:
    print("[google] failed:", type(e).__name__, file=sys.stderr)

# ---------------- employer-site posts found by discover.py (verified by GET + <title>) ----------------
DISC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "discovered_posts.json")
if os.path.exists(DISC):
    seen_urls = {a[4].split("?")[0] for a in active}
    hits = 0
    for p in json.load(open(DISC)):
        u = p["url"]
        if u.split("?")[0] in seen_urls or EXCLUDE.search(p["title"]): continue   # same scope rule as the API boards
        if "jobs.workable.com/view" in u:                       # Workable's own feed: published state is the proof
            active.append((p["company"], p["title"], level(p["title"]), p["location"], u)); hits += 1; continue
        try:
            page = get(u, 30)
        except Exception as e:
            print(f"[discovered] {p['company']}: {type(e).__name__}", file=sys.stderr); continue
        tm = re.search(r"<title>(.*?)</title>", page, re.S); title = (tm.group(1) if tm else "").lower()
        if re.search(r"data scien", title) and not re.search(r"no longer|not found|closed|expired|jobs search|\d,\d{3}\+ ", title):
            active.append((p["company"], p["title"], level(p["title"]), p["location"], u)); hits += 1
    print(f"[discovered] {hits} employer-site posts verified live", file=sys.stderr)

# ---------------- hand-added posts on sites without an API (data/manual_posts.json), verified each run ----------------
try:
    from manual_posts import verified_rows
    for r in verified_rows():
        if EXCLUDE.search(r["Role"]): continue
        if r["Apply URL (unique active post)"].split("?")[0] not in {a[4].split("?")[0] for a in active}:
            active.append((r["Company"], r["Role"], r["Level"], r["Location"], r["Apply URL (unique active post)"]))
except Exception as e:
    print(f"[manual] skipped: {type(e).__name__} {e}", file=sys.stderr)

# ---------------- companies known to have NO active London DS (documented) ----------------
NO_ROLE = [
    ("Wayve", "Moved to Ashby (token wayve) — 0 London DS on the board this run"),
    ("Point72", "London DS post removed; current DS roles are HK/Singapore/NY only"),
    ("OpenAI", "0 London DS on Ashby board (both prior posts closed) — re-check"),
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

# ---------------- scope: a specific non-London UK city on its own is out ----------------
from refresh_roles_scope import london_ok
active = [a for a in active if london_ok(a[3])]
# ---------------- write CSV ----------------
json.dump(UNVERIFIED, open("/tmp/ldn_ds_unverified.json", "w"))
# Proper display names (per CLAUDE.md) instead of raw ATS tokens.
PRETTY = {"openai": "OpenAI", "deepmind": "Google DeepMind", "monzo": "Monzo",
          "mangroup": "Man Group", "gocardless": "GoCardless", "dunnhumby": "dunnhumby",
          "wayve": "Wayve", "datadog": "Datadog", "thetradedesk": "The Trade Desk",
          "quberesearchandtechnologies": "Qube RT", "palantir": "Palantir",
          "anthropic": "Anthropic", "hubspotjobs": "HubSpot", "ocadogroup": "Ocado",
          "coreweave": "CoreWeave", "isomorphiclabs": "Isomorphic Labs", "wise": "Wise",
          "lendable": "Lendable", "multiverse": "Multiverse"}
PRETTY.update(REG.get("display_names", {}))
RECRUITERS = set(REG.get("recruiters_exclude", []))
def clean_title(t):
    """Normalise ATS titles: drop office/location parentheticals and repeated comma segments."""
    t = re.sub(r"\s*\((?=[^)]*(?:office|location|based|hybrid|remote))[^)]*\)", "", t, flags=re.I)
    parts, seen = [], set()
    for seg in [x.strip() for x in t.split(",")]:
        if seg and seg.lower() not in seen: seen.add(seg.lower()); parts.append(seg)
    return ", ".join(parts).strip(" -–")
active = [(PRETTY.get(c, c), clean_title(role), lv, loc, url) for (c, role, lv, loc, url) in active
          if c not in RECRUITERS and url]
order = ["OpenAI", "Google DeepMind", "Google", "Microsoft", "Spotify", "Monzo",
         "Man Group", "Point72", "Qube RT", "G-Research", "Bloomberg", "Amazon",
         "The Trade Desk", "TikTok", "Datadog", "GoCardless", "dunnhumby", "Faculty AI",
         "Wise", "Ocado", "Lendable", "CoreWeave", "Isomorphic Labs", "Multiverse"]
def okey(r):
    c = r[0]
    return (order.index(c) if c in order else 99, 0 if r[2] == "Senior+" else 1, r[1])
active.sort(key=okey)
reg = sum(1 for r in active if r[2] == "Regular/Mid")
std = sum(1 for r in active if role_type(r[1]) == "Standard DS")
with open("/tmp/ldn_ds_active.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Company", "Role", "Role Type", "Level", "Location", "Apply URL (unique active post)", "Status", "Notes"])
    for c, role, lv, loc, url in active:
        w.writerow([c, role, role_type(role), lv, loc, url, "Active", ""])
    w.writerow([""] * 8)
    w.writerow(["— COMPANIES WITH NO ACTIVE LONDON DS ROLE —"] + [""] * 7)
    for c, reason in norole:
        w.writerow([c, "—", "—", "—", "—", "", "No active London DS role", reason])
print(f"\nWROTE /tmp/ldn_ds_active.csv : {len(active)} active roles ({std} Standard DS) "
      f"({reg} regular/mid, {len(active)-reg} senior+) across "
      f"{len({a[0] for a in active})} companies; {len(norole)} no-role companies.")
print("NEXT: build_jd_doc.py, then assistant uploads both files to Drive folder "
      "1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI (see SKILL.md).")
