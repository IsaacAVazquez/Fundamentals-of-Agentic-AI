"""Stage 2: the orchestrator around the enricher role.

The orchestrator is code. It batches, reserves budget, dispatches, validates, retries once,
quarantines, caches by exact text, checkpoints, and resumes. The model only ever sees a
bounded batch of review texts and returns labels. Nothing here decides what a review means.
"""
from __future__ import annotations

import hashlib
import json
import random
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from .backends import TransientError, get_backend
from .config import (BATCH_SCHEMA, DEFAULT_BATCH_SIZE, DEFAULT_EFFORT, DEFAULT_MODEL, MAX_REVIEWS_PER_REQUEST,
                     label_config)
from .prompts import ENRICHER_SYSTEM, enricher_user
from .rates import call_cost, load_rates
from .runlog import log_event, write_summary
from .store import Store, now_iso
from .validate import ValidationError, parse_batch_output, validate_record


class StopRun(Exception):
    pass


@dataclass
class Controls:
    backend: str = "fake"
    model: str | None = None
    effort: str = DEFAULT_EFFORT
    batch_size: int = DEFAULT_BATCH_SIZE
    workers: int = 1
    max_spend_usd: float = 5.0
    max_output_tokens: int = 4000
    max_batches: int | None = None
    max_reviews: int | None = None
    time_limit_s: float | None = None
    fallback_model: str | None = None
    fallback_fraction: float = 0.02
    rates_path: Path | None = None
    backoff_tries: int = 3

    def resolved_model(self) -> str:
        return self.model or DEFAULT_MODEL[self.backend]


@dataclass
class Ledger:
    cap: float
    spent: float = 0.0
    reserved: float = 0.0
    lock: threading.Lock = field(default_factory=threading.Lock)

    def reserve(self, amount: float) -> bool:
        with self.lock:
            if self.spent + self.reserved + amount > self.cap:
                return False
            self.reserved += amount
            return True

    def settle(self, reserved: float, actual: float) -> None:
        with self.lock:
            self.reserved -= reserved
            self.spent += actual


def _checkpoint(store: Store, run_dir: Path, phase: str, moment: str) -> dict:
    counts = store.status_counts()
    ids = [r["review_id"] for r in store.conn.execute("SELECT review_id FROM records WHERE status='completed' ORDER BY review_id")]
    snap = {
        "ts": now_iso(), "phase": phase, "moment": moment, "statuses": counts,
        "completed_count": len(ids),
        "completed_ids_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
        "classify_calls_so_far": store.conn.execute("SELECT COUNT(*) FROM calls WHERE stage='classify'").fetchone()[0],
        "classify_spend_so_far_usd": round(store.spend("classify"), 6),
    }
    ck = Path(run_dir) / "checkpoints"
    ck.mkdir(exist_ok=True)
    n = len(store.get_meta("phases", []))
    (ck / f"{n:02d}_{phase}_{moment}.json").write_text(json.dumps(snap, indent=2))
    (Path(run_dir) / f"checkpoint_{moment}.json").write_text(json.dumps(snap, indent=2))
    return snap


def _estimate_cost(rates, provider, model, system: str, user: str, max_out: int) -> float:
    est_in = (len(system) + len(user)) // 4 + 50
    cost, _ = call_cost(rates, provider, model, {"input_tokens": est_in, "output_tokens": max_out})
    return cost


def _call_with_backoff(backend, controls: Controls, model: str, system: str, user: str, worker: int,
                       phase: str, request_ids: list[str], attempt: int, rates, lc: str):
    """Returns (result_or_None, call_logs). Transient errors are retried with jitter and each try is logged."""
    logs = []
    last_err = None
    for tries in range(controls.backoff_tries):
        started = now_iso()
        t0 = time.time()
        try:
            res = backend.complete(system=system, user=user, schema=BATCH_SCHEMA, model=model,
                                   effort=controls.effort, max_output_tokens=controls.max_output_tokens)
        except TransientError as exc:
            last_err = exc
            logs.append({"stage": "classify", "phase": phase, "role": "enricher", "provider": backend.provider,
                         "model": model, "effort": controls.effort, "label_config": lc, "attempt": attempt,
                         "request_ids": request_ids, "started_at": started, "duration_ms": int((time.time() - t0) * 1000),
                         "status": "transient_error", "error": str(exc)[:500], "usage_known": 0, "cost_usd": 0.0, "worker": worker})
            time.sleep(min(30.0, (2 ** tries) + random.random()))
            continue
        except Exception as exc:  # non-retryable provider error
            logs.append({"stage": "classify", "phase": phase, "role": "enricher", "provider": backend.provider,
                         "model": model, "effort": controls.effort, "label_config": lc, "attempt": attempt,
                         "request_ids": request_ids, "started_at": started, "duration_ms": int((time.time() - t0) * 1000),
                         "status": "error", "error": f"{type(exc).__name__}: {str(exc)[:500]}", "usage_known": 0, "cost_usd": 0.0, "worker": worker})
            return None, logs
        cost, priced = call_cost(rates, backend.provider, model, res.usage())
        logs.append({"stage": "classify", "phase": phase, "role": "enricher", "provider": backend.provider,
                     "model": model, "effort": controls.effort, "label_config": lc, "attempt": attempt,
                     "request_ids": request_ids, "started_at": started, "duration_ms": int((time.time() - t0) * 1000),
                     "status": "ok", "error": None if priced else "unpriced_units", **res.usage(),
                     "usage_known": int(res.usage_known), "cost_usd": cost, "worker": worker})
        return res, logs
    logs[-1]["error"] = f"gave up after {controls.backoff_tries} transient errors: {last_err}"
    return None, logs


def run_classify(run_dir: Path, controls: Controls, synthetic: bool = False) -> dict:
    run_dir = Path(run_dir)
    store = Store(run_dir)
    if not store.get_meta("prepared"):
        raise SystemExit("run prepare first")
    backend = get_backend(controls.backend)
    model = controls.resolved_model()
    lc = label_config(backend.provider, model, controls.effort)
    rates = load_rates(controls.rates_path or (run_dir / "cost" / "rates.csv"))
    if synthetic:
        store.set_meta("synthetic_input", True)
    batch_size = min(controls.batch_size, MAX_REVIEWS_PER_REQUEST)

    # Empty texts never go to a model: quarantine them explicitly with the reason the brief names.
    empties = [r["review_id"] for r in store.empty_pending()]
    if empties:
        store.write_records([], [{"review_id": rid, "reason": "empty_review_text", "attempts": 0, "label_config": lc} for rid in empties], [])
        log_event(run_dir, "quarantined_empty", count=len(empties))

    phases = store.get_meta("phases", [])
    phase = "initial" if not phases else "resume"
    before = _checkpoint(store, run_dir, phase, "before")
    phases.append({"phase": phase, "started_at": now_iso(), "before": before})
    store.set_meta("phases", phases)
    store.set_meta("controls", {**controls.__dict__, "rates_path": str(controls.rates_path) if controls.rates_path else None,
                                "model": model, "label_config": lc})
    store.set_meta("run_id", store.get_meta("run_id") or run_dir.name)
    log_event(run_dir, "classify_start", phase=phase, model=model, label_config=lc, workers=controls.workers,
              batch_size=batch_size, max_spend_usd=controls.max_spend_usd, statuses=before["statuses"])

    ledger = Ledger(cap=controls.max_spend_usd, spent=store.spend("classify"))
    stop = {"flag": False, "reason": None}

    def on_sigint(signum, frame):
        stop["flag"], stop["reason"] = True, "interrupted"
        print("\ninterrupt received: finishing in-flight batches, then saving", flush=True)
    old_handler = signal.signal(signal.SIGINT, on_sigint)

    t_start = time.time()
    batches_done = 0
    completed_this_run = 0
    dispatched_reviews = 0
    fallback_reviews = 0
    cache_hits = 0
    try:
        with ThreadPoolExecutor(max_workers=controls.workers) as pool:
            while not stop["flag"]:
                if controls.max_batches is not None and batches_done >= controls.max_batches:
                    stop["reason"] = "max_batches"; break
                if controls.max_reviews is not None and completed_this_run >= controls.max_reviews:
                    stop["reason"] = "max_reviews"; break
                if controls.time_limit_s is not None and time.time() - t_start > controls.time_limit_s:
                    stop["reason"] = "time_limit"; break
                pending = store.pending_reviews(limit=batch_size * max(controls.workers, 1) * 8)
                if not pending:
                    stop["reason"] = "no_pending"; break

                # Exact-text cache: reuse a completed record for the same text under the same label_config.
                hashes = sorted({r["text_sha256"] for r in pending})
                hits = store.completed_by_text_hash(hashes, lc)
                reused = []
                for r in pending:
                    hit = hits.get(r["text_sha256"])
                    if hit is not None and hit["review_id"] != r["review_id"]:
                        reused.append({
                            "review_id": r["review_id"], "topic": hit["topic"], "intent": hit["intent"],
                            "sentiment": hit["sentiment"], "severity": hit["severity"], "entities": json.loads(hit["entities"] or "[]"),
                            "evidence_quote": hit["evidence_quote"], "needs_review": bool(hit["needs_review"]), "label_config": lc,
                            "cache_source_id": hit["cache_source_id"] or hit["review_id"], "attempts": 0,
                        })
                if reused:
                    store.write_records(reused, [], [])
                    cache_hits += len(reused)
                    completed_this_run += len(reused)
                    log_event(run_dir, "cache_reuse", count=len(reused))
                    continue

                # One representative per distinct text; duplicates wait and become cache hits next loop.
                reps: dict[str, object] = {}
                for r in pending:
                    reps.setdefault(r["text_sha256"], r)
                fresh = [r for r in reps.values()]
                first = [r for r in fresh if (store.record(r["review_id"])["attempts"] or 0) == 0]
                retry = [r for r in fresh if r not in first]
                batches = [first[i:i + batch_size] for i in range(0, len(first), batch_size)]
                batches += [retry[i:i + batch_size] for i in range(0, len(retry), batch_size)]
                if controls.max_batches is not None:
                    batches = batches[: max(0, controls.max_batches - batches_done)]
                batches = batches[: max(controls.workers, 1) * 2]
                if not batches:
                    stop["reason"] = "max_batches"; break

                futures = {}
                for worker_no, batch in enumerate(batches):
                    attempt = 2 if batch[0]["review_id"] in {r["review_id"] for r in retry} else 1
                    use_model = model
                    if attempt == 2 and controls.fallback_model and dispatched_reviews and \
                            (fallback_reviews + len(batch)) / max(dispatched_reviews, 1) <= controls.fallback_fraction:
                        use_model = controls.fallback_model
                        fallback_reviews += len(batch)
                    use_lc = label_config(backend.provider, use_model, controls.effort)
                    user = enricher_user([{"id": r["review_id"], "text": r["review_text"]} for r in batch])
                    est = _estimate_cost(rates, backend.provider, use_model, ENRICHER_SYSTEM, user, controls.max_output_tokens)
                    if not ledger.reserve(est):
                        stop["flag"], stop["reason"] = True, "spend_cap"
                        log_event(run_dir, "spend_cap_reached", spent=ledger.spent, reserved=ledger.reserved, next=est, cap=ledger.cap)
                        break
                    ids = [r["review_id"] for r in batch]
                    fut = pool.submit(_call_with_backoff, backend, controls, use_model, ENRICHER_SYSTEM, user, worker_no,
                                      phase, ids, attempt, rates, use_lc)
                    futures[fut] = (batch, est, attempt, use_lc, use_model)
                    dispatched_reviews += len(batch)

                for fut in as_completed(futures):
                    batch, est, attempt, use_lc, use_model = futures[fut]
                    res, logs = fut.result()
                    actual = 0.0
                    for entry in logs:
                        store.log_call(entry)
                        actual += float(entry.get("cost_usd") or 0.0)
                    ledger.settle(est, actual)
                    batches_done += 1
                    by_id = {r["review_id"]: r for r in batch}
                    completed, quarantined, bumped = [], [], []
                    if res is None:
                        if logs and logs[-1]["status"] == "transient_error":
                            stop["flag"], stop["reason"] = True, "provider_unavailable"
                            log_event(run_dir, "provider_unavailable", ids=list(by_id), error=logs[-1]["error"])
                            continue  # rows stay pending; the run stops and can resume later
                        for rid in by_id:
                            (bumped if attempt == 1 else quarantined).append(rid if attempt == 1 else {"review_id": rid, "reason": "provider_error:" + (logs[-1]["error"] or "")[:120], "attempts": attempt, "label_config": use_lc})
                    else:
                        try:
                            items = parse_batch_output(res.text)
                        except ValidationError as exc:
                            items, batch_error = [], str(exc)
                        else:
                            batch_error = None
                        seen: dict[str, dict] = {}
                        foreign = 0
                        for item in items:
                            rid = str(item.get("id")) if isinstance(item, dict) else None
                            if rid in by_id:
                                seen.setdefault(rid, item)
                            else:
                                foreign += 1
                        for rid, row in by_id.items():
                            if batch_error:
                                failure = batch_error
                            elif rid not in seen:
                                failure = "missing_from_output"
                            else:
                                try:
                                    rec = validate_record(seen[rid], rid, row["review_text"])
                                    rec.update({"label_config": use_lc, "attempts": attempt, "cache_source_id": None})
                                    completed.append(rec)
                                    continue
                                except ValidationError as exc:
                                    failure = str(exc)
                            if attempt == 1:
                                bumped.append(rid)
                            else:
                                quarantined.append({"review_id": rid, "reason": failure, "attempts": attempt, "label_config": use_lc})
                        if foreign:
                            log_event(run_dir, "foreign_ids_ignored", count=foreign)
                    store.write_records(completed, quarantined, bumped)
                    completed_this_run += len(completed)
                    log_event(run_dir, "batch", phase=phase, attempt=attempt, model=use_model, size=len(batch),
                              completed=len(completed), retry_queued=len(bumped), quarantined=len(quarantined),
                              cost_usd=round(actual, 6), spent_usd=round(ledger.spent, 6))
                    if stop["flag"] and stop["reason"] == "interrupted":
                        pass  # keep draining already-submitted futures; the while loop exits afterwards
    finally:
        signal.signal(signal.SIGINT, old_handler)
        after = _checkpoint(store, run_dir, phase, "after")
        phases = store.get_meta("phases", [])
        phases[-1].update({"finished_at": now_iso(), "stop_reason": stop["reason"], "after": after,
                           "batches": batches_done, "completed_this_run": completed_this_run, "cache_hits": cache_hits,
                           "wall_clock_s": round(time.time() - t_start, 3)})
        store.set_meta("phases", phases)
        log_event(run_dir, "classify_stop", phase=phase, reason=stop["reason"], batches=batches_done,
                  completed=completed_this_run, cache_hits=cache_hits, statuses=after["statuses"],
                  spent_usd=round(ledger.spent, 6), wall_clock_s=round(time.time() - t_start, 3))
        summary = write_summary(run_dir, store)
        store.close()
    return {"stop_reason": stop["reason"], "batches": batches_done, "completed": completed_this_run,
            "cache_hits": cache_hits, "statuses": after["statuses"], "spent_usd": round(ledger.spent, 6),
            "wall_clock_s": round(time.time() - t_start, 3), "summary": summary}
