#!/usr/bin/env python3
"""Discovery: every refresh starts from ALL employers that fit the criteria, not a target list.

Runs BEFORE refresh_roles.py. Pulls London Data-Science postings from cross-employer sources,
classifies each title with role_taxonomy, drops agencies, and resolves every lead to the
employer's own posting:
  - a lead on a supported ATS (Greenhouse / Ashby / Lever / Workable / SmartRecruiters /
    Pinpoint / Workday / Teamtailor) yields a board TOKEN, which is appended to boards.json so
    refresh_roles.py enumerates that employer from now on (the registry grows itself);
  - a lead on an employer's own site is verified by GET + <title> and written to
    discovered_posts.json, which refresh_roles.py includes as rows;
  - anything unresolved stays in discovered_leads.json, labelled, never silently dropped.

Sources (no key needed):   LinkedIn guest job search (newest first; covers every employer that
                           posts on LinkedIn), Workable's cross-employer feed, Built In London.
Sources (free key, optional, env): ADZUNA_APP_ID + ADZUNA_APP_KEY, REED_API_KEY — UK-wide
                           aggregators that also cover non-tech employers. Set them for the
                           broadest coverage; the script runs without them.
Usage: python3 discover.py [--bootstrap]   (bootstrap = past month, deeper paging; default = past week)
"""
import json, os, re, sys, time, html, urllib.request, urllib.error, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from role_taxonomy import classify, COLLECT
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "application/json, text/html;q=0.9", "Accept-Language": "en-GB,en;q=0.9"}
BOOT = "--bootstrap" in sys.argv
def get(u, t=25, h=None, tries=3, pause=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(h or {})}), timeout=t) as f:
                return f.status, f.read().decode("utf-8", "replace"), f.geturl()
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1: time.sleep(pause * (i + 1)); continue
            return e.code, "", u
        except Exception as e:
            if i < tries - 1: time.sleep(2); continue
            return -1, type(e).__name__, u
strip = lambda s: html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
LON = re.compile(r"london|united kingdom|\buk\b|england|remote.*(uk|united kingdom)", re.I)
EXC = re.compile(r"intern|graduate|apprentice|placement|industrial year|working student", re.I)
AGENCY = re.compile(r"recruit|talent|staffing|resourcing|headhunt|search partners|selection|consultancy ltd|\bjobs\b|hiring|harnham|understanding recruitment|nicoll curtin|experis|\bhays\b|robert walters|michael page|la fosse|oliver bernard|client server|\btiro\b|xcede|datatech|intellect group|interex|sphere digital|rise technical|spectrum it|manning services|oscar technology|avanti|kimaru|jobgether|degree 6|qurious|stott and may|burns sheehan|lorien|akkodis|computer futures|huxley|real staffing|randstad|reed\b|adecco|hudson|morgan mckinley|spencer ogden|signify technology|allegis|teksystems|iopa|revolent|opus|cognitive group|montash|\bexec\b|associates|people first|the people", re.I)
TOKEN = [("greenhouse", re.compile(r"greenhouse\.io/([A-Za-z0-9_-]+)/jobs")), ("ashby", re.compile(r"ashbyhq\.com/([^/?#]+)/")),
         ("lever", re.compile(r"lever\.co/([^/?#]+)/")), ("workable", re.compile(r"apply\.workable\.com/([^/?#]+)/j/")),
         ("smartrecruiters", re.compile(r"smartrecruiters\.com/([^/?#]+)/\d")), ("pinpoint", re.compile(r"https?://([^./]+)\.pinpointhq\.com")),
         ("teamtailor", re.compile(r"https?://([^./]+)\.teamtailor\.com"))]
WD = re.compile(r"https?://([a-z0-9]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([^/?#]+)/")
reg_path = os.path.join(HERE, "boards.json"); REG = json.load(open(reg_path))
have = {k: {t.lower() for t in REG.get(k, [])} for k in ("greenhouse", "ashby", "lever", "workable", "smartrecruiters", "pinpoint", "recruitee")}
have_wd = {u.lower() for u in REG["workday"].values()}
cands = []
def add(src, co, title, loc, url, posted=""):
    if not (co and title and url): return
    cands.append({"source": src, "company": strip(co).strip(), "title": re.sub(r"\s+", " ", strip(title)).strip(), "location": strip(loc).strip(), "url": url.split("?")[0], "posted": posted})

# ---- 1. LinkedIn guest search: newest first; two title forms; paced (429s are common) ----
tpr = "r2592000" if BOOT else "r604800"; pages = 20 if BOOT else 6
for q in ("Data Scientist", "Data Science"):
    for p in range(pages):
        u = (f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={urllib.parse.quote(q)}"
             f"&location=London%2C%20England%2C%20United%20Kingdom&f_TPR={tpr}&sortBy=DD&start={p*10}")
        s, b, _ = get(u); n = 0
        if s != 200: print(f"[linkedin] {q!r} page {p}: HTTP {s}", file=sys.stderr); break
        for li in re.findall(r"<li>(.*?)</li>", b, re.S):
            m = re.search(r'href="(https://[^"]*linkedin\.com/jobs/view/[^"?]+)', li); t = re.search(r'<span class="sr-only">\s*(.*?)\s*</span>', li, re.S)
            c = re.search(r'base-search-card__subtitle">\s*(?:<a[^>]*>)?\s*(.*?)\s*(?:</a>)?\s*</h4>', li, re.S); l = re.search(r'job-search-card__location">\s*(.*?)\s*</span>', li, re.S)
            d = re.search(r'datetime="([^"]+)"', li)
            if m and t:
                title = re.sub(r"\s+at\s+.*$", "", strip(t.group(1))).strip() if c else strip(t.group(1))
                add("linkedin", c.group(1) if c else "", title, l.group(1) if l else "London", m.group(1), d.group(1) if d else ""); n += 1
        if n == 0: break
        time.sleep(5)

# ---- 2. Workable cross-employer feed (the employer's own live state) ----
tok = ""; 
for p in range(8 if BOOT else 3):
    u = "https://jobs.workable.com/api/v1/jobs?query=data%20scientist&location=London" + (f"&pageToken={tok}" if tok else "")
    s, b, _ = get(u)
    if s != 200: print(f"[workable-feed] page {p}: HTTP {s}", file=sys.stderr); break
    d = json.loads(b)
    for j in d.get("jobs", []):
        co = j.get("company") or {}; co = co.get("title") or co.get("name") or (co if isinstance(co, str) else "")
        add("workable-feed", co, j.get("title", ""), ", ".join(j.get("locations", []) or []) or str((j.get("location") or {}).get("city", "")), j.get("url", ""), j.get("created", ""))
    tok = d.get("nextPageToken") or ""
    if not tok: break

# ---- 3. Built In London (lead source: employer + title; the job page's JSON-LD names the employer) ----
for p in range(1, (4 if BOOT else 2) + 1):
    s, b, _ = get(f"https://builtinlondon.uk/jobs?search=data+scientist&city=London&page={p}")
    if s != 200: break
    links = sorted(set(re.findall(r'href="(/job/[^"]+)"', b)))
    if not links: break
    for l in links[:25]:
        s2, b2, _ = get("https://builtinlondon.uk" + l, tries=1)
        ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', b2, re.S)
        try: J = json.loads(ld.group(1)) if ld else {}
        except Exception: J = {}
        co = ((J.get("hiringOrganization") or {}).get("name")) if isinstance(J, dict) else None
        title = (J.get("title") if isinstance(J, dict) else None) or strip(re.search(r"<h1[^>]*>(.*?)</h1>", b2, re.S).group(1)) if re.search(r"<h1[^>]*>", b2) else None
        apply = re.search(r'"(https?://[^"]+(?:greenhouse\.io|ashbyhq\.com|lever\.co|workable\.com|smartrecruiters\.com|myworkdayjobs\.com|pinpointhq\.com|teamtailor\.com)[^"]*)"', b2)
        if co and title: add("builtin", co, title, "London", apply.group(1) if apply else "https://builtinlondon.uk" + l)
        time.sleep(0.5)

# ---- 4. Adzuna / Reed (official APIs, free keys; UK-wide incl. non-tech employers) ----
aid, akey = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")
if aid and akey:
    for p in range(1, (6 if BOOT else 3) + 1):
        s, b, _ = get(f"https://api.adzuna.com/v1/api/jobs/gb/search/{p}?app_id={aid}&app_key={akey}&what=data%20scientist&where=London&distance=15&results_per_page=50&max_days_old={30 if BOOT else 7}&content-type=application/json")
        if s != 200: print(f"[adzuna] page {p}: HTTP {s}", file=sys.stderr); break
        for r in json.loads(b).get("results", []):
            add("adzuna", (r.get("company") or {}).get("display_name", ""), r.get("title", ""), (r.get("location") or {}).get("display_name", ""), r.get("redirect_url", ""), r.get("created", ""))
else: print("[adzuna] skipped — set ADZUNA_APP_ID and ADZUNA_APP_KEY for UK-wide coverage", file=sys.stderr)
rkey = os.environ.get("REED_API_KEY")
if rkey:
    import base64
    s, b, _ = get("https://www.reed.co.uk/api/1.0/search?keywords=data%20scientist&locationName=London&distanceFromLocation=15&resultsToTake=100", h={"Authorization": "Basic " + base64.b64encode((rkey + ":").encode()).decode()})
    if s == 200:
        for r in json.loads(b).get("results", []): add("reed", r.get("employerName", ""), r.get("jobTitle", ""), r.get("locationName", ""), r.get("jobUrl", ""), r.get("date", ""))
    else: print(f"[reed] HTTP {s}", file=sys.stderr)
else: print("[reed] skipped — set REED_API_KEY for UK-wide coverage", file=sys.stderr)

# ---- normalise, classify, dedupe, agency filter ----
seen = set(); leads = []
for c in cands:
    key = (c["company"].lower(), c["title"].lower())
    if key in seen or not COLLECT.search(c["title"]) or EXC.search(c["title"]) or not LON.search(c["location"] or "London"): continue
    seen.add(key); c["role_type"] = classify(c["title"]); c["agency"] = bool(AGENCY.search(c["company"])); leads.append(c)
print(f"[discover] {len(cands)} raw -> {len(leads)} unique DS-family leads ({sum(1 for l in leads if l['agency'])} agency, "
      f"{sum(1 for l in leads if l['role_type']=='Standard DS' and not l['agency'])} Standard DS at employers)", file=sys.stderr)

# ---- resolve each employer lead to the employer's own posting / ATS token ----
def token_of(url):
    for k, rx in TOKEN:
        m = rx.search(url)
        if m: return k, m.group(1)
    m = WD.search(url)
    if m: return "workday", f"https://{m.group(1)}.{m.group(2)}.myworkdayjobs.com/wday/cxs/{m.group(1)}/{m.group(3)}/jobs"
    return None, None
new_tokens = {}; posts = []; unresolved = []
for l in leads:
    if l["agency"]: continue
    url = l["url"]
    if "linkedin.com/jobs/view" in url:                                  # LinkedIn lead -> the employer's apply URL on the job page
        s, b, _ = get(url, tries=2, pause=8)
        m = re.search(r'applyUrl["\']?\s*[:=]\s*["\']([^"\']+)', b) or re.search(r'<code id="applyUrl">\s*<!--"?([^"]+?)"?-->', b)
        if m: url = html.unescape(m.group(1)); url = urllib.parse.unquote(re.sub(r"^.*?url=", "", url)) if "linkedin.com/" in url and "url=" in url else url
        l["employer_url"] = url if "linkedin.com" not in url else ""
        time.sleep(1.5)
    elif "jobs.workable.com/view" in url: l["employer_url"] = url          # Workable's own feed: live by construction
    elif "adzuna" in url or "reed.co.uk" in url:
        s, b, final = get(url, tries=1); l["employer_url"] = final if final and not re.search(r"adzuna|reed\.co\.uk", final) else ""
    else: l["employer_url"] = url
    eu = l.get("employer_url") or ""
    k, t = token_of(eu) if eu else (None, None)
    if k and t:
        bucket = have.get(k, set()) if k != "workday" else have_wd
        l["resolved"] = f"ats:{k}:{t}"
        if t.lower() not in bucket: new_tokens.setdefault(k, {})[t] = l["company"]
    elif eu:
        l["resolved"] = "employer-site"; posts.append({"company": l["company"], "title": l["title"], "location": l["location"] or "London", "url": eu, "source": l["source"]})
    else:
        l["resolved"] = "unresolved"; unresolved.append(l)

# ---- grow the registry; hand employer-site posts to refresh_roles.py ----
added = 0
for k, toks in new_tokens.items():
    if k == "workday":
        for u, co in toks.items(): REG["workday"][co] = u; added += 1
    else:
        REG.setdefault(k, []); 
        for t, co in toks.items():
            REG[k].append(t); REG.setdefault("display_names", {})[t] = co; added += 1
        REG[k] = sorted(set(REG[k]))
if added: json.dump(REG, open(reg_path, "w"), indent=1)
json.dump(posts, open(os.path.join(HERE, "discovered_posts.json"), "w"), indent=1)
json.dump(leads, open(os.path.join(HERE, "discovered_leads.json"), "w"), indent=1)
print(f"[discover] +{added} new boards registered -> boards.json; {len(posts)} employer-site posts -> discovered_posts.json; "
      f"{len(unresolved)} unresolved leads kept in discovered_leads.json", file=sys.stderr)
for k, toks in new_tokens.items():
    for t, co in toks.items(): print(f"   + {k}: {t}  ({co})", file=sys.stderr)
