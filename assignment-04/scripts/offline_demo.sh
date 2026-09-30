#!/usr/bin/env bash
# Record the whole offline demonstration for the README. Turn Wi-Fi off first, open a NEW terminal, cd here, then run this.
#
# Usage:
#   scripts/offline_demo.sh                         proves the vault is up to date and runs every check
#   FRESH=1 scripts/offline_demo.sh                 empties vault/wiki and index.md first, so the ingest starts from scratch
#   COMPARE_MODEL=gemma4:e2b scripts/offline_demo.sh   also runs the four ask tests on a second model into a subfolder
#   WIKI_MODEL=gemma4:e2b scripts/offline_demo.sh   use another model for the whole run
#   ALLOW_ONLINE=1 WIKI_BACKEND=fake scripts/offline_demo.sh   dry run without Ollama (container testing only)
#
# Every step is a fresh `wiki` process started after the network went down, and `doctor --require-offline`
# runs first and last. The terminal is recorded with script(1) into results/<run-id>/terminal.txt.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -x .venv/bin/wiki ]; then WIKI=(.venv/bin/wiki); else WIKI=(python3 -m personal_wiki); fi
WIKI=("${WIKI_BIN[@]:-${WIKI[@]}}")
MODEL="${WIKI_MODEL:-gemma4:e4b}"
export WIKI_MODEL="$MODEL"
export WIKI_RUN_ID="${WIKI_RUN_ID:-$(date +%Y%m%d-%H%M%S)-${MODEL//[^A-Za-z0-9.-]/-}}"
RESULTS="${WIKI_RESULTS_DIR:-results}"
RUN_DIR="$RESULTS/$WIKI_RUN_ID"
mkdir -p "$RUN_DIR"

if [ "${1:-}" != "--recorded" ]; then
  if command -v script >/dev/null; then
    case "$(uname)" in
      Darwin) exec script -q "$RUN_DIR/terminal.txt" "$0" --recorded ;;
      *)      exec script -q -c "$0 --recorded" "$RUN_DIR/terminal.txt" ;;
    esac
  fi
  echo "script(1) not found; running without a terminal recording"
fi

step() {  # step NAME COMMAND... : runs the command, appends a JSON line to steps.jsonl, stops the run on failure
  local name=$1; shift
  local start end code
  printf '\n================ %s: %s ================\n' "$name" "$*"
  start=$(date +%s)
  set +e; "$@"; code=$?; set -e
  end=$(date +%s)
  printf '{"name":"%s","command":"%s","started_at":%s,"ended_at":%s,"wall_s":%s,"exit_code":%s}\n' \
    "$name" "$(printf '%s' "$*" | sed 's/"/\\"/g')" "$start" "$end" "$((end - start))" "$code" >> "$RUN_DIR/steps.jsonl"
  if [ "$code" -ne 0 ]; then echo "step $name failed with exit code $code; see $RUN_DIR" >&2; exit "$code"; fi
}

echo "offline demo · run $WIKI_RUN_ID · model $MODEL · $(date)"
VAULT="${WIKI_VAULT:-vault}"
if [ "${FRESH:-0}" = 1 ]; then
  echo "FRESH=1: backing up $VAULT/wiki and $VAULT/index.md to $RUN_DIR/vault-before, then emptying them"
  mkdir -p "$RUN_DIR/vault-before"
  cp -R "$VAULT/wiki" "$RUN_DIR/vault-before/" 2>/dev/null || true
  cp "$VAULT/index.md" "$RUN_DIR/vault-before/" 2>/dev/null || true
  find "$VAULT/wiki" -name '*.md' -type f -delete
  rm -f "$VAULT/index.md"
fi

OFFLINE_FLAG="--require-offline"
if [ "${ALLOW_ONLINE:-0}" = 1 ]; then OFFLINE_FLAG=""; fi   # a plain string: macOS bash 3.2 trips on an empty array under set -u

step device    scripts/device_report.sh "$RUN_DIR"
step doctor    "${WIKI[@]}" doctor $OFFLINE_FLAG --save
step ingest-1  "${WIKI[@]}" ingest
step ingest-2  "${WIKI[@]}" ingest
step eval      "${WIKI[@]}" eval tests/questions.json
step chat      "${WIKI[@]}" chat --script tests/chat_checks.txt
step search    "${WIKI[@]}" search "Pac-Man evaluation score"
step ask-S1    "${WIKI[@]}" ask --id S1 "What did my final Pac-Man agent average on the five evaluation games?"
step doctor-2  "${WIKI[@]}" doctor $OFFLINE_FLAG --save
if [ -n "${COMPARE_MODEL:-}" ]; then
  step eval-compare env WIKI_MODEL="$COMPARE_MODEL" WIKI_RUN_ID="$WIKI_RUN_ID/compare-${COMPARE_MODEL//[^A-Za-z0-9.-]/-}" "${WIKI[@]}" eval tests/questions.json
fi
step manifest  "${WIKI[@]}" manifest
echo
echo "Run folder: $RUN_DIR"
echo "Read: $RUN_DIR/ask/summary.md, $RUN_DIR/chat/chat_checks.md, $RUN_DIR/ingest/ingest_log.md, $RUN_DIR/manifest.json"
