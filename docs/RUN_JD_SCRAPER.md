# Runbook — generate the full JDs, commit to GitHub, and upload to Google Drive

Use this in a **fresh Claude Code web session** (it clones `main`, which now
contains everything). Paste the prompt below to the session, or follow the
manual steps.

## Prerequisite: network egress
The scrapers fetch external sites, so the session's environment must allow
outbound web. Set **Network access** to **Full** (or **Custom** with the
domains listed in the project chat / `docs/job-posting-urls.md` hosts) in the
environment settings, then start a **new** session — a running session won't
pick up a policy change. With the default **Trusted** policy every fetch 403s.

## One-shot prompt for the session

> Pull `main`. Run `python3 scripts/fetch_jds.py` to generate
> `docs/job-descriptions-scraped.md`. If many JS-rendered sites come back thin,
> install Playwright (`pip install -r scripts/requirements-scrape.txt && python
> -m playwright install chromium`) and run `python3 scripts/fetch_jds_browser.py`
> instead. Then **save this run as a dated snapshot and commit it**: copy the
> output to `docs/job-descriptions/scraped-<YYYY-MM-DD>.md` (use today's date;
> add `-2`, `-3`… if there's already a snapshot for today), `git add`/`commit`/
> `push` it to `main`, and **do not overwrite or delete any earlier dated
> snapshot** — each run adds a new file so the repo keeps the full version
> history. Finally, create a **new** Google Doc in my Drive folder
> `1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI` ("Job Descriptions - London DS 150k")
> titled "London DS — Full Job Descriptions (scraped) — <YYYY-MM-DD>" from that
> snapshot, using the Google Drive connector; leave all earlier dated Docs in the
> folder untouched. Every rerun therefore produces a new version in both GitHub
> and Drive rather than replacing the last.

## Manual steps

```bash
git pull origin main
python3 scripts/fetch_jds.py          # → docs/job-descriptions-scraped.md
# JS-heavy sites (McKinsey/TikTok/Bloomberg) may need the browser variant:
# pip install -r scripts/requirements-scrape.txt && python -m playwright install chromium
# python3 scripts/fetch_jds_browser.py

# Save this run as a NEW dated snapshot (keeps every prior run):
mkdir -p docs/job-descriptions
cp docs/job-descriptions-scraped.md "docs/job-descriptions/scraped-$(date +%F).md"
# (if a snapshot for today already exists, name the copy scraped-$(date +%F)-2.md, -3, …)

# Commit the new snapshot into the repo (GitHub) — do NOT delete older ones:
git add docs/job-descriptions/
git commit -m "Add scraped job descriptions snapshot $(date +%F)"
git push origin main                  # or push to your working branch
```

### Step 1 — commit the JDs to GitHub (new dated version each run)
Each run is saved as its own dated file under `docs/job-descriptions/`
(`scraped-<YYYY-MM-DD>.md`), so committing and pushing it stores that version of
the job descriptions in GitHub without touching earlier ones. Do this **before**
the Drive upload so the source of truth is version-controlled. The repo therefore
accumulates one snapshot per run — the full version history — and `git log`
over that folder shows exactly when each set was captured. (The scraper's own
`docs/job-descriptions-scraped.md` is just the latest working output; the dated
copy under `docs/job-descriptions/` is the durable version.) If you're running
inside a Claude Code session that is restricted to a feature branch, push there
instead of `main` and open a PR.

### Step 2 — create a new dated Google Doc (keep prior versions)
Then, **as the assistant** (the Python script cannot do this itself — the Drive
connector is only available to Claude, not to scripts): read the dated snapshot
you just committed and create a **new** Google Doc from its text in the Drive
folder **`1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI`** via the Drive MCP `create_file`
tool (`contentMimeType: text/plain`, `parentId` = that folder id), titled:

> **London DS — Full Job Descriptions (scraped) — <YYYY-MM-DD>**

Use the same date as the snapshot. **Do not update or delete the earlier dated
Docs** — leaving them in place is what preserves the version history in Drive, so
the folder ends up with one Doc per run, each dated. (If you reran on a date that
already has a Doc, add a `-2`/`-3` suffix to the title so it stays distinct.)

## Why the script can't upload directly
The Google Drive integration is an Anthropic-managed MCP connector. Its
credentials live server-side and are exposed to the model's tool calls, not to
the shell/`python`. So uploading is a model action, not a script action — hence
the two-step flow above.
