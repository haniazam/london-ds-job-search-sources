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
  - anything unresolved stays in discovered_leads.json, labelled, never silently dropped, and is
    aggregated per employer in discovered_unresolved_employers.json for the weekly manual sweep.

Resolution tiers for a lead that carries no employer URL (LinkedIn's guest pages gate the apply
link behind sign-in, so the page is never fetched):
  1. the employer is already in boards.json (display-name or alias match) -> covered by the registry;
  2. a scripted web search restricted to the ATS hosts — Brave Search API when BRAVE_API_KEY is
     set (2,000 queries/month free), else DuckDuckGo's HTML endpoint at ~15 s pacing with a
     per-run cap (RESOLVE_CAP, default 25; Senior+ Standard DS first) — yields the board token;
  3. otherwise the employer is listed as an unresolved lead; the weekly sweep resolves it by hand.

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
RESOLVE_ONLY = "--resolve-only" in sys.argv
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
AGENCY = re.compile(r"recruit|talent|staffing|resourcing|headhunt|search partners|selection|consultancy ltd|\bjobs\b|hiring|harnham|understanding recruitment|nicoll curtin|experis|\bhays\b|robert walters|michael page|la fosse|oliver bernard|client server|\btiro\b|xcede|datatech|intellect group|interex|sphere digital|rise technical|spectrum it|manning services|oscar technology|avanti|kimaru|jobgether|degree 6|qurious|stott and may|burns sheehan|lorien|akkodis|computer futures|huxley|real staffing|randstad|reed\b|adecco|hudson|morgan mckinley|spencer ogden|signify technology|allegis|teksystems|iopa|revolent|opus|cognitive group|montash|\bexec\b|associates|people first|the people|mccabe & barton|oho group|speak to kit|annapurna|deeprec|neartech|radley james|searchworks|searchability|mthree|q1 technologies|x4 alpha|x4 group", re.I)
TOKEN = [("greenhouse", re.compile(r"greenhouse\.io/([A-Za-z0-9_-]+)/jobs")), ("ashby", re.compile(r"ashbyhq\.com/([^/?#]+)/")),
         ("lever", re.compile(r"lever\.co/([^/?#]+)/")), ("workable", re.compile(r"apply\.workable\.com/([^/?#]+)/j/")),
         ("smartrecruiters", re.compile(r"smartrecruiters\.com/([^/?#]+)/\d")), ("pinpoint", re.compile(r"https?://([^./]+)\.pinpointhq\.com")),
         ("teamtailor", re.compile(r"https?://([^./]+)\.teamtailor\.com"))]
WD = re.compile(r"https?://([a-z0-9]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([^/?#]+)/")
reg_path = os.path.join(HERE, "boards.json"); REG = json.load(open(reg_path))
have = {k: {t.lower() for t in REG.get(k, [])} for k in ("greenhouse", "ashby", "lever", "workable", "smartrecruiters", "pinpoint", "recruitee", "teamtailor")}
have_wd = {u.lower() for u in REG["workday"].values()}
cands = []
def add(src, co, title, loc, url, posted=""):
    if not (co and title and url): return
    cands.append({"source": src, "company": strip(co).strip(), "title": re.sub(r"\s+", " ", strip(title)).strip(), "location": strip(loc).strip(), "url": url.split("?")[0], "posted": posted})

if RESOLVE_ONLY:
    cands = []
else:
  pass
# ---- 1. LinkedIn guest search: newest first; two title forms; paced (429s are common) ----
tpr = "r2592000" if BOOT else "r604800"; pages = 20 if BOOT else 6
for q in ([] if RESOLVE_ONLY else ("Data Scientist", "Data Science")):
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
for p in range(0 if RESOLVE_ONLY else (8 if BOOT else 3)):
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
for p in range(1, (0 if RESOLVE_ONLY else (4 if BOOT else 2)) + 1):
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
if aid and akey and not RESOLVE_ONLY:
    for p in range(1, (6 if BOOT else 3) + 1):
        s, b, _ = get(f"https://api.adzuna.com/v1/api/jobs/gb/search/{p}?app_id={aid}&app_key={akey}&what=data%20scientist&where=London&distance=15&results_per_page=50&max_days_old={30 if BOOT else 7}&content-type=application/json")
        if s != 200: print(f"[adzuna] page {p}: HTTP {s}", file=sys.stderr); break
        for r in json.loads(b).get("results", []):
            add("adzuna", (r.get("company") or {}).get("display_name", ""), r.get("title", ""), (r.get("location") or {}).get("display_name", ""), r.get("redirect_url", ""), r.get("created", ""))
else: print("[adzuna] skipped — set ADZUNA_APP_ID and ADZUNA_APP_KEY for UK-wide coverage", file=sys.stderr)
rkey = os.environ.get("REED_API_KEY")
if rkey and not RESOLVE_ONLY:
    import base64
    s, b, _ = get("https://www.reed.co.uk/api/1.0/search?keywords=data%20scientist&locationName=London&distanceFromLocation=15&resultsToTake=100", h={"Authorization": "Basic " + base64.b64encode((rkey + ":").encode()).decode()})
    if s == 200:
        for r in json.loads(b).get("results", []): add("reed", r.get("employerName", ""), r.get("jobTitle", ""), r.get("locationName", ""), r.get("jobUrl", ""), r.get("date", ""))
    else: print(f"[reed] HTTP {s}", file=sys.stderr)
else: print("[reed] skipped — set REED_API_KEY for UK-wide coverage", file=sys.stderr)

# ---- normalise, classify, dedupe, agency filter ----
seen = set(); leads = []
if RESOLVE_ONLY:
    leads = json.load(open(os.path.join(HERE, "discovered_leads.json")))
    for l in leads: l.pop("resolved", None); l.pop("employer_url", None)
    cands = []
for c in cands:
    key = (c["company"].lower(), c["title"].lower())
    if any(key == (l["company"].lower(), l["title"].lower()) for l in leads): continue
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
norm = lambda n: re.sub(r"[^a-z0-9]", "", re.sub(r"\s*\(.*?\)", "", (n or "").lower()))
known = {norm(v): k for k, v in REG.get("display_names", {}).items()} | {norm(k): k for k in REG["workday"]}
for k in ("greenhouse", "ashby", "lever", "workable", "smartrecruiters", "pinpoint", "recruitee", "teamtailor"):
    for t in REG.get(k, []): known.setdefault(norm(t), t)
for a, c in REG.get("aliases", {}).items():
    if not a.startswith("_"): known.setdefault(norm(a), c)                       # same organisation under another lead name
for n in list(REG.get("employer_sites", {}).keys()) + list(REG.get("oraclehcm", {}).keys()) + list(REG.get("successfactors", {}).keys()) + (["Apple"] if "apple" in REG else []) + ["Amazon", "Google", "TikTok", "Spotify", "Microsoft", "Point72", "Bloomberg", "G-Research", "Bauer Media Group"]:
    if not n.startswith("_"): known.setdefault(norm(n), n)                        # employers enumerated outside the token lists
STOP = {"the", "and", "of", "ltd", "limited", "plc", "inc", "llc", "llp", "group", "holdings", "company", "co", "uk", "global",
        "international", "technologies", "technology", "tech", "solutions", "services", "systems", "labs", "lab", "ai", "io", "com"}
def name_words(company):
    return [w for w in re.findall(r"[a-z0-9]+", re.sub(r"\s*\(.*?\)", "", (company or "").lower())) if w not in STOP] or \
           re.findall(r"[a-z0-9]+", (company or "").lower())
def corroborate(company, token):
    """Does this board token (or Workday tenant) name the employer? The token must START with the employer's first
    significant word; a multi-word name must also share a later word, or the token must be that first word plus at most a
    short suffix. 'bp' -> 'bpinternational' and 'Jack & Jill' -> 'jack-jill-external-ats' pass; 'Meta' -> 'georgetown',
    'Costa Coffee' -> 'cocacola' and 'Acuity Analytics' -> 'acuity-insights' fail."""
    tok = norm(token); key = norm(company); words = name_words(company)
    if not tok or not words: return False
    tenant = tok
    if token.startswith("http"):                                               # Workday: judge the tenant slug only, never the whole URL
        m = WD.search(token); tenant = norm(m.group(1)) if m else tok
    if tenant == key or (len(tenant) >= 4 and key.startswith(tenant)): return True
    if not tenant.startswith(words[0]): return False
    if len(words) == 1: return True
    return any(w in tenant for w in words[1:]) or len(tenant) <= len(words[0]) + 4
PROBE = {   # public list endpoints by platform: (url template, key whose presence marks a live board, name field or None)
    "greenhouse": ("https://boards-api.greenhouse.io/v1/boards/{t}/jobs?content=false", "jobs", None),
    "ashby": ("https://api.ashbyhq.com/posting-api/job-board/{t}", "jobs", None),
    "lever": ("https://api.lever.co/v0/postings/{t}?mode=json", None, None),
    "smartrecruiters": ("https://api.smartrecruiters.com/v1/companies/{t}/postings", "content", None),
    "pinpoint": ("https://{t}.pinpointhq.com/postings.json", "data", None),
    "teamtailor": ("https://{t}.teamtailor.com/jobs.json", "items", "title"),
    "workable": ("https://apply.workable.com/api/v1/widget/accounts/{t}", "jobs", "name"),
}
_probe_cache = {}; _workable_blocked = False
SAMPLE_TITLES = {"head of dei - belfast", "head of dei - us", "head of dei - uk", "marketing manager", "customer service rep"}
def is_demo(items):
    """Pinpoint trial tenants (any slug someone once signed up) ship the same five sample jobs — Head of DEI ×3, Marketing
    Manager, Customer Service Rep in Belfast/Washington/London/Paris/New York — so a guessed slug can 'exist' with a London
    job and still not be the employer. Three or more sample titles means a demo board, not a real one."""
    titles = {str(j.get("title", "")).strip().lower() for j in items if isinstance(j, dict)}
    return len(titles & SAMPLE_TITLES) >= 3
def _locs(k, d):
    """Flatten the locations a probed board lists, so a UK presence can be checked."""
    out = []
    if k == "greenhouse": out = [j.get("location", {}).get("name", "") for j in d.get("jobs", [])]
    elif k == "ashby": out = [f"{j.get('location','')} {' '.join(x.get('location','') for x in j.get('secondaryLocations', []))}" for j in d.get("jobs", [])]
    elif k == "lever": out = [f"{j.get('categories',{}).get('location','')} {' '.join(j.get('categories',{}).get('allLocations',[]) or [])}" for j in d]
    elif k == "smartrecruiters": out = [f"{j.get('location',{}).get('city','')} {j.get('location',{}).get('country','')}" for j in d.get("content", [])]
    elif k == "pinpoint": out = [f"{j.get('location',{}).get('name','')} {j.get('location',{}).get('country','')}" for j in d.get("data", [])]
    elif k == "teamtailor": out = [" ".join(a.get("address", {}).get("addressLocality", "") + " " + a.get("address", {}).get("addressCountry", "") for a in (j.get("_jobposting", {}).get("jobLocation") or [])) for j in d.get("items", [])]
    elif k == "workable": out = [f"{j.get('city','')} {j.get('country','')} {j.get('state','')}" for j in d.get("jobs", [])]
    return out
UKLOC = re.compile(r"london|united kingdom|\bUK\b|\bGB\b|england|remote[^,;|]*(uk|united kingdom|europe|emea)", re.I)
def board_live(k, t, company=None, strict=False):
    """Does the public API for this board answer? With a company (tier 1.5, strict): the board must ALSO look like that
    employer — its name field (where the platform has one) must match AND at least one job must sit in the UK — because a
    guessed slug such as 'prima' or 'haven' can belong to an unrelated firm abroad. Rate-limited or dead boards count as
    not found in strict mode (a guess is never registered on an unknown), but as 'unknown, keep' for search results."""
    global _workable_blocked
    if k == "workday": return True                                             # tenants are verified by the refresh run itself
    if k not in PROBE: return True
    if k == "workable" and _workable_blocked: return not strict
    ck = (k, t.lower(), bool(company))
    if ck in _probe_cache: return _probe_cache[ck]
    url, key, namef = PROBE[k]
    s_, b, _ = get(url.format(t=t), t=10, tries=1)
    ok = False
    if s_ == 429 and k == "workable": _workable_blocked = True; return not strict
    if s_ == 200:
        try:
            d = json.loads(b); ok = (key is None and isinstance(d, list)) or (key is not None and key in d)
            if ok:
                items = d if key is None else d.get(key, [])
                if is_demo(items): ok = False                                  # the platform's sample tenant, not the employer
            if ok and company:
                nm = (d.get(namef) if (namef and isinstance(d, dict)) else None)
                name_ok = (not namef) or (nm and norm(nm) and (norm(nm) in norm(company) or norm(company) in norm(nm)))
                uk_ok = any(UKLOC.search(x or "") for x in _locs(k, d))
                ok = bool(name_ok and uk_ok)
        except Exception: ok = False
    _probe_cache[ck] = ok
    return ok
def probe_token(company):
    """Tier 1.5: guess the board slug from the employer's name and ask each ATS's public API directly — no search engine.
    Found most of the boards in the 10 Oct hand sweep in under two minutes."""
    words = name_words(company); key = norm(company)
    raw = re.findall(r"[a-z0-9]+", re.sub(r"\s*\(.*?\)", "", (company or "").lower()))   # every word, generic ones included ('made-tech')
    slugs = []
    for c in [key, "-".join(raw), "-".join(words), "".join(words), "-".join(raw[:2]), "".join(raw[:2]), words[0] if words else ""]:
        if c and len(c) >= 3 and c not in slugs: slugs.append(c)
    for k in ("greenhouse", "ashby", "lever", "smartrecruiters", "pinpoint", "teamtailor", "workable"):
        for sl in slugs:
            if board_live(k, sl, company, strict=True):
                u = PROBE[k][0].format(t=sl)
                return k, sl, u
    return None, None, None
HOSTS = ("site:job-boards.greenhouse.io OR site:boards.greenhouse.io OR site:job-boards.eu.greenhouse.io OR site:jobs.ashbyhq.com OR "
         "site:jobs.lever.co OR site:apply.workable.com OR site:jobs.smartrecruiters.com OR site:myworkdayjobs.com OR site:pinpointhq.com OR site:teamtailor.com")
def search_token(company):
    """Tier 2: find the employer's ATS board via a web search restricted to ATS hosts."""
    q = f'"{company}" "data scientist" ({HOSTS})'
    urls = []
    # Brave Search: the key arrives either as BRAVE_API_KEY in the environment or injected by the
    # session's Network-secret proxy (header X-Subscription-Token on api.search.brave.com), so the
    # call is always attempted; anything but 200 (no key, 401, 429) falls back to DuckDuckGo.
    bk = os.environ.get("BRAVE_API_KEY"); hdr = {"Accept": "application/json"}
    if bk: hdr["X-Subscription-Token"] = bk
    s, b, _ = get("https://api.search.brave.com/res/v1/web/search?count=10&q=" + urllib.parse.quote(q), h=hdr, tries=1)
    if s == 200:
        try: urls = [r.get("url", "") for r in json.loads(b).get("web", {}).get("results", [])]
        except Exception: urls = []
        time.sleep(1.1)                                                         # Brave free tier: 1 request/second
    else:
        if bk or s not in (401, 422): print(f"  [brave] HTTP {s} — falling back to DuckDuckGo", file=sys.stderr)   # 401/422 = no key configured
        s, b, _ = get("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q), tries=1)
        if s == 200:
            urls = [urllib.parse.unquote(re.search(r"uddg=([^&]+)", u).group(1)) if "uddg=" in u else u for u in re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"', b)]
        time.sleep(15)
    for u in urls:
        k, t = token_of(u)
        if k and t and corroborate(company, t) and board_live(k, t):          # the board's own name must match the employer and the board must answer
            return k, t, u
    return None, None, None
new_tokens = {}; posts = []; unresolved = []; covered = 0; searched = 0
CAP = int(os.environ.get("RESOLVE_CAP", "25"))
pri = lambda l: (0 if (l["role_type"] == "Standard DS" and re.search(r"senior|staff|lead|principal|head|director|manager", l["title"], re.I)) else 1, l["company"])
cache = {}; pcache = {}; probed = 0; PROBE_CAP = int(os.environ.get("PROBE_CAP", "150"))
for l in sorted([x for x in leads if not x["agency"]], key=pri):
    url = l["url"]; eu = ""
    if "jobs.workable.com/view" in url: eu = url                          # Workable's own feed: live by construction
    elif "adzuna" in url or "reed.co.uk" in url:
        s, b, final = get(url, tries=1); eu = final if final and not re.search(r"adzuna|reed\.co\.uk", final) else ""
    elif "linkedin.com/jobs/view" not in url and "builtinlondon.uk" not in url: eu = url
    l["employer_url"] = eu
    k, t = token_of(eu) if eu else (None, None)
    if not k:                                                                  # tier 1: already in the registry?
        kt = known.get(norm(l["company"]))
        if kt: l["resolved"] = f"registry:{kt}"; covered += 1; continue
    if not k and not eu:                                                       # tier 1.5: guess the board slug and probe the ATS APIs directly
        c = pcache.get(norm(l["company"]))
        if c is None and probed < PROBE_CAP:
            c = probe_token(l["company"]); pcache[norm(l["company"])] = c; probed += 1
        if c and c[0]: k, t, eu = c; l["employer_url"] = eu
    if not k and not eu:                                                       # tier 2: search for the board (capped, paced)
        c = cache.get(norm(l["company"]))
        if c is None and searched < CAP:
            c = search_token(l["company"]); cache[norm(l["company"])] = c; searched += 1
        if c and c[0]: k, t, eu = c; l["employer_url"] = eu
    if k and t:
        bucket = have.get(k, set()) if k != "workday" else have_wd
        l["resolved"] = f"ats:{k}:{t}"
        if t.lower() not in bucket: new_tokens.setdefault(k, {})[t] = l["company"]
    elif eu:
        l["resolved"] = "employer-site"; posts.append({"company": l["company"], "title": l["title"], "location": l["location"] or "London", "url": eu, "source": l["source"]})
    else:
        l["resolved"] = "unresolved"; unresolved.append(l)
by_emp = {}
for l in unresolved: by_emp.setdefault(l["company"], []).append(l["title"])
json.dump([{"company": c, "titles": sorted(set(ts)), "source": "linkedin/builtin"} for c, ts in sorted(by_emp.items())],
          open(os.path.join(HERE, "discovered_unresolved_employers.json"), "w"), indent=1)
print(f"[resolve] registry-covered {covered} · probed {probed} (cap {PROBE_CAP}) · searched {searched} (cap {CAP}) · unresolved employers {len(by_emp)}", file=sys.stderr)

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
