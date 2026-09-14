#!/usr/bin/env bash
# Build the Python 3.13 environment the notebook expects. Idempotent.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-/opt/homebrew/bin/python3.13}"
uv venv -q --allow-existing --python "$PY" .venv
uv pip install -q --python .venv/bin/python -r requirements.txt nbclient nbformat ipykernel
.venv/bin/python -c "import torch,sys;print('python',sys.version.split()[0],'torch',torch.__version__,'mps',torch.backends.mps.is_available())"
