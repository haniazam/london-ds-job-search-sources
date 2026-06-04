#!/usr/bin/env python3
"""Fetch full job descriptions from the live posting URLs and build a document.

RUN THIS IN AN ENVIRONMENT WITH OUTBOUND WEB ACCESS. In the environment the URL
list was captured, the egress proxy 403'd every host, so this could not run.

Strategy per host:
  * Greenhouse (job-boards[.eu].greenhouse.io/<board>/jobs/<id>) -> the open
    JSON API boards-api.greenhouse.io/v1/boards/<board>/jobs/<id> (clean HTML
    in `.content`, HTML-unescaped).
  * Ashby (jobs.ashbyhq.com/<org>/<id>) -> api.ashbyhq.com/posting-api/job-board/
    <org>?includeCompensation=true, then match the posting id.
  * Everything else -> fetch the HTML and strip tags (best effort; some sites
    render JD via JS and may need a headless browser).

Writes: docs/job-descriptions-scraped.md

Usage:  python3 scripts/fetch_jds.py
"""
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (compatible; JD-fetch/1.0)"}
TIMEOUT = 30

# (Company, Role label, primary URL). Order = document order.
ROLES = [
    ("OpenAI", "Data Scientist, Safety", "https://jobs.ashbyhq.com/openai/90c711dc-5f50-46e3-a5ab-82359a56d683"),
    ("Citadel Securities", "Data Scientist", "https://www.citadelsecurities.com/careers/details/data-scientist/"),
    ("Stripe", "Data Scientist, EMEA", "https://stripe.com/jobs/listing/data-scientist-emea/7516102"),
    ("Google DeepMind", "Applied Data Scientist (London, FTC)", "https://job-boards.greenhouse.io/deepmind/jobs/7126983"),
    ("The Trade Desk", "Staff Applied Scientist / Data Scientist II", "https://careers.thetradedesk.com/jobs/5118594007/staff-applied-scientist"),
    ("G-Research", "Data Scientist", "https://www.gresearch.com/vacancies/data-scientist/"),
    ("Spotify", "Senior Data Scientist — Platform Mission", "https://www.lifeatspotify.com/jobs/senior-data-scientist-platform-mission"),
    ("Monzo", "Lead Data Scientist", "https://job-boards.greenhouse.io/monzo/jobs/6369658"),
    ("Google", "Product Data Scientist (L5) — London search", "https://www.google.com/about/careers/applications/jobs/results?location=London%2C+UK"),
    ("Bloomberg", "Economics Data Scientist", "https://bloomberg.avature.net/careers/JobDetail/Bloomberg-Economics-Data-Scientist/19933"),
    ("Man Group", "Senior Data Scientist — Responsible Investment", "https://job-boards.eu.greenhouse.io/mangroup/jobs/4863672101"),
    ("TikTok", "Senior Data Scientist, Operations", "https://careers.tiktok.com/position/7344026106091604275/detail"),
    ("Revolut", "Senior Data Scientist", "https://www.revolut.com/careers/position/1a0f390b-ed4a-441a-9535-82d0e185906a/"),
    ("QuantumBlack (McKinsey)", "Senior Data Scientist", "https://www.mckinsey.com/careers/search-jobs/jobs/seniordatascientisti-quantumblackaibymckinsey-108819"),
]

GH_RE = re.compile(r"job-boards(?:\.eu)?\.greenhouse\.io/([^/]+)/jobs/(\d+)")
ASHBY_RE = re.compile(r"jobs\.ashbyhq\.com/([^/]+)/([0-9a-f-]+)")


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", "replace")


def strip_html(s):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|li|h[1-6]|tr)>", "\n", s)
    s = re.sub(r"(?i)<li[^>]*>", "• ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\n[ \t]+", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def fetch_jd(url):
    m = GH_RE.search(url)
    if m:
        board, jid = m.groups()
        data = json.loads(get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{jid}"))
        title = data.get("title", "")
        loc = (data.get("location") or {}).get("name", "")
        return f"{title}  ({loc})\n\n" + strip_html(data.get("content", ""))
    m = ASHBY_RE.search(url)
    if m:
        org, jid = m.groups()
        data = json.loads(get(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true"))
        for job in data.get("jobs", []):
            if job.get("id") == jid or jid in json.dumps(job):
                return f"{job.get('title','')}  ({job.get('location','')})\n\n" + strip_html(job.get("descriptionHtml") or job.get("description", ""))
        titles = [j.get("title", "") for j in data.get("jobs", [])]
        return "Posting id not found in Ashby board. Titles seen:\n- " + "\n- ".join(titles)
    # generic
    return strip_html(get(url))


def main():
    out = ["# London DS — Full Job Descriptions (scraped from live postings)\n",
           "Fetched by `scripts/fetch_jds.py` from the URLs in `docs/job-posting-urls.md`.\n"]
    for company, role, url in ROLES:
        print(f"fetching {company} …", file=sys.stderr)
        out.append(f"\n---\n\n## {company} — {role}\n\n<{url}>\n")
        try:
            out.append("```\n" + fetch_jd(url) + "\n```\n")
        except Exception as e:  # noqa: BLE001
            out.append(f"**Could not fetch:** {type(e).__name__}: {e}\n")
    Path("docs").mkdir(exist_ok=True)
    Path("docs/job-descriptions-scraped.md").write_text("\n".join(out), encoding="utf-8")
    print("wrote docs/job-descriptions-scraped.md", file=sys.stderr)


if __name__ == "__main__":
    main()
