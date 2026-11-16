# Weekly deep sweep — 16 Nov 2026

Run: `RESOLVE_CAP=150 PROBE_CAP=150 python3 .claude/skills/refresh-london-ds/discover.py --bootstrap`
(foreground via a harness-managed background shell; completed in ~25 min. Brave Search was reachable through the
session proxy, so tier-2 searches ran for the first time since 11 Oct.)

`433 raw -> 230 unique DS-family leads (22 agency, 185 Standard DS)` · registry-covered 116 · probed 72 · searched 60 · unresolved employers 45 (before this sweep's manual resolution).

## Boards proposed by the run: 24 — kept 17, dropped 7 (each checked against the ATS public API)
Kept (own board, ≥1 UK posting):
- greenhouse `monks` (Monks; 8 UK posts incl. Junior Data Scientist), `oodlefinance` (Oodle Finance; London Data Scientist).
- ashby `cint` (Cint; Senior Data Scientist, UK among its locations), `refractal` (Refractal; London Senior Data Scientist), `arrive` (Arrive, the merged EasyPark/Flowbird/ParkMobile group; 24 UK posts), `edited` (EDITED; London Junior Data Scientist).
- teamtailor `argusmedia` (Argus Media; Senior Data Scientist (GenAI) + Data Scientist – Generative AI), `labgenius` (LabGenius; Data Scientist), `tailscom` (Tails.com; Data Scientist), `volter-demo` (Volter — the slug says "demo" but the board is Volter's own: hiringOrganization Volter / careers.getvolter.com, London Data Scientist; kept).
- smartrecruiters `entain` (Entain; 76 UK posts; public API answers for this company).
- workday Formula 1 (`formulaone/F1`; 33 posts, London/Biggin Hill, display name fixed from "Formula."), AEGIS London (`aegislondon/Careers`; London Data Scientist), Centrica (`centrica/Centrica`; Data Scientist Cardiff/Reading/Flexible — UK board, kept at 0 London DS), Visa (`visa/Visa`; 58 UK posts; the lead was Featurespace, now Visa).
- pinpoint `youlend` (YouLend; London Senior Decision Scientist), `ravelin` (Ravelin; London).

Dropped and deny-listed:
- greenhouse `archer56` — Archer Aviation (US eVTOL, 2 UK posts, neither DS). The London "Archer" lead is hackajob's rebranded hiring marketplace (added to the agency regex).
- greenhouse `digitalfuturesacademy` — 0 postings; Digital Futures is a trainee academy (agency regex).
- greenhouse `orbisk` — Orbisk (Dutch food-waste startup, 0 UK), not Orbis Group, which is a London recruiter (agency regex).
- ashby `alan` — Alan (French health insurer, 138 posts, 0 UK), not The Alan Turing Institute.
- workday `standard` — The Standard (US insurer, Portland OR), not Standard Chartered.
- workable `friendmts` — unverifiable: Cloudflare 1015/429 on every attempt and not in the Workable cross-employer feed.
- pinpoint `ipsos` — genuine Ipsos board but 0 postings; Ipsos's live roles are on Oracle HCM (registered below).
Also deny-listed from a hand probe: greenhouse `dcd` (exists, 0 postings, not confirmable as DatacenterDynamics).

## Boards registered by hand from the site-scoped searches: 6
- pinpoint `uktv` — UKTV (BBC Studios' channel group); 6 London posts, the Lead Data Scientist post found by search has closed. Kept at 0 DS.
- workday Betway (Super Group) — `myhcm.wd3 / Betway`; London (St Pancras) + North London locations, 0 DS today.
- workday Haleon — `gsknch.wd3 / GSKCareers`; Senior + Principal Data Scientist at London Bankside.
- oraclehcm Ipsos — `ecqf.fa.em2.oraclecloud.com / IpsosCareers`; Data Scientist + Senior Data Scientist (Synthetic Data team), London.
- oraclehcm Ocado Logistics — `iahbme.fa.ocs.oraclecloud.com / CX_1`; Senior Data Scientist, Hatfield (UK board, not London).
- teamtailor `careers.smg.team` — SMG (retail media agency); Senior Data Scientist, London. `refresh_roles.py` now accepts a custom Teamtailor host (token containing a dot) as well as a `<token>.teamtailor.com` slug.
Aliases added: LexisNexis Risk Solutions → RELX; Ipsos in the UK → Ipsos; "QuantumBlack, AI by McKinsey" → QuantumBlack (McKinsey).

## Manual posts added: 7 (own-site postings, page title names the role; none returned by a registered board or the Workable feed)
- CEERISK Consulting — Data Scientist, Kingston upon Thames (full-time, on-site).
- Daintta — Data Scientist; Data Scientist Analyst (Breezy board, London, full-time).
- Muzz — Senior Data Scientist; Marketing Data Scientist (London, hybrid).
- British Airways — Senior Product Data Scientist (Heathrow; the Principal Data Scientist page has died).
- The Alan Turing Institute — Data Scientist - ARC (London, permanent, £46,415–£52,494, closes 22 Nov 2026).

## Dropped after verification (no London-eligible Standard DS post)
Haven (Senior Data Scientist is Hemel Hempstead head office), Ford (only UK DS post is Manufacturing Data Scientist, Dunton), Gamingtec (Lead Data Scientist is Limassol/Tbilisi/Yerevan), Costa Coffee (only an Associate Data Science Analyst), Earnix (Comeet board; only "Insurance Data Science Consultant", London — classified Other DS-family), Acuity Analytics (JazzHR board `ascent.applytojob.com`, AI-engineer posts only), Bibby Financial Services (own site, no DS post), MarketCast (JobScore account gone, 410; the DS post was Reading), Compare the Market (own careers site blocks bots; no ATS found), PureGym (Dayforce portal, JS-only).

## Recruiters / job boards confirmed and added to the agency regex
MPower Plus, Orbis Group, Bodhi (Resourcing), DataCareers, Edenbrook, Franklin Bates, Infused Solutions, Marshall Wolfe, Morson Edge, Stanton House, William Alexander, TRG, Women in Data, FDE Times, Game Companies, Digital Futures, hackajob/Archer.

## Still unresolved (own career sites with no public API, or no board found)
- JS-only or gated career sites: IBM, Meta (metacareers), Goldman Sachs (higher.gs.com), McKinsey/QuantumBlack (mckinsey.com; the LinkedIn manual posts stand in), King (careers.king.com, Phenom — API rejects unknown tenant), AtkinsRéalis (careers.atkinsrealis.com, JS), Capgemini Invent, VOIS/Vodafone, Standard Chartered (SuccessFactors; search page JS-only and posting pages carry a generic title), BBC (careers.bbc.co.uk, same SuccessFactors template — 0 server-rendered rows), Welltower, Defra (Civil Service Jobs, session-gated), Jazz Pharmaceuticals (Workday tenant `vhr-jazz` found but the CXS API returns 422 for every site name tried).
- No board found: Betway Global's DS post closed (board registered), Keit Industrial Analytics, Magic Memories (Wix site), Obsero, Unique AI, Axom Gaming, Synthesis, Tact, VE3, Scrumconnect Consulting, MakiPeople, SBS, DatacenterDynamics, Qogita (site 403; Otta/Built In only), Daintta/CEERISK/Muzz/BA/Turing now covered by manual posts.
