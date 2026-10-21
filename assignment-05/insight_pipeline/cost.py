"""The 100-review cost and runtime calculator.

pilot:   runs the real pipeline on cost_100.csv with one worker and an empty cache (paid, explicit).
warm:    reruns on the same saved state and shows zero new enrichment calls.
replay:  the default, offline. Recomputes every cost from saved usage x editable rates and
         projects the full 660,622-row run under editable controls. Needs no API key.
"""
from __future__ import annotations

import csv
import json
import shutil
import time
from pathlib import Path

from .classify import Controls, run_classify
from .config import CORPUS
from .group import run_group
from .memo import run_memo
from .prepare import prepare
from .rank import run_rank
from .rates import UNITS, call_cost, load_rates, write_default_rates
from .export import contract_call, contract_record
from .store import Store, now_iso
from .verify import run_verify

DEFAULT_PROJECTION = {
    "_comment": "Editable. Volume fields project the full run; control fields cap it. Changing these never changes the measured pilot.",
    "rows": CORPUS["rows"], "nonempty": CORPUS["nonempty"], "empty": CORPUS["empty"],
    "distinct_nonempty_texts": CORPUS["distinct_nonempty_texts"],
    "exact_text_reuse": True,
    "verification_sample_rate": 0.002, "fallback_fraction": 0.02, "fallback_token_multiplier": 1.0,
    "fallback_price_multiplier": 20.0, "retry_rate": 0.02,
    "fixed_overhead_usd": 0.0, "fixed_overhead_seconds": 600,
    "memo_calls": 1, "grouping_calls": 8,
    "workers": 4, "spending_limit_usd": 100.0, "output_token_cap_per_request": 8000,
    "conservative_token_multiplier": 1.5, "conservative_retry_rate": 0.05,
    "local_compute_usd_per_hour": 0.0,
}


def _stage_dirs(cost_dir: Path, cold: bool) -> Path:
    return cost_dir / ("pilot-cold" if cold else "pilot-warm")


def run_pilot(input_csv: Path, cost_dir: Path, controls: Controls, warm: bool = False, synthetic: bool = False) -> dict:
    cost_dir = Path(cost_dir)
    cost_dir.mkdir(parents=True, exist_ok=True)
    rates_path = cost_dir / "rates.csv"
    if not rates_path.exists():
        write_default_rates(rates_path)
    controls = Controls(**{**controls.__dict__, "workers": 1, "rates_path": rates_path})
    run_dir = cost_dir / "pilot-run"
    if not warm:
        if run_dir.exists():
            shutil.rmtree(run_dir)
        run_dir.mkdir()
    stage_times = {}
    t_all = time.time()
    t = time.time(); prepare(input_csv, run_dir); stage_times["prepare"] = round(time.time() - t, 3)
    store = Store(run_dir)
    calls_before = store.conn.execute("SELECT COUNT(*) FROM calls WHERE stage='classify'").fetchone()[0]
    last_call_id = store.conn.execute("SELECT COALESCE(MAX(call_id), 0) FROM calls").fetchone()[0]
    store.close()
    t = time.time(); c = run_classify(run_dir, controls, synthetic=synthetic); stage_times["classify"] = round(time.time() - t, 3)
    t = time.time(); v = run_verify(run_dir, controls, sample_size=10, seed=100, plant=True); stage_times["verify"] = round(time.time() - t, 3)
    t = time.time(); run_group(run_dir, controls, name_with_model=True); stage_times["group"] = round(time.time() - t, 3)
    t = time.time(); run_rank(run_dir); stage_times["rank"] = round(time.time() - t, 3)
    t = time.time(); run_memo(run_dir, controls); stage_times["memo"] = round(time.time() - t, 3)
    wall = round(time.time() - t_all, 3)
    store = Store(run_dir)
    calls_after = store.conn.execute("SELECT COUNT(*) FROM calls WHERE stage='classify'").fetchone()[0]
    label = "warm" if warm else "cold"
    run_id = f"pilot-{label}-{cost_dir.name}"
    # pilot_records: the contract's row hash and common labels per pilot id (COST_CALCULATOR.md section 5).
    with open(cost_dir / f"pilot_records_{label}.jsonl", "w") as fh:
        for r in store.iter_records():
            fh.write(json.dumps({"pilot_run": label, **contract_record(r)}, ensure_ascii=False) + "\n")
    # pilot_calls: only the attempts this run made (the warm run shares the cold run's state file).
    with open(cost_dir / f"pilot_calls_{label}.jsonl", "w") as fh:
        for row in store.iter_calls():
            if row["call_id"] > last_call_id:
                fh.write(json.dumps({"pilot_run": label, "run_id": run_id, **contract_call(row, run_id)}) + "\n")
    usage = _usage_rows(store)
    with open(cost_dir / f"usage_{label}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(usage[0].keys()) if usage else ["stage"])
        w.writeheader(); w.writerows(usage)
    if not warm:
        shutil.copy(cost_dir / "pilot_records_cold.jsonl", cost_dir / "pilot_records.jsonl")
        shutil.copy(cost_dir / "usage_cold.csv", cost_dir / "usage.csv")
    # pilot_calls.jsonl holds every attempt of both runs, each line tagged with its pilot_run.
    with open(cost_dir / "pilot_calls.jsonl", "w") as fh:
        for name in ("pilot_calls_cold.jsonl", "pilot_calls_warm.jsonl"):
            if (cost_dir / name).exists():
                fh.write((cost_dir / name).read_text())
    measured = {
        "label": label, "measured_at": now_iso(), "input": str(input_csv), "synthetic_input": synthetic,
        "rows": store.review_count(), "statuses": store.status_counts(), "stage_seconds": stage_times, "wall_clock_seconds": wall,
        "new_enrichment_calls_this_run": calls_after - calls_before, "classify_stop_reason": c["stop_reason"],
        "verifier": {k: v[k] for k in ("sample_size", "agreement", "disagreement_rate", "planted_error_caught")},
        "controls": {"workers": 1, "batch_size": controls.batch_size, "effort": controls.effort, "model": controls.resolved_model(),
                     "backend": controls.backend, "max_output_tokens": controls.max_output_tokens},
    }
    store.close()
    (cost_dir / f"measured_{label}.json").write_text(json.dumps(measured, indent=2))
    if not (cost_dir / "projection.json").exists():
        (cost_dir / "projection.json").write_text(json.dumps(DEFAULT_PROJECTION, indent=2))
    replay(cost_dir)
    return measured


def _usage_rows(store: Store) -> list[dict]:
    rows = {}
    for c in store.iter_calls():
        key = (c["stage"], c["provider"], c["model"], c["effort"] or "", c["label_config"] or "")
        r = rows.setdefault(key, {"stage": key[0], "provider": key[1], "model": key[2], "effort": key[3], "label_config": key[4],
                                  "requests": 0, "succeeded": 0, "failed": 0, "records_requested": 0, "usage_unknown": 0,
                                  "input_tokens": 0, "cached_input_tokens": 0, "cache_write_tokens": 0, "output_tokens": 0, "duration_ms_sum": 0})
        r["requests"] += 1
        r["succeeded" if c["status"] == "ok" else "failed"] += 1
        r["records_requested"] += len(json.loads(c["request_ids"]) if c["request_ids"] else [])
        r["usage_unknown"] += int(not c["usage_known"])
        for u in UNITS:
            r[f"{u}_tokens"] += int(c[f"{u}_tokens"] or 0)
        r["duration_ms_sum"] += int(c["duration_ms"] or 0)
    return list(rows.values())


def replay(cost_dir: Path, rates_override: Path | None = None, projection_override: Path | None = None,
           price_as: str | None = None) -> dict:
    """Offline. Reads usage_*.csv, rates.csv, measured_*.json, projection.json and writes report.md + replay.json.

    price_as="anthropic:claude-haiku-5-5" reprices every measured call at that model's rates, which is how a
    zero-cost (fake or local) pilot still yields a dollar projection. The report says when this was done.
    """
    cost_dir = Path(cost_dir)
    rates = load_rates(rates_override or cost_dir / "rates.csv")
    if price_as:
        prov, mod = price_as.split(":", 1)
        for (p_, m_, u_), price in list(rates.items()):
            if (p_, m_) == (prov, mod):
                for key in [k for k in rates if k[2] == u_]:
                    rates[key] = price
    projection = json.loads((projection_override or cost_dir / "projection.json").read_text()) if (projection_override or cost_dir / "projection.json").exists() else dict(DEFAULT_PROJECTION)
    out = {"replayed_at": now_iso(), "rates_file": str(rates_override or cost_dir / "rates.csv"), "api_calls_made": 0,
           "priced_as": price_as, "runs": {}}
    for label in ("cold", "warm"):
        usage_path = cost_dir / f"usage_{label}.csv"
        measured_path = cost_dir / f"measured_{label}.json"
        if not usage_path.exists():
            continue
        measured = json.loads(measured_path.read_text()) if measured_path.exists() else {}
        rows = list(csv.DictReader(open(usage_path, newline="")))
        stages = []
        unknown_cost = False
        for r in rows:
            usage = {f"{u}_tokens": int(r[f"{u}_tokens"]) for u in UNITS}
            cost, priced = call_cost(rates, r["provider"], r["model"], usage)
            unknown_cost |= (not priced) or int(r["usage_unknown"]) > 0
            stages.append({**r, **{k: int(v) for k, v in usage.items()}, "api_cost_usd": round(cost, 6), "priced": priced,
                           "billing_items": [{"unit": u, "tokens": usage[f"{u}_tokens"], "usd_per_million": rates.get((r["provider"], r["model"], u)),
                                              "usd": round(usage[f"{u}_tokens"] * (rates.get((r["provider"], r["model"], u)) or 0) / 1e6, 6)} for u in UNITS]})
        api_total = round(sum(s["api_cost_usd"] for s in stages), 6)
        enrich = [s for s in stages if s["stage"] == "classify"]
        enrich_cost = round(sum(s["api_cost_usd"] for s in enrich), 6)
        completed = (measured.get("statuses") or {}).get("completed", 0)
        n_rows = measured.get("rows", 0)
        wall = measured.get("wall_clock_seconds")
        local_hours = (wall or 0) / 3600
        out["runs"][label] = {
            "measured": measured, "stages": stages, "api_cost_usd": api_total, "enrichment_api_cost_usd": enrich_cost,
            "cost_per_1000_inputs_usd": round(enrich_cost / n_rows * 1000, 6) if n_rows else None,
            "cost_per_completed_record_usd": round(api_total / completed, 8) if completed else None,
            "throughput_records_per_minute": round(completed / (wall / 60), 2) if wall else None,
            "wall_clock_seconds": wall, "summed_call_duration_seconds": round(sum(int(s["duration_ms_sum"]) for s in stages) / 1000, 3),
            "local_compute_estimate_usd": round(local_hours * projection.get("local_compute_usd_per_hour", 0.0), 6),
            "unknown_costs": unknown_cost,
            "note": "API spend = billed tokens x rates.csv. Summed call durations are not wall-clock when calls overlap.",
        }
    cold = out["runs"].get("cold")
    if cold and cold["measured"].get("rows"):
        out["projection"] = _project(cold, projection, rates)
    suffix = f"_priced_as_{price_as.replace(':', '_')}" if price_as else ""
    (cost_dir / f"replay{suffix}.json").write_text(json.dumps(out, indent=2))
    (cost_dir / f"report{suffix}.md").write_text(_report_md(out, projection))
    return out


def _project(cold: dict, p: dict, rates) -> dict:
    """Scale the measured per-record enrichment usage to the full corpus, with and without exact-text reuse."""
    n = cold["measured"]["rows"]
    completed = cold["measured"]["statuses"]["completed"] or 1
    enrich = [s for s in cold["stages"] if s["stage"] == "classify"]
    if not enrich:
        return {"error": "no classify usage in the cold pilot"}
    main = max(enrich, key=lambda s: s["requests"])
    per_rec = {u: main[f"{u}_tokens"] / completed for u in UNITS}
    price = {u: rates.get((main["provider"], main["model"], u)) or 0.0 for u in UNITS}
    per_rec_cost = sum(per_rec[u] * price[u] / 1e6 for u in UNITS)
    seconds_per_rec = (cold["measured"]["stage_seconds"].get("classify") or 0) / completed

    def scenario(name, token_mult, retry_rate, reuse):
        first_pass = p["distinct_nonempty_texts"] if reuse else p["nonempty"]
        enrichment = first_pass * per_rec_cost * token_mult * (1 + retry_rate)
        verification = p["nonempty"] * p["verification_sample_rate"] * per_rec_cost * token_mult
        fallback = first_pass * p["fallback_fraction"] * per_rec_cost * token_mult * p["fallback_token_multiplier"] * p["fallback_price_multiplier"]
        grouping_memo = (p["grouping_calls"] + p["memo_calls"]) * per_rec_cost * 50  # bounded calls, each about one 50-review request
        api = enrichment + verification + fallback + grouping_memo + p["fixed_overhead_usd"]
        hours_one_worker = (first_pass * (1 + retry_rate) * seconds_per_rec * token_mult + p["fixed_overhead_seconds"]) / 3600
        hours = hours_one_worker / max(p["workers"], 1)
        return {"scenario": name, "exact_text_reuse": reuse, "first_pass_records": first_pass, "token_multiplier": token_mult, "retry_rate": retry_rate,
                "enrichment_usd": round(enrichment, 2), "verification_usd": round(verification, 2), "fallback_usd": round(fallback, 2),
                "grouping_and_memo_usd": round(grouping_memo, 4), "fixed_overhead_usd": p["fixed_overhead_usd"], "api_total_usd": round(api, 2),
                "exceeds_spending_limit": api > p["spending_limit_usd"],
                "hours_one_worker": round(hours_one_worker, 2), "hours_with_workers": round(hours, 2), "workers": p["workers"],
                "local_compute_usd": round(hours * p.get("local_compute_usd_per_hour", 0.0), 2),
                "note": "worker speedup is modeled, not measured; rate limits can make more workers slower"}
    return {
        "basis": {"pilot_rows": n, "pilot_completed": completed, "model": f"{main['provider']}:{main['model']}", "effort": main["effort"],
                  "per_record_tokens": {u: round(per_rec[u], 2) for u in UNITS}, "per_record_api_usd": round(per_rec_cost, 8),
                  "seconds_per_record_one_worker": round(seconds_per_rec, 4), "prices_usd_per_million": price},
        "volume": {k: p[k] for k in ("rows", "nonempty", "empty", "distinct_nonempty_texts")},
        "controls": {k: p[k] for k in ("spending_limit_usd", "output_token_cap_per_request", "workers", "fallback_fraction")},
        "scenarios": [
            scenario("base_with_reuse", 1.0, p["retry_rate"], True),
            scenario("base_no_reuse", 1.0, p["retry_rate"], False),
            scenario("conservative_with_reuse", p["conservative_token_multiplier"], p["conservative_retry_rate"], True),
            scenario("conservative_no_reuse", p["conservative_token_multiplier"], p["conservative_retry_rate"], False),
        ],
        "memo_note": "One memo and eight grouping calls are counted once; the memo cost is never multiplied by the review count.",
    }


def _report_md(out: dict, p: dict) -> str:
    lines = [f"# 100-review cost and runtime report", "", f"Replayed offline at {out['replayed_at']} from saved usage and `{Path(out['rates_file']).name}`. API calls made by this replay: {out['api_calls_made']}.", ""]
    if out.get("priced_as"):
        lines += [f"**Every call below is repriced at the rates of `{out['priced_as']}`.** The usage is the pilot's measured usage; the provider in the stage table is the one that actually ran.", ""]
    for label, run in out["runs"].items():
        m = run["measured"]
        lines += [f"## {label} run", "",
                  f"Input `{Path(m.get('input', '?')).name}`, {m.get('rows')} rows, statuses {m.get('statuses')}, measured at {m.get('measured_at')}.{' SYNTHETIC INPUT.' if m.get('synthetic_input') else ''}", "",
                  f"Wall clock {run['wall_clock_seconds']} s (summed call durations {run['summed_call_duration_seconds']} s). New enrichment calls in this run: {m.get('new_enrichment_calls_this_run')}.", "",
                  f"API spend ${run['api_cost_usd']} (enrichment ${run['enrichment_api_cost_usd']}); cost per 1,000 inputs ${run['cost_per_1000_inputs_usd']}; cost per completed record ${run['cost_per_completed_record_usd']}; throughput {run['throughput_records_per_minute']} records/min; local compute estimate ${run['local_compute_estimate_usd']}; unknown costs: {run['unknown_costs']}.", "",
                  "| stage | provider | model | effort | requests | ok | failed | records | input | cached | cache write | output | USD |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for s in run["stages"]:
            lines.append(f"| {s['stage']} | {s['provider']} | {s['model']} | {s['effort']} | {s['requests']} | {s['succeeded']} | {s['failed']} | {s['records_requested']} | {s['input_tokens']} | {s['cached_input_tokens']} | {s['cache_write_tokens']} | {s['output_tokens']} | {s['api_cost_usd']} |")
        lines.append("")
    proj = out.get("projection")
    if proj and "scenarios" in proj:
        b = proj["basis"]
        lines += ["## Full-run projection", "",
                  f"Basis: {b['model']} at effort {b['effort']}, {b['per_record_tokens']} tokens per record, ${b['per_record_api_usd']} per record, {b['seconds_per_record_one_worker']} s per record on one worker. Volume {proj['volume']}. Controls {proj['controls']}.", "",
                  "| scenario | reuse | first-pass records | enrichment | verification | fallback | total API USD | over limit | hours (1 worker) | hours (workers) |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for s in proj["scenarios"]:
            lines.append(f"| {s['scenario']} | {s['exact_text_reuse']} | {s['first_pass_records']:,} | {s['enrichment_usd']} | {s['verification_usd']} | {s['fallback_usd']} | {s['api_total_usd']} | {s['exceeds_spending_limit']} | {s['hours_one_worker']} | {s['hours_with_workers']} |")
        lines += ["", proj["memo_note"], "", "Worker speedup is modeled, not measured. Refresh this projection after the 500 and 10,000 checkpoints."]
    return "\n".join(lines) + "\n"


def checkpoint_refresh(cost_dir: Path, run_dir: Path, label: str) -> dict:
    """Offline. Record a finished checkpoint run's measured enrichment cost and throughput next to the pilot and
    extrapolate the full run from it. Appends to cost/checkpoints.json; never touches the pilot files."""
    cost_dir, run_dir = Path(cost_dir), Path(run_dir)
    summary = json.loads((run_dir / "run_summary.json").read_text())
    projection = json.loads((cost_dir / "projection.json").read_text()) if (cost_dir / "projection.json").exists() else dict(DEFAULT_PROJECTION)
    store = Store(run_dir)
    rows = store.review_count()
    direct = store.conn.execute("SELECT COUNT(*) FROM records WHERE status='completed' AND cache_source_id IS NULL").fetchone()[0]
    cached = store.conn.execute("SELECT COUNT(*) FROM records WHERE status='completed' AND cache_source_id IS NOT NULL").fetchone()[0]
    store.close()
    classify = summary["stages"].get("classify", {})
    phases = summary.get("phases", [])
    wall = sum(p.get("wall_clock_s", 0) for p in phases)
    workers = (summary.get("controls") or {}).get("workers")
    per_direct_usd = classify.get("cost_usd", 0) / direct if direct else None
    per_direct_s = wall / direct if direct else None
    first_pass = projection["distinct_nonempty_texts"] if projection.get("exact_text_reuse", True) else projection["nonempty"]
    entry = {
        "label": label, "run_dir": str(run_dir), "recorded_at": now_iso(), "rows": rows, "statuses": summary["statuses"],
        "directly_classified": direct, "cache_copies": cached, "workers": workers,
        "classify_calls": classify.get("calls"), "classify_failed_calls": classify.get("failed"),
        "classify_cost_usd": round(classify.get("cost_usd", 0), 6), "total_cost_usd": summary.get("total_cost_usd"),
        "classify_wall_clock_s": round(wall, 3), "phases": [{k: p.get(k) for k in ("phase", "stop_reason", "batches", "wall_clock_s")} for p in phases],
        "usd_per_directly_classified_record": round(per_direct_usd, 8) if per_direct_usd else None,
        "seconds_per_directly_classified_record_at_this_concurrency": round(per_direct_s, 4) if per_direct_s else None,
        "full_run_extrapolation": {
            "first_pass_records": first_pass,
            "enrichment_usd": round(first_pass * per_direct_usd, 2) if per_direct_usd else None,
            "hours_at_this_concurrency": round(first_pass * per_direct_s / 3600, 2) if per_direct_s else None,
            "note": "measured at the checkpoint's own worker count; the pilot projection models workers, this does not",
        },
    }
    path = cost_dir / "checkpoints.json"
    entries = json.loads(path.read_text()) if path.exists() else []
    entries = [e for e in entries if e["label"] != label] + [entry]
    path.write_text(json.dumps(entries, indent=2))
    return entry
