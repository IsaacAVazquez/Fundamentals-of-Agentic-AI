"""Stage 1, code only: read the whole CSV, hash every row, profile it, queue pending work.

The CSV is read in streaming mode with the standard csv module, which handles quoted
multiline review text. Nothing here calls a model.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from .config import CORPUS
from .store import Store, now_iso

COLUMNS = ["review_id", "review_text", "review_rating", "review_likes", "app_version", "review_timestamp"]

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_hash(row: dict) -> str:
    """GRADING_CONTRACT.md row hash: SHA-256 of the compact JSON list of the six source strings, in order.

    This is byte-for-byte the row_sha helper in the course's check_submission.py (json.dumps with
    ensure_ascii=False and no spaces; no trimming or Unicode normalization).
    """
    return sha256_text(json.dumps([row.get(c, "") or "" for c in COLUMNS], ensure_ascii=False, separators=(",", ":")))


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def prepare(input_csv: Path, run_dir: Path, chunk_rows: int = 5000, limit: int | None = None) -> dict:
    input_csv = Path(input_csv)
    store = Store(run_dir, create=True)
    if store.get_meta("prepared"):
        report = json.loads((Path(run_dir) / "ingestion_report.json").read_text())
        store.close()
        return report

    months: Counter = Counter()
    ratings: Counter = Counter()
    versions_missing = 0
    empty = 0
    duplicate_ids = 0
    seen_ids: set[str] = set()
    text_hashes: set[str] = set()
    total = 0
    buffer: list[tuple] = []
    header_ok = False
    parsed_rows = hashlib.sha256()  # the helper's parsed_rows_sha256: every row hash, as bytes, in file order
    first_ts, last_ts = None, None

    with open(input_csv, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or [c.strip() for c in reader.fieldnames] != COLUMNS:
            raise SystemExit(f"unexpected columns {reader.fieldnames}; expected {COLUMNS}")
        header_ok = True
        for row in reader:
            if limit and total >= limit:
                break
            rid = row["review_id"] or ""
            text = row["review_text"] or ""
            row_hash = source_hash(row)
            parsed_rows.update(bytes.fromhex(row_hash))
            ts = row["review_timestamp"] or ""
            first_ts = ts if first_ts is None else min(first_ts, ts)
            last_ts = ts if last_ts is None else max(last_ts, ts)
            if rid in seen_ids:
                duplicate_ids += 1
                continue
            seen_ids.add(rid)
            is_empty = int(text.strip() == "")
            empty += is_empty
            if not (row["app_version"] or "").strip():
                versions_missing += 1
            ratings[row["review_rating"] or ""] += 1
            months[ts[:7]] += 1
            th = sha256_text(text)
            if not is_empty:
                text_hashes.add(th)
            buffer.append((rid, total, text, row["review_rating"], row["review_likes"], row["app_version"],
                           row["review_timestamp"], row_hash, th, is_empty))
            total += 1
            if len(buffer) >= chunk_rows:
                store.insert_reviews(buffer)
                buffer = []
    if buffer:
        store.insert_reviews(buffer)

    report = {
        "generated_at": now_iso(),
        "source_file": str(input_csv),
        "source_sha256": file_sha256(input_csv),
        "source_bytes": input_csv.stat().st_size,
        "columns": COLUMNS,
        "header_ok": header_ok,
        "rows": total,
        "unique_review_ids": len(seen_ids),
        "duplicate_review_ids_skipped": duplicate_ids,
        "empty_review_texts": empty,
        "nonempty_reviews": total - empty,
        "distinct_nonempty_texts": len(text_hashes),
        "exact_duplicate_nonempty_texts": (total - empty) - len(text_hashes),
        "missing_app_version": versions_missing,
        "rating_counts": dict(sorted(ratings.items())),
        "rows_by_month": dict(sorted(months.items())),
        "row_hash_definition": 'sha256(utf8(json.dumps([review_id, review_text, review_rating, review_likes, app_version, review_timestamp], ensure_ascii=False, separators=(",", ":")))), the row_sha helper in check_submission.py',
        "text_hash_definition": "sha256(utf8(review_text))",
        "expected_full_corpus": CORPUS,
        "matches_full_corpus_profile": (
            total == CORPUS["rows"] and empty == CORPUS["empty"] and versions_missing == CORPUS["missing_app_version"]
            and duplicate_ids == 0 and len(text_hashes) == CORPUS["distinct_nonempty_texts"]
        ),
    }
    # The exact object check_submission.py's `profile` command produces; the export copies it to grading/ingestion.json.
    report["contract_profile"] = {
        "file_sha256": report["source_sha256"], "parsed_rows_sha256": parsed_rows.hexdigest(),
        "counts": {"records": total + duplicate_ids, "duplicate_review_ids": duplicate_ids, "empty_review_text": empty,
                   "missing_app_version": versions_missing},
        "reviews_by_month": dict(months), "reviews_by_rating": dict(ratings), "first_review": first_ts, "last_review": last_ts,
    }
    (Path(run_dir) / "ingestion_report.json").write_text(json.dumps(report, indent=2))
    manifest = {
        "source": {"file": input_csv.name, "sha256": report["source_sha256"], "bytes": report["source_bytes"]},
        "prepared_at": report["generated_at"],
        "rows": total,
        "pending_ids": "records.status = 'pending' in state.sqlite",
    }
    (Path(run_dir) / "data_manifest.json").write_text(json.dumps(manifest, indent=2))
    store.set_meta("prepared", True)
    store.set_meta("source", manifest["source"])
    store.close()
    return report
