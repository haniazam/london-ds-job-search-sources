# Weekly deep sweep — 19 Oct 2026

Run: `RESOLVE_CAP=150 PROBE_CAP=150 python3 .claude/skills/refresh-london-ds/discover.py --bootstrap`
(first foreground attempt hit the 10-minute tool limit; re-run to completion in the background).

`434 raw -> 218 unique DS-family leads (23 agency, 166 Standard DS)` · registry-covered 141 · probed 37 · searched 34 · unresolved employers 31.

## Boards registered: 5 (all reviewed against the ATS public API)
- ashby `beamery` (Beamery) — own board; lists a London Senior Data Scientist.
- ashby `teya` (Teya) — own board; includes London and other UK locations.
- workday `aig` (AIG) — own tenant; London postings incl. "Data Scientist, GenAI".
- workable `infosys-consulting-europe` (Infosys Consulting) — own board; API rate-limited (429/1015) during review, accepted because the Workable feed shows its London "Data Scientist - GenAI - Consultant" post.
- greenhouse `via` (Via) — own board; lists London, "Remote - England" and multi-city UK postings.

## Boards dropped: 0 proposed this run
Deny-list re-hits (MPower Plus, GoldmanSachs2, magic.dev) were correctly suppressed.
Extra probe: greenhouse `haven` exists but is Haven Interactive Studios (Montreal games) — not the London Haven; added to the deny list.

## Manual posts added: 0
12 employer-site posts in `discovered_posts.json` came from the Workable feed (Kroo Data Scientist and Infosys DS are already returned by the Workable feed/new board; the rest are ML-engineer titles, out of Standard DS scope).

## Searches
Token probes (greenhouse/ashby/lever) for BBC Studios, Bibby, Haven, PureGym, Compare the Market, Betway, Earnix, Qogita, Costa, Daintta, Klarna, Zepz, Unique AI, MarketCast, CEERISK found no board other than the rejected `haven`. WebSearch site-scoped queries were not run in this scheduled session (tool not loaded), so those employers stay unresolved.

## Still unresolved (31)
Acuity Analytics, BBC Studios, Betway Global, Bibby Financial Services, CEERISK Consulting, Compare the Market, Costa Coffee, Daintta, DatacenterDynamics, Earnix, Ford Motor Company, Goldman Sachs, Haven, IBM, MPower Plus, Magic Memories, MarketCast, McKinsey & Company, Meta, PureGym, Qogita, QuantumBlack, SBS and others in `discovered_unresolved_employers.json`.
