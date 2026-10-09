#!/usr/bin/env python3
"""Fetch full job descriptions from the live posting URLs and build a document.

RUN THIS IN AN ENVIRONMENT WITH OUTBOUND WEB ACCESS. In the environment the URL
list was captured, the egress proxy 403'd every host, so this could not run.

Covers ALL links from the Target List tab (columns D–H), grouped by company,
with the primary (column D) posting marked.

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

# Company -> list of (label, url, is_primary). Order = document order.
# Primary = column D (the role each tailored resume targets).
# URL list refreshed 2026-10-09 against each employer's live ATS (Greenhouse /
# Ashby open APIs where available). Prefer Greenhouse/Ashby URLs — the scraper
# pulls clean JD text from their JSON APIs. Entries marked "[walled]" sit behind
# Cloudflare/JS and need the browser variant or manual capture; "[search]"
# entries are listing pages to monitor (no single live JD to scrape).
COMPANIES = [
    ("OpenAI", [
        ("Data Scientist, Safety", "https://jobs.ashbyhq.com/openai/90c711dc-5f50-46e3-a5ab-82359a56d683", True),
        # Live London role (Ashby). Replaces the two openai.com/careers links that 403'd.
        ("Protection Scientist Engineer, Integrity — London", "https://jobs.ashbyhq.com/openai/3fefc615-6950-4a29-9214-eefdc4e659e3", False),
    ]),
    ("Citadel Securities", [
        # [walled] Cloudflare bot-check blocks plain fetch AND headless Chromium ("security verification") — manual paste only.
        ("Data Scientist (Expression of Interest)", "https://www.citadelsecurities.com/careers/details/data-scientist/", True),
    ]),
    ("Revolut", [
        # [walled] Cloudflare challenge blocks plain fetch AND headless Chromium ("Just a moment...") — manual paste only; no public API.
        ("Senior Data Scientist", "https://www.revolut.com/careers/position/1a0f390b-ed4a-441a-9535-82d0e185906a/", True),
        ("Senior DS (Computer Vision)", "https://www.revolut.com/careers/position/senior-data-scientist-computer-vision-85b790a2-ca60-4095-a28f-b4e29f0136eb/", False),
        ("DS (Risk)", "https://www.revolut.com/careers/position/data-scientist-risk-46917c00-41ca-4c82-be38-00894cc2c136/", False),
        ("DS (NLP / Deep-Learning Eng)", "https://www.revolut.com/careers/position/data-scientist-nlp-deep-learning-engineer-7fdeec15-cd49-4ca9-b509-ae6ca2613cd5/", False),
        ("DS (Core)", "https://www.revolut.com/careers/position/76be454e-fe77-4daf-abd6-9ae9c41afd70/", False),
    ]),
    ("Stripe", [
        # [search] DS, EMEA (7516102) no longer live; Stripe is on Greenhouse (board 'stripe'), no London DS currently.
        ("Data Scientist — London search", "https://stripe.com/jobs/search?l=London", True),
    ]),
    ("Google DeepMind", [
        # [search] DeepMind left the 'deepmind' Greenhouse board (all old IDs 404); roles now only on the JS careers site.
        ("DeepMind careers — London DS/RS (ATS moved off Greenhouse)", "https://deepmind.google/about/careers/", True),
    ]),
    ("The Trade Desk", [
        # [search] Staff Applied Scientist (5118594007) gone; board 'thetradedesk' live but no London DS/applied-sci currently.
        ("Applied Scientist / DS — careers board", "https://job-boards.greenhouse.io/thetradedesk", True),
    ]),
    ("G-Research", [
        # 'data-scientist' vacancy is filled/removed; these slugs are live as of 2026-10-09.
        ("Machine Learning Researcher", "https://www.gresearch.com/vacancies/machine-learning-researcher/", True),
        ("NLP Researcher", "https://www.gresearch.com/vacancies/natural-language-processing-researcher/", False),
        ("Machine Learning Engineer", "https://www.gresearch.com/vacancies/machine-learning-engineer/", False),
        ("AI Engineer", "https://www.gresearch.com/vacancies/ai-engineer/", False),
    ]),
    ("Spotify", [
        # [search] Old lifeatspotify slugs all 404; roles churn fast, so monitor the London Data Science search.
        ("Data Science — London search", "https://www.lifeatspotify.com/jobs?c=data-science&l=london", True),
    ]),
    ("Monzo", [
        ("Lead Data Scientist", "https://job-boards.greenhouse.io/monzo/jobs/6369658", True),
        # 'Senior ML Scientist, Borrowing' (7686352) gone; nearest current role + extra live DS roles.
        ("Senior ML Manager, Borrowing", "https://job-boards.greenhouse.io/monzo/jobs/7996955", False),
        ("Senior Data Scientist", "https://job-boards.greenhouse.io/monzo/jobs/6180814", False),
        ("Staff Data Scientist", "https://job-boards.greenhouse.io/monzo/jobs/8232732", False),
    ]),
    ("Google", [
        ("Product Data Scientist (L5) — London search", "https://www.google.com/about/careers/applications/jobs/results?location=London%2C+UK", True),
    ]),
    ("Bloomberg", [
        # [walled] Avature JobDetail 19933 expired (404); careers.bloomberg.com 403s. Monitor the Avature DS search.
        ("Data Scientist — search (Avature)", "https://bloomberg.avature.net/careers/SearchJobs/data%20scientist", True),
    ]),
    ("QuantumBlack (McKinsey)", [
        # [walled] mckinsey.com careers are JS-rendered (plain fetch times out) — browser variant gets them (no Cloudflare).
        # 'Senior Data Scientist I' 108819 is dead (upstream error); Data Scientist I 102714 is the live London role (2026-10-09).
        ("Data Scientist I — London", "https://www.mckinsey.com/careers/search-jobs/jobs/datascientisti-quantumblackaibymckinsey-102714", True),
    ]),
    ("Man Group", [
        # All four old Greenhouse IDs expired; these are the current live London quant roles (board 'mangroup', EU).
        ("Quant Researcher — Macro; Futures/FX", "https://job-boards.eu.greenhouse.io/mangroup/jobs/4966466101", True),
        ("Quant Researcher — Macro Trend", "https://job-boards.eu.greenhouse.io/mangroup/jobs/4880305101", False),
        ("Quant — Systematic Multi-Strategy", "https://job-boards.eu.greenhouse.io/mangroup/jobs/4965180101", False),
        ("Quantitative Developer — Systematic", "https://job-boards.eu.greenhouse.io/mangroup/jobs/4844843101", False),
    ]),
    ("TikTok", [
        # [walled] careers.tiktok.com own ATS, JS-rendered — browser variant / manual.
        ("Senior Data Scientist, Operations", "https://careers.tiktok.com/position/7344026106091604275/detail", True),
    ]),
    ("XTX Markets", [
        ("Careers landing (no DS live — monitoring only)", "https://www.xtxmarkets.com/careers/", True),
    ]),
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
           "Fetched by `scripts/fetch_jds.py` from the URLs in `docs/job-posting-urls.md` "
           "(Target List columns D–H). Primary = the role each tailored resume targets.\n"]
    for company, postings in COMPANIES:
        out.append(f"\n========================================================\n"
                   f"## {company}\n")
        for label, url, primary in postings:
            tag = " — **PRIMARY**" if primary else ""
            print(f"fetching {company} :: {label} …", file=sys.stderr)
            out.append(f"\n### {label}{tag}\n\n<{url}>\n")
            try:
                out.append("```\n" + fetch_jd(url) + "\n```\n")
            except Exception as e:  # noqa: BLE001
                out.append(f"**Could not fetch:** {type(e).__name__}: {e}\n")
    Path("docs").mkdir(exist_ok=True)
    Path("docs/job-descriptions-scraped.md").write_text("\n".join(out), encoding="utf-8")
    n = sum(len(p) for _, p in COMPANIES)
    print(f"wrote docs/job-descriptions-scraped.md ({n} postings)", file=sys.stderr)
    print("NEXT (assistant action, not the script): upload "
          "docs/job-descriptions-scraped.md to Google Drive folder "
          "1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI via the Drive connector "
          "(create_file, text/plain). See docs/RUN_JD_SCRAPER.md.", file=sys.stderr)


if __name__ == "__main__":
    main()
