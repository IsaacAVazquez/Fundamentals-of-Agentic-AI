"""Small text helpers shared by the index, the fake backend, and the citation check."""
from __future__ import annotations

import math
import re

TOKEN_RE = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?")

STOPWORDS = frozenset("""
a an and are as at be been but by did do does for from had has have he her his how i if in into is it its
me my no nor not of on or our she so than that the their them then there these they this those to us was
we were what when where which who whom why will with would you your yes also any can could should may
might must shall very just about above after again all am before being below between both down during
each few further here more most off once only other out over own same some such through under until up
""".split())

_HTML_IMG = re.compile(r"<img\b[^>]*?\balt=\"([^\"]*)\"[^>]*>", re.IGNORECASE)
_HTML_TAG = re.compile(r"<[^>]+>")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[`])")


def tokenize(text: str) -> list[str]:
    """Lowercase word and number tokens. Keeps decimals ("0.0001") and alphanumerics ("m4", "e4b")."""
    return TOKEN_RE.findall(text.lower())


def stem(token: str) -> str:
    """A light suffix stripper: trains/trained/training -> train, games -> game. Numbers are untouched."""
    if token[0].isdigit():
        return token
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 5 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and (token.endswith("sses") or token.endswith("shes") or token.endswith("ches") or token.endswith("xes")):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def content_terms(text: str) -> list[str]:
    """Stemmed tokens without stopwords, in order."""
    return [stem(t) for t in tokenize(text) if t not in STOPWORDS]


def strip_html(text: str) -> str:
    text = _HTML_IMG.sub(lambda m: m.group(1), text)
    return _HTML_TAG.sub("", text)


def split_sentences(text: str) -> list[str]:
    parts = [p.strip() for p in _SENTENCE_SPLIT.split(text.strip())]
    return [p for p in parts if p]


def estimate_tokens(text: str) -> int:
    """A rough count: four characters per token."""
    return math.ceil(len(text) / 4)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "untitled"


def truncate(text: str, limit: int, marker: str = " [...]") -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - len(marker))].rstrip() + marker
