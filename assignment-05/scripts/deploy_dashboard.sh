#!/usr/bin/env bash
# Load a finished run into Postgres and deploy the dashboard folder to Vercel.
# Needs DATABASE_URL (a Neon connection string) and a logged-in `vercel` CLI.
set -euo pipefail
cd "$(dirname "$0")/.."
RUN="${1:?run dir}"
: "${DATABASE_URL:?set DATABASE_URL to the Neon connection string}"
P=".venv/bin/pipeline"; [ -x "$P" ] || P="python3 -m insight_pipeline"
$P dashboard-load --run-dir "$RUN" --database-url "$DATABASE_URL"
cd dashboard
vercel env add DATABASE_URL production <<< "$DATABASE_URL" || true
vercel --prod
