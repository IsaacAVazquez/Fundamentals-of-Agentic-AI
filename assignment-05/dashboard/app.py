"""Dashboard backend: a FastAPI app that reads the loaded run from the database and serves it
as JSON plus the static page. It never reads run folders and never calls a model."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse


def default_url(url: str | None) -> str:
    return url or os.environ.get("DATABASE_URL") or "sqlite:///dashboard/dashboard.sqlite"


class DB:
    """Read-only connection: '?' placeholders for SQLite, '%s' for psycopg. The deploy root is dashboard/, so this
    file cannot import the writer in insight_pipeline/dashboard_load.py; the two stay small on purpose."""

    def __init__(self, url: str):
        self.url = url
        if url.startswith("sqlite"):
            self.conn = sqlite3.connect(url.split("///", 1)[1] if "///" in url else url.split("sqlite:", 1)[1])
            self.conn.row_factory = sqlite3.Row
            self.ph = "?"
        else:
            import psycopg
            from psycopg.rows import dict_row
            self.conn = psycopg.connect(url, row_factory=dict_row)
            self.ph = "%s"

    def fetchall(self, sql: str, params=()):
        return [dict(r) for r in self.conn.execute(sql.replace("?", self.ph) if self.ph != "?" else sql, params).fetchall()]

    def close(self):
        self.conn.close()

app = FastAPI(title="Spotify review insight dashboard", docs_url="/api/docs")
STATIC = Path(__file__).resolve().parent / "static"


def db() -> DB:
    try:
        return DB(default_url(os.environ.get("DATABASE_URL")))
    except Exception as exc:  # connection failure surfaces as a 503, not a crash
        raise HTTPException(503, f"database unavailable: {type(exc).__name__}")


def latest_run(d: DB, run_id: str | None = None) -> dict:
    rows = d.fetchall("SELECT run_id, loaded_at, synthetic FROM runs WHERE run_id = ?", (run_id,)) if run_id else \
        d.fetchall("SELECT run_id, loaded_at, synthetic FROM runs ORDER BY loaded_at DESC LIMIT 1")
    if not rows:
        raise HTTPException(404, "no run loaded; run `pipeline dashboard-load`")
    return rows[0]


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health():
    d = db()
    try:
        runs = d.fetchall("SELECT run_id, loaded_at, synthetic FROM runs ORDER BY loaded_at DESC")
    finally:
        d.close()
    return {"ok": True, "database": "postgres" if not d.url.startswith("sqlite") else "sqlite", "runs": runs}


@app.get("/api/summary")
def summary(run_id: str | None = None):
    d = db()
    try:
        run = latest_run(d, run_id)
        metrics = {r["name"]: json.loads(r["value"]) for r in d.fetchall("SELECT name, value FROM metrics WHERE run_id = ?", (run["run_id"],))}
        rec = d.fetchall("SELECT priority_issue_id, recommendation, model, generated_at FROM recommendations WHERE run_id = ?", (run["run_id"],))
    finally:
        d.close()
    return {"run": run, "metrics": metrics, "recommendation": rec[0] if rec else None}


@app.get("/api/issues")
def issues(run_id: str | None = None):
    d = db()
    try:
        run = latest_run(d, run_id)
        rows = d.fetchall("SELECT * FROM issues WHERE run_id = ? ORDER BY rank", (run["run_id"],))
    finally:
        d.close()
    return {"run_id": run["run_id"], "issues": rows}


@app.get("/api/issues/{issue_id}")
def issue(issue_id: str, run_id: str | None = None):
    d = db()
    try:
        run = latest_run(d, run_id)
        rows = d.fetchall("SELECT * FROM issues WHERE run_id = ? AND issue_id = ?", (run["run_id"], issue_id))
        if not rows:
            raise HTTPException(404, "unknown issue")
        ev = d.fetchall("SELECT review_id, severity, intent, quote, review_rating, review_timestamp FROM evidence WHERE run_id = ? AND issue_id = ? ORDER BY severity DESC, review_id", (run["run_id"], issue_id))
        claims = d.fetchall("SELECT claim_id, metric, value, computation FROM claims WHERE run_id = ? AND issue_id = ? ORDER BY claim_id", (run["run_id"], issue_id))
        trend = d.fetchall("SELECT month, complaints, month_total, share, partial FROM trend WHERE run_id = ? AND issue_id = ? ORDER BY month", (run["run_id"], issue_id))
    finally:
        d.close()
    return {"issue": rows[0], "evidence": ev, "claims": claims, "trend": trend}


@app.get("/api/claims")
def claims(run_id: str | None = None):
    d = db()
    try:
        run = latest_run(d, run_id)
        rows = d.fetchall("SELECT claim_id, issue_id, metric, value, computation FROM claims WHERE run_id = ? ORDER BY CAST(SUBSTR(claim_id, 2) AS INTEGER)", (run["run_id"],))
    finally:
        d.close()
    return {"run_id": run["run_id"], "claims": rows}


@app.get("/api/recommendations")
def recommendations(run_id: str | None = None):
    d = db()
    try:
        run = latest_run(d, run_id)
        rows = d.fetchall("SELECT * FROM recommendations WHERE run_id = ?", (run["run_id"],))
    finally:
        d.close()
    if not rows:
        return JSONResponse({"run_id": run["run_id"], "recommendation": None})
    r = rows[0]
    r["alternatives"] = json.loads(r.pop("alternatives_json") or "[]")
    r["cited_claims"] = json.loads(r.pop("cited_claims_json") or "[]")
    r["memo_check"] = json.loads(r.pop("memo_check_json") or "{}")
    return {"run_id": run["run_id"], "recommendation": r}
