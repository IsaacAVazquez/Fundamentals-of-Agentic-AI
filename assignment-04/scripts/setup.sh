#!/usr/bin/env bash
# Build the Python 3.13 environment and install the `wiki` command into it. Idempotent.
# uv uses any Python 3.13 it can find, or downloads one; set PYTHON=/path/to/python3.13 to pick a specific one.
# The harness itself needs only the standard library; pytest is installed for tests/.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v uv >/dev/null || { echo "uv is not installed. See https://docs.astral.sh/uv/getting-started/installation/ (on a Mac: brew install uv)" >&2; exit 1; }
uv venv -q --allow-existing --python "${PYTHON:-3.13}" .venv
uv pip install -q --python .venv/bin/python -e . -r requirements.txt
.venv/bin/wiki --version
.venv/bin/python -c 'import sys; print("python", sys.version.split()[0])'
if command -v ollama >/dev/null; then
  ollama --version
else
  echo "ollama is not installed. On a Mac: brew install ollama (or download the app from https://ollama.com/download), start it, then run scripts/pull_model.sh"
fi
