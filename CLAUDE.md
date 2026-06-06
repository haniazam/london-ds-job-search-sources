# London DS job search — project memory

Output conventions for the two living deliverables in the Google Drive folder
`1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI` ("Job Descriptions - London DS 150k").
The `refresh-london-ds` skill regenerates both; keep them in these formats.

## Scope / selection preferences
- **London (or London-eligible)** Data-Science-family roles only. London-eligible =
  London / Remote-UK / "London or Stockholm" / multi-location lists that include London.
- **Include BOTH regular/mid AND senior roles.** Do not restrict to senior.
- **Exclude intern / graduate / apprentice / placement** roles.
- Every listed role must be a **unique, active individual job post** (resolves to a
  live posting), never a careers landing/search page or a perennial talent-pool / EOI.
- Dedupe by URL. Re-verify links each refresh — IDs go 404 often.

## Consolidated spreadsheet (CSV → Google Sheet)
- Columns, in order: `Company, Role, Level, Location, Apply URL (unique active post), Status, Notes`.
- `Level` = `Senior+` (title has senior/staff/lead/principal/head/director/manager/sr/distinguished)
  or `Regular/Mid` otherwise.
- **Active roles first**, one row per URL, grouped by company; use proper display
  names (e.g. "Google DeepMind", "Qube RT", not ATS tokens).
- Then a divider row `— COMPANIES WITH NO ACTIVE LONDON DS ROLE —`, followed by the
  no-active-role companies (one row each) with a short reason in `Notes`.
- Title pattern: `London DS — Combined Active Job Posts vN (<YYYY-MM-DD>)`.

## Job-descriptions document (TXT → Google Doc)
- **Plain text only — NO markdown.** No `#`, `*`, `**`, or backticks.
- Structure: a top title + summary line; per company a banner of `=` lines with the
  company name in UPPERCASE; per role a `-` divider, the role title, a
  `Level: …    Location: …` line, an `Apply: <url>` line, another `-` divider, then
  the body.
- Body = role/responsibilities/requirements, boilerplate (company intro, benefits,
  EEO) trimmed; bullets as `-`. Keep the file small enough to upload in one shot
  (per-role cap ~1.1k chars; whole doc < ~90 KB).
- Title pattern: `London DS — Active Role JDs & Requirements vN (<YYYY-MM-DD>)`.

## Visual style guide (from the user's Claude Doc Style Guide, claude.ai artifact)
Applies to planning/tracking docs (this JD doc + tracker) — NOT to ATS resume bodies
(those stay plain, no tables/graphics).
- Body: Lato 10pt, color `#202124`, line spacing 1.2.
- Headings: slate blue `#3D5A80`, using named heading styles only.
- One accent colour only across the doc (the slate blue). Do not over-style — restraint is the goal.
- Tables: header row tinted `#EAEFF5` with bold accent text; pale gridlines; padded cells.
- Space before headings ~10–12pt; HR dividers between major sections.
- Produce the Google Doc by uploading **HTML** (`contentMimeType: text/html`) so Drive
  converts it to a styled Doc with real heading styles/colours/tables — NOT markdown and
  NOT raw plain text. (A native Google Sheet cannot be cell-styled via `create_file`, which
  only ingests raw CSV values; keep the tracker as a data Sheet, or render the roster as a
  styled table inside a Doc if styling is required.)

## Upload mechanism
- The Google Drive connector is a model-only tool; scripts cannot upload. The
  assistant reads the generated file and calls `mcp__Google_Drive__create_file`
  (`text/csv` → Sheet, `text/plain` → Doc) with `parentId` = the folder above.

## Known dead/blocked (re-check, don't trust blindly)
McKinsey/QuantumBlack (Akamai 503), Snap (Contentful SPA), Citadel (talent-pool EOI
only), Stripe (no London DS). See `.claude/skills/refresh-london-ds/SKILL.md` for the
full endpoint map and gotchas.
