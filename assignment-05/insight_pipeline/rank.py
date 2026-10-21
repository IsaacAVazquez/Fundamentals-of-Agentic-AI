"""Stage 5, code only: priority_score(issue) = complaint_count x mean_severity = severity_sum.

Reads saved records and membership, writes aggregates.csv, ranking.csv, claims.csv and
trend.csv. No model is involved, so anyone can re-run this and compare the output.

Two entry points share the same arithmetic. run_rank reads a run's state.sqlite. rank_from_export
reads a grading/ folder (records.jsonl.gz and membership.csv), which is what a grader has from the
release, and writes the same ranking.csv, aggregates.csv and claims.csv; the export carries no review
timestamps, so it cannot rebuild trend.csv."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from .runlog import log_event
from .store import Store, now_iso

FORMULA = "priority_score = complaint_count x mean_severity = severity_sum; sort priority_score desc, issue_id asc"


def mean6(total: int, count: int) -> str:
    if count == 0:
        return "0.000000"
    return str((Decimal(total) / Decimal(count)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


def _aggregate(issues: dict, members: dict, records: dict) -> list[dict]:
    """issues: issue_id -> {name, topic}; members: issue_id -> set of review ids; records: review_id -> labels."""
    agg = {}
    for iid, issue in issues.items():
        sev_sum = 0
        intents = Counter()
        sent_sum = 0.0
        needs_review = 0
        for rid in members[iid]:
            r = records[rid]
            sev_sum += int(r["severity"])
            intents[r["intent"]] += 1
            sent_sum += float(r["sentiment"] or 0.0)
            needs_review += int(r["needs_review"] or 0)
        n = len(members[iid])
        agg[iid] = {
            "issue_id": iid, "name": issue["name"], "topic": issue["topic"],
            "complaint_count": n, "cancellation_count": intents["cancellation"], "severity_sum": sev_sum,
            "mean_severity": mean6(sev_sum, n), "priority_score": sev_sum,
            "mean_sentiment": mean6(int(round(sent_sum * 1_000_000)), n * 1_000_000) if n else "0.000000",
            "needs_review_count": needs_review,
            "share_of_complaint_records": mean6(n * 1_000_000, max(sum(len(v) for v in members.values()), 1) * 1_000_000),
        }
    ranked = sorted(agg.values(), key=lambda a: (-a["priority_score"], a["issue_id"]))
    for i, a in enumerate(ranked, 1):
        a["rank"] = i
    return ranked


def _claims(ranked: list[dict], members: dict, statuses: dict, total_rows: int) -> list[dict]:
    claims = []
    def claim(issue_id, metric, value, computation):
        claims.append({"claim_id": f"C{len(claims) + 1}", "issue_id": issue_id, "metric": metric, "value": value, "computation": computation})
    claim("", "source_rows", total_rows, "count of rows ingested")
    claim("", "completed_records", statuses["completed"], "records with status completed")
    claim("", "quarantined_records", statuses["quarantined"], "records with status quarantined (incl. empty texts)")
    claim("", "pending_records", statuses["pending"], "records not yet classified")
    claim("", "complaint_records", sum(len(v) for v in members.values()), "completed records with intent complaint or cancellation")
    for a in ranked:
        claim(a["issue_id"], "rank", a["rank"], "position after sorting by score desc, issue_id asc")
        claim(a["issue_id"], "complaint_count", a["complaint_count"], "members of the issue")
        claim(a["issue_id"], "cancellation_count", a["cancellation_count"], "members with intent cancellation")
        claim(a["issue_id"], "severity_sum", a["severity_sum"], "sum of member severities")
        claim(a["issue_id"], "mean_severity", a["mean_severity"], "severity_sum / complaint_count, 6 decimals half-up")
        claim(a["issue_id"], "priority_score", a["priority_score"], "complaint_count x mean_severity = severity_sum")
    return claims


def _write_tables(out_dir: Path, ranked: list[dict], claims: list[dict]) -> None:
    with open(out_dir / "aggregates.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ranked[0].keys()) if ranked else ["issue_id"])
        w.writeheader()
        w.writerows(ranked)
    with open(out_dir / "ranking.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "issue_id", "complaint_count", "severity_sum", "mean_severity", "priority_score"])  # GRADING_CONTRACT.md columns
        for a in ranked:
            w.writerow([a["rank"], a["issue_id"], a["complaint_count"], a["severity_sum"], a["mean_severity"], a["priority_score"]])
    with open(out_dir / "claims.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["claim_id", "issue_id", "metric", "value", "computation"])
        w.writeheader()
        w.writerows(claims)


def run_rank(run_dir: Path) -> dict:
    run_dir = Path(run_dir)
    store = Store(run_dir, create=False)
    members = defaultdict(set)
    for iid, rid in store.membership():
        members[iid].add(rid)
    # An issue with no complaint or cancellation member has no baseline row (GRADING_CONTRACT.md ranks members only).
    issues = {i["issue_id"]: dict(i) for i in store.issues() if members[i["issue_id"]]}
    records = {r["review_id"]: r for r in store.iter_records("completed")}
    statuses = store.status_counts()
    total_rows = store.review_count()

    ranked = _aggregate(issues, members, records)
    claims = _claims(ranked, members, statuses, total_rows)
    _write_tables(run_dir, ranked, claims)

    monthly = defaultdict(Counter)   # issue -> month -> complaint count
    month_totals = Counter()         # month -> all completed records (denominator)
    for r in records.values():
        month_totals[(r["review_timestamp"] or "")[:7]] += 1
    for iid in issues:
        for rid in members[iid]:
            monthly[iid][(records[rid]["review_timestamp"] or "")[:7]] += 1
    months = sorted(m for m in month_totals if m)
    with open(run_dir / "trend.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["month", "issue_id", "complaints", "all_completed_records_in_month", "complaint_share", "partial_month"])
        for m in months:
            for iid in sorted(issues):
                n = monthly[iid][m]
                w.writerow([m, iid, n, month_totals[m], mean6(n * 1_000_000, month_totals[m] * 1_000_000),
                            int(m in (months[0], months[-1]))])

    result = {"generated_at": now_iso(), "ranking": ranked, "claims": claims, "statuses": statuses, "formula": FORMULA,
              "months": months, "partial_months": [months[0], months[-1]] if months else []}
    (run_dir / "ranking.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    log_event(run_dir, "rank_done", top=[a["issue_id"] for a in ranked[:3]], claims=len(claims))
    store.close()
    return result


def rank_from_export(export_dir: Path, out_dir: Path | None = None, issues_path: Path | None = None) -> dict:
    """Rerank from a grading/ folder with no state.sqlite and no model call. issues_path is a run's issues.json,
    which supplies the issue names for aggregates.csv; without it the name column repeats the issue id."""
    export_dir = Path(export_dir)
    out_dir = Path(out_dir) if out_dir else export_dir / "rerank"
    out_dir.mkdir(parents=True, exist_ok=True)
    rec_path = next((p for p in (export_dir / "records.jsonl.gz", export_dir / "records.jsonl") if p.exists()), None)
    if rec_path is None or not (export_dir / "membership.csv").exists():
        raise SystemExit(f"{export_dir} needs records.jsonl.gz (or records.jsonl) and membership.csv from `pipeline export`")
    members = defaultdict(set)
    with open(export_dir / "membership.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            members[row["issue_id"]].add(row["review_id"])
    wanted = set().union(*members.values()) if members else set()
    records, statuses, total_rows = {}, {"pending": 0, "completed": 0, "quarantined": 0}, 0
    with (gzip.open if rec_path.suffix == ".gz" else open)(rec_path, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            total_rows += 1
            statuses[r["status"]] = statuses.get(r["status"], 0) + 1
            if r["status"] == "completed" and r["review_id"] in wanted:
                records[r["review_id"]] = r
    missing = wanted - records.keys()
    if missing:
        raise SystemExit(f"{len(missing)} membership ids have no completed record in {rec_path.name}, e.g. {sorted(missing)[0]}")
    names = {}
    if issues_path:
        saved = json.loads(Path(issues_path).read_text())
        names = {i["issue_id"]: i for i in (saved["issues"] if isinstance(saved, dict) else saved)}
    issues = {iid: {"name": names.get(iid, {}).get("name") or iid, "topic": names.get(iid, {}).get("topic") or iid.removeprefix("ISS-")}
              for iid in sorted(members) if members[iid]}

    ranked = _aggregate(issues, members, records)
    claims = _claims(ranked, members, statuses, total_rows)
    _write_tables(out_dir, ranked, claims)
    result = {
        "generated_at": now_iso(), "source": str(export_dir), "records_file": rec_path.name, "issues_file": str(issues_path) if issues_path else None,
        "model_calls_made": 0, "formula": FORMULA, "statuses": statuses, "source_rows": total_rows,
        "sha256": {name: hashlib.sha256((out_dir / name).read_bytes()).hexdigest() for name in ("ranking.csv", "aggregates.csv", "claims.csv")},
        "not_rebuilt": "trend.csv, because records.jsonl carries no review timestamps",
        "ranking": [{k: a[k] for k in ("rank", "issue_id", "complaint_count", "severity_sum", "mean_severity", "priority_score")} for a in ranked],
    }
    (out_dir / "rerank.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result
