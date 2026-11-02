# Weekly deep sweep — 2 Nov 2026

Run: `RESOLVE_CAP=150 PROBE_CAP=150 python3 .claude/skills/refresh-london-ds/discover.py --bootstrap`
(exceeds the 10-minute foreground limit; ran detached to completion).
Resolve: registry-covered 123 · probed 56 · searched 48 · unresolved employers 41. The script proposed 12 boards.

## Boards registered: 6 (reviewed against each ATS public API)
- smartrecruiters `entain` (Entain) — own board; 254 UK postings.
- workday `Formula.` (formulaone/F1) — own tenant; London postings.
- workday `Visa` (visa/Visa) — own tenant; London postings.
- pinpoint `youlend` (YouLend) — own board; London roles incl. Lead Data Analyst.
- ashby `hawk` (Hawk) — own board; London postings (its Data Scientist is Munich).
- teamtailor `labgenius` (LabGenius) — own feed; London Data Scientist posted 28 Oct.

## Boards dropped: 6 (added to board_denylist.json)
- greenhouse `pulse` — healthcare staffing agency, not an employer.
- smartrecruiters `Verisk` — 0 UK postings.
- workable `friendmts` — empty board.
- pinpoint `royal` — Paris/New York roles, not Royal Mail UK.
- workday `dell` — CXS API returns 422; UK posting unverifiable.
- workday `roberthalf` — recruiter (fr-CA site).

## Manual posts added: 1
- MVF — Senior Data Scientist, Decision Science (London). Own Teamtailor-hosted career site; listed in its jobs.json (16 Oct) and page title confirmed.

The 10 posts in `discovered_posts.json` all come from the Workable feed (Kroo DS is already returned; the rest are ML-engineer titles out of Standard DS scope), so none were added.

## Site-scoped searches
Searched Muzz, MVF, Haleon, Ocado, Perspectum, Unique AI, Qogita, PureGym over the ATS hosts: no new ATS boards surfaced (results were aggregators only). Muzz's postings found were closed. Haleon/Ocado hits were aggregator-only, several junior/FTC; not added without a verifiable own-site posting URL. Perspectum's Senior DS is Oxford (not London). PureGym/Qogita seen only on Built In.

## Still unresolved (40)
Remaining entries of `discovered_unresolved_employers.json` after MVF, e.g. AtkinsRéalis, Betway Global, Capgemini Invent, Costa Coffee, Domino's UK, Earnix, Ford, GlobalLogic, Goldman Sachs, Haleon, Haven, IBM, Magic Memories, MarketCast, McKinsey/QuantumBlack, Meta, MHCLG, Muzz, Network Rail, Ocado, Perspectum, PureGym, Qogita, SBS, SMG, Sainsbury's, TUI, UKHSA, Unique AI, Volter and others. Most were not individually searched this run.
