#!/usr/bin/env python3
"""Headless-browser job-description scraper (for JS-rendered postings).

Companion to scripts/fetch_jds.py. Same 40-posting list (imported), but the
sites that render their JD via JavaScript (McKinsey/Workday, TikTok, Bloomberg
avature, Stripe, Citadel, G-Research, lifeatspotify, thetradedesk, Revolut,
Google) are fetched with a real Chromium browser instead of a plain HTTP GET.
Greenhouse and Ashby still use their open JSON APIs (fast, no browser needed).

RUN THIS IN AN ENVIRONMENT WITH OUTBOUND WEB ACCESS.

Setup:
    pip install playwright
    python -m playwright install chromium
Run:
    python3 scripts/fetch_jds_browser.py

Writes: docs/job-descriptions-scraped.md
"""
import glob
import os
import re
import sys
from pathlib import Path

# Reuse the canonical posting list + API helpers from the plain scraper.
from fetch_jds import COMPANIES, GH_RE, ASHBY_RE, fetch_jd, strip_html  # noqa: E402


def _chromium_executable():
    """Locate a pre-installed Chromium (e.g. PLAYWRIGHT_BROWSERS_PATH on managed
    runners) so we don't depend on `playwright install` matching the pip build."""
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")
    cands = []
    if base:
        cands.append(os.path.join(base, "chromium"))  # common symlink
        cands += sorted(glob.glob(os.path.join(base, "chromium-*/chrome-linux/chrome")))
        cands += sorted(glob.glob(os.path.join(base, "chromium-*/chrome-linux/headless_shell")))
    return next((c for c in cands if os.path.exists(c)), None)


def _proxied():
    """True when outbound HTTPS goes through a proxy with its own CA (managed
    cloud runners). Only then do we relax TLS verification, so normal runs stay
    strict."""
    return bool(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"))


def _launch(p):
    args = ["--ignore-certificate-errors"] if _proxied() else []
    try:
        return p.chromium.launch(headless=True, args=args)
    except Exception:  # noqa: BLE001 — fall back to a pre-installed binary
        exe = _chromium_executable()
        if not exe:
            raise
        return p.chromium.launch(headless=True, executable_path=exe, args=args)

# Optional per-host CSS selector to wait for / extract (best-effort). Falls back
# to document.body.innerText when the selector is absent.
CONTENT_SELECTORS = {
    "stripe.com": "div.JobDetail, main",
    "www.citadelsecurities.com": "main, .careers-detail",
    "www.gresearch.com": "main, article, .vacancy",
    "www.lifeatspotify.com": "main, .job-details",
    "careers.thetradedesk.com": "main, .job, [data-automation-id]",
    "www.revolut.com": "main, article",
    "bloomberg.avature.net": "#content, main, .jobDescription",
    "careers.bloomberg.com": "main, .job-description",
    "www.mckinsey.com": "main, .job-details, .JobDetail",
    "careers.tiktok.com": "main, .jobDetail, .position-detail",
    "www.google.com": "main, c-wiz",
    "datasciencejobs.com": "main, article, .job",
    "openai.com": "main, article",
}


def host_of(url):
    return re.sub(r"^https?://", "", url).split("/")[0]


def fetch_with_browser(page, url):
    page.goto(url, wait_until="networkidle", timeout=60000)
    sel = CONTENT_SELECTORS.get(host_of(url))
    if sel:
        try:
            page.wait_for_selector(sel.split(",")[0].strip(), timeout=8000)
        except Exception:  # noqa: BLE001
            pass
        html = page.content()
        # Prefer the selector's HTML if it matches, else whole page.
        try:
            el = page.query_selector(sel.split(",")[0].strip())
            if el:
                return strip_html(el.inner_html())
        except Exception:  # noqa: BLE001
            pass
        return strip_html(html)
    return strip_html(page.content())


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright not installed. Run: pip install playwright && "
                 "python -m playwright install chromium")

    out = ["# London DS — Full Job Descriptions (headless-browser scrape)\n",
           "Greenhouse/Ashby via JSON API; all other hosts via Chromium "
           "(JS-rendered). Source URLs: `docs/job-posting-urls.md`.\n"]

    with sync_playwright() as p:
        browser = _launch(p)
        context = browser.new_context(
            ignore_https_errors=_proxied(),  # trust the runner's proxy CA
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"))
        page = context.new_page()
        for company, postings in COMPANIES:
            out.append(f"\n========================================================\n"
                       f"## {company}\n")
            for label, url, primary in postings:
                tag = " — **PRIMARY**" if primary else ""
                print(f"fetching {company} :: {label} …", file=sys.stderr)
                out.append(f"\n### {label}{tag}\n\n<{url}>\n")
                try:
                    if GH_RE.search(url) or ASHBY_RE.search(url):
                        text = fetch_jd(url)              # JSON API, no browser
                    else:
                        text = fetch_with_browser(page, url)
                    out.append("```\n" + text.strip() + "\n```\n")
                except Exception as e:  # noqa: BLE001
                    out.append(f"**Could not fetch:** {type(e).__name__}: {e}\n")
        browser.close()

    Path("docs").mkdir(exist_ok=True)
    Path("docs/job-descriptions-scraped.md").write_text("\n".join(out), encoding="utf-8")
    print("wrote docs/job-descriptions-scraped.md", file=sys.stderr)
    print("NEXT (assistant action, not the script): upload "
          "docs/job-descriptions-scraped.md to Google Drive folder "
          "1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI via the Drive connector "
          "(create_file, text/plain). See docs/RUN_JD_SCRAPER.md.", file=sys.stderr)


if __name__ == "__main__":
    main()
