#!/usr/bin/env bash
# Build .venv with uv on Python 3.11+ and install the pipeline command plus optional extras.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v uv >/dev/null; then echo "install uv first: https://docs.astral.sh/uv/"; exit 1; fi
uv venv .venv --python 3.13 || uv venv .venv
uv pip install --python .venv/bin/python -e ".[anthropic,dashboard,test]"
echo "ok: .venv/bin/pipeline --help"
