"""SQLite state store for one run. Every stage reads and writes through here.

One file, runs/<run_id>/state.sqlite, holds the source rows, the record statuses, every
model call, the issue membership, and checkpoints. Writes happen in short transactions so a
killed process leaves a consistent file that the next start can resume from.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    row_index INTEGER NOT NULL,
    review_text TEXT NOT NULL,
    review_rating TEXT,
    review_likes TEXT,
    app_version TEXT,
    review_timestamp TEXT,
    source_sha256 TEXT NOT NULL,
    text_sha256 TEXT NOT NULL,
    is_empty INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS reviews_text_hash ON reviews(text_sha256);
CREATE TABLE IF NOT EXISTS records (
    review_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,              -- pending | completed | quarantined
    topic TEXT, intent TEXT, sentiment REAL, severity INTEGER,
    entities TEXT, evidence_quote TEXT, needs_review INTEGER,
    label_config TEXT, cache_source_id TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    reason TEXT,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS records_status ON records(status);
CREATE TABLE IF NOT EXISTS calls (
    call_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage TEXT NOT NULL, phase TEXT NOT NULL, role TEXT NOT NULL,
    provider TEXT, model TEXT, effort TEXT, label_config TEXT,
    attempt INTEGER, request_ids TEXT, started_at TEXT, duration_ms INTEGER,
    status TEXT, error TEXT,
    input_tokens INTEGER, cached_input_tokens INTEGER, cache_write_tokens INTEGER, output_tokens INTEGER,
    usage_known INTEGER, cost_usd REAL, worker INTEGER, provider_request_id TEXT
);
CREATE TABLE IF NOT EXISTS membership (
    issue_id TEXT NOT NULL, review_id TEXT NOT NULL,
    PRIMARY KEY (issue_id, review_id)
);
CREATE TABLE IF NOT EXISTS issues (
    issue_id TEXT PRIMARY KEY, topic TEXT NOT NULL, name TEXT, description TEXT, named_by TEXT
);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Store:
    def __init__(self, run_dir: Path, create: bool = False):
        """Only prepare creates a run's database (create=True). Every other command opens a prepared run and stops when
        there is none, so pointed at a committed results/ copy or an unzipped grading export it cannot create an empty
        database, and an empty one left behind by an older version cannot unlock an overwrite of the saved outputs."""
        self.run_dir = Path(run_dir)
        self.path = self.run_dir / "state.sqlite"
        missing = (f"{self.path} has no prepared run. Run `pipeline prepare --input <csv> --run-dir {self.run_dir}` first. The full run's "
                   "state is not committed or released; to rerank from a grading export use: pipeline rank --from-export <grading dir> --issues <issues.json>")
        if not create and not self.path.exists():
            raise SystemExit(missing)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, timeout=60, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.executescript(SCHEMA)
        if not create and self.review_count() == 0:
            self.conn.close()
            raise SystemExit(missing)

    # ---- meta -------------------------------------------------------------
    def set_meta(self, key: str, value) -> None:
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, json.dumps(value)))

    def get_meta(self, key: str, default=None):
        row = self.conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    # ---- reviews ----------------------------------------------------------
    def insert_reviews(self, rows: list[tuple]) -> None:
        with self.conn:
            self.conn.executemany(
                "INSERT OR IGNORE INTO reviews VALUES (?,?,?,?,?,?,?,?,?,?)", rows
            )
            self.conn.executemany(
                "INSERT OR IGNORE INTO records(review_id, status, attempts) VALUES (?, 'pending', 0)",
                [(r[0],) for r in rows],
            )

    def review_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]

    def status_counts(self) -> dict[str, int]:
        rows = self.conn.execute("SELECT status, COUNT(*) AS n FROM records GROUP BY status").fetchall()
        counts = {"pending": 0, "completed": 0, "quarantined": 0}
        for r in rows:
            counts[r["status"]] = r["n"]
        return counts

    def pending_reviews(self, limit: int | None = None, nonempty_only: bool = True):
        sql = (
            "SELECT r.* FROM reviews r JOIN records c ON c.review_id = r.review_id "
            "WHERE c.status = 'pending'" + (" AND r.is_empty = 0" if nonempty_only else "") +
            " ORDER BY r.row_index"
        )
        if limit:
            sql += f" LIMIT {int(limit)}"
        return self.conn.execute(sql).fetchall()

    def empty_pending(self):
        return self.conn.execute(
            "SELECT r.review_id FROM reviews r JOIN records c ON c.review_id = r.review_id "
            "WHERE c.status = 'pending' AND r.is_empty = 1"
        ).fetchall()

    def completed_by_text_hash(self, text_hashes: list[str], label_config: str) -> dict[str, sqlite3.Row]:
        """Earliest completed record for each text hash under this exact label_config."""
        out: dict[str, sqlite3.Row] = {}
        for i in range(0, len(text_hashes), 500):
            chunk = text_hashes[i:i + 500]
            marks = ",".join("?" * len(chunk))
            # Drive from the text-hash index: with hundreds of thousands of completed rows the planner otherwise
            # scanned records by status and this lookup took five seconds per loop on the full corpus.
            rows = self.conn.execute(
                "SELECT r.text_sha256 AS h, c.* FROM reviews r INDEXED BY reviews_text_hash "
                "JOIN records c ON c.review_id = r.review_id "
                f"WHERE r.text_sha256 IN ({marks}) AND c.status = 'completed' AND c.label_config = ? "
                "ORDER BY r.row_index",
                [*chunk, label_config],
            ).fetchall()
            for row in rows:
                out.setdefault(row["h"], row)
        return out

    # ---- records ----------------------------------------------------------
    def write_records(self, completed: list[dict], quarantined: list[dict], bumped: list[str]) -> None:
        """One transaction per batch: completed rows, quarantined rows, and attempt bumps for retries."""
        ts = now_iso()
        with self.conn:
            self.conn.executemany(
                "UPDATE records SET status='completed', topic=?, intent=?, sentiment=?, severity=?, entities=?, "
                "evidence_quote=?, needs_review=?, label_config=?, cache_source_id=?, attempts=?, reason=NULL, updated_at=? "
                "WHERE review_id=? AND status='pending'",
                [
                    (r["topic"], r["intent"], r["sentiment"], r["severity"], json.dumps(r["entities"]),
                     r["evidence_quote"], int(r["needs_review"]), r["label_config"], r.get("cache_source_id"),
                     r.get("attempts", 1), ts, r["review_id"])
                    for r in completed
                ],
            )
            self.conn.executemany(
                "UPDATE records SET status='quarantined', reason=?, attempts=?, label_config=?, updated_at=? "
                "WHERE review_id=? AND status='pending'",
                [(q["reason"], q.get("attempts", 1), q.get("label_config"), ts, q["review_id"]) for q in quarantined],
            )
            self.conn.executemany(
                "UPDATE records SET attempts = attempts + 1, updated_at=? WHERE review_id=? AND status='pending'",
                [(ts, rid) for rid in bumped],
            )

    def record(self, review_id: str):
        return self.conn.execute(
            "SELECT c.*, r.review_text, r.text_sha256, r.source_sha256, r.review_rating, r.review_timestamp "
            "FROM records c JOIN reviews r ON r.review_id = c.review_id WHERE c.review_id = ?", (review_id,)
        ).fetchone()

    def iter_records(self, status: str | None = None):
        sql = ("SELECT c.*, r.review_text, r.text_sha256, r.source_sha256, r.review_rating, r.review_likes, "
               "r.app_version, r.review_timestamp, r.row_index, r.is_empty FROM records c JOIN reviews r ON r.review_id = c.review_id")
        if status:
            sql += f" WHERE c.status = '{status}'"
        sql += " ORDER BY r.row_index"
        return self.conn.execute(sql)

    def reset_record(self, review_id: str) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE records SET status='pending', topic=NULL, intent=NULL, sentiment=NULL, severity=NULL, entities=NULL, "
                "evidence_quote=NULL, needs_review=NULL, label_config=NULL, cache_source_id=NULL, attempts=0, reason=NULL WHERE review_id=?",
                (review_id,),
            )

    # ---- calls ------------------------------------------------------------
    def log_call(self, call: dict) -> int:
        cols = ["stage", "phase", "role", "provider", "model", "effort", "label_config", "attempt", "request_ids",
                "started_at", "duration_ms", "status", "error", "input_tokens", "cached_input_tokens",
                "cache_write_tokens", "output_tokens", "usage_known", "cost_usd", "worker", "provider_request_id"]
        values = [call.get(c) for c in cols]
        if isinstance(values[8], list):
            values[8] = json.dumps(values[8])
        with self.conn:
            cur = self.conn.execute(
                f"INSERT INTO calls({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", values
            )
        return cur.lastrowid

    def iter_calls(self, stage: str | None = None):
        sql = "SELECT * FROM calls"
        if stage:
            sql += f" WHERE stage = '{stage}'"
        return self.conn.execute(sql + " ORDER BY call_id")

    def spend(self, stage: str | None = None) -> float:
        sql = "SELECT COALESCE(SUM(cost_usd), 0) FROM calls"
        if stage:
            sql += f" WHERE stage = '{stage}'"
        return float(self.conn.execute(sql).fetchone()[0])

    # ---- issues -----------------------------------------------------------
    def replace_membership(self, issues: list[dict], membership: list[tuple[str, str]]) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM membership")
            self.conn.execute("DELETE FROM issues")
            self.conn.executemany("INSERT INTO issues VALUES (?,?,?,?,?)",
                                  [(i["issue_id"], i["topic"], i.get("name"), i.get("description"), i.get("named_by")) for i in issues])
            self.conn.executemany("INSERT INTO membership VALUES (?,?)", membership)

    def name_issue(self, issue_id: str, name: str, description: str, named_by: str) -> None:
        with self.conn:
            self.conn.execute("UPDATE issues SET name=?, description=?, named_by=? WHERE issue_id=?",
                              (name, description, named_by, issue_id))

    def issues(self):
        return self.conn.execute("SELECT * FROM issues ORDER BY issue_id").fetchall()

    def membership(self):
        return self.conn.execute("SELECT issue_id, review_id FROM membership ORDER BY issue_id, review_id").fetchall()

    def close(self) -> None:
        self.conn.close()
