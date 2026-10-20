#!/usr/bin/env bash
# The full-corpus sequence, in order, with the controls I used. Every step that spends money is marked.
# Usage: scripts/run_full.sh data/spotify_reviews_18months.csv runs/full-<date>
set -euo pipefail
cd "$(dirname "$0")/.."
INPUT="${1:?input csv}"; RUN="${2:?run dir}"
P=".venv/bin/pipeline"; [ -x "$P" ] || P="python3 -m insight_pipeline"
BACKEND="${BACKEND:-anthropic}"; MODEL="${MODEL:-claude-haiku-5-5}"; WORKERS="${WORKERS:-4}"; MAX_SPEND="${MAX_SPEND:-100}"

$P prepare --input "$INPUT" --run-dir "$RUN"                                   # no model
mkdir -p "$RUN/cost" && [ -f "$RUN/cost/rates.csv" ] || cp results/cost-synthetic/rates.csv "$RUN/cost/rates.csv"
$P classify --run-dir "$RUN" --backend "$BACKEND" --model "$MODEL" --effort low \
   --batch-size 25 --workers "$WORKERS" --max-spend "$MAX_SPEND" --rates "$RUN/cost/rates.csv" \
   --fallback-model claude-sonnet-5-5 --fallback-fraction 0.02                   # PAID; Ctrl-C saves progress, rerun resumes
$P verify --run-dir "$RUN" --backend "$BACKEND" --model "$MODEL" --sample 1000 --seed 20261020   # PAID (1,000 reviews)
$P group --run-dir "$RUN" --backend "$BACKEND" --model "$MODEL" --name          # PAID (8 small calls)
$P rank --run-dir "$RUN"                                                        # no model
$P memo --run-dir "$RUN" --backend "$BACKEND" --model claude-sonnet-5-5         # PAID (1 call)
$P eval golden --run-dir "$RUN" --golden evals/golden_50.csv                    # no model
$P eval reproducibility --run-dir "$RUN"                                        # no model
$P export --run-dir "$RUN"                                                      # no model; writes $RUN/grading/
python3 data/check_submission.py "$RUN/grading" || true                         # the course checker, if the ZIP is unpacked in data/
