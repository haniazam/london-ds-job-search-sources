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
COMPANIES = [
    ("OpenAI", [
        ("Data Scientist, Safety", "https://jobs.ashbyhq.com/openai/90c711dc-5f50-46e3-a5ab-82359a56d683", True),
        ("DS, Integrity Measurement", "https://openai.com/careers/data-scientist-integrity-measurement-london-uk/", False),
        ("DS, Monitoring Ops", "https://datasciencejobs.com/jobs/data-scientist-openai-united-kingdom-11/", False),
        ("Protection Scientist Engineer", "https://openai.com/careers/protection-scientist-engineer-intelligence-and-investigations-london-uk/", False),
    ]),
    ("Citadel Securities", [
        ("Data Scientist (Expression of Interest)", "https://www.citadelsecurities.com/careers/details/data-scientist/", True),
    ]),
    ("Revolut", [
        ("Senior Data Scientist", "https://www.revolut.com/careers/position/1a0f390b-ed4a-441a-9535-82d0e185906a/", True),
        ("Senior DS (Computer Vision)", "https://www.revolut.com/careers/position/senior-data-scientist-computer-vision-85b790a2-ca60-4095-a28f-b4e29f0136eb/", False),
        ("DS (Risk)", "https://www.revolut.com/careers/position/data-scientist-risk-46917c00-41ca-4c82-be38-00894cc2c136/", False),
        ("DS (NLP / Deep-Learning Eng)", "https://www.revolut.com/careers/position/data-scientist-nlp-deep-learning-engineer-7fdeec15-cd49-4ca9-b509-ae6ca2613cd5/", False),
        ("DS (Core)", "https://www.revolut.com/careers/position/76be454e-fe77-4daf-abd6-9ae9c41afd70/", False),
    ]),
    ("Stripe", [
        ("Data Scientist, EMEA", "https://stripe.com/jobs/listing/data-scientist-emea/7516102", True),
    ]),
    ("Google DeepMind", [
        ("Applied Data Scientist — London (FTC)", "https://job-boards.greenhouse.io/deepmind/jobs/7126983", True),
        ("Research Scientist, Gemini Diffusion", "https://job-boards.greenhouse.io/deepmind/jobs/7700399", False),
        ("Research Scientist, Reinforcement Learning", "https://job-boards.greenhouse.io/deepmind/jobs/7716037", False),
        ("Research Scientist, World Models (London/Toronto)", "https://job-boards.greenhouse.io/deepmind/jobs/7372638", False),
        ("Research Engineer, Frontier Safety", "https://job-boards.greenhouse.io/deepmind/jobs/7493360", False),
    ]),
    ("The Trade Desk", [
        ("Staff Applied Scientist / Data Scientist II", "https://careers.thetradedesk.com/jobs/5118594007/staff-applied-scientist", True),
    ]),
    ("G-Research", [
        ("Data Scientist", "https://www.gresearch.com/vacancies/data-scientist/", True),
        ("Machine Learning Researcher", "https://www.gresearch.com/vacancies/machine-learning-researcher/", False),
        ("NLP Researcher", "https://www.gresearch.com/vacancies/natural-language-processing-researcher/", False),
        ("Machine Learning Engineer", "https://www.gresearch.com/vacancies/machine-learning-engineer/", False),
    ]),
    ("Spotify", [
        ("Senior Data Scientist — Platform Mission", "https://www.lifeatspotify.com/jobs/senior-data-scientist-platform-mission", True),
        ("Senior DS — Global Strategy & Operations", "https://www.lifeatspotify.com/jobs/senior-data-scientist-global-strategy-operations-people", False),
        ("DS — Subscriptions", "https://www.lifeatspotify.com/jobs/data-scientist-subscriptions-2", False),
        ("DS — Platform & Partner Experience", "https://www.lifeatspotify.com/jobs/data-scientist-platform-partner-experience", False),
        ("DS — Content Understanding", "https://www.lifeatspotify.com/jobs/data-scientist-content-understanding", False),
    ]),
    ("Monzo", [
        ("Lead Data Scientist", "https://job-boards.greenhouse.io/monzo/jobs/6369658", True),
        ("Senior ML Scientist, Borrowing", "https://job-boards.greenhouse.io/monzo/jobs/7686352", False),
    ]),
    ("Google", [
        ("Product Data Scientist (L5) — London search", "https://www.google.com/about/careers/applications/jobs/results?location=London%2C+UK", True),
    ]),
    ("Bloomberg", [
        ("Economics Data Scientist", "https://bloomberg.avature.net/careers/JobDetail/Bloomberg-Economics-Data-Scientist/19933", True),
        ("Data Scientist (req 111117)", "https://careers.bloomberg.com/job/detail/111117", False),
        ("DS search (all live)", "https://bloomberg.avature.net/careers/SearchJobs/data%20scientist", False),
    ]),
    ("QuantumBlack (McKinsey)", [
        ("Senior Data Scientist I", "https://www.mckinsey.com/careers/search-jobs/jobs/seniordatascientisti-quantumblackaibymckinsey-108819", True),
        ("Data Scientist I", "https://www.mckinsey.com/careers/search-jobs/jobs/datascientisti-quantumblackaibymckinsey-102714", False),
    ]),
    ("Man Group", [
        ("Senior DS — Responsible Investment", "https://job-boards.eu.greenhouse.io/mangroup/jobs/4863672101", True),
        ("Senior DS Analyst (12m FTC)", "https://job-boards.eu.greenhouse.io/mangroup/jobs/4807838101", False),
        ("Quant Researcher — Macro", "https://job-boards.eu.greenhouse.io/mangroup/jobs/4724414101", False),
        ("Quant Researcher — Discretionary", "https://job-boards.eu.greenhouse.io/mangroup/jobs/4772820101", False),
    ]),
    ("TikTok", [
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


if __name__ == "__main__":
    main()
