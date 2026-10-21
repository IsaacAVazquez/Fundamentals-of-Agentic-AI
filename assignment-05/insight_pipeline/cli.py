"""The `pipeline` command. Every stage is a subcommand; `run` chains them.

Paid model execution only happens through classify, verify, group --name, memo, run, cost pilot,
and eval injection with a non-fake backend. Everything else is offline.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .classify import Controls, run_classify


def _load_dotenv() -> None:
    env = Path(".env")
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _controls(a) -> Controls:
    return Controls(backend=a.backend, model=a.model, effort=a.effort, batch_size=a.batch_size, workers=a.workers,
                    max_spend_usd=a.max_spend, max_output_tokens=a.max_output_tokens, max_batches=getattr(a, "max_batches", None),
                    max_reviews=getattr(a, "max_reviews", None), time_limit_s=getattr(a, "time_limit", None),
                    fallback_model=getattr(a, "fallback_model", None), fallback_fraction=getattr(a, "fallback_fraction", 0.02),
                    rates_path=Path(a.rates) if getattr(a, "rates", None) else None)


def _add_model_args(p, with_limits=True):
    p.add_argument("--backend", default="fake", choices=["fake", "anthropic", "openai"])
    p.add_argument("--model", default=None, help="provider model id; default per backend in config.py")
    p.add_argument("--effort", default="low")
    p.add_argument("--batch-size", type=int, default=25, help="reviews per request, at most 50")
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--max-spend", type=float, default=5.0, help="USD cap for the classify stage of this run")
    p.add_argument("--max-output-tokens", type=int, default=8000)
    p.add_argument("--rates", default=None, help="rates.csv to price calls (default cost/rates.csv in the run or built-in)")
    if with_limits:
        p.add_argument("--max-batches", type=int, default=None)
        p.add_argument("--max-reviews", type=int, default=None)
        p.add_argument("--time-limit", type=float, default=None, help="seconds")
        p.add_argument("--fallback-model", default=None)
        p.add_argument("--fallback-fraction", type=float, default=0.02)


def main(argv=None) -> None:
    _load_dotenv()
    ap = argparse.ArgumentParser(prog="pipeline", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare", help="stage 1: ingest, hash, profile, queue (no model)")
    p.add_argument("--input", required=True); p.add_argument("--run-dir", required=True); p.add_argument("--limit", type=int, default=None)

    p = sub.add_parser("classify", help="stage 2: enrich pending reviews (model calls)")
    p.add_argument("--run-dir", required=True); p.add_argument("--synthetic", action="store_true", help="mark the input as synthetic test data")
    _add_model_args(p)

    p = sub.add_parser("verify", help="stage 3: blind re-label of a random sample (model calls)")
    p.add_argument("--run-dir", required=True); p.add_argument("--sample", type=int, default=200); p.add_argument("--seed", type=int, default=20261020)
    p.add_argument("--no-plant", action="store_true"); _add_model_args(p, with_limits=False)

    p = sub.add_parser("group", help="stage 4: issue membership by code, names by model if --name")
    p.add_argument("--run-dir", required=True); p.add_argument("--name", action="store_true"); _add_model_args(p, with_limits=False)

    p = sub.add_parser("rank", help="stage 5: deterministic ranking from saved outputs (no model)")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--run-dir", help="a run folder with state.sqlite")
    src.add_argument("--from-export", help="a grading/ folder (records.jsonl.gz + membership.csv), e.g. unzipped from the release")
    p.add_argument("--issues", default=None, help="with --from-export: the run's issues.json, for the issue names in aggregates.csv")
    p.add_argument("--out", default=None, help="with --from-export: where to write; default <export>/rerank")

    p = sub.add_parser("memo", help="stage 6: decision memo from aggregates (model call), then code checks")
    p.add_argument("--run-dir", required=True); _add_model_args(p, with_limits=False)

    p = sub.add_parser("memo-check", help="re-run the code checks on a saved memo.md (no model)")
    p.add_argument("--run-dir", required=True)

    p = sub.add_parser("run", help="all six stages on an input CSV")
    p.add_argument("--input", required=True); p.add_argument("--run-dir", required=True); p.add_argument("--synthetic", action="store_true")
    p.add_argument("--verify-sample", type=int, default=200); p.add_argument("--limit", type=int, default=None); _add_model_args(p)

    p = sub.add_parser("export", help="write the grading/ folder from saved state (no model)")
    p.add_argument("--run-dir", required=True); p.add_argument("--out", default=None); p.add_argument("--no-gzip", action="store_true")
    p.add_argument("--ingestion", default=None, help="full-corpus profile from check_submission.py, for runs on a sample")

    p = sub.add_parser("status", help="counts, spend, and phases for a run")
    p.add_argument("--run-dir", required=True)

    p = sub.add_parser("eval", help="golden-template | golden | fields | injection | resume | reproducibility")
    es = p.add_subparsers(dest="which", required=True)
    e = es.add_parser("golden-template"); e.add_argument("--run-dir", required=True); e.add_argument("--out", required=True); e.add_argument("--n", type=int, default=50); e.add_argument("--seed", type=int, default=50)
    e = es.add_parser("golden"); e.add_argument("--run-dir", required=True); e.add_argument("--golden", required=True); e.add_argument("--out", default=None)
    e = es.add_parser("injection"); e.add_argument("--out", required=True); _add_model_args(e, with_limits=False)
    e = es.add_parser("resume"); e.add_argument("--input", required=True); e.add_argument("--out", required=True); e.add_argument("--first-batches", type=int, default=2); e.add_argument("--keep-run", default=None); _add_model_args(e)
    e = es.add_parser("reproducibility"); e.add_argument("--run-dir", required=True); e.add_argument("--out", default=None)
    e = es.add_parser("fields", help="offline: needs_review, entities, and a quote-support worksheet from saved records")
    e.add_argument("--golden", required=True); e.add_argument("--records", required=True, help="records.jsonl.gz or enriched.jsonl.gz from the export")
    e.add_argument("--verifier-dir", default=None, help="folder with verifier_predictions.jsonl and disagreements.json"); e.add_argument("--out", required=True)

    p = sub.add_parser("cost", help="pilot (paid, explicit) | replay (offline, default)")
    cs = p.add_subparsers(dest="which", required=True)
    c = cs.add_parser("pilot", help="run the real pipeline on cost_100.csv; one worker, empty cache"); c.add_argument("--input", required=True); c.add_argument("--cost-dir", required=True)
    c.add_argument("--warm", action="store_true", help="rerun on the saved state to show zero new enrichment calls"); c.add_argument("--synthetic", action="store_true"); c.add_argument("--i-understand-this-is-paid", action="store_true"); _add_model_args(c, with_limits=False)
    c = cs.add_parser("replay", help="recompute costs and projections from saved files; no API key"); c.add_argument("--cost-dir", required=True); c.add_argument("--rates", default=None); c.add_argument("--projection", default=None)
    c.add_argument("--price-as", default=None, help="reprice measured usage at another model, e.g. anthropic:claude-haiku-5-5")
    c = cs.add_parser("checkpoint", help="offline: record a finished checkpoint run's measured cost and throughput next to the pilot"); c.add_argument("--cost-dir", required=True); c.add_argument("--run-dir", required=True); c.add_argument("--label", required=True)
    c = cs.add_parser("rebuild-usage", help="offline: rewrite usage_*.csv from the saved pilot_calls_*.jsonl"); c.add_argument("--cost-dir", required=True)

    p = sub.add_parser("dashboard-load", help="load a run's saved outputs into the dashboard database")
    p.add_argument("--run-dir", required=True); p.add_argument("--database-url", default=None, help="postgres://... or sqlite:///path; default $DATABASE_URL or sqlite:///dashboard/dashboard.sqlite")

    a = ap.parse_args(argv)
    if a.cmd == "prepare":
        from .prepare import prepare
        print(json.dumps(prepare(Path(a.input), Path(a.run_dir), limit=a.limit), indent=2))
    elif a.cmd == "classify":
        r = run_classify(Path(a.run_dir), _controls(a), synthetic=a.synthetic)
        print(json.dumps({k: v for k, v in r.items() if k != "summary"}, indent=2))
    elif a.cmd == "verify":
        from .verify import run_verify
        print(json.dumps(run_verify(Path(a.run_dir), _controls(a), sample_size=a.sample, seed=a.seed, plant=not a.no_plant), indent=2))
    elif a.cmd == "group":
        from .group import run_group
        r = run_group(Path(a.run_dir), _controls(a), name_with_model=a.name)
        print(json.dumps({"member_count": r["member_count"], "counts": r["counts"]}, indent=2))
    elif a.cmd == "rank":
        from .rank import rank_from_export, run_rank
        if a.from_export:
            r = rank_from_export(Path(a.from_export), Path(a.out) if a.out else None, Path(a.issues) if a.issues else None)
            print(json.dumps({k: r[k] for k in ("ranking", "sha256", "statuses", "model_calls_made")}, indent=2))
            return
        r = run_rank(Path(a.run_dir))
        print(json.dumps([{k: x[k] for k in ("rank", "issue_id", "complaint_count", "mean_severity", "priority_score")} for x in r["ranking"]], indent=2))
    elif a.cmd == "memo":
        from .memo import run_memo
        r = run_memo(Path(a.run_dir), _controls(a))
        print(json.dumps({k: r[k] for k in ("priority_issue_id", "recommendation", "memo_check_passed")}, indent=2))
    elif a.cmd == "memo-check":
        from .memo import recheck_memo
        print(json.dumps(recheck_memo(Path(a.run_dir)), indent=2))
    elif a.cmd == "run":
        from .export import export_grading
        from .group import run_group
        from .memo import run_memo
        from .prepare import prepare
        from .rank import run_rank
        from .verify import run_verify
        ctl = _controls(a)
        rd = Path(a.run_dir)
        prepare(Path(a.input), rd, limit=a.limit)
        c = run_classify(rd, ctl, synthetic=a.synthetic)
        print("classify:", c["stop_reason"], c["statuses"], file=sys.stderr)
        v = run_verify(rd, ctl, sample_size=a.verify_sample)
        print("verify:", v["agreement"], "planted caught:", v["planted_error_caught"], file=sys.stderr)
        run_group(rd, ctl, name_with_model=True)
        run_rank(rd)
        m = run_memo(rd, ctl)
        print("memo check passed:", m["memo_check_passed"], file=sys.stderr)
        print(json.dumps(export_grading(rd), indent=2))
    elif a.cmd == "export":
        from .export import export_grading
        print(json.dumps(export_grading(Path(a.run_dir), Path(a.out) if a.out else None, compress=not a.no_gzip, ingestion=Path(a.ingestion) if a.ingestion else None), indent=2))
    elif a.cmd == "status":
        from .store import Store
        s = Store(Path(a.run_dir), create=False)
        print(json.dumps({"statuses": s.status_counts(), "rows": s.review_count(), "spend_usd": round(s.spend(), 6),
                          "phases": s.get_meta("phases", []), "controls": s.get_meta("controls")}, indent=2))
        s.close()
    elif a.cmd == "eval":
        from . import evals
        if a.which == "golden-template":
            print("wrote", evals.golden_template(Path(a.run_dir), Path(a.out), a.n, a.seed), "rows to", a.out)
        elif a.which == "golden":
            print(json.dumps(evals.score_golden(Path(a.run_dir), Path(a.golden), Path(a.out) if a.out else None), indent=2))
        elif a.which == "injection":
            r = evals.injection_test(_controls(a), Path(a.out))
            print(json.dumps({k: r[k] for k in ("passed", "reason", "record")}, indent=2))
        elif a.which == "resume":
            r = evals.resume_demo(Path(a.input), _controls(a), Path(a.out), a.first_batches, Path(a.keep_run) if a.keep_run else None)
            print(json.dumps({k: r[k] for k in ("passed", "phase_initial", "phase_resume", "completed_ids_resent_in_resume")}, indent=2))
        elif a.which == "reproducibility":
            print(json.dumps(evals.reproducibility(Path(a.run_dir), Path(a.out) if a.out else None), indent=2))
        elif a.which == "fields":
            r = evals.field_checks(Path(a.golden), Path(a.records), Path(a.verifier_dir) if a.verifier_dir else None, Path(a.out))
            print(json.dumps({k: v for k, v in r.items() if k != "entities"} | {"entities": {k: v for k, v in r["entities"].items() if k != "list"}}, indent=2))
    elif a.cmd == "cost":
        from . import cost
        if a.which == "pilot":
            if a.backend != "fake" and not a.i_understand_this_is_paid:
                raise SystemExit("cost pilot with a real backend spends money; add --i-understand-this-is-paid")
            r = cost.run_pilot(Path(a.input), Path(a.cost_dir), _controls(a), warm=a.warm, synthetic=a.synthetic)
            print(json.dumps({k: r[k] for k in ("label", "rows", "statuses", "wall_clock_seconds", "new_enrichment_calls_this_run")}, indent=2))
        elif a.which == "checkpoint":
            print(json.dumps(cost.checkpoint_refresh(Path(a.cost_dir), Path(a.run_dir), a.label), indent=2))
        elif a.which == "rebuild-usage":
            print(json.dumps(cost.rebuild_usage(Path(a.cost_dir)), indent=2))
        else:
            r = cost.replay(Path(a.cost_dir), Path(a.rates) if a.rates else None, Path(a.projection) if a.projection else None, price_as=a.price_as)
            print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk in ("api_cost_usd", "cost_per_1000_inputs_usd", "wall_clock_seconds")} for k, v in r["runs"].items()}, indent=2))
            if "projection" in r:
                print(json.dumps([{k: s[k] for k in ("scenario", "api_total_usd", "exceeds_spending_limit", "hours_with_workers")} for s in r["projection"]["scenarios"]], indent=2))
    elif a.cmd == "dashboard-load":
        from .dashboard_load import load_run
        print(json.dumps(load_run(Path(a.run_dir), a.database_url), indent=2))


if __name__ == "__main__":
    main()
