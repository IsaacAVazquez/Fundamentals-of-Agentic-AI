import csv
import gzip
import json

import pytest

from insight_pipeline.classify import Controls, run_classify
from insight_pipeline.evals import field_checks, injection_test, reproducibility, resume_demo
from insight_pipeline.export import export_grading
from insight_pipeline.group import run_group
from insight_pipeline.memo import check_memo, run_memo
from insight_pipeline.prepare import prepare
from insight_pipeline.rank import rank_from_export, run_rank
from insight_pipeline.store import Store
from insight_pipeline.verify import run_verify


def _full_run(synthetic_csv, run_dir, controls):
    prepare(synthetic_csv, run_dir)
    out = run_classify(run_dir, controls, synthetic=True)
    assert out["stop_reason"] == "no_pending"
    return out


def test_every_row_is_accounted_for(synthetic_csv, tmp_path, fake_controls):
    rd = tmp_path / "run"
    out = _full_run(synthetic_csv, rd, fake_controls)
    s = out["statuses"]
    assert s["pending"] == 0 and s["completed"] + s["quarantined"] == 300
    store = Store(rd)
    reasons = [r["reason"] for r in store.iter_records("quarantined")]
    assert reasons == ["empty_review_text", "empty_review_text"]
    # every call carried at most 50 ids and every completed row has a valid label_config
    for c in store.iter_calls("classify"):
        assert len(json.loads(c["request_ids"])) <= 50
    assert all(r["label_config"] for r in store.iter_records("completed"))
    store.close()


def test_exact_text_cache_has_provenance(synthetic_csv, tmp_path, fake_controls):
    rd = tmp_path / "run"
    _full_run(synthetic_csv, rd, fake_controls)
    store = Store(rd)
    copies = list(store.conn.execute("SELECT c.review_id, c.cache_source_id, r.text_sha256 FROM records c JOIN reviews r ON r.review_id=c.review_id WHERE c.cache_source_id IS NOT NULL"))
    assert copies, "the synthetic file repeats texts, so some rows must be cache copies"
    for row in copies:
        src = store.conn.execute("SELECT text_sha256, review_id FROM reviews WHERE review_id = ?", (row["cache_source_id"],)).fetchone()
        assert src["text_sha256"] == row["text_sha256"]
        assert store.record(row["cache_source_id"])["cache_source_id"] is None  # provenance points at a direct classification
    store.close()


def test_retry_once_then_quarantine(tmp_path, fake_controls):
    p = tmp_path / "f.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["review_id", "review_text", "review_rating", "review_likes", "app_version", "review_timestamp"])
        w.writerow(["ok", "Can't log in since the update", "1", "0", "", "2023-01-01 00:00:00"])
        w.writerow(["fail-once", "The app crashes constantly [[FAIL_ONCE]]", "1", "0", "", "2023-01-01 00:00:00"])
        w.writerow(["drop-once", "Charged twice this month [[DROP_ONCE]]", "1", "0", "", "2023-01-01 00:00:00"])
        w.writerow(["bad-quote", "Support never answered [[BAD_QUOTE]]", "1", "0", "", "2023-01-01 00:00:00"])
    rd = tmp_path / "run"
    prepare(p, rd)
    run_classify(rd, fake_controls)
    store = Store(rd)
    rec = {r["review_id"]: r for r in store.iter_records()}
    # "ok" shared a request with the malformed one, so the whole batch was retried once and it completed on attempt 2.
    assert rec["ok"]["status"] == "completed" and rec["ok"]["attempts"] <= 2
    assert rec["fail-once"]["status"] == "completed" and rec["fail-once"]["attempts"] == 2
    assert rec["drop-once"]["status"] == "completed" and rec["drop-once"]["attempts"] == 2
    assert rec["bad-quote"]["status"] == "quarantined" and rec["bad-quote"]["attempts"] == 2
    assert rec["bad-quote"]["reason"] == "quote_not_substring"
    store.close()


def test_transient_error_stops_and_resumes(tmp_path, fake_controls):
    p = tmp_path / "t.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["review_id", "review_text", "review_rating", "review_likes", "app_version", "review_timestamp"])
        w.writerow(["a", "Playback lags constantly [[APIERROR_ONCE]]", "1", "0", "", "2023-01-01 00:00:00"])
    rd = tmp_path / "run"
    prepare(p, rd)
    c = Controls(backend="fake", backoff_tries=1)
    out = run_classify(rd, c)
    assert out["stop_reason"] == "provider_unavailable" and out["statuses"]["pending"] == 1
    out2 = run_classify(rd, c)
    assert out2["stop_reason"] == "no_pending" and out2["statuses"]["completed"] == 1
    store = Store(rd)
    phases = store.get_meta("phases")
    assert [p["phase"] for p in phases] == ["initial", "resume"]
    store.close()


def test_spend_cap_stops_admission(synthetic_csv, tmp_path):
    rd = tmp_path / "run"
    prepare(synthetic_csv, rd)
    rates = tmp_path / "rates.csv"
    rates.write_text("provider,model,unit,usd_per_million_tokens,currency,source_and_date\n" + "".join(
        f"fake,fake-deterministic-v1,{u},1.0,USD,test\n" for u in ("input", "cached_input", "cache_write", "output")))
    out = run_classify(rd, Controls(backend="fake", max_spend_usd=0.0001, batch_size=10, rates_path=rates), synthetic=True)
    assert out["stop_reason"] == "spend_cap" and out["batches"] == 0


def test_downstream_stages_and_export(synthetic_csv, tmp_path, fake_controls):
    rd = tmp_path / "run"
    _full_run(synthetic_csv, rd, fake_controls)
    v = run_verify(rd, fake_controls, sample_size=30, seed=1)
    assert v["compared"] == 30 and v["planted_error_caught"] is True
    g = run_group(rd, fake_controls, name_with_model=True)
    assert g["member_count"] > 0
    r = run_rank(rd)
    scores = [a["priority_score"] for a in r["ranking"]]
    assert scores == sorted(scores, reverse=True)
    for a in r["ranking"]:
        assert a["priority_score"] == a["severity_sum"]
        assert round(a["complaint_count"] * float(a["mean_severity"])) == a["severity_sum"]
    m = run_memo(rd, fake_controls)
    assert m["memo_check_passed"] is True
    assert m["priority_issue_id"] == r["ranking"][0]["issue_id"]
    e = export_grading(rd)
    out = rd / "grading"
    for name in ("run.json", "ingestion.json", "records.jsonl.gz", "membership.csv", "ranking.csv", "claims.csv", "calls.jsonl", "checkpoint_before.json", "checkpoint_after.json"):
        assert (out / name).exists(), name
    with gzip.open(out / "records.jsonl.gz", "rt") as fh:
        ids = [json.loads(line)["review_id"] for line in fh]
    assert len(ids) == 300 and len(set(ids)) == 300
    assert e["counts"]["completed"] + e["counts"]["quarantined"] == 300
    with gzip.open(rd / "enriched.jsonl.gz", "rt") as fh:
        assert sum(1 for _ in fh) == e["counts"]["completed"]
    assert sum(1 for _ in open(rd / "quarantine.jsonl")) == e["counts"]["quarantined"]
    rep = reproducibility(rd)
    assert rep["passed"] is True
    # A grader has the export, not state.sqlite: reranking from it must give the same bytes.
    rr = rank_from_export(out, tmp_path / "rerank", rd / "issues.json")
    assert rr["model_calls_made"] == 0
    for name in ("ranking.csv", "aggregates.csv", "claims.csv"):
        assert (tmp_path / "rerank" / name).read_bytes() == (rd / name).read_bytes(), name
    # Per-field checks read only the export: copy three completed records' labels into a golden file, then break one.
    store = Store(rd)
    picked = [r for r in store.iter_records("completed")][:3]
    store.close()
    golden = tmp_path / "golden.csv"
    with open(golden, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["review_id", "review_text", "human_topic", "human_intent", "human_severity", "human_sentiment", "human_evidence_quote", "notes"])
        for i, r in enumerate(picked):
            w.writerow([r["review_id"], r["review_text"], r["topic"], r["intent"], r["severity"] if i else 6 - r["severity"], r["sentiment"], "", "ambiguous" if i == 2 else ""])
    fc = field_checks(golden, out / "records.jsonl.gz", None, tmp_path / "fields")
    assert fc["golden_compared"] == 3 and fc["model_calls_made"] == 0
    assert fc["needs_review_vs_golden_label_miss"]["truth_positive"] == (picked[0]["severity"] != 3)
    assert fc["needs_review_vs_golden_ambiguous_notes"]["truth_positive"] == 1
    assert fc["quote_support"]["rows"] == 3 and fc["quote_support"]["human_judgments_filled"] == 0


def test_read_only_commands_refuse_a_folder_without_state(tmp_path):
    saved = tmp_path / "results-copy"
    saved.mkdir()
    (saved / "ranking.csv").write_text("rank,issue_id\n1,ISS-billing\n")
    with pytest.raises(SystemExit, match="state.sqlite not found"):
        run_rank(saved)
    assert not (saved / "state.sqlite").exists()
    assert (saved / "ranking.csv").read_text() == "rank,issue_id\n1,ISS-billing\n"


def test_memo_checker_rejects_bad_numbers():
    claims = [{"claim_id": "C1", "issue_id": "ISS-billing", "metric": "complaint_count", "value": 1200}]
    good = check_memo("Billing has 1,200 [C1] complaints [ISS-billing].", claims, {"ISS-billing"}, {}, set())
    assert good["passed"]
    bad = check_memo("Billing has 1,300 [C1] complaints and 9,999 more.", claims, {"ISS-billing"}, {}, set())
    assert not bad["passed"] and bad["number_claim_mismatches"] and "9,999" in bad["unmatched_numbers"]
    comma = check_memo("Billing has 1,200 [C1] complaints, one cancellation, and [C1] again.", claims, {"ISS-billing"}, {}, set())
    assert comma["passed"], comma
    months = check_memo("Billing has 1,200 [C1] complaints; 2023-11 and 2022-06-01 are partial.", claims, {"ISS-billing"}, {}, set())
    assert months["passed"], months
    unknown = check_memo("See [C7] and [ISS-magic]; revenue at risk is high.", claims, {"ISS-billing"}, {}, set())
    assert unknown["unknown_claims"] == ["C7"] and unknown["unknown_issues"] == ["ISS-magic"] and unknown["forbidden_phrases"]


def test_injection_is_treated_as_content(tmp_path, fake_controls):
    r = injection_test(fake_controls, tmp_path)
    assert r["passed"] and r["record"]["topic"] == "playback" and r["record"]["intent"] != "praise"


def test_resume_never_resends_completed_ids(synthetic_csv, tmp_path, fake_controls):
    r = resume_demo(synthetic_csv, fake_controls, tmp_path, first_batches=2)
    assert r["passed"] and r["phase_initial"]["batches"] == 2 and r["completed_ids_resent_in_resume"] == []


def test_golden_scoring(synthetic_csv, tmp_path, fake_controls):
    from insight_pipeline.evals import golden_template, score_golden
    rd = tmp_path / "run"
    _full_run(synthetic_csv, rd, fake_controls)
    tpl = tmp_path / "golden.csv"
    assert golden_template(rd, tpl, n=10, seed=1) == 10
    rows = list(csv.DictReader(open(tpl, newline="", encoding="utf-8")))
    assert [k for k in rows[0]] == ["review_id", "review_text", "human_topic", "human_intent", "human_severity", "human_sentiment", "human_evidence_quote", "notes"]
    # Hand-label four rows (two agree with the fake labels, two deliberately disagree) and score.
    store = Store(rd)
    labeled = []
    for i, r in enumerate(rows[:4]):
        rec = store.record(r["review_id"])
        if i < 2:
            r.update(human_topic=rec["topic"], human_intent=rec["intent"], human_severity=str(rec["severity"]), human_sentiment=str(rec["sentiment"]), notes="")
        else:
            r.update(human_topic="support" if rec["topic"] != "support" else "billing", human_intent=rec["intent"], human_severity=str(5 if rec["severity"] != 5 else 1), notes="ambiguous wording")
        labeled.append(r)
    store.close()
    with open(tpl, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    rep = score_golden(rd, tpl)
    assert rep["rows_with_human_labels"] == 4 and rep["compared"] == 4
    assert rep["topic_agreement"] == 0.5 and rep["severity_exact_agreement"] == 0.5 and rep["ambiguous_cases"] == 2
    assert rep["quote_substring_failures"] == 0 and (rd / "evals" / "golden_per_case.csv").exists()
