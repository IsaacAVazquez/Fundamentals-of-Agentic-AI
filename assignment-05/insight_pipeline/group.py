"""Stage 4: group complaint and cancellation records into issues.

Membership is decided by code from the fixed topic label, so it is stable and reproducible:
one issue per topic, each review in at most one issue. A model may name the issue from a
bounded set of examples; the name is cosmetic and the membership never depends on it.
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

from .backends import TransientError, get_backend
from .classify import Controls
from .config import TOPICS, label_config
from .prompts import GROUPER_SYSTEM
from .rates import call_cost, load_rates
from .runlog import log_event, write_summary
from .store import Store, now_iso

GROUPING_RULE = "issue_id = 'ISS-' + topic for every completed record whose intent is complaint or cancellation; one issue per review"
NAME_SCHEMA = {"type": "object", "properties": {"name": {"type": "string"}, "description": {"type": "string"}},
               "required": ["name", "description"], "additionalProperties": False}


def run_group(run_dir: Path, controls: Controls | None = None, name_with_model: bool = False, examples_per_issue: int = 8) -> dict:
    run_dir = Path(run_dir)
    store = Store(run_dir)
    issues = [{"issue_id": f"ISS-{t}", "topic": t, "name": f"{t} problems", "description": TOPICS[t], "named_by": "code"} for t in TOPICS]
    membership = []
    examples: dict[str, list] = {i["issue_id"]: [] for i in issues}
    for r in store.iter_records("completed"):
        if r["intent"] in ("complaint", "cancellation"):
            iid = f"ISS-{r['topic']}"
            membership.append((iid, r["review_id"]))
            ex = examples[iid]
            if len(ex) < 200:
                ex.append((-(r["severity"] or 0), r["review_id"], r["evidence_quote"]))
    store.replace_membership(issues, membership)

    if name_with_model and controls is not None:
        backend = get_backend(controls.backend)
        model = controls.resolved_model()
        rates = load_rates(controls.rates_path or (run_dir / "cost" / "rates.csv"))
        lc = label_config(backend.provider, model, controls.effort)
        for issue in issues:
            ex = sorted(examples[issue["issue_id"]])[:examples_per_issue]
            if not ex:
                continue
            user = json.dumps({"topic": issue["topic"], "examples": [{"id": rid, "quote": q} for _, rid, q in ex]}, ensure_ascii=False)
            started, t0 = now_iso(), time.time()
            try:
                res = backend.complete(system=GROUPER_SYSTEM, user=user, schema=NAME_SCHEMA, model=model,
                                       effort=controls.effort, max_output_tokens=300)
            except TransientError as exc:
                store.log_call({"stage": "group", "phase": "initial", "role": "grouper", "provider": backend.provider, "model": model,
                                "effort": controls.effort, "label_config": lc, "attempt": 1, "request_ids": [rid for _, rid, _ in ex],
                                "started_at": started, "duration_ms": int((time.time() - t0) * 1000), "status": "transient_error",
                                "error": str(exc)[:300], "usage_known": 0, "cost_usd": 0.0, "worker": 0})
                continue
            cost, _ = call_cost(rates, backend.provider, model, res.usage())
            store.log_call({"stage": "group", "phase": "initial", "role": "grouper", "provider": backend.provider, "model": model,
                            "effort": controls.effort, "label_config": lc, "attempt": 1, "request_ids": [rid for _, rid, _ in ex],
                            "started_at": started, "duration_ms": int((time.time() - t0) * 1000), "status": "ok", "error": None,
                            **res.usage(), "usage_known": int(res.usage_known), "cost_usd": cost, "worker": 0})
            try:
                data = json.loads(res.text)
                name, desc = str(data["name"])[:80], str(data["description"])[:300]
            except (ValueError, KeyError, TypeError):
                continue
            issue["name"], issue["description"], issue["named_by"] = name, desc, f"{backend.provider}:{model}"
            store.name_issue(issue["issue_id"], name, desc, issue["named_by"])

    with open(run_dir / "issues.json", "w") as fh:
        json.dump({"grouping_rule": GROUPING_RULE, "issues": issues}, fh, indent=2, ensure_ascii=False)
    with open(run_dir / "membership.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["issue_id", "review_id"])
        w.writerows(sorted(membership))
    counts = {i["issue_id"]: 0 for i in issues}
    for iid, _ in membership:
        counts[iid] += 1
    log_event(run_dir, "group_done", members=len(membership), issues=len(issues), named_by_model=name_with_model)
    write_summary(run_dir, store)
    store.close()
    return {"issues": issues, "member_count": len(membership), "counts": counts}
