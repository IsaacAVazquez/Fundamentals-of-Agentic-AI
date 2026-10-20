"""Append-only run log (run_log.jsonl) plus the rolled-up run_summary.json."""
from __future__ import annotations

import json
from pathlib import Path

from .store import Store, now_iso


def log_event(run_dir: Path, event: str, **fields) -> None:
    line = {"ts": now_iso(), "event": event, **fields}
    with open(Path(run_dir) / "run_log.jsonl", "a") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")


def write_summary(run_dir: Path, store: Store, extra: dict | None = None) -> dict:
    by_stage: dict[str, dict] = {}
    for c in store.iter_calls():
        s = by_stage.setdefault(c["stage"], {"calls": 0, "succeeded": 0, "failed": 0, "input_tokens": 0,
                                              "cached_input_tokens": 0, "cache_write_tokens": 0, "output_tokens": 0,
                                              "cost_usd": 0.0, "usage_unknown_calls": 0, "duration_ms": 0,
                                              "models": {}})
        s["calls"] += 1
        s["succeeded" if c["status"] == "ok" else "failed"] += 1
        for k in ("input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens", "duration_ms"):
            s[k] += int(c[k] or 0)
        s["cost_usd"] = round(s["cost_usd"] + float(c["cost_usd"] or 0), 6)
        if not c["usage_known"]:
            s["usage_unknown_calls"] += 1
        key = f"{c['provider']}:{c['model']}"
        s["models"][key] = s["models"].get(key, 0) + 1
    summary = {
        "generated_at": now_iso(),
        "run_id": store.get_meta("run_id"),
        "source": store.get_meta("source"),
        "statuses": store.status_counts(),
        "stages": by_stage,
        "total_cost_usd": round(sum(s["cost_usd"] for s in by_stage.values()), 6),
        "controls": store.get_meta("controls"),
        "phases": store.get_meta("phases", []),
        "synthetic_input": store.get_meta("synthetic_input", False),
    }
    if extra:
        summary.update(extra)
    (Path(run_dir) / "run_summary.json").write_text(json.dumps(summary, indent=2))
    return summary
