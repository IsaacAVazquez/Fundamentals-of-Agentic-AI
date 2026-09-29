#!/usr/bin/env bash
# Download the Gemma weights once while online. Usage: scripts/pull_model.sh [tag ...]
# Default tags: gemma4:e4b (the model the README is written around) and gemma4:e2b (the comparison run).
set -euo pipefail
cd "$(dirname "$0")/.."
HOST="${WIKI_HOST:-http://localhost:11434}"
command -v ollama >/dev/null || { echo "ollama is not installed. On a Mac: brew install ollama, or install the app from https://ollama.com/download" >&2; exit 1; }
curl -fsS "$HOST/api/version" >/dev/null || { echo "Ollama is not running at $HOST. Run 'ollama serve' or open the Ollama app, then retry." >&2; exit 1; }
tags=("$@")
[ ${#tags[@]} -gt 0 ] || tags=(gemma4:e4b gemma4:e2b)
for tag in "${tags[@]}"; do
  echo "== ollama pull $tag =="
  ollama pull "$tag"
done
echo "== installed models =="
ollama list
echo "== wiki doctor =="
if [ -x .venv/bin/wiki ]; then .venv/bin/wiki doctor; else python3 -m personal_wiki doctor; fi
