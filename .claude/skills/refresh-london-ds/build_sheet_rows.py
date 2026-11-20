#!/usr/bin/env python3
"""Turn the enriched CSV into the Sheet's rows (9 columns), diffed by URL against the previous run.

usage: build_sheet_rows.py /tmp/ldn_ds_active_pay.csv [previous_rows.json] [YYYY-MM-DD]
writes: <out_dir>/sheet_values_<date>.json  (rows for A2:I…), data/snapshots/<date>.csv (Standard DS rows),
        updates data/set_aside.json: roles that closed since the previous run are added with a reason, roles that are
        live again are removed. Prints the diff (new / closed / unchanged) so the Routine can report it."""
import csv, json, os, re, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
from refresh_roles_scope import EXCLUDE, SENIOR, BRIEF, via_of, london_ok, norm_loc   # shared scope rules
SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ldn_ds_active_pay.csv"
PREV = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].endswith(".json") else None
DATE = sys.argv[3] if len(sys.argv) > 3 else datetime.date.today().isoformat()
OUT_DIR = os.environ.get("SHEET_OUT", "/tmp")
COLS = ["Company", "Role", "Role Type", "Level", "Approx London TC", "Location", "Apply URL (unique active post)", "Status", "Notes"]
rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r.get("Role Type") == "Standard DS" and not EXCLUDE.search(r["Role"]) and london_ok(r["Location"])]
for r in rows: r["Location"] = norm_loc(r["Location"])
def key(u):
    """Dedupe key for a posting URL: drop the query and trailing slash; SmartRecruiters posts are the numeric id (the API appends a title slug the Sheet's URL lacks)."""
    u = (u or "").split("?")[0].rstrip("/")
    u = re.sub(r"(smartrecruiters\.com/)([^/]+)(/\d+)[^/]*$", lambda m: m.group(1) + m.group(2).lower() + m.group(3), u)
    return u
# every row the run returned, before the scope filter: a previous row that IS here but failed the filter was re-located / re-titled, not closed by its board
all_rows = {key(r["Apply URL (unique active post)"]): r for r in csv.DictReader(open(SRC, encoding="utf-8"))}
enumerated = {r["Company"].lower() for r in all_rows.values()}          # employers whose board the run read and that returned at least one row
BOARD_HOSTS = ("greenhouse.io", "ashbyhq.com", "lever.co", "smartrecruiters.com", "pinpointhq.com", "teamtailor.com", "myworkdayjobs.com", "amazon.jobs", "apply.workable.com")
prev_rows, prev_date = [], None
if PREV:
    prev_rows = json.load(open(PREV))
    # when the previous rows were generated: the newest refresh date the Sheet's own Notes mention (NEW (refresh …) / last verified …),
    # else the newest snapshot before DATE — the JSON's mtime is just when this run read the Sheet
    dates = sorted({d for r in prev_rows for d in re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", " ".join(r[7:9]) if len(r) >= 9 else "") if d < DATE})
    SNAP = os.path.join(ROOT, "data", "snapshots")
    snaps = sorted(f[:10] for f in (os.listdir(SNAP) if os.path.isdir(SNAP) else []) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.csv", f) and f[:10] < DATE)
    prev_date = (dates or snaps or [datetime.date.fromtimestamp(os.path.getmtime(PREV)).isoformat()])[-1]
else:                                                                               # default baseline: newest snapshot strictly before DATE
    SNAP = os.path.join(ROOT, "data", "snapshots")
    snaps = sorted(f for f in (os.listdir(SNAP) if os.path.isdir(SNAP) else []) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.csv", f) and f[:10] < DATE)
    if snaps:
        prev_rows = [r for r in csv.reader(open(os.path.join(SNAP, snaps[-1]), encoding="utf-8"))][1:]
        prev_date = snaps[-1][:10]
        print(f"[sheet] no previous rows given; diffing against data/snapshots/{snaps[-1]}", file=sys.stderr)
prev_active = {key(r[6]): r for r in prev_rows if len(r) >= 9 and r[6].startswith("http")}
seen, out = set(), []
for r in sorted(rows, key=lambda r: (r["Company"].lower(), r["Level"] != "Senior+", r["Role"].lower())):
    u = key(r["Apply URL (unique active post)"])
    if u in seen: continue
    seen.add(u)
    brief = r["Level"] == "Senior+" and bool(BRIEF.search(r["Role"]))
    notes = []
    if u not in prev_active: notes.append(f"NEW (refresh {DATE})")
    if brief: notes.append("FITS BRIEF")
    notes.append(f"verified via {via_of(r['Apply URL (unique active post)'])}")
    out.append([r["Company"], r["Role"], "Standard DS", r["Level"], r["Approx London TC"], r["Location"],
                r["Apply URL (unique active post)"], "Active", "; ".join(notes)])
missing = [v for k, v in prev_active.items() if k not in seen]
# a board the run could not read (429 / gated) makes its rows unverified, never closed: carry them forward
unv_path = "/tmp/ldn_ds_unverified.json"; unv = json.load(open(unv_path)) if os.path.exists(unv_path) else {}
def unreadable(url):
    """The platform key whose board the run could not read, or None."""
    if "workable" in url and "workable" in unv: return "workable"
    if url.split("?")[0] in unv.get("manual", []): return "manual"
    return next((k for k, ts in unv.items() for t in ts if f"/{t}" in url or f"//{t}." in url), None)
REASON = {"spa": "JS site not reachable this run (Playwright absent or fetch failed)", "manual": "post page fetch failed this run", "page": "no board returned it and its job page could not be fetched"}
# ---- a row no enumerated source returned is re-checked on its own job page before it is called closed ----
# (2026-11-16: six live rows — boards that discover.py had found but never registered, and a Microsoft post past the
# Eightfold search's first 50 — were about to be closed because no board returned them; a GET on the post decides.)
SPA_HOSTS = ("apply.careers.microsoft", "jobs.careers.microsoft", "lifeatspotify", "gresearch.com", "bloomberg.avature", "careers.point72", "careers.tiktok", "lifeattiktok")
DEAD_TITLE = re.compile(r"no longer|not found|not available|closed|expired|jobs search|\d,\d{3}\+ |\bjobs in (the )?united states|^careers at |^jobs at |^job search", re.I)
PAGE_DEAD = re.compile(r'"status"\s*,\s*"EXPIRED"|>\s*Expired\s*<|This (job|position|vacancy) (has expired|is no longer (available|open|accepting))|job is not available anymore', re.I)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept-Language": "en-GB,en;q=0.9"}
_pw = {}
def _spa_title(url):
    """<title> of a JS-rendered job page via the pre-installed Chromium; None when Playwright is unavailable (-> unverified)."""
    try:
        if "pg" not in _pw:
            import glob
            from playwright.sync_api import sync_playwright
            _pw["p"] = sync_playwright().start()
            try: b = _pw["p"].chromium.launch(headless=True, args=["--ignore-certificate-errors"])
            except Exception:
                exe = (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome") or [None])[0]
                if not exe: raise
                b = _pw["p"].chromium.launch(headless=True, executable_path=exe, args=["--ignore-certificate-errors"])
            _pw["b"] = b; _pw["pg"] = b.new_context(ignore_https_errors=True, locale="en-GB").new_page()
        pg = _pw["pg"]; pg.goto(url, wait_until="domcontentloaded", timeout=45000)
        try: pg.wait_for_load_state("networkidle", timeout=8000)
        except Exception: pass
        pg.wait_for_timeout(2500)
        return pg.title() or ""
    except Exception as e:
        print(f"[recheck] playwright: {type(e).__name__} {e}", file=sys.stderr); return None
def page_check(url, role):
    """'live' when the post page still carries the role, 'closed' on 404/410 or a generic title, 'unverified' on any other failure."""
    import html as _h, urllib.request, urllib.error
    spa = any(h in url for h in SPA_HOSTS)
    wd = re.match(r"https://([^./]+)\.(wd\d+)\.myworkdayjobs\.com/[^/]+/([^/]+)/job/(.+)$", url.split("?")[0])
    if wd:
        # Workday job pages are an SPA shell for live and closed posts alike (empty <title>), so the HTML never settles it:
        # ask the CXS job endpoint instead — 200 live, 404/410 closed, anything else (403 S22, 429 challenge) unverified.
        api = f"https://{wd[1]}.{wd[2]}.myworkdayjobs.com/wday/cxs/{wd[1]}/{wd[3]}/job/{wd[4]}"
        try:
            with urllib.request.urlopen(urllib.request.Request(api, headers={**UA, "Accept": "application/json"}), timeout=35) as f:
                return "live" if f.status == 200 else "unverified"
        except urllib.error.HTTPError as e:
            return "closed" if e.code in (404, 410) else "unverified"
        except Exception:
            return "unverified"
    if spa:
        title = _spa_title(url)
        if title is None: return "unverified"
        page = ""
    else:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=35) as f: page = f.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return "closed" if e.code in (404, 410) else "unverified"
        except Exception:
            return "unverified"
        m = re.search(r"<title>(.*?)</title>", page, re.S); title = _h.unescape(m.group(1)) if m else ""
    words = [w for w in re.findall(r"[a-z]{3,}", role.lower()) if w not in ("and", "the", "for", "with")]
    tl = title.lower(); hit = sum(w in tl for w in words) / max(1, len(words))
    if (hit >= 0.6 or "data scien" in tl) and not DEAD_TITLE.search(title) and not PAGE_DEAD.search(page): return "live"
    return "closed"
closed, carried, kept = [], [], []
# a row whose board token is on board_denylist.json is not an employer's post (demo boards, wrong-company matches): it closes with that reason,
# never gets page-verified (2026-11-18: the Teamtailor demo board 'volter-demo' was kept live by its own page after discover.py had registered it once)
DENY = json.load(open(os.path.join(HERE, "board_denylist.json"))).get("tokens", {}) if os.path.exists(os.path.join(HERE, "board_denylist.json")) else {}
def denylisted(url):
    u = url.lower()
    return next((f"board '{t}' is deny-listed ({why})" for m in DENY.values() for t, why in m.items() if f"//{t.lower()}." in u or f"/{t.lower()}/" in u), None)
for v in missing:
    k = unreadable(v[6])
    row = list(v)
    why = denylisted(v[6])
    if why:
        print(f"[recheck] {v[0]} | {v[1]} -> closed: {why}", file=sys.stderr)
        closed.append(list(v) + [why]); continue
    prior = re.sub(r"^(not re-verified on \S+ \([^)]*\); last verified [^;]*; )+", "", re.sub(r"^NEW \(refresh [^)]*\); ", "", row[8]))
    prior = re.sub(r"^(re-verified by page fetch on \S+ \([^)]*\); )+", "", prior)
    if not k and key(v[6]) in all_rows:                      # its board still lists it, but outside scope now (e.g. Lovable Agent/Product -> Stockholm-only, 2026-11-16)
        a = all_rows[key(v[6])]
        why = (f"now located {norm_loc(a['Location'])}" if not london_ok(a["Location"]) else
               f"title now {a['Role']!r} ({a.get('Role Type')})" if a.get("Role Type") != "Standard DS" else "title now excluded (intern/FTC/part-time)")
        print(f"[recheck] {v[0]} | {v[1]} -> out of scope: {why}", file=sys.stderr)
        closed.append(list(v) + [why]); continue
    if not k and any(h in v[6] for h in BOARD_HOSTS) and v[0].lower() in enumerated:
        # its own board was read this run and still returns other London DS rows for this employer, but not this URL: the board dropped it
        # (or moved it out of London — Lovable's Agent/Product DS posts went Stockholm-only on 2026-11-16); a page GET cannot see that, the board can
        print(f"[recheck] {v[0]} | {v[1]} -> dropped by its board", file=sys.stderr)
        closed.append(v); continue
    if not k:
        verdict = page_check(v[6], v[1])
        print(f"[recheck] {v[0]} | {v[1]} -> {verdict}", file=sys.stderr)
        if verdict == "live":
            row[7] = "Active"; row[8] = f"re-verified by page fetch on {DATE} (no enumerated board returned it); " + prior
            out.append(row); kept.append(row); continue
        if verdict == "closed": closed.append(v); continue
        k = "page"
    row[7] = "Unverified"
    row[8] = f"not re-verified on {DATE} ({REASON.get(k, 'board API rate-limited')}); last verified {prev_date}; " + prior
    out.append(row); carried.append(row)
if "b" in _pw:
    try: _pw["b"].close(); _pw["p"].stop()
    except Exception: pass
out.sort(key=lambda r: (r[0].lower(), r[3] != "Senior+", r[1].lower()))
# ---- set-aside: closed roles in, re-verified roles out ----
sa_path = os.path.join(ROOT, "data", "set_aside.json"); sa = json.load(open(sa_path))
live_names = {f"{r[0]} ({r[1]})" for r in out}
sa = [e for e in sa if not (e[2] == "unv" and any(e[0].startswith(r[0]) and r[1].split(" - ")[0].split(",")[0] in e[0] for r in out) and e[0] in live_names)]
sa = [e for e in sa if not (e[2] == "unv" and e[0] == "Wise (Senior DS Lead, AML Risk)" and any(r[0] == "Wise" and "AML Risk" in r[1] for r in out))]
have = {e[0] for e in sa}
for c in closed:
    name = f"{c[0]} ({c[1]})"
    if name not in have:
        why = c[9] if len(c) > 9 else f"not returned by {via_of(c[6]).replace('verified via ', '')}"
        sa.append([name, f"Closed — {why} on the {DATE} refresh (was live on {prev_date})", "scope" if len(c) > 9 and c[9].startswith("now located") else "closed"]); have.add(name)
json.dump(sa, open(sa_path, "w"), indent=1, ensure_ascii=False); open(sa_path, "a").write("\n")
LABEL = {"closed": "No active London DS role", "mon": "No active London DS role", "unv": "Unverified lead", "scope": "Out of scope", "floor": "Below floor", "caution": "Caution", "profile": "Profile mismatch", "mismatch": "Profile mismatch"}
tail = [[""] * 9, ["— COMPANIES WITH NO ACTIVE LONDON DS ROLE / UNVERIFIED LEADS —"] + [""] * 8]
for e in sa: tail.append([e[0], "—", "—", "—", "—", "—", "", LABEL.get(e[2], e[2].title()), e[1]])
values = out + tail
os.makedirs(os.path.join(ROOT, "data", "snapshots"), exist_ok=True)
with open(os.path.join(ROOT, "data", "snapshots", f"{DATE}.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(COLS); w.writerows(out)
jp = os.path.join(OUT_DIR, f"sheet_values_{DATE}.json"); json.dump(values, open(jp, "w"), ensure_ascii=False)
new = [r for r in out if r[8].startswith("NEW")]
print(f"[sheet] {len(out)} Standard DS rows at {len({r[0] for r in out})} employers; {len(new)} new, {len(closed)} closed, {len(carried)} carried forward unverified since {prev_date}; "
      f"{len(sa)} set-aside rows; {len(values)} rows -> A2:I{len(values)+1}; wrote {jp}")
for r in new: print(f"   + {r[0]} | {r[1]} | {r[4]} | {r[5]}")
for c in closed: print(f"   - {c[0]} | {c[1]} | {c[6]}")
for r in kept: print(f"   = kept (page-verified, board not enumerated) {r[0]} | {r[1]} | {r[6]}")
for r in carried: print(f"   ? unverified {r[0]} | {r[1]} | {r[6]}")
