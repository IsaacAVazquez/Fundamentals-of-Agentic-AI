#!/usr/bin/env bash
# Copy a finished run folder and the executed notebook into results/<name>/ for the repository.
# Usage: scripts/publish_run.sh llm_runs/<run folder> <name>
set -euo pipefail
cd "$(dirname "$0")/.."
RUN="${1%/}"; NAME="$2"; DEST="results/$NAME"
[ -f "$RUN/config.json" ] || { echo "$RUN has no config.json" >&2; exit 1; }
mkdir -p "$DEST"
cp -R "$RUN"/. "$DEST"/
cp custom_llm.ipynb "$DEST/custom_llm.executed.ipynb"
ls -la "$DEST" && du -sh "$DEST"
