"""Standardized grading/ export: the files named in the brief, in one folder, from saved state.

GRADING_CONTRACT.md in the dataset ZIP is the required format. The field names here follow
the brief's text; the conformance pass against the contract is tracked in the README.
"""
from __future__ import annotations

import gzip
import json
import shutil
from pathlib import Path

from .store import Store, now_iso


def export_grading(run_dir: Path, out_dir: Path | None = None, compress: bool = True) -> dict:
    run_dir = Path(run_dir)
    out = Path(out_dir) if out_dir else run_dir / "grading"
    out.mkdir(parents=True, exist_ok=True)
    store = Store(run_dir)
    controls = store.get_meta("controls") or {}
    phases = store.get_meta("phases", [])
    counts = store.status_counts()
    nonempty = store.conn.execute("SELECT COUNT(*) FROM reviews WHERE is_empty = 0").fetchone()[0]
    classified = store.conn.execute(
        "SELECT COUNT(*) FROM records c JOIN reviews r ON r.review_id = c.review_id WHERE c.status='completed' AND r.is_empty=0").fetchone()[0]
    cache_copies = store.conn.execute("SELECT COUNT(*) FROM records WHERE status='completed' AND cache_source_id IS NOT NULL").fetchone()[0]
    models = {}
    for c in store.iter_calls():
        key = f"{c['provider']}:{c['model']}"
        models.setdefault(key, {"calls": 0, "stages": set()})
        models[key]["calls"] += 1
        models[key]["stages"].add(c["stage"])
    run = {
        "exported_at": now_iso(),
        "run_id": store.get_meta("run_id") or run_dir.name,
        "synthetic_input": bool(store.get_meta("synthetic_input", False)),
        "source": store.get_meta("source"),
        "row_hash_definition": "sha256(utf8(review_id + US + review_text + US + review_rating + US + review_likes + US + app_version + US + review_timestamp)), US = \\x1f",
        "label_config": controls.get("label_config"),
        "controls": controls,
        "models": {k: {"calls": v["calls"], "stages": sorted(v["stages"])} for k, v in models.items()},
        "phases": phases,
        "counts": {"source_rows": store.review_count(), "nonempty_rows": nonempty, **counts,
                   "classified_nonempty": classified, "completed_via_exact_text_cache": cache_copies},
        "enrichment_limit_per_request": 50,
        "files": ["run.json", "ingestion.json", "records.jsonl" + (".gz" if compress else ""), "membership.csv", "ranking.csv",
                  "claims.csv", "calls.jsonl", "checkpoint_before.json", "checkpoint_after.json"],
    }
    (out / "run.json").write_text(json.dumps(run, indent=2))
    shutil.copy(run_dir / "ingestion_report.json", out / "ingestion.json")

    rec_path = out / ("records.jsonl.gz" if compress else "records.jsonl")
    opener = gzip.open if compress else open
    with opener(rec_path, "wt", encoding="utf-8") as fh:
        for r in store.iter_records():
            fh.write(json.dumps({
                "review_id": r["review_id"], "source_sha256": r["source_sha256"], "text_sha256": r["text_sha256"],
                "status": r["status"], "topic": r["topic"], "intent": r["intent"], "sentiment": r["sentiment"],
                "severity": r["severity"], "entities": json.loads(r["entities"]) if r["entities"] else None,
                "evidence_quote": r["evidence_quote"], "needs_review": bool(r["needs_review"]) if r["needs_review"] is not None else None,
                "label_config": r["label_config"], "cache_source_id": r["cache_source_id"], "attempts": r["attempts"],
                "quarantine_reason": r["reason"],
            }, ensure_ascii=False) + "\n")
    for name in ("membership.csv", "ranking.csv", "claims.csv", "checkpoint_before.json", "checkpoint_after.json"):
        src = run_dir / name
        if src.exists():
            shutil.copy(src, out / name)
    with open(out / "calls.jsonl", "w") as fh:
        for c in store.iter_calls():
            d = dict(c)
            d["request_ids"] = json.loads(d["request_ids"]) if d["request_ids"] else []
            fh.write(json.dumps(d) + "\n")
    store.close()
    return {"out_dir": str(out), "counts": run["counts"]}
