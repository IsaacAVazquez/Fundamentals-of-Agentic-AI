#!/usr/bin/env bash
# Offline rerun after the post-deadline cleanup: the full offline demo (with the E2B comparison), then a forced
# re-ingest of one source against a copy of the vault to prove it rewrites the same notes. Wi-Fi off first.
set -euo pipefail
cd "$(dirname "$0")/.."
export WIKI_RUN_ID="$(date +%Y%m%d-%H%M%S)-gemma4-e4b"
R="results/$WIKI_RUN_ID"

COMPARE_MODEL=gemma4:e2b scripts/offline_demo.sh

echo
echo "================ forced re-ingest of one source on a vault copy ================"
rsync -a --exclude .obsidian vault/ "$R/vault-reingest/"
(cd "$R/vault-reingest" && find wiki -name '*.md' | sort) > "$R/notes-before.txt"
.venv/bin/wiki ingest "$R/vault-reingest/raw/Networking Tracker README.md" --force \
  --vault "$R/vault-reingest" --index-dir "$R/index-reingest" --run-id "$WIKI_RUN_ID/reingest" \
  2>&1 | tee "$R/reingest.txt"
(cd "$R/vault-reingest" && find wiki -name '*.md' | sort) > "$R/notes-after.txt"
if diff "$R/notes-before.txt" "$R/notes-after.txt"; then echo "no duplicates"; else echo "NOTE LIST CHANGED"; fi

echo
echo "Done. Run folder: $R"
