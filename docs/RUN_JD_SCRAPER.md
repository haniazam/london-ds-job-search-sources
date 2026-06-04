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
> instead. Then **commit `docs/job-descriptions-scraped.md` and push it to
> `main`** so the scraped JDs live in the repo. Finally, upload that same file to
> my Google Drive folder `1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI` ("Job Descriptions -
> London DS 150k") as a new Google Doc titled "London DS — Full Job Descriptions
> (scraped)" using the Google Drive connector.

## Manual steps

```bash
git pull origin main
python3 scripts/fetch_jds.py          # → docs/job-descriptions-scraped.md
# JS-heavy sites (McKinsey/TikTok/Bloomberg) may need the browser variant:
# pip install -r scripts/requirements-scrape.txt && python -m playwright install chromium
# python3 scripts/fetch_jds_browser.py

# Commit the scraped JDs into the repo (GitHub):
git add docs/job-descriptions-scraped.md
git commit -m "Update scraped job descriptions"
git push origin main                  # or push to your working branch
```

### Step 1 — commit the JDs to GitHub
The generated `docs/job-descriptions-scraped.md` lives in the repo, so committing
and pushing it (the `git add/commit/push` above) is all it takes to store the job
descriptions in GitHub. Do this **before** the Drive upload so the source of
truth is version-controlled. If you're running inside a Claude Code session that
is restricted to a feature branch, push there instead of `main` and open a PR.

### Step 2 — upload to Google Drive
Then, **as the assistant** (the Python script cannot do this itself — the Drive
connector is only available to Claude, not to scripts): read
`docs/job-descriptions-scraped.md` and create a Google Doc from its text in the
Drive folder **`1jkaK-hFTZf8U6iRJ9clV6Q-LSxJ3eaYI`** via the Drive MCP
`create_file` tool (`contentMimeType: text/plain`, `parentId` = that folder id).

## Why the script can't upload directly
The Google Drive integration is an Anthropic-managed MCP connector. Its
credentials live server-side and are exposed to the model's tool calls, not to
the shell/`python`. So uploading is a model action, not a script action — hence
the two-step flow above.
