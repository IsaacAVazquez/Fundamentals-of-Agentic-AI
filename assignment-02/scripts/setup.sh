#!/usr/bin/env bash
# Build the Python 3.13 environment the notebook expects. Idempotent.
# uv uses any Python 3.13 it can find, or downloads one; set PYTHON=/path/to/python3.13 to pick a specific one.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v uv >/dev/null || { echo "uv is not installed. See https://docs.astral.sh/uv/getting-started/installation/" >&2; exit 1; }
uv venv -q --allow-existing --python "${PYTHON:-3.13}" .venv
uv pip install -q --python .venv/bin/python -r requirements.txt pip nbclient nbformat ipykernel
# The notebook's metadata and tests/verify_notebook.py name the kernel py313.
.venv/bin/python -m ipykernel install --sys-prefix --name py313 --display-name "Python 3.13" >/dev/null
.venv/bin/python -c "import torch,sys;print('python',sys.version.split()[0],'torch',torch.__version__,'mps',torch.backends.mps.is_available())"
