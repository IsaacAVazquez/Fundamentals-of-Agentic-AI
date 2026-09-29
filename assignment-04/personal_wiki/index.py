"""The retrieval index: BM25 over passages from vault/raw and vault/wiki.

The index is two files in the index folder, outside the vault: chunks.jsonl (one
passage per line) and bm25.json (term statistics). It is rebuilt whenever the vault's
fingerprint (paths, sizes, modification times) changes.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from .chunking import Passage, chunk_file, collect_vault_files
from .config import Settings, utc_now_iso
from .errors import NothingToIndex, VaultMissing
from .textutil import content_terms

INDEX_VERSION = 1
K1 = 1.5
B = 0.75
HEADING_WEIGHT = 3
EXTRA_WEIGHT = 2


@dataclass
class Bm25Index:
    version: int
    built_at: str
    fingerprint: str
    k1: float
    b: float
    n_docs: int
    avgdl: float
    doc_len: list
    df: dict
    postings: dict          # term -> list of [doc_index, term_frequency]
    passages: list

    def idf(self, term: str) -> float:
        n = self.df.get(term, 0)
        return math.log(1.0 + (self.n_docs - n + 0.5) / (n + 0.5))

    def stats(self) -> dict:
        kinds = Counter(p.kind for p in self.passages)
        return {"built_at": self.built_at, "passages": self.n_docs, "raw_passages": kinds.get("raw", 0),
                "wiki_passages": kinds.get("wiki", 0), "terms": len(self.df),
                "files": len({p.path for p in self.passages})}


def doc_terms(p: Passage) -> list:
    """Stemmed content terms of a passage, with heading and extra terms repeated as a boost."""
    terms = content_terms(p.text)
    terms += content_terms(" ".join(p.heading_path)) * HEADING_WEIGHT
    terms += content_terms(" ".join(p.extra_terms)) * EXTRA_WEIGHT
    return terms


def vault_fingerprint(vault: Path) -> str:
    h = hashlib.sha256(f"v{INDEX_VERSION}\n".encode())
    for rel in collect_vault_files(vault):
        st = os.stat(vault / rel)
        h.update(f"{rel}\t{st.st_size}\t{st.st_mtime_ns}\n".encode("utf-8"))
    return h.hexdigest()


def build_index(vault: Path, index_dir: Path) -> Bm25Index:
    if not (vault / "raw").is_dir() and not (vault / "wiki").is_dir():
        raise VaultMissing(f"no vault at {vault} (expected raw/ and wiki/ inside it). Run from assignment-04/ or pass --vault PATH.")
    files = collect_vault_files(vault)
    passages: list = []
    for rel in files:
        passages.extend(chunk_file(vault, rel))
    if not passages:
        raise NothingToIndex(f"nothing to index: {vault / 'raw'} and {vault / 'wiki'} contain no .md or .txt files. Copy sources into vault/raw and run \"wiki ingest\".")
    df: dict = defaultdict(int)
    postings: dict = defaultdict(list)
    doc_len: list = []
    for i, p in enumerate(passages):
        counts = Counter(doc_terms(p))
        doc_len.append(sum(counts.values()))
        for term, tf in counts.items():
            df[term] += 1
            postings[term].append([i, tf])
    index = Bm25Index(INDEX_VERSION, utc_now_iso(), vault_fingerprint(vault), K1, B, len(passages),
                      sum(doc_len) / len(doc_len), doc_len, dict(df), dict(postings), passages)
    save_index(index, index_dir)
    return index


def save_index(index: Bm25Index, index_dir: Path) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
    chunks_tmp = index_dir / "chunks.jsonl.tmp"
    with chunks_tmp.open("w", encoding="utf-8") as f:
        for p in index.passages:
            f.write(json.dumps(p.to_dict(), ensure_ascii=False) + "\n")
    meta = {k: v for k, v in index.__dict__.items() if k != "passages"}
    meta_tmp = index_dir / "bm25.json.tmp"
    meta_tmp.write_text(json.dumps(meta), encoding="utf-8")
    os.replace(chunks_tmp, index_dir / "chunks.jsonl")
    os.replace(meta_tmp, index_dir / "bm25.json")


def load_index(index_dir: Path):
    chunks, meta = index_dir / "chunks.jsonl", index_dir / "bm25.json"
    if not chunks.exists() or not meta.exists():
        return None
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
        if data.get("version") != INDEX_VERSION:
            return None
        passages = [Passage.from_dict(json.loads(line)) for line in chunks.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None
    return Bm25Index(passages=passages, **data)


def index_is_fresh(settings: Settings) -> bool:
    index = load_index(settings.index_dir)
    return index is not None and index.fingerprint == vault_fingerprint(settings.vault)


def ensure_index(settings: Settings, quiet: bool = False) -> Bm25Index:
    """Load the index, rebuilding it when it is missing or the vault changed."""
    index = load_index(settings.index_dir)
    current = vault_fingerprint(settings.vault)
    if index is not None and index.fingerprint == current:
        return index
    if not quiet:
        print("Index missing or stale, rebuilding from the vault...", file=sys.stderr)
    index = build_index(settings.vault, settings.index_dir)
    if not quiet:
        s = index.stats()
        print(f"Indexed {s['passages']} passages from {s['files']} files ({s['raw_passages']} raw, {s['wiki_passages']} wiki).", file=sys.stderr)
    return index
