# Resolver sweep — 10 Oct 2026

Run: `RESOLVE_CAP=150 python3 .claude/skills/refresh-london-ds/discover.py --resolve-only`

## Outcome in one paragraph

The script's own tier-2 search cannot work in this cloud container: Brave returns `422 SUBSCRIPTION_TOKEN_INVALID` for the
proxy-injected key, and the DuckDuckGo fallback is cut at the egress proxy (`html.duckduckgo.com`, `lite.duckduckgo.com` —
tunnel closed after 12 s). The run therefore resolved **0 of 108** unresolved employers (final `[resolve]` line of the run is appended at the foot of this file when it completes; every search attempt fails before any URL is returned) (baseline rebuilt
with `--bootstrap`, past month; the gitignored leads file from the earlier 114-employer run is not in the repo).
The same 108 were then swept by hand with direct ATS-API slug probes, web search restricted to ATS hosts, and JobDataLake.
**44 employers resolve to a registered board** (37 new boards + 7 name aliases to boards already in the registry), **2 more**
sit on Teamtailor (no enumerator yet), **16** post only on their own career site, and **46** could not be tied to any
supported board (own enterprise ATS, posting gone, or recruiter).

## A. Resolved to a supported ATS board (added to `boards.json`)

| Employer | Board | London DS role on the board today | Source |
|---|---|---|---|
| ASOS | smartrecruiters:`asos` | Applied Scientist; Senior Applied Scientist (London) | [board](https://jobs.smartrecruiters.com/asos) |
| AVEVA | workday `aveva.wd3/AVEVA_careers` | Product Intelligence Data Scientist (2 locations) | [board](https://aveva.wd3.myworkdayjobs.com/AVEVA_careers) |
| Abtrace | workable:`abtrace` | board live; no DS post open now | [board](https://apply.workable.com/abtrace/) |
| Betsson Group | greenhouse:`betsson` | Senior Quantitative Data Analyst (London) | [board](https://job-boards.greenhouse.io/betsson) |
| Blenheim Chalcot | greenhouse:`blenheimchalcot` | Data Scientist (London) | [board](https://job-boards.greenhouse.io/blenheimchalcot) |
| bp | workday `bpinternational.wd3/bpCareers` | Senior data scientist (London); Expert DS (Sunbury) | [board](https://bpinternational.wd3.myworkdayjobs.com/bpCareers) |
| C3 AI | greenhouse:`c3iot` | Data Scientist - Defence; DS / Senior DS (London) | [board](https://job-boards.greenhouse.io/c3iot) |
| Carwow | ashby:`carwow` | Senior Data Scientist (London) | [post](https://jobs.ashbyhq.com/carwow/06c4d36a-c237-4226-a11f-1ee2aa69adba) |
| Coalition, Inc. | greenhouse:`coalition` | Senior Data Scientist (UK remote) | [board](https://job-boards.greenhouse.io/coalition) |
| CoMind | ashby:`comind` | Principal Data Scientist | [board](https://jobs.ashbyhq.com/comind) |
| Equifax | workday `equifax.wd5/External` | Data Scientist - Fraud (London / Nottingham / Leeds) | [post](https://careers.equifax.com/en/jobs/j00178995/data-scientist-fraud) |
| Flutter UK & Ireland | workday `flutterbe.wd3/FlutterUKI_External` | Lead Data Scientist (3 locations) | [post](https://flutterbe.wd3.myworkdayjobs.com/en-US/FlutterUKI_External/job/Lead-Data-Scientist_JR139717) |
| Hometrack | workable:`hometrack` | Senior Data Scientist | [board](https://apply.workable.com/hometrack/) |
| Howden | workday `hyperiongrp.wd3/Hyperion_External` | Lead Data Scientist (London) | [post](https://hyperiongrp.wd3.myworkdayjobs.com/en-US/Hyperion_External/job/Lead-Data-Scientist_R0019143-1) |
| Humara | workable:`humara-2` | Senior Data Scientist (Brighton, hybrid — not London) | [board](https://apply.workable.com/humara-2/) |
| JD.com | workday `jd.wd103/Careers_at_JD` | board live; the London DS post has closed | [board](https://jd.wd103.myworkdayjobs.com/Careers_at_JD) |
| Kharon | pinpoint:`kharon` | Data Scientist, Retrieval & Agentic Systems (London) | [board](https://kharon.pinpointhq.com/) |
| LSEG | workday `lseg.wd3/Careers` | Senior Applied Data Scientist (London, Paternoster Sq) | [board](https://lseg.wd3.myworkdayjobs.com/Careers) |
| loveholidays | ashby:`loveholidays` | Data Scientist | [board](https://jobs.ashbyhq.com/loveholidays) |
| Made Tech | pinpoint:`made-tech` | Senior Data Scientist - SC cleared (any UK hub incl. London) | [board](https://made-tech.pinpointhq.com/) |
| Neko Health | ashby:`neko-health` | Data Science Lead (CV + ML) | [board](https://jobs.ashbyhq.com/neko-health) |
| Oxford Economics | pinpoint:`oxfordeconomics` | Sr. Economist / Data Scientist - Economic Impact (London) | [board](https://oxfordeconomics.pinpointhq.com/) |
| Preply | ashby:`preply` | Senior DS - Insights (London); Staff DS - Marketing | [board](https://jobs.ashbyhq.com/preply) |
| Product Madness | workable:`productmadness` | board live; Data Scientist post seen in search, not in API today | [post](https://apply.workable.com/productmadness/j/2BBBE69B57/) |
| Qube RT | greenhouse:`quberesearchandtechnologies` | Data Scientist; Data Scientist - Fixed Income (London) | [board](https://job-boards.greenhouse.io/quberesearchandtechnologies) |
| RELX / LexisNexis | workday `relx.wd3/relx` (umbrella site; Elsevier site already registered) | Senior Data Scientist II (London Wall) and others | [board](https://relx.wd3.myworkdayjobs.com/relx) |
| Relay | ashby:`relay` | Staff DS - Geospatial; Senior DS - Last Mile Pricing | [board](https://jobs.ashbyhq.com/relay) |
| Resultance | workable:`resultance` | Senior Consultant - Data & AI (Luxembourg; not London) | [post](https://apply.workable.com/resultance/j/2A79300DA5/) |
| Soho House & Co | greenhouse:`sohohouseco` | Lead Data Scientist (London) | [board](https://job-boards.greenhouse.io/sohohouseco) |
| StackAdapt | greenhouse:`stackadapt` | Senior/Staff Applied Machine Learning Scientist (UK) | [board](https://job-boards.greenhouse.io/stackadapt) |
| Surgo Health | pinpoint:`surgohealth` | Senior Research Scientist (London, UK) | [board](https://surgohealth.pinpointhq.com/) |
| SynMax | lever:`synmax` | board live; no geospatial DS post open now | [board](https://jobs.lever.co/synmax) |
| The Voleon Group | ashby:`voleon` | Data Scientist (London) | [post](https://jobs.ashbyhq.com/voleon/5c966855-af8b-4bf5-9f58-6701e1cc2238) |
| Tripledot Studios | greenhouse:`tripledotstudios` | Data Scientist (London) | [board](https://job-boards.greenhouse.io/tripledotstudios) |
| Vortexa | workable:`vortexa` | Principal Data Scientist | [board](https://apply.workable.com/vortexa/) |
| Woven by Toyota | lever:`woven-by-toyota` | Senior Data Scientist, AD/ADAS (London) | [board](https://jobs.lever.co/woven-by-toyota) |
| WPP Media | greenhouse:`wppmedia` | Data Scientist; DS - Marketing Science; Assoc. Director DS (London) | [board](https://job-boards.greenhouse.io/wppmedia) |
| Zilch | ashby:`zilch` | Senior Data Scientist | [board](https://jobs.ashbyhq.com/zilch) |

## B. Already registered — the lead name just didn't match (aliases added to `boards.json`)

| Lead name | Registered as | Evidence |
|---|---|---|
| Fin | Intercom (greenhouse:`intercom`) | board lists "Senior Data Scientist - Product Analytics, London" verbatim — [board](https://job-boards.greenhouse.io/intercom) |
| Zopa Bank | Zopa (lever:`zopa`) | Data Scientist (Mid and Senior Level), London — [board](https://jobs.lever.co/zopa) |
| Expedia Group | Expedia (employer_sites) | same org |
| LexisNexis / LexisNexis IP Solutions | RELX (workday) | same Workday tenant |
| Tesco Technology | Tesco | same org (Tesco itself is not registered; see C) |
| ASOS.com / Coalition, Inc. / Qube Research & Technologies / Relay Technologies | the boards in A | display-name variants |

## C. Board found, but on Teamtailor (no enumerator in `refresh_roles.py` yet)

| Employer | Board | Role | Source |
|---|---|---|---|
| Blue Light Card | teamtailor:`bluelightcard` | Principal Product Data Scientist (Cossington / London, hybrid) | [post](https://careers.bluelightcard.co.uk/jobs/8527585-principal-product-data-scientist) |
| Yonder | teamtailor:`yonder` | Data Scientist (London) | [board](https://yonder.teamtailor.com/jobs) |

## D. Own career site only (no supported ATS) — candidates for `data/manual_posts.json`

| Employer | Role | Location | Source |
|---|---|---|---|
| Haven (Bourne Leisure) | Senior Data Scientist | Hemel Hempstead, remote-first UK | [post](https://jobs.haven.com/job/75809473) |
| Fitch Solutions | Associate Director, Data Scientist | London | [listing](https://careers.fitch.group/go/Fitch-Solutions/8973301/) |
| Stantec | Principal Data Scientist - Water Sector | London / Brighton / High Wycombe | [post](https://careers-uk-ireland.stantec.com/vacancies/8744/principal-data-scientist--water-sector.html) |
| DraftKings | Senior Data Science Engineer (×2) | London | [post](https://careers.draftkings.com/jobs/jr11597/senior-data-science-engineer/) |
| SEGA Europe | Senior Data Scientist | London | [vacancies](https://careers.sega.co.uk/vacancies) |
| NatWest Group | Data Scientist, Economic Crime Hub | Manchester / Edinburgh / London (site 403s scripts) | [post](https://jobs.natwestgroup.com/jobs/18243434-data-scientist-economic-crime-hub) |
| Sky | Data Scientist (Gen AI), Principal DS and others | London / Osterley | [careers](https://careers.sky.com/) |
| IBM | Data Scientist - Public Sector | Hursley / Leicester / London | [post](https://careers.ibm.com/en_US/careers/JobDetail/Data-Scientist-Public-Sector/48969) |
| Sagacity | Data Scientist | London hybrid | [careers](https://www.sagacitysolutions.co.uk/about/company/careers) |
| Tesco | (Senior) Data Scientist - Neural Net Forecasting | Welwyn Garden City — not London | [post](https://careers.tesco.com/en_GB/careers/JobDetail/Data-Scientist-Neural-Net-Forecasting/181995) |
| TUI | Senior Data Scientist | Luton — not London | [careers](https://careers.tuigroup.com/en) |
| Prima | Data Scientist - Pricing UK; Senior DS - Fraud | London — both postings now 404 | [careers](https://www.helloprima.com/careers/locations/the-uk) |
| Oritain | Lead Statistical Data Scientist | Auckland — not London | [post](https://careers.oritain.com/jobs/7355520-lead-statistical-data-scientist) |
| Compare the Market (BGL) | no DS title on the board today | Peterborough / London | [board](https://www.bglgroup.co.uk/careers/search-and-apply?brand=comparethemarket.com) |
| UBS, BNY, Citi, Goldman Sachs, JPMorganChase, Apple, BAE Systems, Chubb, McKinsey / QuantumBlack, HCLTech, L.E.K. | enterprise ATS (Oracle HCM, Taleo, SuccessFactors, in-house) | — | not scriptable with the current enumerators |

## E. Not resolved

| Employer | What the sweep found |
|---|---|
| Qogita | Lever board gone (API and posting both 404) — posting closed |
| Klarna | Teamtailor board removed; no London fraud DS post indexed |
| Zepz | Greenhouse embed `zepzgroup` now 404 |
| British Airways, Costa Coffee, PureGym, Welltower, Perspectum, Magic Memories, MarketCast, Jack & Jill, CEERISK, SBS, Twelve, Raylo, trg., Acuity Analytics, Daintta, DatacenterDynamics, Unique AI, SMG, Systematic, i3Works, myPOS, MAGIC AI, Q1 Technologies | no posting on any supported ATS host; several are generic names that only produce false matches (Pinpoint demo tenants, a Montreal game studio for "Haven", a Swedish clinic for "Prima") |

## F. Recruiters that the agency filter missed (now added to `AGENCY` in `discover.py`)

McCabe & Barton, Oho Group, Speak to Kit, Annapurna, DeepRec.ai, NearTech Search, Radley James, SearchWorks, Searchability NS&D, mthree, Q1 Technologies.

## Recommendation

Direct slug probing of the ATS public APIs (Greenhouse, Ashby, Lever, Workable, SmartRecruiters, Pinpoint; Workday via the
`wday/cxs` search endpoint) found 29 of the 37 new boards with no search engine at all, in under two minutes, and is immune
to the Brave/DuckDuckGo problems. It would be a cheap tier 1.5 in `discover.py` between the registry match and the web search.
A Teamtailor enumerator would add Blue Light Card and Yonder.

## Script run log

_pending — the run was still in its search loop when this file was first committed._
