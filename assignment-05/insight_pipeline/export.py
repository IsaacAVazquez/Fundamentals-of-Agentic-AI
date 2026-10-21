"""The grading/ folder, in the shape GRADING_CONTRACT.md (v1, a5-audit-v1) requires, from saved state.

Nothing here calls a model. The files are run.json, ingestion.json, records.jsonl.gz, membership.csv,
ranking.csv, claims.csv, calls.jsonl, checkpoint_before.json, checkpoint_after.json, plus
claims_context.csv for the memo's non-issue numbers, which the contract says to explain separately.
"""
from __future__ import annotations

import csv
import gzip
import json
import shutil
from pathlib import Path

from .store import Store, now_iso

CONTRACT_VERSION = "a5-audit-v1"
CONTRACT_METRICS = ("complaint_count", "severity_sum", "mean_severity", "priority_score")


def contract_call(c, run_id: str) -> dict:
    """One calls.jsonl line: the contract's fields first, then everything else the store logged."""
    d = dict(c)
    ids = json.loads(d.pop("request_ids") or "[]")
    return {
        "request_id": f"{run_id}:call-{d['call_id']}",
        "provider_request_id": d.get("provider_request_id"),
        "role": d["role"], "review_ids": ids, "model": d["model"], "phase": d["phase"],
        "outcome": "succeeded" if d["status"] == "ok" else "failed",
        "label_config": d["label_config"],
        "input_tokens": int(d["input_tokens"] or 0), "output_tokens": int(d["output_tokens"] or 0),
        "cached_input_tokens": int(d["cached_input_tokens"] or 0), "cache_write_tokens": int(d["cache_write_tokens"] or 0),
        **{k: d[k] for k in ("call_id", "stage", "provider", "effort", "attempt", "started_at", "duration_ms", "status", "error",
                             "usage_known", "cost_usd", "worker")},
    }


def contract_record(r) -> dict:
    """One records.jsonl line: completed records carry the labels, quarantined ones carry the reason."""
    base = {"review_id": r["review_id"], "source_sha256": r["source_sha256"], "status": r["status"]}
    if r["status"] == "completed":
        base.update({
            "topic": r["topic"], "intent": r["intent"], "sentiment": float(r["sentiment"]), "severity": int(r["severity"]),
            "entities": json.loads(r["entities"] or "[]"), "evidence_quote": r["evidence_quote"],
            "needs_review": bool(r["needs_review"]), "label_config": r["label_config"],
        })
        if r["cache_source_id"]:
            base["cache_source_id"] = r["cache_source_id"]
    else:
        base["reason"] = r["reason"] or "unknown"
        if r["label_config"]:
            base["label_config"] = r["label_config"]
    base.update({"text_sha256": r["text_sha256"], "attempts": r["attempts"]})
    return base


def _pick_checkpoints(run_dir: Path) -> tuple[Path | None, Path | None]:
    """before = the snapshot saved when the first resume started (what was complete at the interruption);
    after = the last snapshot of all. With a single uninterrupted phase there is no resume evidence."""
    ck = sorted((run_dir / "checkpoints").glob("*.json")) if (run_dir / "checkpoints").exists() else []
    resume_before = [p for p in ck if p.name.endswith("_resume_before.json")]
    afters = [p for p in ck if p.name.endswith("_after.json")]
    before = resume_before[0] if resume_before else (ck[0] if ck else None)
    return before, (afters[-1] if afters else None)


def export_grading(run_dir: Path, out_dir: Path | None = None, compress: bool = True, ingestion: Path | None = None) -> dict:
    """ingestion: a profile of the FULL corpus written by `check_submission.py profile`, for checkpoint runs whose
    input is a sample; the contract wants the full-file profile in every grading folder. Omit for the full run."""
    run_dir = Path(run_dir)
    out = Path(out_dir) if out_dir else run_dir / "grading"
    store = Store(run_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_id = store.get_meta("run_id") or run_dir.name
    controls = store.get_meta("controls") or {}
    source = store.get_meta("source") or {}
    counts = store.status_counts()
    nonempty = store.conn.execute("SELECT COUNT(*) FROM reviews WHERE is_empty = 0").fetchone()[0]
    classified = store.conn.execute(
        "SELECT COUNT(*) FROM records c JOIN reviews r ON r.review_id = c.review_id WHERE c.status='completed' AND r.is_empty=0").fetchone()[0]
    cache_copies = store.conn.execute("SELECT COUNT(*) FROM records WHERE status='completed' AND cache_source_id IS NOT NULL").fetchone()[0]
    models: dict[str, dict] = {}
    for c in store.iter_calls():
        m = models.setdefault(f"{c['provider']}:{c['model']}", {"calls": 0, "roles": set()})
        m["calls"] += 1
        m["roles"].add(c["role"])
    report = json.loads((run_dir / "ingestion_report.json").read_text())

    run = {
        # GRADING_CONTRACT.md run.json
        "version": CONTRACT_VERSION,
        "analysis_count": store.review_count(),
        "analysis_sha256": source.get("sha256"),
        "classification_input_fields": ["review_text"],
        "allow_multi_issue": False,
        # extras
        "exported_at": now_iso(), "run_id": run_id,
        "synthetic_input": bool(store.get_meta("synthetic_input", False)),
        "source": source,
        "row_hash_definition": report.get("row_hash_definition"),
        "label_config": controls.get("label_config"), "controls": controls,
        "models": {k: {"calls": v["calls"], "roles": sorted(v["roles"])} for k, v in models.items()},
        "phases": store.get_meta("phases", []),
        "counts": {"source_rows": store.review_count(), "nonempty_rows": nonempty, **counts,
                   "classified_nonempty": classified, "completed_via_exact_text_cache": cache_copies},
        "enrichment_limit_per_request": 50,
        "group_and_memo_inputs": "group calls carry the example review ids they were sent; the memo call consumes claims.csv, ranking.json, and the evidence pack in recommendations.json, so its review_ids is empty",
        "files": ["run.json", "ingestion.json", "records.jsonl" + (".gz" if compress else ""), "membership.csv", "ranking.csv",
                  "claims.csv", "claims_context.csv", "calls.jsonl", "checkpoint_before.json", "checkpoint_after.json"],
    }
    (out / "run.json").write_text(json.dumps(run, indent=2))
    if ingestion:
        shutil.copy(ingestion, out / "ingestion.json")
    else:
        (out / "ingestion.json").write_text(json.dumps(report["contract_profile"], ensure_ascii=False, sort_keys=True, indent=2) + "\n")

    rec_path = out / ("records.jsonl.gz" if compress else "records.jsonl")
    # Same records, split by status into the run folder: enriched.jsonl.gz (completed) and quarantine.jsonl (reason, attempts).
    with (gzip.open if compress else open)(rec_path, "wt", encoding="utf-8") as fh, \
            gzip.open(run_dir / "enriched.jsonl.gz", "wt", encoding="utf-8") as enr, \
            open(run_dir / "quarantine.jsonl", "w", encoding="utf-8") as qua:
        for r in store.iter_records():
            line = json.dumps(contract_record(r), ensure_ascii=False) + "\n"
            fh.write(line)
            if r["status"] in ("completed", "quarantined"):
                (enr if r["status"] == "completed" else qua).write(line)

    shutil.copy(run_dir / "membership.csv", out / "membership.csv")
    shutil.copy(run_dir / "ranking.csv", out / "ranking.csv")
    claims = list(csv.DictReader(open(run_dir / "claims.csv", newline="")))
    with open(out / "claims.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["claim_id", "issue_id", "metric", "value"], extrasaction="ignore")
        w.writeheader()
        w.writerows(c for c in claims if c["issue_id"] and c["metric"] in CONTRACT_METRICS)
    with open(out / "claims_context.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(claims[0].keys()) if claims else ["claim_id"])
        w.writeheader()
        w.writerows(c for c in claims if not (c["issue_id"] and c["metric"] in CONTRACT_METRICS))

    with open(out / "calls.jsonl", "w") as fh:
        for c in store.iter_calls():
            fh.write(json.dumps(contract_call(c, run_id)) + "\n")

    before, after = _pick_checkpoints(run_dir)
    for src, name in ((before, "checkpoint_before.json"), (after, "checkpoint_after.json")):
        if src is not None:
            shutil.copy(src, out / name)
    store.close()
    return {"out_dir": str(out), "counts": run["counts"], "checkpoint_before": before.name if before else None,
            "checkpoint_after": after.name if after else None}
