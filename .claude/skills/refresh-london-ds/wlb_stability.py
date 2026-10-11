#!/usr/bin/env python3
"""Work-life balance (WLB) and stability: how they are assessed and classified.

These are RESEARCHED judgements, never computed from job-post text. The method, kept here so
it survives any page or artifact being deleted:

WLB (a score out of 5, per company, data-science cohort where available)
  Sources, in order of preference: Glassdoor UK — the Data Science / Analytics cohort rating if
  the sample is >= 10 reviews, else the company-wide rating; Levels.fyi WLB reviews; Blind
  threads as colour only. Record the source and date with the score. Thresholds used on the
  board: > 4.5 strong, 4.0-4.5 moderate, < 4.0 weak; null = not researched (shown as such, never
  guessed). A company with a documented long-hours culture (e.g. Revolut, QuantumBlack) is
  "weak" even if a thin sample scores higher.

Stability (one of Growing / Stable / Caution), from 2024-26 layoff reporting
  Growing  — no company-wide layoff round in the last ~24 months; net hiring in data/analytics;
             positive financial signal (profit, funding, licence, volume).
  Stable   — steady; any cuts were small, local, or did not touch data/analytics.
  Caution  — a recent round touched the function or the London office, a large company-wide
             cut (>= ~10%), a weak financial signal, or a regulatory overhang.
  Sources: company statements, FT/Reuters/Sifted/TechCrunch layoff reporting, layoffs.fyi,
  Companies House filings for UK-registered firms. Record the evidence sentence and date.

How the board uses them: fit, WLB and stability are shown as chips; WLB and stability from this
file are merged into any role at that company; a company not in the file shows
"not researched". Add or refresh an entry by editing data/wlb_stability.json with the score,
tag, evidence and date — never by inferring from the posting.
"""
import json, os
PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "data", "wlb_stability.json")
def load():
    return json.load(open(PATH))["companies"] if os.path.exists(PATH) else {}
def wlb_class(w):
    return "na" if w is None else "hi" if w > 4.5 else "mid" if w >= 4.0 else "lo"
def lookup(company, table=None):
    """Return {'wlb','wlb_source','wlb_note','stability','stability_evidence','as_of'} or None."""
    table = table if table is not None else load()
    key = company.strip().lower()
    for name, rec in table.items():
        if name.lower() == key or key in [a.lower() for a in rec.get("aliases", [])]: return rec
    return None
if __name__ == "__main__":
    t = load(); print(f"{len(t)} companies with researched WLB/stability")
    for n, r in t.items(): print(f"  {n:34s} WLB {r.get('wlb')}  {r.get('stability'):8s} {r.get('as_of')}")
