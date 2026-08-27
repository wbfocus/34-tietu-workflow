#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$REPO_ROOT/.cursor/skills/34-tietu-workflow/scripts"
BROWSERS="$REPO_ROOT/.playwright-browsers"

echo "Repo: $REPO_ROOT"
command -v node >/dev/null || { echo "need Node.js 20+"; exit 1; }
command -v npm >/dev/null || { echo "need npm"; exit 1; }
if ! command -v python3 >/dev/null && ! command -v python >/dev/null; then
  echo "need Python 3"; exit 1
fi
command -v ffmpeg >/dev/null || echo "WARN: ffmpeg not in PATH (needed for MP4)"

mkdir -p "$BROWSERS"
export PLAYWRIGHT_BROWSERS_PATH="$BROWSERS"
cd "$SCRIPTS"
npm install
npx playwright install chromium
echo "OK  Playwright Chromium -> $BROWSERS"
