"""The retrieval tool: a query in, ranked original passages out. It never calls the model."""
from __future__ import annotations

from dataclasses import dataclass

from .chunking import Passage
from .index import Bm25Index
from .textutil import STOPWORDS, stem, tokenize

# A small, documented query-side synonym map (weight 0.5). BM25 matches exact stems,
# so a question that says "machine" would otherwise miss a passage that says "laptop".
SYNONYMS = {
    "machine": ["laptop", "computer"],
    "computer": ["laptop", "machine"],
    "hardware": ["laptop", "chip", "cores"],
    "gpu": ["mps", "metal", "cuda"],
    "cpu": ["processor", "cores"],
    "grade": ["score", "points", "graded"],
    "grades": ["score", "points", "graded"],
    "lr": ["learning", "rate"],
    "notes": ["wiki", "note"],
    "speed": ["time", "seconds", "elapsed"],
    "memory": ["ram", "gb"],
}


@dataclass
class Hit:
    passage: Passage
    score: float
    rank: int
    matched_terms: list

    def to_dict(self, include_text: bool = True) -> dict:
        d = {"n": self.rank, "path": self.passage.path, "kind": self.passage.kind, "heading": self.passage.heading,
             "heading_path": list(self.passage.heading_path), "lines": [self.passage.start_line, self.passage.end_line],
             "score": round(self.score, 3), "chars": len(self.passage.text), "matched_terms": self.matched_terms,
             "id": self.passage.id}
        if include_text:
            d["text"] = self.passage.text
        return d


def expand_query(query: str) -> dict:
    """Stemmed content terms with weight 1.0, plus synonyms at 0.5."""
    weights: dict = {}
    for tok in tokenize(query):
        if tok in STOPWORDS:
            continue
        weights[stem(tok)] = max(weights.get(stem(tok), 0.0), 1.0)
        for syn in SYNONYMS.get(tok, ()):
            weights[stem(syn)] = max(weights.get(stem(syn), 0.0), 0.5)
    return weights


def search(index: Bm25Index, query: str, k: int = 6, scope: str = "all") -> list:
    """Rank passages by BM25 for the query; scope is raw, wiki, or all."""
    weights = expand_query(query)
    scores: dict = {}
    matched: dict = {}
    for term, w in weights.items():
        postings = index.postings.get(term)
        if not postings:
            continue
        idf = index.idf(term)
        for doc, tf in postings:
            dl = index.doc_len[doc]
            denom = tf + index.k1 * (1 - index.b + index.b * dl / index.avgdl)
            scores[doc] = scores.get(doc, 0.0) + w * idf * tf * (index.k1 + 1) / denom
            matched.setdefault(doc, []).append(term)
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    hits: list = []
    for doc, score in ranked:
        p = index.passages[doc]
        if scope != "all" and p.kind != scope:
            continue
        hits.append(Hit(p, score, len(hits) + 1, sorted(set(matched[doc]))))
        if len(hits) >= k:
            break
    return hits


def select_for_prompt(hits: list, budget_chars: int) -> list:
    """Keep whole passages in rank order until the character budget would be exceeded; renumber 1..m."""
    chosen: list = []
    used = 0
    for h in hits:
        if chosen and used + len(h.passage.text) > budget_chars:
            break
        chosen.append(Hit(h.passage, h.score, len(chosen) + 1, h.matched_terms))
        used += len(h.passage.text)
    return chosen


def format_passages(hits: list) -> str:
    parts = []
    for h in hits:
        p = h.passage
        parts.append(f"[{h.rank}] {p.path} # {p.heading} (lines {p.start_line}-{p.end_line})\n{p.text}")
    return "\n\n".join(parts)
