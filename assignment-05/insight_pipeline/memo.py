"""Stage 6: the memo role receives only the saved aggregates, claim ids, and a bounded evidence
pack. Code then checks every cited claim, issue, review id, and number against the saved
calculations before the memo is accepted."""
from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path

from .backends import TransientError, get_backend
from .classify import Controls
from .config import label_config
from .prompts import MEMO_SYSTEM
from .rates import call_cost, load_rates
from .runlog import log_event, write_summary
from .store import Store, now_iso

MEMO_SCHEMA = {
    "type": "object",
    "properties": {
        "memo_markdown": {"type": "string"}, "priority_issue_id": {"type": "string"}, "recommendation": {"type": "string"},
        "alternatives": {"type": "array", "items": {"type": "string"}}, "cited_claims": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["memo_markdown", "priority_issue_id", "recommendation", "alternatives", "cited_claims"],
    "additionalProperties": False,
}


def build_evidence_pack(store: Store, ranking: list[dict], per_issue: int = 5, top_issues: int = 4) -> dict:
    pack = {}
    for a in ranking[:top_issues]:
        rows = store.conn.execute(
            "SELECT c.review_id, c.severity, c.intent, c.evidence_quote FROM membership m JOIN records c ON c.review_id = m.review_id "
            "WHERE m.issue_id = ? ORDER BY c.severity DESC, c.review_id ASC LIMIT ?", (a["issue_id"], per_issue)).fetchall()
        pack[a["issue_id"]] = [{"review_id": r["review_id"], "severity": r["severity"], "intent": r["intent"], "quote": r["evidence_quote"]} for r in rows]
    return pack


def check_memo(memo: str, claims: list[dict], issue_ids: set[str], members: dict[str, set[str]], all_review_ids: set[str]) -> dict:
    by_id = {c["claim_id"]: c for c in claims}
    cited = re.findall(r"\[(C\d+)\]", memo)
    unknown_claims = sorted({c for c in cited if c not in by_id})
    cited_issues = re.findall(r"\[(ISS-[a-z]+)\]", memo)
    unknown_issues = sorted({i for i in cited_issues if i not in issue_ids})
    # Every number of three or more digits must match a claim value exactly (commas allowed).
    # Review ids, claim ids, and calendar months (2023-11) are removed first so their digits are not read as numbers.
    scrubbed = re.sub(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b|\b[A-Za-z]+-\d+\b|\[C\d+\]|\b\d{4}-\d{2}(?:-\d{2})?\b", " ", memo)
    numbers = re.findall(r"(?<![\w.])\d{1,3}(?:,\d{3})+(?![\w.])|(?<![\w.,])\d{3,}(?![\w.,])", scrubbed)
    claim_values = {str(c["value"]).replace(",", "") for c in claims}
    claim_values |= {f"{int(v):,}" for v in claim_values if v.isdigit()}
    unmatched_numbers = sorted({n for n in numbers if n.replace(",", "") not in claim_values})
    # Numbers directly before a claim id must equal that claim's value.
    mismatched = []
    for num, cid in re.findall(r"(\d[\d,]*(?:\.\d+)?)\s*(?:[a-zA-Z -]{0,40})?\[(C\d+)\]", memo):
        if cid in by_id and num.replace(",", "") != str(by_id[cid]["value"]).replace(",", ""):
            mismatched.append({"number": num, "claim_id": cid, "claim_value": by_id[cid]["value"]})
    review_ids = set(re.findall(r"\b(syn-\d{7}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", memo))
    unknown_reviews = sorted(r for r in review_ids if r not in all_review_ids)
    forbidden = [w for w in ("revenue at risk", "churn rate", "retention improvement", "causal") if w in memo.lower()]
    return {
        "cited_claims": sorted(set(cited)), "unknown_claims": unknown_claims, "unknown_issues": unknown_issues,
        "unmatched_numbers": unmatched_numbers, "number_claim_mismatches": mismatched,
        "cited_review_ids": sorted(review_ids), "unknown_review_ids": unknown_reviews, "forbidden_phrases": forbidden,
        "passed": not (unknown_claims or unknown_issues or unmatched_numbers or mismatched or unknown_reviews or forbidden),
    }


def recheck_memo(run_dir: Path) -> dict:
    """Re-run the code checks on the saved memo.md with no model call; rewrites memo_check.json and the flag in recommendations.json."""
    run_dir = Path(run_dir)
    store = Store(run_dir)
    ranking = json.loads((run_dir / "ranking.json").read_text())
    claims = list(csv.DictReader(open(run_dir / "claims.csv", newline="")))
    members: dict[str, set[str]] = {}
    for iid, rid in store.membership():
        members.setdefault(iid, set()).add(rid)
    all_ids = {r["review_id"] for r in store.conn.execute("SELECT review_id FROM reviews")}
    store.close()
    memo_md = (run_dir / "memo.md").read_text()
    check = check_memo(memo_md, claims, {a["issue_id"] for a in ranking["ranking"]}, members, all_ids)
    (run_dir / "memo_check.json").write_text(json.dumps(check, indent=2))
    rec_path = run_dir / "recommendations.json"
    if rec_path.exists():
        rec = json.loads(rec_path.read_text())
        rec.update({"memo_check_passed": check["passed"], "cited_claims": check["cited_claims"], "memo_rechecked_at": now_iso()})
        rec_path.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    return check


def run_memo(run_dir: Path, controls: Controls) -> dict:
    run_dir = Path(run_dir)
    store = Store(run_dir)
    ranking = json.loads((run_dir / "ranking.json").read_text())
    claims = list(csv.DictReader(open(run_dir / "claims.csv", newline="")))
    issue_ids = {a["issue_id"] for a in ranking["ranking"]}
    members: dict[str, set[str]] = {}
    for iid, rid in store.membership():
        members.setdefault(iid, set()).add(rid)
    all_ids = {r["review_id"] for r in store.conn.execute("SELECT review_id FROM reviews")}
    pack = build_evidence_pack(store, ranking["ranking"])
    statuses = ranking["statuses"]
    synthetic = bool(store.get_meta("synthetic_input", False))
    scope = {
        "completed_records": statuses["completed"], "quarantined_records": statuses["quarantined"], "pending_records": statuses["pending"],
        "partial_months": ranking["partial_months"], "synthetic_input": synthetic,
        "limitations": [
            "Reviews are self-selected public app store posts, not a customer population.",
            "No account, plan, revenue, or cancellation data exists; cancellation intent is expressed, not observed.",
            "Labels come from a model checked against a 50-review golden set and a verifier sample; see evals/.",
            "Quarantined and pending records are not classified and are excluded from every count.",
        ] + (["THE INPUT WAS SYNTHETIC TEST DATA; nothing here describes Spotify."] if synthetic else []),
    }
    table = [{"claim_id": c["claim_id"], "issue_id": c["issue_id"], "metric": c["metric"], "value": c["value"]} for c in claims]
    user = ("AGGREGATE TABLE (every number you may use, with its claim id):\n" + json.dumps(table, ensure_ascii=False) +
            "\n\nRANKED ISSUES:\n" + json.dumps([{k: a[k] for k in ("rank", "issue_id", "name", "complaint_count", "mean_severity", "priority_score")} for a in ranking["ranking"]], ensure_ascii=False) +
            "\n\nEVIDENCE PACK:\n" + json.dumps(pack, ensure_ascii=False) + "\n\nSCOPE AND LIMITATIONS:\n" + json.dumps(scope, ensure_ascii=False))
    backend = get_backend(controls.backend)
    model = controls.resolved_model()
    rates = load_rates(controls.rates_path or (run_dir / "cost" / "rates.csv"))
    lc = label_config(backend.provider, model, controls.effort)
    started, t0 = now_iso(), time.time()
    try:
        res = backend.complete(system=MEMO_SYSTEM, user=user, schema=MEMO_SCHEMA, model=model, effort=controls.effort, max_output_tokens=8000)
    except TransientError as exc:
        store.log_call({"stage": "memo", "phase": "initial", "role": "memo", "provider": backend.provider, "model": model, "effort": controls.effort,
                        "label_config": lc, "attempt": 1, "request_ids": [], "started_at": started, "duration_ms": int((time.time() - t0) * 1000),
                        "status": "transient_error", "error": str(exc)[:300], "usage_known": 0, "cost_usd": 0.0, "worker": 0})
        store.close()
        raise SystemExit(f"memo call failed: {exc}")
    cost, _ = call_cost(rates, backend.provider, model, res.usage())
    store.log_call({"stage": "memo", "phase": "initial", "role": "memo", "provider": backend.provider, "model": model, "effort": controls.effort,
                    "label_config": lc, "attempt": 1, "request_ids": [], "started_at": started, "duration_ms": int((time.time() - t0) * 1000),
                    "status": "ok", "error": None, **res.usage(), "usage_known": int(res.usage_known), "cost_usd": cost, "worker": 0,
                    "provider_request_id": res.extra.get("request_id")})
    try:
        data = json.loads(res.text)
        memo_md = str(data["memo_markdown"])
    except (ValueError, KeyError, TypeError) as exc:
        store.close()
        raise SystemExit(f"memo output was not the expected JSON: {exc}")
    check = check_memo(memo_md, claims, issue_ids, members, all_ids)
    header = ("> SYNTHETIC INPUT: this memo was generated from templated test reviews, not the Spotify dataset.\n\n" if synthetic else "")
    (run_dir / "memo.md").write_text(header + memo_md + "\n")
    (run_dir / "memo_check.json").write_text(json.dumps(check, indent=2))
    rec = {
        "generated_at": now_iso(), "model": f"{backend.provider}:{model}", "effort": controls.effort,
        "priority_issue_id": data.get("priority_issue_id"), "recommendation": data.get("recommendation"),
        "alternatives": data.get("alternatives", []), "cited_claims": check["cited_claims"], "memo_check_passed": check["passed"],
        "evidence_pack": pack, "scope": scope, "memo_markdown": memo_md,
    }
    (run_dir / "recommendations.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    log_event(run_dir, "memo_done", passed=check["passed"], priority=rec["priority_issue_id"], cost_usd=cost)
    write_summary(run_dir, store)
    store.close()
    return rec
