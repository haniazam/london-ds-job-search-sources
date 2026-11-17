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
key = lambda u: (u or "").split("?")[0].rstrip("/")
prev_rows, prev_date = [], None
if PREV:
    prev_rows = json.load(open(PREV))
    # the Sheet's rows date from the last refresh = the newest committed snapshot before DATE (the JSON's mtime is just now)
    SNAP = os.path.join(ROOT, "data", "snapshots")
    snaps = sorted(f for f in (os.listdir(SNAP) if os.path.isdir(SNAP) else []) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.csv", f) and f[:10] < DATE)
    prev_date = snaps[-1][:10] if snaps else datetime.date.fromtimestamp(os.path.getmtime(PREV)).isoformat()
else:                                                                               # default baseline: newest snapshot strictly before DATE
    SNAP = os.path.join(ROOT, "data", "snapshots")
    snaps = sorted(f for f in (os.listdir(SNAP) if os.path.isdir(SNAP) else []) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.csv", f) and f[:10] < DATE)
    if snaps:
        prev_rows = [r for r in csv.reader(open(os.path.join(SNAP, snaps[-1]), encoding="utf-8"))][1:]
        prev_date = snaps[-1][:10]
        print(f"[sheet] no previous rows given; diffing against data/snapshots/{snaps[-1]}", file=sys.stderr)
prev_active = {key(r[6]): r for r in prev_rows if len(r) >= 9 and r[6].startswith("http")}
seen, out = set(), []
norm_title = lambda t: re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
own_board = {(r["Company"].lower(), norm_title(r["Role"])) for r in rows if "linkedin.com" not in r["Apply URL (unique active post)"]}
for r in sorted(rows, key=lambda r: (r["Company"].lower(), r["Level"] != "Senior+", r["Role"].lower())):
    u = key(r["Apply URL (unique active post)"])
    if u in seen: continue
    # a LinkedIn mirror of a post that is on the employer's own board is the same role, not a second unique post
    if "linkedin.com" in u and (r["Company"].lower(), norm_title(r["Role"])) in own_board: seen.add(u); continue
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
REASON = {"spa": "JS site not reachable this run (Playwright absent or fetch failed)", "manual": "post page fetch failed this run",
          "page": "post page fetch failed this run"}
import urllib.request
GENERIC = re.compile(r"jobs at |job search|all jobs|open roles|\d,\d{3}\+|search jobs|careers$|page not found|not found", re.I)
def page_check(url, role):
    """A row the boards did not return this run is re-verified by its own page before it may close:
    'live' (200, still on the post, <title> names the role), 'closed' (404 / redirected to a listing / generic title) or 'error'."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36", "Accept": "text/html"})
        with urllib.request.urlopen(req, timeout=30) as f:
            body = f.read(400000).decode("utf-8", "ignore"); final = f.geturl()
    except urllib.error.HTTPError as e:
        return "closed" if e.code in (404, 410) else "error"
    except Exception:
        return "error"
    t = (re.findall(r"<title[^>]*>(.*?)</title>", body, re.S | re.I) or [""])[0].strip()
    m = re.match(r"https?://jobs\.smartrecruiters\.com/([^/]+)/(\d+)", url)      # SmartRecruiters renders closed posts; the API knows
    if m:
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://api.smartrecruiters.com/v1/companies/{m.group(1)}/postings/{m.group(2)}", headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as f:
                return "live" if json.load(f).get("active") else "closed"
        except Exception: pass
    if not t: return "error"                                                        # JS shell (e.g. jobs.apple.com): nothing to judge by
    if GENERIC.search(t) and not re.search(r"scientist|data science", t, re.I): return "closed"
    core = "scientist" if re.search(r"scientist", role, re.I) else role.split(",")[0].split(" - ")[0].strip()
    if re.search(re.escape(core), t, re.I) and key(final).split("/")[-1] and key(final) == key(url) or re.search(re.escape(core), t, re.I) and key(url).split("/")[-1] in final:
        return "live"
    return "closed"
reg_path = "/tmp/ldn_ds_registry.json"; REGRUN = json.load(open(reg_path)) if os.path.exists(reg_path) else {}
HOSTED = {"pinpoint": "//{t}.", "teamtailor": "//{t}.", "recruitee": "//{t}.", "workday": "//{t}.", "oraclehcm": "//{t}/", "successfactors": "//{t}/", "apple": "//{t}/"}
def enumerated(url):
    """True when the run read the board this URL belongs to, so the board's own verdict (not returned = closed) stands."""
    u = url.lower()
    return any((HOSTED[p].format(t=t.lower()) in u) if p in HOSTED else (f"/{t.lower()}/" in u)
               for p, ts in REGRUN.items() for t in ts)
closed, carried, kept = [], [], []
for v in missing:
    k = unreadable(v[6])
    if not k and not enumerated(v[6]):
        verdict = page_check(v[6], v[1])
        if verdict == "live":
            row = list(v); row[7] = "Active"
            prior = re.sub(r"^(not re-verified on \S+ \([^)]*\); last verified [^;]*; )+", "", re.sub(r"^NEW \(refresh [^)]*\); ", "", row[8]))
            prior = re.sub(r"^(re-verified by page fetch on \S+ \(board not enumerated\); )+", "", prior)
            row[8] = f"re-verified by page fetch on {DATE} (board not enumerated); " + prior
            out.append(row); kept.append(row); continue
        if verdict == "error": k = "page"
    if k:
        row = list(v); row[7] = "Unverified"
        prior = re.sub(r"^(not re-verified on \S+ \([^)]*\); last verified [^;]*; )+", "", re.sub(r"^NEW \(refresh [^)]*\); ", "", row[8]))
        row[8] = f"not re-verified on {DATE} ({REASON.get(k, 'board API rate-limited')}); last verified {prev_date}; " + prior
        out.append(row); carried.append(row)
    else: closed.append(v)
out.sort(key=lambda r: (r[0].lower(), r[3] != "Senior+", r[1].lower()))
# ---- set-aside: closed roles in, re-verified roles out ----
sa_path = os.path.join(ROOT, "data", "set_aside.json"); sa = json.load(open(sa_path))
live_names = {f"{r[0]} ({r[1]})" for r in out}
sa = [e for e in sa if not (e[2] == "unv" and any(e[0].startswith(r[0]) and r[1].split(" - ")[0].split(",")[0] in e[0] for r in out) and e[0] in live_names)]
sa = [e for e in sa if not (e[2] == "unv" and e[0] == "Wise (Senior DS Lead, AML Risk)" and any(r[0] == "Wise" and "AML Risk" in r[1] for r in out))]
# a role parked as closed on an earlier refresh that is live again (re-posted, same company + title) leaves set-aside
sa = [e for e in sa if not (e[2] == "closed" and e[0] in live_names)]
have = {e[0] for e in sa}
for c in closed:
    name = f"{c[0]} ({c[1]})"
    if name not in have:
        sa.append([name, f"Closed — not returned by {via_of(c[6]).replace('verified via ', '')} on the {DATE} refresh (was live on {prev_date})", "closed"]); have.add(name)
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
print(f"[sheet] {len(out)} Standard DS rows at {len({r[0] for r in out})} employers; {len(new)} new, {len(closed)} closed, {len(carried)} carried forward unverified, {len(kept)} kept live by page fetch since {prev_date}; "
      f"{len(sa)} set-aside rows; {len(values)} rows -> A2:I{len(values)+1}; wrote {jp}")
for r in new: print(f"   + {r[0]} | {r[1]} | {r[4]} | {r[5]}")
for c in closed: print(f"   - {c[0]} | {c[1]} | {c[6]}")
for r in kept: print(f"   = {r[0]} | {r[1]} | page fetch | {r[6]}")
for r in carried: print(f"   ? {r[0]} | {r[1]} | {r[8].split(';')[0]}")
