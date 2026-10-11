"""Scope regexes shared by refresh_roles.py and build_sheet_rows.py (kept importable without running the refresh)."""
import re
EXCLUDE = re.compile(r"intern|graduate|apprentice|placement|industrial year|working student|fixed.?term|\bFTC\b|\bcontract\b|fractional|part.?time", re.I)
SENIOR = re.compile(r"senior|staff|lead|principal|head|director|manager|\bsr\b|distinguished", re.I)
BRIEF = re.compile(r"product|experiment|causal|measurement|growth|staff|principal|lead", re.I)   # senior + one of these = fits the brief
def via_of(u):
    """How a posting was verified, from its URL host (shown in the Sheet's Notes and on the board)."""
    for k, v in (("greenhouse.io", "Greenhouse API"), ("ocadogroup", "Greenhouse API"), ("coinbase.com", "Greenhouse API"), ("ashbyhq.com", "Ashby API"), ("lever.co", "Lever API"),
                 ("jobs.workable.com", "Workable feed"), ("workable.com", "Workable API"), ("smartrecruiters", "SmartRecruiters API"), ("pinpointhq", "Pinpoint API"),
                 ("myworkdayjobs", "Workday API"), ("teamtailor", "Teamtailor API"), ("amazon.jobs", "amazon.jobs API"), ("google.com", "google.com post (title verified)"),
                 ("linkedin.com", "LinkedIn (title verified)"), ("tiktok.com", "careers.tiktok.com (title verified)"), ("lifeatspotify", "lifeatspotify.com (title verified)")):
        if k in u: return v
    return "employer site (title verified)"
NOT_LONDON = re.compile(r"united kingdom\s*[-–]\s*(?!london)[a-z]|\b(sunbury|cambridge|manchester|leeds|edinburgh|bristol|birmingham|glasgow|cardiff|oxford|reading|luton|leicester|nottingham|sheffield|belfast|newcastle|welwyn|peterborough|brighton|milton keynes|hemel)\b", re.I)
def london_ok(loc):
    """London or London-eligible: names London, or is UK-wide / remote-UK, but not a specific other UK city on its own."""
    l = (loc or "").lower()
    if "london" in l: return True
    if "remote" in l or "any location" in l or "hybrid" in l: return True
    return not NOT_LONDON.search(l)
def norm_loc(loc):
    l = (loc or "").strip()
    l = re.sub(r"\s*\(verify\)", "", l)
    return l or "London"
