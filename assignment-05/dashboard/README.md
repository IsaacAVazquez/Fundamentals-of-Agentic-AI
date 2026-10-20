# Dashboard

A FastAPI backend that reads one loaded run from a database and serves JSON to a static page. See the assignment README for the deployment steps; in short, load a run with `pipeline dashboard-load --run-dir <run> --database-url <postgres url>`, set `DATABASE_URL` on the host, and deploy this folder as the project root. The page and the API never read run folders and never call a model.

Local: `DATABASE_URL=sqlite:///dashboard/dashboard.sqlite uvicorn dashboard.app:app --port 8000` from `assignment-05/`, then open http://localhost:8000.
