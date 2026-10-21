"""Stage 5, code only: priority_score(issue) = complaint_count x mean_severity = severity_sum.

Reads saved records and membership, writes aggregates.csv, ranking.csv, claims.csv and
trend.csv. No model is involved, so anyone can re-run this and compare the output."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from .runlog import log_event
from .store import Store, now_iso


def mean6(total: int, count: int) -> str:
    if count == 0:
        return "0.000000"
    return str((Decimal(total) / Decimal(count)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


def run_rank(run_dir: Path) -> dict:
    run_dir = Path(run_dir)
    store = Store(run_dir)
    members = defaultdict(set)
    for iid, rid in store.membership():
        members[iid].add(rid)
    # An issue with no complaint or cancellation member has no baseline row (GRADING_CONTRACT.md ranks members only).
    issues = {i["issue_id"]: dict(i) for i in store.issues() if members[i["issue_id"]]}
    records = {r["review_id"]: r for r in store.iter_records("completed")}
    statuses = store.status_counts()
    total_rows = store.review_count()

    agg = {}
    monthly = defaultdict(Counter)   # issue -> month -> complaint count
    month_totals = Counter()         # month -> all completed records (denominator)
    for r in records.values():
        month_totals[(r["review_timestamp"] or "")[:7]] += 1
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
            monthly[iid][(r["review_timestamp"] or "")[:7]] += 1
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

    with open(run_dir / "aggregates.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ranked[0].keys()) if ranked else ["issue_id"])
        w.writeheader()
        w.writerows(ranked)
    with open(run_dir / "ranking.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "issue_id", "complaint_count", "severity_sum", "mean_severity", "priority_score"])  # GRADING_CONTRACT.md columns
        for a in ranked:
            w.writerow([a["rank"], a["issue_id"], a["complaint_count"], a["severity_sum"], a["mean_severity"], a["priority_score"]])

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
    with open(run_dir / "claims.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["claim_id", "issue_id", "metric", "value", "computation"])
        w.writeheader()
        w.writerows(claims)

    months = sorted(m for m in month_totals if m)
    with open(run_dir / "trend.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["month", "issue_id", "complaints", "all_completed_records_in_month", "complaint_share", "partial_month"])
        for m in months:
            for iid in sorted(issues):
                n = monthly[iid][m]
                w.writerow([m, iid, n, month_totals[m], mean6(n * 1_000_000, month_totals[m] * 1_000_000),
                            int(m in (months[0], months[-1]))])

    result = {"generated_at": now_iso(), "ranking": ranked, "claims": claims, "statuses": statuses,
              "formula": "priority_score = complaint_count x mean_severity = severity_sum; sort priority_score desc, issue_id asc",
              "months": months, "partial_months": [months[0], months[-1]] if months else []}
    (run_dir / "ranking.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    log_event(run_dir, "rank_done", top=[a["issue_id"] for a in ranked[:3]], claims=len(claims))
    store.close()
    return result
