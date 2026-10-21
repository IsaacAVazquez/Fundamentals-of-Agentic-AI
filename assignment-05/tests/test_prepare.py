import csv
import json
from pathlib import Path

import pytest

from insight_pipeline.prepare import prepare, source_hash
from insight_pipeline.store import Store


def test_prepare_counts_and_hashes(synthetic_csv, tmp_path):
    report = prepare(synthetic_csv, tmp_path / "run")
    assert report["rows"] == 300
    assert report["empty_review_texts"] == 2
    assert report["nonempty_reviews"] == 298
    assert report["duplicate_review_ids_skipped"] == 0
    assert report["distinct_nonempty_texts"] < 298  # the generator repeats texts on purpose
    store = Store(tmp_path / "run")
    assert store.review_count() == 300
    assert store.status_counts() == {"pending": 300, "completed": 0, "quarantined": 0}
    row = next(csv.DictReader(open(synthetic_csv, newline="", encoding="utf-8")))
    stored = store.conn.execute("SELECT source_sha256 FROM reviews WHERE review_id = ?", (row["review_id"],)).fetchone()[0]
    assert stored == source_hash(row)
    store.close()
    assert json.loads((tmp_path / "run" / "data_manifest.json").read_text())["rows"] == 300


def test_prepare_is_idempotent(synthetic_csv, tmp_path):
    a = prepare(synthetic_csv, tmp_path / "run")
    b = prepare(synthetic_csv, tmp_path / "run")
    assert a["rows"] == b["rows"]


def test_multiline_text_survives(tmp_path):
    p = tmp_path / "m.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["review_id", "review_text", "review_rating", "review_likes", "app_version", "review_timestamp"])
        w.writerow(["a", "line one\nline two, with a comma", "3", "0", "", "2023-01-01 00:00:00"])
    prepare(p, tmp_path / "run")
    s = Store(tmp_path / "run")
    assert s.conn.execute("SELECT review_text FROM reviews").fetchone()[0] == "line one\nline two, with a comma"
    s.close()


def test_row_hash_and_profile_match_the_course_checker(tmp_path):
    """source_hash and contract_profile must equal check_submission.py's row_sha and profile byte for byte."""
    import importlib.util
    import sys
    helper = Path(__file__).resolve().parent.parent / "data" / "check_submission.py"
    if not helper.exists():
        pytest.skip("dataset ZIP not unpacked into data/")
    spec = importlib.util.spec_from_file_location("check_submission", helper)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    sample = helper.parent / "cost_100.csv"
    rows = list(csv.DictReader(open(sample, newline="", encoding="utf-8")))
    assert all(source_hash(r) == checker.row_sha(r) for r in rows)
    report = prepare(sample, tmp_path / "run")
    assert report["contract_profile"] == checker.profile(sample)
