#!/usr/bin/env bash
# Open the notebook in JupyterLab using the project environment.
set -euo pipefail
cd "$(dirname "$0")/.."
exec .venv/bin/jupyter lab pacman_dqn.ipynb
