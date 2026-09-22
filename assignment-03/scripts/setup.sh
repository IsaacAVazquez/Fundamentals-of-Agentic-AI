#!/usr/bin/env bash
# Build the Python 3.13 environment the notebook expects. Idempotent.
# numpy is added because run_evals.py hashes model weights through NumPy and torch no longer pulls it in.
# pillow is for scripts/render_session.py only.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-/opt/homebrew/bin/python3.13}"
uv venv -q --allow-existing --python "$PY" .venv
uv pip install -q --python .venv/bin/python -r requirements.txt numpy pillow pip nbconvert nbclient nbformat ipykernel
.venv/bin/python -c 'import torch, pypdf, numpy, sys; print("python", sys.version.split()[0], "torch", torch.__version__, "numpy", numpy.__version__, "pypdf", pypdf.__version__)'
