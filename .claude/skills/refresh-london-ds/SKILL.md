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

## Discovery — keeping the company universe exhaustive (run every refresh)
The script only enumerates boards listed in `boards.json`; a company not in the registry is
never seen. So each refresh starts with a **harvest** step (assistant action — WebSearch is
model-only) that widens the registry before the script runs:

1. **Site-scoped searches** over each ATS host, two title forms each ("Data Scientist" and
   "Data Science", plus Senior/Lead/Staff/Principal/Head variants) and the London-eligible
   location forms ("London", "Remote (UK)", "United Kingdom"):
   `site:job-boards.greenhouse.io`, `site:boards.greenhouse.io`, `site:job-boards.eu.greenhouse.io`,
   `site:jobs.ashbyhq.com`, `site:jobs.lever.co`, `site:apply.workable.com`,
   `site:jobs.smartrecruiters.com`, `site:myworkdayjobs.com`, `site:pinpointhq.com`,
   `site:teamtailor.com`, `site:recruitee.com`. The **board token in each result URL** is the
   harvest (greenhouse.io/<token>/, ashbyhq.com/<org>/, lever.co/<org>/, workable.com/<acct>/,
   smartrecruiters.com/<Company>/, <tenant>.<wdN>.myworkdayjobs.com/.../<Site>/,
   <acct>.pinpointhq.com). A result may be stale — the token is what matters; the API decides
   liveness.
2. **Known-employer probe**: guess tokens for London DS employers by name (fintechs, quant
   funds, scale-ups); a wrong guess just 404s. Keep every reachable board even at 0 London DS.
3. Add new tokens to `boards.json` (+ `display_names`). Never list recruiters/agencies as
   employers — put them in `recruiters_exclude` (Jobgether, Degree 6, Qurious, KIMARU…).
4. Run `refresh_roles.py`; it enumerates the whole registry and filters London + DS title.

Gotchas: Workable rate-limits (429) aggressively — the script paces calls; a 429 run leaves
that board unverified, not empty. SmartRecruiters' public API is gated per company (IQVIA,
Checkout.com, Trainline return 0 even with live posts) — verify those by GET on the posting
URL (server-rendered; dead posts change the <title>). JobDataLake MCP, when connected, is a
faster first pass (`search_jobs`, countries=GB, location=London) but it was down on 2026-10-09.
As of the 2026-10-09 sweep the registry holds ~70 Greenhouse, 25 Ashby, 10 Lever, 10 Workable,
7 SmartRecruiters, 6 Pinpoint, 7 Workday boards; the sweep found ~75 live London DS posts at
~32 employers that the old fixed list had never looked at.

## Role-type rule: classify by core role, never by keyword (role_taxonomy.py)
"Standard DS" means the title's CORE ROLE is in the Data Scientist family — Data Scientist
with any prefix/suffix, Data Science Manager/Lead/Head/Director in any word order,
Decision/Product/Analytics Scientist, or a Scientist title with a product-DS signal
(experimentation, measurement, causal, product analytics, growth). A specialism modifier
NEVER excludes: "Senior Data Scientist (Economist)", "Data Scientist, Machine Learning",
"Research Data Scientist", "Staff Scientist, Experimentation", "Director, Data Science" are
all in. A title is "Other DS-family" only when its core IS another discipline (Research
Scientist/Engineer, ML/AI Engineer or Scientist, Applied Scientist, Quant
Researcher/Trader/Developer, Data/Analytics Engineer, Analyst, Economist, Statistician).
The old keyword blacklist (any of research|machine learning|ml|applied|analyst|engineer|
economist|quant anywhere in the title) silently dropped exactly the senior product-DS
titles the search exists for. `python3 role_taxonomy.py` runs its tests; when a real
title is misclassified, add it to TESTS and fix the pattern — never special-case a company.

## Sheet build rule (learned the hard way on 2026-10-09)
The Sheet is built FROM the script's CSV — `refresh_roles.py` → `pay_enrich.py` → filter
`Role Type == Standard DS` → write the Sheet in place. Never hand-merge "the rows I audited"
with "the new companies I found": that dropped 12 live Standard-DS roles at 8 registry
companies (Monzo ×5 incl. a £124k–£165k Staff post, Spotify, TikTok, GoCardless) because the
original-registry output never reached the Sheet. Every refresh also diffs against the
external lists in `boards.json` (`external_lists`, e.g. the ChatGPT Job Search Radar at
`/api/state`): a role there but not here is dead, out of scope, or a missing board token —
classify each, never ignore. Employer sites with no ATS API are in `employer_sites`; verify
those by GET + `<title>`.

## Comp coverage (run `pay_enrich.py` after `refresh_roles.py`)
`pay_enrich.py /tmp/ldn_ds_active.csv` writes `/tmp/ldn_ds_active_pay.csv` with an
"Approx London TC" column that is never blank and always labelled: **posted** (the
employer's range, from structured ATS pay fields or a £-range regex on the text; ~15% of
London posts disclose) → **sourced** (company figure in `pay_overrides.json`, each with
source + date; add one whenever a Levels.fyi/Glassdoor London figure for that employer is
found) → **market est.** (ITJobsWatch London median for the title, -15%/+25%, fetched
live). The Sheet's comp column is this output. Never present a market band as if it were
company data — the label is the point.

## Company taxonomy (as of 2026-06)
- **Greenhouse boards** (`boards-api.greenhouse.io/v1/boards/<token>/jobs`):
  deepmind, monzo, gocardless, dunnhumby, quberesearchandtechnologies, ocadogroup, coreweave, isomorphiclabs, wise,
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
- **Board drift (Oct-2026 link audit):** Wayve left Greenhouse (`wayve` → 404; now no DS
  roles at all). Ocado's token is `ocadogroup`, not `ocado`. Lendable and Multiverse are on
  **Ashby**, not Greenhouse. Point72 currently has no London DS (HK/Singapore/NY only).
  OpenAI has 0 London DS on its Ashby board. LinkedIn mirrors expire silently — a dead
  LinkedIn job returns HTTP 200 but redirects to a generic "N,000+ … jobs" listing; judge
  liveness by the page `<title>` (must name the company + role), never by status code.
  Same for Google: a closed google.com post returns 200 with title "Jobs search — Google
  Careers"; a live one is titled "<Role> — Google Careers". Google postings turn over
  fast (the Staff/Shopping DS post closed within a day of being listed).
- **Point72**: `careers.point72.com` CSOD — anchors `/CSJobDetail?jobName=...&jobCode=...`.
- **Bloomberg**: `bloomberg.avature.net/careers/SearchJobs/data%20scientist`
  → `/careers/JobDetail/<slug>/<id>` (London DS = Economics DS).
- **Google**: `google.com/about/careers/applications/jobs/results/?location=London%2C+UK&q=data+scientist`
  → server-rendered HTML embeds `/jobs/results/<id>-<slug>`; `refresh_roles.py`
  now parses these via urllib (no browser). Filter slug to `data-scientist`/
  `data-science`, drop `research-(scientist|engineer)`/`software-engineer`; mark
  `London (verify)` and confirm the location on the post (some results are
  London+Dublin). Do NOT rely on Playwright for Google — the page is JS-heavy and
  the slugs are in the raw HTML anyway. DeepMind DS is covered via Greenhouse.
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
