#!/usr/bin/env python3
"""Verify the hand-added postings in data/manual_posts.json by GET + <title> and return CSV rows.

Why this exists: some live postings sit on sites with no API (LinkedIn, employer career sites,
Teamtailor). They used to be merged into the Sheet by hand, which is how roles got lost. Now
they are data: refresh_roles.py imports verified_rows() and includes them like any other
source, and a post that stops verifying is reported, not silently kept.
Usage (standalone, to append to an existing run): python3 manual_posts.py /tmp/ldn_ds_active_pay.csv
"""
import csv, json, os, re, sys, time, html, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from role_taxonomy import classify
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE))); PATH = os.path.join(ROOT, "data", "manual_posts.json")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept-Language": "en-GB,en;q=0.9"}
SEN = re.compile(r"senior|staff|lead|principal|head|director|manager|\bsr\.?\b|distinguished|vice president|\bvp\b|\bavp\b|executive director", re.I)
DEAD = re.compile(r"no longer|not found|not available|closed|expired|jobs search|\d,\d{3}\+ |\bjobs in (the )?united states", re.I)
# a page whose <title> still names the role but whose body marks it expired (inploi/Haven: "status","EXPIRED" + an Expired badge)
PAGE_DEAD = re.compile(r'"status"\s*,\s*"EXPIRED"|>\s*Expired\s*<|This (job|position|vacancy) (has expired|is no longer (available|open|accepting))|job is not available anymore', re.I)
UNVERIFIED_URLS = []   # posts whose page could not be fetched this run (network/429/5xx): unverified, not closed
def verified_rows(pause=3.0):
    rows = []; UNVERIFIED_URLS.clear()
    if not os.path.exists(PATH): return rows
    for p in json.load(open(PATH))["posts"]:
        try:
            with urllib.request.urlopen(urllib.request.Request(p["url"], headers=UA), timeout=35) as f: page = f.read().decode("utf-8", "replace")
        except Exception as e:
            print(f"[manual] {p['company']} — {p['title']}: {type(e).__name__} (unverified this run)", file=sys.stderr)
            if not (isinstance(e, urllib.error.HTTPError) and e.code in (404, 410)): UNVERIFIED_URLS.append(p["url"].split("?")[0])
            continue
        m = re.search(r"<title>(.*?)</title>", page, re.S); title = html.unescape(m.group(1)) if m else ""
        if re.search(r"data scien", title, re.I) and not DEAD.search(title) and not PAGE_DEAD.search(page):
            rows.append({"Company": p["company"], "Role": p["title"], "Role Type": classify(p["title"]), "Level": "Senior+" if SEN.search(p["title"]) else "Regular/Mid",
                         "Location": p.get("location", "London"), "Apply URL (unique active post)": p["url"], "Status": "Active", "Notes": "manual post, title-verified", "Approx London TC": p.get("comp", "")})
        else:
            print(f"[manual] {p['company']} — {p['title']}: CLOSED or generic title {title[:60]!r}", file=sys.stderr)
        time.sleep(pause)
    print(f"[manual] {len(rows)} hand-added posts verified live", file=sys.stderr)
    return rows
if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ldn_ds_active_pay.csv"
    rows = verified_rows()
    with open(target, newline="", encoding="utf-8") as f: rd = csv.DictReader(f); cols = rd.fieldnames; existing = list(rd)
    have = {r.get("Apply URL (unique active post)", "").split("?")[0] for r in existing}
    add = [r for r in rows if r["Apply URL (unique active post)"].split("?")[0] not in have]
    for r in add:
        if not r.get("Approx London TC"):
            k = "senior" if SEN.search(r["Role"]) else "data scientist"; med = 95 if k == "senior" else 90
            r["Approx London TC"] = f"£{int(med*0.85)}k–£{int(med*1.25)}k (market est.; ITJobsWatch London median £{med}k for {k})"
    # insert before the divider row so the active block stays contiguous
    div = next((i for i, r in enumerate(existing) if (r.get("Company") or "").startswith("— COMPANIES")), len(existing))
    out = existing[:div] + [{c: r.get(c, "") for c in cols} for r in add] + existing[div:]
    with open(target, "w", newline="", encoding="utf-8") as f: w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
    print(f"appended {len(add)} manual posts to {target}")
