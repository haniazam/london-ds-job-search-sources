# Job-posting URLs (London DS target list)

Primary posting per role = the one each tailored resume targets. The scraper
(`scripts/fetch_jds.py`) holds the authoritative copy of these URLs in its
`COMPANIES` list; this file mirrors it for humans.

> **Last refreshed: 2026-10-09** against each employer's live ATS. Prefer
> **Greenhouse/Ashby** URLs — the scraper pulls clean JD text from their open
> JSON APIs. Tags below:
> - **[walled]** — Cloudflare/JS-protected, no public API. Plain fetch 403s or
>   times out; needs the browser variant (`scripts/fetch_jds_browser.py`) or a
>   manual paste. Even headless Chromium hits Cloudflare challenges on some.
> - **[search]** — the specific posting closed; URL is a listing/search page to
>   monitor (no single live JD to scrape).

## OpenAI — Data Scientist, Safety
- **Primary:** https://jobs.ashbyhq.com/openai/90c711dc-5f50-46e3-a5ab-82359a56d683
- Protection Scientist Engineer, Integrity — London: https://jobs.ashbyhq.com/openai/3fefc615-6950-4a29-9214-eefdc4e659e3
- _Dropped 2026-10-09:_ the `openai.com/careers` "DS, Integrity Measurement" and
  "Protection Scientist Engineer" links (403'd); "DS, Monitoring Ops"
  datasciencejobs.com mirror (role expired). No live London DS on Ashby beyond
  the two above.

## Citadel Securities — Data Scientist  [walled — manual only]
- **Primary:** https://www.citadelsecurities.com/careers/details/data-scientist/
  (Cloudflare bot-check blocks plain fetch **and** headless Chromium — manual paste only)

## Revolut — Senior Data Scientist  [walled — manual only]
_All revolut.com careers pages sit behind a Cloudflare challenge that blocks plain fetch **and** headless Chromium; no public ATS API found — manual paste only._
- **Primary:** https://www.revolut.com/careers/position/1a0f390b-ed4a-441a-9535-82d0e185906a/
- Senior DS (Computer Vision): https://www.revolut.com/careers/position/senior-data-scientist-computer-vision-85b790a2-ca60-4095-a28f-b4e29f0136eb/
- DS (Risk): https://www.revolut.com/careers/position/data-scientist-risk-46917c00-41ca-4c82-be38-00894cc2c136/
- DS (NLP / DL Eng): https://www.revolut.com/careers/position/data-scientist-nlp-deep-learning-engineer-7fdeec15-cd49-4ca9-b509-ae6ca2613cd5/
- DS (Core): https://www.revolut.com/careers/position/76be454e-fe77-4daf-abd6-9ae9c41afd70/

## Stripe — Data Scientist  [search]
- **Primary (search):** https://stripe.com/jobs/search?l=London
  (DS, EMEA 7516102 closed; Stripe is on Greenhouse board `stripe`, no London DS live now)

## Google DeepMind — Applied Data Scientist / Research Scientist  [search]
- **Primary (careers site):** https://deepmind.google/about/careers/
  (DeepMind left the `deepmind` Greenhouse board — all old job IDs now 404; roles
  live only on the JS careers site, so per-role clean scrape isn't possible)

## The Trade Desk — Applied Scientist / Data Scientist  [search]
- **Primary (board):** https://job-boards.greenhouse.io/thetradedesk
  (Staff Applied Scientist 5118594007 closed; board live but no London DS/applied-sci currently)

## G-Research — ML / NLP Research
_The `data-scientist` vacancy is filled/removed; slugs below are live as of 2026-10-09._
- **Primary (ML Researcher):** https://www.gresearch.com/vacancies/machine-learning-researcher/
- NLP Researcher: https://www.gresearch.com/vacancies/natural-language-processing-researcher/
- ML Engineer: https://www.gresearch.com/vacancies/machine-learning-engineer/
- AI Engineer: https://www.gresearch.com/vacancies/ai-engineer/

## Spotify — Data Science  [search]
- **Primary (London DS search):** https://www.lifeatspotify.com/jobs?c=data-science&l=london
  (old per-role lifeatspotify slugs all 404; roles churn fast — monitor the search)

## Monzo — Data Science (Greenhouse board `monzo`)
- **Primary (Lead Data Scientist):** https://job-boards.greenhouse.io/monzo/jobs/6369658
- Senior ML Manager, Borrowing: https://job-boards.greenhouse.io/monzo/jobs/7996955
  (replaces "Senior ML Scientist, Borrowing" 7686352, now closed)
- Senior Data Scientist: https://job-boards.greenhouse.io/monzo/jobs/6180814
- Staff Data Scientist: https://job-boards.greenhouse.io/monzo/jobs/8232732

## Google — Product Data Scientist (L5)  [search]
- **Primary (London search):** https://www.google.com/about/careers/applications/jobs/results?location=London%2C+UK

## Bloomberg — Data Scientist  [walled]
- **Primary (Avature DS search):** https://bloomberg.avature.net/careers/SearchJobs/data%20scientist
  (Economics DS Avature JobDetail 19933 expired/404; careers.bloomberg.com 403s)

## QuantumBlack (McKinsey) — Data Scientist I  [walled — browser variant works]
_mckinsey.com careers are JS-rendered (plain fetch times out) but NOT Cloudflare-walled, so the browser variant fetches them. "Senior Data Scientist I" 108819 is dead (upstream error); Data Scientist I 102714 is the live London role (2026-10-09). Other QuantumBlack DS roles are Toronto/São Paulo/Seoul/Germany, not London._
- **Primary (Data Scientist I — London):** https://www.mckinsey.com/careers/search-jobs/jobs/datascientisti-quantumblackaibymckinsey-102714

## Man Group — Quant Research (Greenhouse board `mangroup`, EU)
_All four earlier IDs (incl. Responsible Investment) expired; current live London roles:_
- **Primary (Quant Researcher — Macro; Futures/FX):** https://job-boards.eu.greenhouse.io/mangroup/jobs/4966466101
- Quant Researcher — Macro Trend: https://job-boards.eu.greenhouse.io/mangroup/jobs/4880305101
- Quant — Systematic Multi-Strategy: https://job-boards.eu.greenhouse.io/mangroup/jobs/4965180101
- Quantitative Developer — Systematic: https://job-boards.eu.greenhouse.io/mangroup/jobs/4844843101

## TikTok — Senior Data Scientist, Operations  [walled]
- **Primary:** https://careers.tiktok.com/position/7344026106091604275/detail
  (own ATS, JS-rendered — needs browser variant / manual)

## XTX Markets — (no live DS role; monitoring only)
- Careers landing: https://www.xtxmarkets.com/careers/
