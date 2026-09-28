#!/usr/bin/env bash
# Build the Python 3.13 environment the notebook expects. Idempotent.
# uv uses any Python 3.13 it can find, or downloads one; set PYTHON=/path/to/python3.13 to pick a specific one.
# numpy is added because run_evals.py hashes model weights through NumPy and torch no longer pulls it in.
# pillow is for scripts/render_session.py only.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v uv >/dev/null || { echo "uv is not installed. See https://docs.astral.sh/uv/getting-started/installation/" >&2; exit 1; }
uv venv -q --allow-existing --python "${PYTHON:-3.13}" .venv
uv pip install -q --python .venv/bin/python -r requirements.txt numpy pillow pip nbconvert nbclient nbformat ipykernel
.venv/bin/python -c 'import torch, pypdf, numpy, sys; print("python", sys.version.split()[0], "torch", torch.__version__, "numpy", numpy.__version__, "pypdf", pypdf.__version__)'
