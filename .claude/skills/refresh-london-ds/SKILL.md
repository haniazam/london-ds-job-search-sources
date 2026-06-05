---
name: refresh-london-ds
description: >-
  Refresh the London Data Scientist job search — re-verify which companies have
  ACTIVE, unique London (or London-eligible) Data Science roles, rebuild the
  consolidated Google Sheet (active roles + companies with no role), and
  regenerate the plain-text job-descriptions Google Doc. Use when asked to
  refresh / re-check / update the London DS roles list, the combined jobs sheet,
  or the JD doc. Covers regular/mid AND senior roles; excludes intern/grad.
---

# Refresh London DS job list + JD doc

Two artdefacts live in the Google Drive folder
`1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI` ("Job Descriptions - London DS 150k"):

1. **Consolidated sheet** — one row per active unique London DS job URL (with a
   `Level` column: Regular/Mid vs Senior+), then companies with no active role.
2. **JD doc** — plain text (NO markdown), one section per role with
   responsibilities + requirements + apply link.

This skill regenerates both. The scripts do the scraping; **the assistant does
the Drive upload** (the Drive connector is only available to the model, not to
shell scripts).

## Prerequisites
- **Network access must be "Full"** in the environment settings (the scrapers
  hit external sites). Start a fresh session after changing it.
- Install Playwright for the JS-rendered sites:
  ```bash
  pip install playwright && python -m playwright install chromium
  ```

## Steps
1. `python3 .claude/skills/refresh-london-ds/refresh_roles.py`
   → writes `/tmp/ldn_ds_active.csv` (active roles + no-role companies, with Level).
   Pure-ATS companies (Greenhouse/Lever/Ashby/Amazon/Workday) are enumerated via
   urllib; the JS sites (Spotify, TikTok, Microsoft, Point72, Google, Bloomberg,
   Faculty, Revolut, Citadel, G-Research) are refreshed with Playwright.
2. `python3 .claude/skills/refresh-london-ds/build_jd_doc.py`
   → writes `/tmp/ldn_ds_jds.txt` (plain text, ~75 KB, no markdown).
3. **Assistant uploads** via the Google Drive `create_file` tool into folder
   `1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI`:
   - `/tmp/ldn_ds_active.csv` → `contentMimeType: text/csv`,
     title e.g. `London DS — Combined Active Job Posts vN (<date>)`.
   - `/tmp/ldn_ds_jds.txt` → `contentMimeType: text/plain`,
     title e.g. `London DS — Active Role JDs & Requirements vN (<date>)`.
   Read each file first (they fit in one Read page) and pass the content as
   `textContent`. text/csv → Google Sheet, text/plain → Google Doc automatically.

## How roles are decided
- **Active = a unique individual job-post URL** that resolves to a live posting
  in London or London-eligible (London / Remote-UK / London-or-Stockholm /
  London+other multi-location). NEVER a careers landing/search page or a
  perennial "expression of interest" talent pool.
- **Level**: `Senior+` if the title contains senior/staff/lead/principal/head/
  director/manager/sr/distinguished, else `Regular/Mid`. Include both.
- **Exclude** intern / graduate / apprentice programmes.
- Keep roles deduped by URL.

## Company taxonomy (as of 2026-06)
- **Greenhouse boards** (`boards-api.greenhouse.io/v1/boards/<token>/jobs`):
  deepmind, monzo, gocardless, dunnhumby, quberesearchandtechnologies, wayve,
  datadog, thetradedesk; Man Group is on the EU host
  (`boards-api.greenhouse.io` token `mangroup`, job URLs `job-boards.eu...`).
  Many big-tech boards exist but return 0 London DS (databricks, cloudflare,
  braze, amplitude, figma, mongodb, elastic, unity3d, catonetworks, polyai,
  truelayer) — still enumerated so new roles get caught.
- **Ashby** (`api.ashbyhq.com/posting-api/job-board/<org>`): openai.
- **Lever** (`api.lever.co/v0/postings/<org>?mode=json`): palantir (0 London DS).
- **Amazon**: `www.amazon.jobs/en/search.json?base_query=...&loc_query=London&country=GBR`
  — has `description`, `basic_qualifications`, `preferred_qualifications`.
- **Workday CXS** (POST `.../wday/cxs/<t>/<site>/jobs`): nvidia, salesforce,
  mastercard (0 London DS as of last run).
- **Microsoft**: Eightfold `apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=data%20scientist&num=50`
  — returns positions under `data`; only render in-browser (urllib gets 503).
- **Spotify**: `api.lifeatspotify.com/wp-json/animal/v1/job/search`; the record
  `id` IS the URL slug → `lifeatspotify.com/jobs/<id>`; filter
  `sub_category.slug == data-science` and a `london` location.
- **TikTok**: `api.lifeattiktok.com/api/v1/public/supplier/search/job/posts`
  (captured by loading `lifeattiktok.com/search?keyword=data%20scientist`);
  job URL `careers.tiktok.com/position/<id>/detail`.
- **Point72**: `careers.point72.com` CSOD — anchors `/CSJobDetail?jobName=...&jobCode=...`.
- **Bloomberg**: `bloomberg.avature.net/careers/SearchJobs/data%20scientist`
  → `/careers/JobDetail/<slug>/<id>` (London DS = Economics DS).
- **Google**: `google.com/about/careers/applications/jobs/results?location=London%2C+UK&q=data+scientist`
  → anchors `/jobs/results/<id>-<slug>`.
- **G-Research**: `gresearch.com/vacancies/` → individual `/vacancies/<slug>/`.
- **Faculty**: `faculty.ai/job-listing/london/.../<role>` (unique pages).
- **Revolut**: careers SPA; type "data scientist" in search, collect
  `/careers/position/<slug>` (note: roles are EU/remote, not London → list as
  no-active-London unless a London one appears).

## Known dead / blocked / not-queryable (re-check, don't trust blindly)
- **McKinsey/QuantumBlack**: Akamai 503 from datacenter IPs — cannot verify.
- **Snap**: Contentful-backed SPA, no queryable endpoint.
- **Atlassian / Apple / ServiceNow / Mastercard / American Express**: bespoke
  ATS; Atlassian's `atlassian.com/endpoint/careers/listings` works in-browser
  (179 listings, 0 London DS last run).
- **Citadel Securities**: only a perennial "Data Scientist" talent-pool EOI
  (Miami/global), not a live London role.

## Gotchas (learned the hard way)
- **TLS-intercepting proxy**: launch Chromium with
  `args=["--ignore-certificate-errors"]` AND a context with
  `ignore_https_errors=True`, else every `goto` fails with
  `net::ERR_CERT_AUTHORITY_INVALID`. (urllib trusts the proxy fine.)
- **Greenhouse `content` is HTML-ENTITY-ESCAPED.** When stripping tags you must
  `html.unescape()` FIRST, then remove tags, or you get literal `<p>`/`<li>`
  text in the output.
- **SPA waits**: use `wait_until="domcontentloaded"` + a short
  `wait_for_load_state("networkidle", timeout=8000)`; `networkidle` as the main
  wait times out on analytics-heavy SPAs and returns empty shells.
- **Upload size**: the Drive connector takes content inline and the model's
  Read paginates ~25k tokens, so keep each file under ~90 KB (the JD builder
  trims per-role bodies to do this). If a JD doc grows too big, lower the cap in
  `build_jd_doc.py`.
- Verify every "active" URL actually resolves (200, not a 404/landing) — Stripe,
  Revolut, Spotify, TikTok, DeepMind have all had stale IDs go 404.

## Output format reminders
- Sheet columns: `Company, Role, Level, Location, Apply URL, Status, Notes`,
  active rows first, then a divider row and the no-active-role companies.
- JD doc: plain text only. Company banners with `===`, role dividers with `---`,
  `Level: … Location: …` then `Apply: <url>`, bullets as `-`. No `#`/`*`/backticks.
