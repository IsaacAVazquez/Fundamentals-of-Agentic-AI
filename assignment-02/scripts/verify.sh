#!/usr/bin/env bash
# Execute the notebook end to end with a 5-episode run and check the artifacts. Takes about a minute on Apple Silicon.
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python tests/verify_notebook.py --kernel python3 --no-popups
