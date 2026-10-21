"""Load a finished run's saved outputs into the dashboard database.

Works against Postgres (DATABASE_URL=postgres://...) through psycopg, or a local SQLite file
(sqlite:///path). The backend in dashboard/ reads these tables and nothing else.
"""
from __future__ import annotations

import csv
import json
import os
import sqlite3
from pathlib import Path

from .store import Store, now_iso

DDL = [
    "CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, loaded_at TEXT, synthetic INTEGER, source_json TEXT, summary_json TEXT, ingestion_json TEXT)",
    "CREATE TABLE IF NOT EXISTS metrics (run_id TEXT, name TEXT, value TEXT, PRIMARY KEY (run_id, name))",
    "CREATE TABLE IF NOT EXISTS issues (run_id TEXT, issue_id TEXT, rank INTEGER, name TEXT, topic TEXT, description TEXT, complaint_count INTEGER, cancellation_count INTEGER, severity_sum INTEGER, mean_severity TEXT, score INTEGER, mean_sentiment TEXT, needs_review_count INTEGER, share TEXT, PRIMARY KEY (run_id, issue_id))",
    "CREATE TABLE IF NOT EXISTS claims (run_id TEXT, claim_id TEXT, issue_id TEXT, metric TEXT, value TEXT, computation TEXT, PRIMARY KEY (run_id, claim_id))",
    "CREATE TABLE IF NOT EXISTS evidence (run_id TEXT, issue_id TEXT, review_id TEXT, severity INTEGER, intent TEXT, quote TEXT, review_rating TEXT, review_timestamp TEXT, PRIMARY KEY (run_id, issue_id, review_id))",
    "CREATE TABLE IF NOT EXISTS trend (run_id TEXT, month TEXT, issue_id TEXT, complaints INTEGER, month_total INTEGER, share TEXT, partial INTEGER, PRIMARY KEY (run_id, month, issue_id))",
    "CREATE TABLE IF NOT EXISTS recommendations (run_id TEXT PRIMARY KEY, model TEXT, priority_issue_id TEXT, recommendation TEXT, alternatives_json TEXT, cited_claims_json TEXT, memo_markdown TEXT, memo_check_json TEXT, generated_at TEXT)",
]


class DB:
    """Tiny two-driver wrapper: '?' placeholders for SQLite, '%s' for psycopg."""

    def __init__(self, url: str):
        self.url = url
        if url.startswith("sqlite"):
            path = url.split("///", 1)[1] if "///" in url else url.split("sqlite:", 1)[1]
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(path)
            self.conn.row_factory = sqlite3.Row
            self.ph = "?"
        else:
            import psycopg
            from psycopg.rows import dict_row
            self.conn = psycopg.connect(url, row_factory=dict_row)
            self.ph = "%s"

    def q(self, sql: str) -> str:
        return sql.replace("?", self.ph) if self.ph != "?" else sql

    def execute(self, sql: str, params=()):
        return self.conn.execute(self.q(sql), params)

    def executemany(self, sql: str, rows):
        cur = self.conn.cursor()
        cur.executemany(self.q(sql), rows)
        return cur

    def fetchall(self, sql: str, params=()):
        rows = self.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def default_url(url: str | None) -> str:
    return url or os.environ.get("DATABASE_URL") or "sqlite:///dashboard/dashboard.sqlite"


def load_run(run_dir: Path, database_url: str | None = None, evidence_per_issue: int = 12) -> dict:
    run_dir = Path(run_dir)
    db = DB(default_url(database_url))
    for ddl in DDL:
        db.execute(ddl)
    store = Store(run_dir)
    run_id = store.get_meta("run_id") or run_dir.name
    summary = json.loads((run_dir / "run_summary.json").read_text()) if (run_dir / "run_summary.json").exists() else {}
    ingestion = json.loads((run_dir / "ingestion_report.json").read_text())
    ranking = json.loads((run_dir / "ranking.json").read_text())
    rec = json.loads((run_dir / "recommendations.json").read_text()) if (run_dir / "recommendations.json").exists() else {}
    check = json.loads((run_dir / "memo_check.json").read_text()) if (run_dir / "memo_check.json").exists() else {}
    issues = {i["issue_id"]: dict(i) for i in store.issues()}

    for t in ("runs", "metrics", "issues", "claims", "evidence", "trend", "recommendations"):
        db.execute(f"DELETE FROM {t} WHERE run_id = ?", (run_id,))
    db.execute("INSERT INTO runs VALUES (?,?,?,?,?,?)", (run_id, now_iso(), int(bool(store.get_meta("synthetic_input", False))),
                                                        json.dumps(store.get_meta("source")), json.dumps(summary), json.dumps(ingestion)))
    statuses = store.status_counts()
    nonempty = store.conn.execute("SELECT COUNT(*) FROM reviews WHERE is_empty = 0").fetchone()[0]
    cache_copies = store.conn.execute("SELECT COUNT(*) FROM records WHERE status='completed' AND cache_source_id IS NOT NULL").fetchone()[0]
    evals_dir = run_dir / "evals"
    golden = json.loads((evals_dir / "golden_results.json").read_text()) if (evals_dir / "golden_results.json").exists() else {}
    verifier = json.loads((evals_dir / "verifier_report.json").read_text()) if (evals_dir / "verifier_report.json").exists() else {}
    metrics = {
        "source_rows": store.review_count(), "nonempty_rows": nonempty, "completed": statuses["completed"],
        "quarantined": statuses["quarantined"], "pending": statuses["pending"],
        "classified_share_of_nonempty": round(statuses["completed"] / nonempty, 6) if nonempty else 0,
        "completed_via_exact_text_cache": cache_copies,
        "complaint_records": sum(a["complaint_count"] for a in ranking["ranking"]),
        "total_cost_usd": summary.get("total_cost_usd"), "golden_topic_agreement": golden.get("topic_agreement"),
        "golden_intent_agreement": golden.get("intent_agreement"), "golden_severity_exact_agreement": golden.get("severity_exact_agreement"),
        "verifier_sample": verifier.get("sample_size"), "verifier_disagreement_rate": verifier.get("disagreement_rate"),
        "label_config": (store.get_meta("controls") or {}).get("label_config"), "synthetic_input": int(bool(store.get_meta("synthetic_input", False))),
        "months_covered": ",".join(ranking.get("months", [])),
    }
    db.executemany("INSERT INTO metrics VALUES (?,?,?)", [(run_id, k, json.dumps(v)) for k, v in metrics.items()])
    db.executemany("INSERT INTO issues VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
        (run_id, a["issue_id"], a["rank"], a["name"], a["topic"], issues.get(a["issue_id"], {}).get("description"), a["complaint_count"],
         a["cancellation_count"], a["severity_sum"], a["mean_severity"], a["priority_score"], a["mean_sentiment"], a["needs_review_count"],
         a["share_of_complaint_records"]) for a in ranking["ranking"]])
    db.executemany("INSERT INTO claims VALUES (?,?,?,?,?,?)", [(run_id, c["claim_id"], c["issue_id"], c["metric"], str(c["value"]), c["computation"]) for c in ranking["claims"]])
    ev = []
    for iid in issues:
        rows = store.conn.execute(
            "SELECT c.review_id, c.severity, c.intent, c.evidence_quote, r.review_rating, r.review_timestamp FROM membership m "
            "JOIN records c ON c.review_id = m.review_id JOIN reviews r ON r.review_id = c.review_id WHERE m.issue_id = ? "
            "ORDER BY c.severity DESC, c.review_id ASC LIMIT ?", (iid, evidence_per_issue)).fetchall()
        ev += [(run_id, iid, r["review_id"], r["severity"], r["intent"], r["evidence_quote"], r["review_rating"], r["review_timestamp"]) for r in rows]
    db.executemany("INSERT INTO evidence VALUES (?,?,?,?,?,?,?,?)", ev)
    if (run_dir / "trend.csv").exists():
        db.executemany("INSERT INTO trend VALUES (?,?,?,?,?,?,?)", [
            (run_id, t["month"], t["issue_id"], int(t["complaints"]), int(t["all_completed_records_in_month"]), t["complaint_share"], int(t["partial_month"]))
            for t in csv.DictReader(open(run_dir / "trend.csv", newline=""))])
    if rec:
        db.execute("INSERT INTO recommendations VALUES (?,?,?,?,?,?,?,?,?)", (
            run_id, rec.get("model"), rec.get("priority_issue_id"), rec.get("recommendation"), json.dumps(rec.get("alternatives", [])),
            json.dumps(rec.get("cited_claims", [])), rec.get("memo_markdown"), json.dumps(check), rec.get("generated_at")))
    db.commit()
    db.close()
    store.close()
    return {"database_url": default_url(database_url).split("@")[-1], "run_id": run_id, "issues": len(ranking["ranking"]),
            "claims": len(ranking["claims"]), "evidence_rows": len(ev), "metrics": len(metrics)}
