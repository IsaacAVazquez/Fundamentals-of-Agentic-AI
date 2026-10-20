import pytest

from insight_pipeline.validate import ValidationError, parse_batch_output, validate_record

GOOD = {"id": "r1", "topic": "billing", "intent": "complaint", "sentiment": -0.7, "severity": 4,
        "entities": ["invoice"], "evidence_quote": "charged twice", "needs_review": False}
TEXT = "I was charged twice this month"


def test_valid_record():
    rec = validate_record(GOOD, "r1", TEXT)
    assert rec["topic"] == "billing" and rec["severity"] == 4 and rec["entities"] == ["invoice"]


@pytest.mark.parametrize("patch,reason", [
    ({"topic": "pricing"}, "bad_topic"), ({"intent": "angry"}, "bad_intent"), ({"severity": 6}, "severity_out_of_range"),
    ({"severity": "4"}, "severity_not_integer"), ({"sentiment": 2}, "sentiment_out_of_range"),
    ({"evidence_quote": "charged thrice"}, "quote_not_substring"), ({"id": "r2"}, "id_mismatch"), ({"needs_review": "no"}, "needs_review_not_bool"),
])
def test_invalid_records(patch, reason):
    with pytest.raises(ValidationError) as exc:
        validate_record({**GOOD, **patch}, "r1", TEXT)
    assert reason in str(exc.value)


def test_parse_shapes():
    assert parse_batch_output('{"records": [1]}') == [1]
    assert parse_batch_output('[1]') == [1]
    with pytest.raises(ValidationError):
        parse_batch_output('{"records": [ broken')
