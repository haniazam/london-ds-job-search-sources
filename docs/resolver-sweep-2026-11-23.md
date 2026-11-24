# Weekly deep sweep — 23 Nov 2026

Run: `RESOLVE_CAP=150 PROBE_CAP=150 python3 .claude/skills/refresh-london-ds/discover.py --bootstrap`
(foreground attempt hit the 10-minute tool limit again and finished in the background, ~35 min).

`434 raw -> 228 unique DS-family leads (22 agency, 178 Standard DS at employers)` · registry-covered 108 · probed 75 · searched 61 · unresolved employers 47 (56 leads).
The script proposed 25 boards and 13 Workable-feed employer-site posts (all 13 are already returned by the Workable feed; 9 are ML-engineer titles out of Standard DS scope).

## Boards registered: 17 (every token checked against the ATS public API: own board + ≥1 UK posting)
- greenhouse `oodlefinance` (Oodle Car Finance) — 3 jobs, all UK; Data Scientist, London.
- ashby `cint` (Cint) — Senior Data Scientist with a UK location; `refractal` (Refractal) — 16 UK posts, Senior Data Scientist London; `arrive` (Arrive) — 23 UK posts, "Data Scientist, Pricing" London; `edited` (EDITED) — Junior Data Scientist, London Office; `hawk` (Hawk) — 6 UK posts, Data Scientist London.
- teamtailor `argusmedia` (Argus Media) — Senior Data Scientist (GenAI), London; `labgenius` (LabGenius) — Data Scientist, London; `tailscom` (Tails.com) — Data Scientist, Richmond GB (note: `LON` in refresh_roles.py will not match "Richmond", so this post only shows once the location regex is widened).
- smartrecruiters `sportradar` (Sportradar) — Senior Data Scientist, London; `entain` (Entain) — 283 posts, 15 UK on the first page, 0 DS today.
- pinpoint `youlend` (YouLend) — Senior Data Scientist, London; `ravelin` (Ravelin) — 5 posts, 1 London.
- workday Cisco (`cisco.wd5`) — "Senior Economist / Data Scientist, Technology Markets", London; Formula 1 (`formulaone.wd3`, key renamed from the lead name "Formula.") — own tenant, 32 posts incl. London, 0 DS today (verified in-browser; the CXS API was 429 all session).
- oraclehcm **Compare the Market** (manual find) — `ebet.fa.em3.oraclecloud.com`, site `CX_1` (vanity host jobs.comparethemarketcareers.com/en/sites/MK): Staff Data Scientist, London, posted 2026-11-18, plus two ML-engineering posts. Note the finder only returns `requisitionList` with `expand=requisitionList…`, which refresh_roles.py already sends.

## Boards dropped: 9 (removed from boards.json, added to board_denylist.json)
- greenhouse `digitalfuturesacademy` — 0 postings; hire-train-deploy academy. `capgeminideutschlandgmbh` — Capgemini Invent Germany, 127 posts, 0 UK. `orbisk` — Orbisk (Utrecht), not Orbis Group.
- ashby `alan` — Alan (Paris insurer) matched "The Alan Turing Institute"; 0 UK.
- teamtailor `volter-demo` — demo tenant.
- smartrecruiters `JACOBSDOUWEEGBERTS` — Jacobs Douwe Egberts, not Jacobs; `mottmacdonald` — single 2019 stub titled "d".
- workable `friendmts` — board empty (0 jobs).
- pinpoint `ipsos` — board empty (0 postings).
- workday `standard` (proposed as "Standard Chartered") — tenant is The Standard, a US insurer.

## Manual posts added: 6 (data/manual_posts.json; page title names the role, London, not on any enumerated board)
- Goldman Sachs — Real Estate Data Science, Vice President — https://higher.gs.com/roles/185227 (the AWM Associate post 176638 and six other higher.gs.com IDs now error out).
- Muzz — Senior Data Scientist (£80k–£90k + equity, Aldgate) — https://engineering.muzz.com/careers/data-scientist
- Muzz — Marketing Data Scientist (£55k–£75k + equity, Aldgate) — https://engineering.muzz.com/careers/marketing-data-scientist
- Institute for Government — Data Scientist (closes 6 Dec 2026) — https://www.instituteforgovernment.org.uk/about-us/careers/current-vacancies/data-scientist
- BAE Systems — NSL- Data Scientist, London — https://cybercareers.baesystems.com/job/London-NSL-Data-Scientist/1458896033/ (the site is SuccessFactors but its search page carries no `jobLocation` spans, so the successfactors handler cannot enumerate it).
- Sainsbury's — Senior Data Scientist, London Store Support Centre — https://www.sainsburys.jobs/jobs/description/400062217/ (15 other sainsburys.jobs DS IDs from search are 404; the site search ignores the query).

## Other changes
- `role_taxonomy.py`: "Real Estate Data Science, Vice President" was Other DS-family; added the bank-grade suffix form (`Data Science, Vice President/VP/AVP/Executive Director/Director/Head/Manager/Lead`) + test (44/44 pass).
- `discover.py` AGENCY: added Cognify, DataCareers, Franklin Bates, GamblingCareers, Infused Solutions, McGregor Boyall, Morson, Pentasia, Stanton House, William Alexander, Women in Data (all appeared as "employers" this run).
- `boards.json` aliases: LexisNexis Risk Solutions → RELX, Viator → Tripadvisor, trg. → TRG Screen, Formula. → Formula 1. `employer_sites`: Meta (metacareers London DS search) and IBM (careers search, UK) for future hand-verification — both render titles only in-browser, so manual_posts' `<title>` check cannot verify them.

## Resolved as "no eligible London post" (searched this sweep)
Earnix (Comeet feed: London roles are sales/marketing only), BBC/BBC Studios (only a Level-6 DS apprenticeship in London), PureGym (Dayforce portal: 0 "data scientist" results), Bibby Financial Services (Lead DS closed; 6 open roles, none DS), Qogita (Data Scientist (Economics) closed on the VC board; qogita.com 403), British Airways (Senior Product Data Scientist closed 22 Nov; other careers.ba.com DS IDs 404), SoftServe (Lead DS posts are PL/UA/LatAm), Defra (no live HEO DS post), Avetix Bio (US), Gamingtec (Limassol/remote EU), CEERISK Arabia, OneJar (analyst).

## Still unresolved (own career sites with no API or title; or no board found)
Meta (3 live London posts: Data Scientist, Product Analytics ×2 and Data Scientist, Analytics (Technical Leadership) — metacareers IDs 1144181248272927, 4502174973433397, 1407517847676303; page `<title>` is always "Meta Careers"), IBM (3 UK "Multiple Cities" DS posts, JS-only pages), Klarna (klarnagroup.teamtailor.com is gone, klarna.com/careers is JS), Zepz (greenhouse `zepzgroup` 404), Depop, Canopius, Haleon (Workday tenant unknown; 429/422), King (Phenom), Welltower (UltiPro, URL not found), Vodafone/VOIS (opportunities.vodafone.com 403 to scripts), AtkinsRéalis (Phenom, redirects to US search), QuantumBlack/McKinsey (Akamai), Compare the Market is now covered, plus Unique AI, SBS, Obsero, Tact, beaumont, i3, Atana Elements, Scrumconnect, Betway (junior DS only, no source URL), Standard Chartered (real tenant not found), Mott MacDonald (real board not found), Jacobs, Haven.
