#!/usr/bin/env bash
# Set the three section 1 choices, then execute the notebook top to bottom in place.
# Usage: scripts/run_experiment.sh STEPS LEARNING_RATE [CORPUS_FOLDER]
set -euo pipefail
cd "$(dirname "$0")/.."
STEPS="$1"; LR="$2"; FOLDER="${3:-corpus}"
.venv/bin/python - "$STEPS" "$LR" "$FOLDER" <<'PY'
import json, sys
steps, lr, folder = sys.argv[1:]
nb = json.load(open("custom_llm.ipynb"))
cell = nb["cells"][1]
assert cell["cell_type"] == "code" and "TRAINING_STEPS" in "".join(cell["source"])
cell["source"] = [
    'CORPUS = "classroom"       # Teaching sentences + files; "folder" uses only files\n',
    f'CORPUS_FOLDER = "{folder}"   # Add .pdf, .txt and .md files here, including subfolders\n',
    f'TRAINING_STEPS = {int(steps)}      # 10 for setup; 3000 for the main experiment\n',
    f'LEARNING_RATE = {float(lr)}',
]
json.dump(nb, open("custom_llm.ipynb", "w"), indent=1, ensure_ascii=False)
print("Section 1:", "".join(cell["source"]).replace("\n", " | "))
PY
before=$(ls -d llm_runs/*/ 2>/dev/null | sort | tail -1 || true)
caffeinate -is .venv/bin/jupyter-nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.kernel_name=python3 --ExecutePreprocessor.timeout=-1 custom_llm.ipynb
after=$(ls -d llm_runs/*/ | sort | tail -1)
[ "$after" != "$before" ] || { echo "No new run folder was created" >&2; exit 1; }
echo "Run folder: $after"
