#!/usr/bin/env python3
"""Build the London DS Job Board page from the refresh output (no hand-merging, ever).

Input : /tmp/ldn_ds_active_pay.csv (refresh_roles.py -> pay_enrich.py), filtered to
        Role Type == Standard DS; data/wlb_stability.json for researched WLB/stability;
        data/set_aside.json for the no-role / unverified entries (edit it with reasons).
Output: /tmp/london-ds-board.html — publish it to the SAME artifact file path / url so the
        link never changes. The page is board_template.html with the data arrays filled in.
Score (printed on the page): fit (Strong 4 / Stretch 2 / Level gap 1) + comp (ceiling >= 150k:
4 posted/sourced, 3 estimated; 120-149k: 2; 100-119k: 1) + London-proper 1 + verified 1.
Usage: python3 build_board.py [/tmp/ldn_ds_active_pay.csv] [/tmp/london-ds-board.html]
"""
import csv, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from wlb_stability import load as load_wlb, lookup
from role_taxonomy import classify
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ldn_ds_active_pay.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/london-ds-board.html"
from refresh_roles_scope import BRIEF, via_of, EXCLUDE, london_ok, norm_loc
SEN = re.compile(r"senior|staff|lead|principal|head|director|manager|\bsr\.?\b|distinguished|vice president|\bvp\b|\bavp\b|executive director", re.I)
def comp_parse(c):
    c = c or ""; m = re.search(r"£(\d+)k\s*[–-]\s*£(\d+)k", c); mp = re.search(r"£(\d+)k\+", c); mu = re.search(r"up to £(\d+)k", c); mf = re.search(r"from £(\d+)k", c)
    lo, hi = (int(m.group(1)), int(m.group(2))) if m else (int(mp.group(1)), None) if mp else (None, int(mu.group(1))) if mu else (int(mf.group(1)), None) if mf else (None, None)
    prov = "p" if "(posted" in c else "s" if "sourced" in c and "L6" not in c else "m" if "market est" in c else "a" if c else "n"
    return lo, hi, prov
def loctype(loc):
    loc = loc or ""
    if re.search(r"remote", loc, re.I) and not re.search(r"london", loc, re.I): return "Remote-UK"
    if re.search(r"london", loc, re.I) and re.search(r";|/|\+|,\s*[A-Z]|Dublin|Barcelona|Cardiff|remote", loc, re.I) and loc.strip().lower() not in ("london", "london, united kingdom", "london, england", "london, uk", "london office"): return "London (+ other locations)"
    return "London" if re.search(r"london", loc, re.I) else "UK (London-eligible)"
wlb_tab = load_wlb(); rows = []
with open(SRC, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        url = r.get("Apply URL (unique active post)", "")
        if not url.startswith("http"): continue
        if (r.get("Role Type") or classify(r["Role"])) != "Standard DS": continue   # older CSVs lack the column
        if EXCLUDE.search(r["Role"]): continue                                       # scope rule (FTC, fractional, intern…)
        if not london_ok(r.get("Location", "")): continue                              # a non-London UK city on its own is out
        r["Location"] = norm_loc(r.get("Location", "")); ver = 0 if (r.get("Status") or "Active").startswith("Unverified") else 1
        title = r["Role"].strip(); lv = "Senior+" if SEN.search(title) else "Regular/Mid"; lo, hi, prov = comp_parse(r.get("Approx London TC", ""))
        loc = loctype(r.get("Location", "")); brief = lv == "Senior+" and bool(BRIEF.search(title))
        fit = 4 if brief else 2 if lv == "Senior+" else 1; ceil = hi if hi is not None else (lo or 0)
        comp = (4 if prov in "ps" else 3) if ceil >= 150 else 2 if ceil >= 120 else 1 if ceil >= 100 else 0
        score = fit + comp + (1 if loc == "London" else 0) + ver
        w = lookup(r["Company"], wlb_tab) or {}
        rows.append({"co": r["Company"], "t": title, "lv": "sr" if lv == "Senior+" else "mid", "lo": lo, "hi": hi, "prov": prov, "loc": None if loc == "London" else loc,
                     "via": via_of(url), "url": r["Apply URL (unique active post)"], "new": "NEW" in (r.get("Notes", "") or ""), "brief": brief,
                     "score": score, "parts": {"fit": fit, "comp": comp, "loc": 1 if loc == "London" else 0, "ver": ver},
                     "fit": "Strong" if brief else "Stretch" if lv == "Senior+" else "Level gap",
                     "wlb": w.get("wlb"), "stab": w.get("stability", "Not researched"), "wlbCav": w.get("wlb_note", "Not researched."), "layoff": w.get("stability_evidence", "Not researched."),
                     "jd": None, "quals": None, "fitCav": None, "def": "apply" if score >= 7 else "monitor",
                     "next": ("Apply — pay clears the floor on the employer's own or a sourced figure; confirm sponsorship and TC structure in the first call." if prov in "ps" and ceil >= 150
                              else "Gate TC early — the ceiling is an estimate, not a published figure." if ceil >= 150
                              else "Base is published and below the floor — ask about equity and bonus before investing time." if prov == "p"
                              else "Pay not published — gate total comp in the first conversation.")})
rows.sort(key=lambda r: (r["co"].lower(), 0 if r["lv"] == "sr" else 1, r["t"]))
aside_path = os.path.join(ROOT, "data", "set_aside.json")
aside = json.load(open(aside_path)) if os.path.exists(aside_path) else []
tpl = open(os.path.join(HERE, "board_template.html"), encoding="utf-8").read()
page = (tpl.replace("__ROLES__", json.dumps(rows, ensure_ascii=False)).replace("__ASIDE__", json.dumps(aside, ensure_ascii=False))
           .replace("__NROLES__", str(len(rows))).replace("__NCOS__", str(len({r["co"] for r in rows}))).replace("__NASIDE__", str(len(aside))))
open(OUT, "w", encoding="utf-8").write(page)
print(f"WROTE {OUT}: {len(rows)} Standard DS roles at {len({r['co'] for r in rows})} employers; {len(aside)} set-aside; WLB/stability for {sum(1 for r in rows if r['wlb'] is not None or r['stab']!='Not researched')} rows")
