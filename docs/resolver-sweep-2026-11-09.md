# Weekly deep sweep — 9 Nov 2026

Run: `RESOLVE_CAP=150 PROBE_CAP=150 python3 .claude/skills/refresh-london-ds/discover.py --bootstrap`
(the first foreground attempt hit the 10-minute tool limit before writing anything; re-run to completion in the background).

`434 raw -> 221 unique DS-family leads (28 agency, 166 Standard DS)` · registry-covered 120 · probed 58 · searched 49 · unresolved employers 39.
The run proposed 17 boards; each was checked against its ATS public API.

## Boards registered: 10
- ashby `refractal` (Refractal) — London postings (16 UK of 30).
- ashby `edited` (EDITED) — London office (3 UK).
- ashby `hawk` (Hawk) — London postings (6 UK).
- greenhouse `archer56` (Archer) — own board; 2 UK postings (Hampshire). Low relevance; kept because it is the employer's own board with UK roles.
- teamtailor `argusmedia` (Argus Media) — 55 postings, UK-based.
- teamtailor `labgenius` (LabGenius Therapeutics) — lists "Data Scientist".
- smartrecruiters `entain` (Entain) — 87 of the first 100 postings are GB.
- pinpoint `youlend` (YouLend) — 29 postings, mostly London.
- workday `formulaone` (Formula.) — London postings (8 for "london" search).
- workday `visa` (Visa) — London postings (GB - London); DS roles seen were India/US, UK roles are non-DS today.

## Boards dropped: 7 (4 denied, 3 unverifiable)
Added to `board_denylist.json`:
- greenhouse `pulse` — healthcare staffing agency (NHS locum/nursing), not an employer.
- ashby `alan` — the French health insurer Alan, not The Alan Turing Institute; no UK posts.
- ashby `ATG` — only US (NYC/SF) roles.
- smartrecruiters `Acuity1` — one posting, Vienna only.

Removed but NOT denied (could not verify, may be valid later):
- workable `friendmts` (Friend MTS) — API returned 429/1015 on every retry.
- workday `dell` and `justeat` — the cxs endpoint returned HTTP 422 for every request body, so UK postings could not be confirmed.

## Manual posts added: 1
- Muzz — Senior Data Scientist, London hybrid (https://engineering.muzz.com/careers/data-scientist). Page title and JSON-LD name the role; posted £80k–£90k + equity.

## Searches
Site-scoped WebSearch run for Muzz, MVF, Haleon, Canopius only. MVF's posting (careers.mvfglobal.com/jobs/5407614) returns 410 Gone; Haleon and Canopius results were aggregator-only/stale (Haleon's fixed-term role excluded); no ATS board found for any.

## Still unresolved (39)
Everything in `discovered_unresolved_employers.json` except Muzz: incl. Ampstek, AtkinsRéalis, Axom Gaming, Betway Global, Bodhi, Canopius, Capgemini Invent, Ford, GlobalLogic, Goldman Sachs, Haleon, Haven, IBM, Jazz Pharmaceuticals, Keit, LexisNexis Risk, MVF, McKinsey/QuantumBlack, Meta, Network Rail, Ocado Logistics, Qogita, SMG, Unique AI, VE3, VOIS, Welltower, i3 and several recruiters. Not searched this run (time cap): the remainder beyond the four above.
