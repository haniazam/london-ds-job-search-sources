# Weekly deep sweep — 26 Oct 2026

Run: `RESOLVE_CAP=150 PROBE_CAP=150 python3 .claude/skills/refresh-london-ds/discover.py --bootstrap`
(foreground attempt hit the 10-minute tool limit; re-run to completion in the background).

`437 raw -> 229 unique DS-family leads (23 agency, 182 Standard DS)` · registry-covered 140 · probed 51 · searched 48 · unresolved employers 41.

## Boards registered: 6
Proposed by discover.py and kept after checking the ATS public API:
- greenhouse `rightmovecareers` (Rightmove) — own board; London "Associate Data Scientist" and other London posts.
- greenhouse `archer56` (Archer) — own board (eVTOL maker); only 3 UK postings (South East Hampshire), none London DS. Kept as it meets the own-board + UK-posting bar.
- lever `ekimetrics` (Ekimetrics) — own board; London "Manager, Data Science & Marketing Effectiveness (MMM)" (interns excluded).

Found by site-scoped search and verified via API:
- workday `Haleon` (gsknch.wd3 / GSKCareers) — Haleon's tenant; live London Bankside "Data Scientist" and "Senior Data Scientist".
- workday `FCA` (fca.wd3 / FCA_Careers) — Financial Conduct Authority; London "Data Scientist" (JR0022593-1, also Leeds/Edinburgh).
- oraclehcm `Sainsbury's` (hdhe.fa.em3 / CX) — Sainsbury's/Argos tenant; two London "Data Scientist" reqs (400091330, 400078333) among many London roles.

## Boards dropped: 5 (added to board_denylist.json)
- greenhouse `pulse` — healthcare-staffing recruiter (2,700+ NHS-style roles), not an employer DS board.
- workable `friendmts` — unverifiable (Workable 1015/429).
- smartrecruiters `BAESystems3` — US stub, all 9 postings US.
- pinpoint `royal` — unrelated tenant (Paris/NY/London), not Royal Mail.
- workday `ocado` — cxs endpoint 403; unverifiable.
Deny-list re-hits (Domino's, GoldmanSachs2, magic.dev) were suppressed.

## Manual posts added: 0
11 posts in `discovered_posts.json` all came from the Workable feed; only Kroo "Data Scientist" is Standard DS and is already returned by the feed. The rest are ML-engineer titles (out of scope).

## Searches
Site-scoped searches (ATS hosts) run for King, MVF, Haleon, Zepz, Qogita, PureGym, Bibby, Sainsbury's, Tesco, TUI, BBC Studios, Compare the Market, Costa, FCA, Munich Re, Earnix, Betway. Not run per-employer: the remaining long-tail names. Zepz: `zepzgroup` greenhouse embed exists but the board API returns 404 — unverified, not registered. Tesco's only hit is Bengaluru (denied).

## Still unresolved (35)
Acuity Analytics, AtkinsRéalis, Axom Gaming, BBC Studios, Betway Global, Bibby Financial Services, Costa Coffee, DatacenterDynamics, Domino's UK, Ford, Goldman Sachs, Haven, IBM, King, MVF, Magic Memories, MarketCast, Marshall Wolfe, McKinsey, Meta, MHCLG, Munich Re, PureGym, Qogita, QuantumBlack, SBS, SMG, Syntrace, TUI, Tenth Revolution Group, Tesco, UKHSA, VE3, Zepz and others in `discovered_unresolved_employers.json`.
