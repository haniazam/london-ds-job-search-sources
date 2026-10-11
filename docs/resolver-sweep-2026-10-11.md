# Weekly deep sweep — 11 Oct 2026 (manual test run, ahead of the Monday schedule)

Run (in the Routine session `session_01VXwQYbNNEhQrhiJbpWM5rn`):
`RESOLVE_CAP=150 PROBE_CAP=150 python3 .claude/skills/refresh-london-ds/discover.py --bootstrap`

`[discover] 432 raw -> 229 unique DS-family leads (24 agency, 177 Standard DS)` ·
`[resolve] registry-covered 148 · probed 32 · searched 32 · unresolved employers 27` · 5 boards proposed, 18 employer-site posts.

The Routine session could not push (git proxy 403: repo not in the session's sources, and `add_repo` is not
loadable there), so its edits were re-applied by hand from its transcript into this branch. Every post URL was
re-fetched before committing (all 200 with the role in `<title>`).

## Boards registered: 0

All five proposed tokens were reverted from `boards.json` (each is a repeat of a false match already dropped on 10–11 Oct):

| Proposed | Verdict |
|---|---|
| smartrecruiters `Dominos` | Domino's US corporate board (24,843 postings, all `us`), not Domino's Pizza UK & Ireland |
| smartrecruiters `GoldmanSachs2` | three-job stub, all US |
| smartrecruiters `HCLTechHungary` | regional (Hungary) board, 0 postings |
| workable `magic-careers` | Workable 429s from the container — unverifiable; not confirmed as MAGIC AI's board |
| ashby `magic.dev` | Magic.dev (San Francisco ML lab), not Magic Memories |

Follow-up for the script: the single-word corroboration rule still re-proposes these every bootstrap; they could go in a deny-list.

## Manual posts added: 8 (`data/manual_posts.json`)

From `discovered_posts.json` (Workable job-feed, employers with no registered board). Each page fetched today and its `<title>` names the role; fractional, ML-engineer and non-DS titles skipped.

G MASS (Senior Data Scientist, FP&A, full-time), Informed Solutions (Lead DS; Senior DS), Solirius Reply (Senior DS),
Adzuna (DS, AI & Innovation — Fulham), Coefficient (DS), LoopMe (AVP Data Science), MAGIC (AI/Data Scientist).

Note: the Workable pages' `<title>` is only "<Company> | Jobs by Workable"-style for dead and live alike on some tenants — the refresh's by-title re-verify will catch closures.

## Site-scoped searches for unresolved employers

Searched PureGym, Unique AI, Zepz, MarketCast, Klarna, British Airways. No new ATS board found for any.
Leads that surfaced were dead on fetch: BA Principal Product DS (careers.ba.com, 404 "Custom Job Error"), Klarna Senior DS (klarnagroup.teamtailor.com, 404; `jobs.json` 404), PureGym (careers.puregym.com/job/75802224, 404).
The BA Principal DS Finance & Transformation post appears only on the itjobboard.co.uk aggregator (Harmondsworth, not verified on BA's site) — not added.
The remaining 21 employers were not re-searched; they are unchanged from the 10 Oct sweep (section E / "not fixable from the container").

## Radar diff — NOT DONE

`https://hani-job-search-radar.azamhani95.chatgpt.site/api/state` returned **HTTP 401 "Sign in required"** from the container, so no
comparison against the registry could be made. Needs a public/token-bearing endpoint or a manual export.

## Still unresolved (27)

Acuity Analytics, BAE Systems, British Airways, CEERISK Consulting, Chubb, Compare the Market, Costa Coffee, DatacenterDynamics,
GamblingCareers.com (job board), IBM, Klarna, L.E.K. Consulting, MarketCast, McKinsey & Company, Meta, NatWest Group, PureGym,
Qogita, QuantumBlack, SBS, SMG, Tesco (Welwyn, not London), Unique AI, Welltower, Zepz, i3, trg.
