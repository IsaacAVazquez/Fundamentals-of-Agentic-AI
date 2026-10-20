"""Code-side validation of a model's enrichment output. A record that fails here is retried
once, then quarantined with the reason recorded. Nothing is silently dropped."""
from __future__ import annotations

import json
from typing import Any

from .config import INTENTS, TOPICS


class ValidationError(ValueError):
    pass


def parse_batch_output(text: str) -> list[dict]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid_json: {exc.msg}") from exc
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and isinstance(data.get("records"), list):
        records = data["records"]
    else:
        raise ValidationError("invalid_shape: expected {'records': [...]}")
    return records


def validate_record(item: Any, review_id: str, review_text: str) -> dict:
    """Return a clean record dict or raise ValidationError naming the first failing check."""
    if not isinstance(item, dict):
        raise ValidationError("not_an_object")
    for key in ("id", "topic", "intent", "sentiment", "severity", "entities", "evidence_quote", "needs_review"):
        if key not in item:
            raise ValidationError(f"missing_key:{key}")
    if str(item["id"]) != review_id:
        raise ValidationError("id_mismatch")
    topic = item["topic"]
    if topic not in TOPICS:
        raise ValidationError(f"bad_topic:{topic}")
    intent = item["intent"]
    if intent not in INTENTS:
        raise ValidationError(f"bad_intent:{intent}")
    try:
        sentiment = float(item["sentiment"])
    except (TypeError, ValueError):
        raise ValidationError("sentiment_not_number")
    if not -1.0 <= sentiment <= 1.0:
        raise ValidationError("sentiment_out_of_range")
    severity = item["severity"]
    if isinstance(severity, bool) or not isinstance(severity, int):
        if isinstance(severity, float) and severity.is_integer():
            severity = int(severity)
        else:
            raise ValidationError("severity_not_integer")
    if not 1 <= severity <= 5:
        raise ValidationError("severity_out_of_range")
    entities = item["entities"]
    if not isinstance(entities, list) or not all(isinstance(e, str) for e in entities):
        raise ValidationError("entities_not_string_list")
    quote = item["evidence_quote"]
    if not isinstance(quote, str) or not quote.strip():
        raise ValidationError("quote_empty")
    if quote not in review_text:
        raise ValidationError("quote_not_substring")
    needs_review = item["needs_review"]
    if not isinstance(needs_review, bool):
        raise ValidationError("needs_review_not_bool")
    return {
        "review_id": review_id,
        "topic": topic,
        "intent": intent,
        "sentiment": round(sentiment, 3),
        "severity": severity,
        "entities": [e.strip().lower() for e in entities if e.strip()][:10],
        "evidence_quote": quote,
        "needs_review": needs_review,
    }
