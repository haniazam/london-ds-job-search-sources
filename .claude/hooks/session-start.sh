#!/bin/bash
# SessionStart hook: make the JS-site pass of refresh_roles.py work in Claude Code cloud sessions
# (daily/weekly Routines included). Chromium is pre-installed at $PLAYWRIGHT_BROWSERS_PATH; only
# the Python package is missing. refresh_roles.py falls back to that Chromium when pip's Playwright
# expects a newer build, so no browser download is needed. Idempotent; remote sessions only.
set -euo pipefail
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
if python3 -c "import playwright" 2>/dev/null; then
  echo "playwright already installed"
  exit 0
fi
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
pip install -q --disable-pip-version-check playwright
python3 -c "import playwright, sys; print('playwright', playwright.__version__ if hasattr(playwright, '__version__') else 'installed')"
