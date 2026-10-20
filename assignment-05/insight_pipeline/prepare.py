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
FIELD_SEP = "\x1f"  # unit separator: cannot appear in the source fields, so the row hash is unambiguous

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_hash(row: dict) -> str:
    """Hash of the six retained source values, joined by a separator that never appears in them.

    This is the row identity the grading export reports as source_sha256. If GRADING_CONTRACT.md
    in the dataset ZIP defines a different canonical form, change this one function.
    """
    return sha256_text(FIELD_SEP.join(row.get(c, "") or "" for c in COLUMNS))


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def prepare(input_csv: Path, run_dir: Path, chunk_rows: int = 5000, limit: int | None = None) -> dict:
    input_csv = Path(input_csv)
    store = Store(run_dir)
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

    with open(input_csv, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or [c.strip() for c in reader.fieldnames] != COLUMNS:
            raise SystemExit(f"unexpected columns {reader.fieldnames}; expected {COLUMNS}")
        header_ok = True
        for row in reader:
            if limit and total >= limit:
                break
            rid = (row["review_id"] or "").strip()
            text = row["review_text"] or ""
            if rid in seen_ids:
                duplicate_ids += 1
                continue
            seen_ids.add(rid)
            is_empty = int(text.strip() == "")
            empty += is_empty
            if not (row["app_version"] or "").strip():
                versions_missing += 1
            ratings[(row["review_rating"] or "").strip()] += 1
            months[(row["review_timestamp"] or "")[:7]] += 1
            th = sha256_text(text)
            if not is_empty:
                text_hashes.add(th)
            buffer.append((rid, total, text, row["review_rating"], row["review_likes"], row["app_version"],
                           row["review_timestamp"], source_hash(row), th, is_empty))
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
        "row_hash_definition": "sha256(utf8(review_id + US + review_text + US + review_rating + US + review_likes + US + app_version + US + review_timestamp)), US = \\x1f",
        "text_hash_definition": "sha256(utf8(review_text))",
        "expected_full_corpus": CORPUS,
        "matches_full_corpus_profile": (
            total == CORPUS["rows"] and empty == CORPUS["empty"] and versions_missing == CORPUS["missing_app_version"]
            and duplicate_ids == 0 and len(text_hashes) == CORPUS["distinct_nonempty_texts"]
        ),
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
