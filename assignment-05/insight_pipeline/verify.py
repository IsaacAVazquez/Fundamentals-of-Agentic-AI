"""Stage 3: an independent verifier re-labels a declared random sample without seeing the first
label. Code compares the two and writes the disagreement report. A planted wrong label in a
separate test copy checks that disagreement is actually detected."""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

from .backends import TransientError, get_backend
from .classify import Controls
from .config import BATCH_SCHEMA, MAX_REVIEWS_PER_REQUEST, TOPICS, label_config
from .prompts import VERIFIER_SYSTEM, enricher_user
from .rates import call_cost, load_rates
from .runlog import log_event, write_summary
from .store import Store, now_iso
from .validate import ValidationError, parse_batch_output, validate_record


def _label_batch(store, backend, controls, model, rows, rates, stage, role, system):
    lc = label_config(backend.provider, model, controls.effort)
    user = enricher_user([{"id": r["review_id"], "text": r["review_text"]} for r in rows])
    started, t0 = now_iso(), time.time()
    try:
        res = backend.complete(system=system, user=user, schema=BATCH_SCHEMA, model=model,
                               effort=controls.effort, max_output_tokens=controls.max_output_tokens)
    except TransientError as exc:
        store.log_call({"stage": stage, "phase": "initial", "role": role, "provider": backend.provider, "model": model,
                        "effort": controls.effort, "label_config": lc, "attempt": 1, "request_ids": [r["review_id"] for r in rows],
                        "started_at": started, "duration_ms": int((time.time() - t0) * 1000), "status": "transient_error",
                        "error": str(exc)[:300], "usage_known": 0, "cost_usd": 0.0, "worker": 0})
        return {}
    cost, _ = call_cost(rates, backend.provider, model, res.usage())
    store.log_call({"stage": stage, "phase": "initial", "role": role, "provider": backend.provider, "model": model,
                    "effort": controls.effort, "label_config": lc, "attempt": 1, "request_ids": [r["review_id"] for r in rows],
                    "started_at": started, "duration_ms": int((time.time() - t0) * 1000), "status": "ok", "error": None,
                    **res.usage(), "usage_known": int(res.usage_known), "cost_usd": cost, "worker": 0,
                    "provider_request_id": res.extra.get("request_id")})
    out = {}
    try:
        items = parse_batch_output(res.text)
    except ValidationError as exc:
        return {r["review_id"]: {"error": str(exc)} for r in rows}
    by_id = {r["review_id"]: r for r in rows}
    for item in items:
        rid = str(item.get("id")) if isinstance(item, dict) else None
        if rid in by_id and rid not in out:
            try:
                out[rid] = validate_record(item, rid, by_id[rid]["review_text"])
            except ValidationError as exc:
                out[rid] = {"error": str(exc)}
    for rid in by_id:
        out.setdefault(rid, {"error": "missing_from_output"})
    return out


def run_verify(run_dir: Path, controls: Controls, sample_size: int = 200, seed: int = 20261020, plant: bool = True) -> dict:
    run_dir = Path(run_dir)
    store = Store(run_dir)
    backend = get_backend(controls.backend)
    model = controls.resolved_model()
    rates = load_rates(controls.rates_path or (run_dir / "cost" / "rates.csv"))
    evals_dir = run_dir / "evals"
    evals_dir.mkdir(exist_ok=True)

    # Declared sample: seeded choice over the sorted ids of directly classified records (not cache copies).
    ids = [r["review_id"] for r in store.conn.execute(
        "SELECT review_id FROM records WHERE status='completed' AND cache_source_id IS NULL ORDER BY review_id")]
    rng = random.Random(seed)
    sample_ids = sorted(rng.sample(ids, min(sample_size, len(ids)))) if ids else []
    rows = [store.record(rid) for rid in sample_ids]
    log_event(run_dir, "verify_start", sample=len(rows), seed=seed, model=model)

    predictions: dict[str, dict] = {}
    size = min(controls.batch_size, MAX_REVIEWS_PER_REQUEST)
    for i in range(0, len(rows), size):
        predictions.update(_label_batch(store, backend, controls, model, rows[i:i + size], rates, "verify", "verify", VERIFIER_SYSTEM))

    agree = {"topic": 0, "intent": 0, "severity_exact": 0}
    sev_abs = 0.0
    sent_abs = 0.0
    compared = 0
    disagreements = []
    with open(evals_dir / "verifier_predictions.jsonl", "w") as fh:
        for r in rows:
            p = predictions.get(r["review_id"], {"error": "no_prediction"})
            first = {"topic": r["topic"], "intent": r["intent"], "severity": r["severity"], "sentiment": r["sentiment"]}
            line = {"review_id": r["review_id"], "first": first, "verifier": p}
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")
            if "error" in p:
                disagreements.append({"review_id": r["review_id"], "kind": "verifier_failed", "detail": p["error"]})
                continue
            compared += 1
            agree["topic"] += int(p["topic"] == first["topic"])
            agree["intent"] += int(p["intent"] == first["intent"])
            agree["severity_exact"] += int(p["severity"] == first["severity"])
            sev_abs += abs(p["severity"] - first["severity"])
            sent_abs += abs(p["sentiment"] - (first["sentiment"] or 0.0))
            if p["topic"] != first["topic"] or p["intent"] != first["intent"] or abs(p["severity"] - first["severity"]) >= 2:
                disagreements.append({"review_id": r["review_id"], "kind": "label_disagreement", "first": first,
                                      "verifier": {k: p[k] for k in ("topic", "intent", "severity", "sentiment")},
                                      "text": r["review_text"][:300]})

    planted = None
    if plant and rows:
        # A separate test copy: one sampled record with a deliberately wrong topic and severity.
        victim = rows[0]
        wrong_topic = next(t for t in TOPICS if t != victim["topic"])
        wrong_sev = 1 if (victim["severity"] or 1) >= 3 else 5
        p = predictions.get(victim["review_id"], {})
        caught = ("error" not in p) and (p["topic"] != wrong_topic or p["severity"] != wrong_sev)
        planted = {"synthetic_test": True, "excluded_from_aggregates": True, "review_id": victim["review_id"],
                   "original": {"topic": victim["topic"], "severity": victim["severity"]},
                   "planted_wrong": {"topic": wrong_topic, "severity": wrong_sev},
                   "verifier": {k: p.get(k) for k in ("topic", "intent", "severity")} if "error" not in p else p,
                   "caught": bool(caught)}
        (evals_dir / "planted_error.json").write_text(json.dumps(planted, indent=2))

    report = {
        "generated_at": now_iso(), "seed": seed, "sample_requested": sample_size, "sample_size": len(rows),
        "compared": compared, "verifier_failures": len(rows) - compared,
        "model": f"{backend.provider}:{model}", "effort": controls.effort,
        "agreement": {k: round(v / compared, 4) if compared else None for k, v in agree.items()},
        "severity_mae": round(sev_abs / compared, 4) if compared else None,
        "sentiment_mae": round(sent_abs / compared, 4) if compared else None,
        "disagreement_count": sum(1 for d in disagreements if d["kind"] == "label_disagreement"),
        "disagreement_rate": round(sum(1 for d in disagreements if d["kind"] == "label_disagreement") / compared, 4) if compared else None,
        "planted_error_caught": planted["caught"] if planted else None,
        "cost_usd": round(store.spend("verify"), 6),
    }
    (evals_dir / "verifier_report.json").write_text(json.dumps(report, indent=2))
    (evals_dir / "disagreements.json").write_text(json.dumps(disagreements, indent=2, ensure_ascii=False))
    log_event(run_dir, "verify_done", **{k: v for k, v in report.items() if k != "generated_at"})
    write_summary(run_dir, store)
    store.close()
    return report
