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
    prev_date = datetime.date.fromtimestamp(os.path.getmtime(PREV)).isoformat()      # when the previous rows were generated
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
    return next((k for k, ts in unv.items() for t in ts if f"/{t}" in url or f"//{t}." in url), None)
REASON = {"spa": "JS site; Playwright absent in this run"}
closed, carried = [], []
for v in missing:
    k = unreadable(v[6])
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
print(f"[sheet] {len(out)} Standard DS rows at {len({r[0] for r in out})} employers; {len(new)} new, {len(closed)} closed, {len(carried)} carried forward unverified since {prev_date}; "
      f"{len(sa)} set-aside rows; {len(values)} rows -> A2:I{len(values)+1}; wrote {jp}")
for r in new: print(f"   + {r[0]} | {r[1]} | {r[4]} | {r[5]}")
for c in closed: print(f"   - {c[0]} | {c[1]} | {c[6]}")
