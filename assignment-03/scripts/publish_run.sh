#!/usr/bin/env bash
# Copy a finished run folder and the executed notebook into results/<name>/ for the repository.
# Usage: scripts/publish_run.sh llm_runs/<run folder> <name>
set -euo pipefail
[ $# -eq 2 ] || { echo "usage: $0 llm_runs/<run folder> <name>" >&2; exit 1; }
RUN="$(cd "$1" && pwd)"  # resolved before changing directory, so a path relative to the caller works
NAME="$2"
cd "$(dirname "$0")/.."
DEST="results/$NAME"
[ -f "$RUN/config.json" ] || { echo "$RUN has no config.json" >&2; exit 1; }
mkdir -p "$DEST"
cp -R "$RUN"/. "$DEST"/
cp custom_llm.ipynb "$DEST/custom_llm.executed.ipynb"
ls -la "$DEST" && du -sh "$DEST"
