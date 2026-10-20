"""A deterministic, zero-cost stand-in for a model. Keyword rules only.

It exists so the orchestrator, the validator, the cache, the resume path, the exports, and
the dashboard can be exercised and tested without an API key. Its labels are crude on
purpose; nothing it produces is a measured result. Markers in a review text make it
misbehave on demand so the failure paths can be tested:
  [[FAIL_ONCE]]      first call for that review returns malformed JSON
  [[DROP_ONCE]]      first call omits that review's id from the output
  [[BAD_QUOTE]]      the evidence quote is not a substring (every call)
  [[APIERROR_ONCE]]  first call raises a transient error for the whole batch
"""
from __future__ import annotations

import json
import re
import threading

from ..config import INTENTS, TOPICS
from .base import Backend, CallResult, TransientError

TOPIC_KEYWORDS = {
    "access": ["log in", "login", "password", "locked", "two factor", "sign in", "account"],
    "billing": ["charged", "charge", "price", "refund", "paywall", "premium", "subscription fee", "paid for", "billing"],
    "support": ["support", "customer service", "ticket", "no reply", "answered"],
    "downloads": ["download", "offline", "saved music"],
    "playback": ["crash", "freeze", "lag", "stutter", "stop", "skip", "won't play", "wont play", "playback"],
    "catalog": ["search", "lyrics", "greyed", "recommend", "catalog", "podcast", "album", "missing"],
    "usability": ["ads", "layout", "navigation", "interface", "button", "confusing", "shuffle"],
}
SEV5 = ["charged twice", "double charged", "refund", "deleted", "leaked", "stolen", "lost my library"]
SEV4 = ["can't", "cant", "cannot", "won't", "wont", "crash", "locked", "blocked", "never arrives", "unavailable"]
SEV3 = ["lag", "stutter", "greyed", "missing", "disappear", "half", "skips", "freezes"]
SEV2 = ["ads", "annoying", "confusing", "ugly", "too many", "slow"]
CANCEL = ["cancel", "unsubscrib", "switching to", "done with this app", "leaving"]
REQUEST = ["please add", "would be nice", "wish", "should add", "feature request"]
PRAISE = ["love", "great", "best", "amazing", "awesome", "perfect", "five stars"]

_TOPIC_ORDER = ["billing", "access", "support", "downloads", "playback", "catalog", "usability"]


def _first_sentence_with(text: str, keywords: list[str]) -> str | None:
    low = text.lower()
    for kw in keywords:
        pos = low.find(kw)
        if pos >= 0:
            start = max(low.rfind(".", 0, pos), low.rfind("\n", 0, pos)) + 1
            end_candidates = [i for i in (low.find(".", pos), low.find("\n", pos)) if i >= 0]
            end = min(end_candidates) if end_candidates else len(text)
            quote = text[start:end].strip()
            if quote:
                return quote
    return None


def label_text(text: str) -> dict:
    low = text.lower()
    matched = [t for t in _TOPIC_ORDER if any(k in low for k in TOPIC_KEYWORDS[t])]
    topic = matched[0] if matched else "other"
    if any(k in low for k in SEV5):
        severity = 5
    elif any(k in low for k in SEV4):
        severity = 4
    elif any(k in low for k in SEV3):
        severity = 3
    elif any(k in low for k in SEV2):
        severity = 2
    else:
        severity = 1
    if any(k in low for k in CANCEL):
        intent = "cancellation"
    elif topic != "other" or severity >= 2:
        intent = "complaint"
    elif any(k in low for k in REQUEST):
        intent = "request"
    elif any(k in low for k in PRAISE):
        intent = "praise"
    else:
        intent = "unclear"
    if intent in ("praise", "request", "unclear"):
        severity = 1
    sentiment = {1: 0.6 if intent == "praise" else 0.0, 2: -0.3, 3: -0.5, 4: -0.8, 5: -0.95}[severity]
    keywords = TOPIC_KEYWORDS.get(topic, []) + SEV5 + SEV4 + SEV3 + SEV2 + CANCEL
    quote = _first_sentence_with(text, keywords) or text.split("\n", 1)[0].strip()[:200] or text[:200]
    entities = sorted({k for k in TOPIC_KEYWORDS.get(topic, []) if k in low})[:4]
    return {
        "topic": topic, "intent": intent, "sentiment": sentiment, "severity": severity,
        "entities": entities, "evidence_quote": quote, "needs_review": len(text.strip()) < 8 or intent == "unclear",
    }


def _fake_memo(user: str) -> str:
    """Compose a memo from the aggregate table in the prompt so the code-side checks have something to check."""
    table = json.loads(user.split("AGGREGATE TABLE (every number you may use, with its claim id):\n", 1)[1].split("\n\nRANKED ISSUES:", 1)[0])
    ranked = json.loads(user.split("RANKED ISSUES:\n", 1)[1].split("\n\nEVIDENCE PACK:", 1)[0])
    pack = json.loads(user.split("EVIDENCE PACK:\n", 1)[1].split("\n\nSCOPE AND LIMITATIONS:", 1)[0])
    by = {(c["issue_id"], c["metric"]): c for c in table}
    top = ranked[0]
    alts = [a["issue_id"] for a in ranked[1:3]]
    def cite(iid, metric):
        c = by[(iid, metric)]
        v = c["value"]
        return f"{int(v):,} [{c['claim_id']}]" if str(v).isdigit() else f"{v} [{c['claim_id']}]"
    quotes = pack.get(top["issue_id"], [])[:2]
    ev = " ".join(f'Review {q["review_id"]} says "{q["quote"]}" (severity {q["severity"]}).' for q in quotes)
    memo = (f"## Recommendation\n\nPut the next quarter of product effort on [{top['issue_id']}] ({top['name']}).\n\n"
            f"## Why this issue\n\nIt has {cite(top['issue_id'], 'complaint_count')} complaint records with a mean severity of "
            f"{cite(top['issue_id'], 'mean_severity')}, for a score of {cite(top['issue_id'], 'score')}, the highest of the "
            f"{len(ranked)} issues. {ev}\n\n## Alternatives considered\n\n"
            + " ".join(f"[{a['issue_id']}] scored {cite(a['issue_id'], 'score')} on {cite(a['issue_id'], 'complaint_count')} complaints." for a in ranked[1:3])
            + f"\n\n## Limitations\n\nOnly {cite('', 'completed_records')} records were classified and {cite('', 'quarantined_records')} were quarantined. "
            "Reviews are self-selected and nothing here measures revenue or churn.")
    cited = sorted(set(re.findall(r"\[(C\d+)\]", memo)))
    return json.dumps({"memo_markdown": memo, "priority_issue_id": top["issue_id"], "recommendation": f"Prioritize {top['name']}",
                       "alternatives": alts, "cited_claims": cited})


class FakeBackend(Backend):
    provider = "fake"

    _seen: set[str] = set()          # process-wide, so "once" survives a new backend instance (a resumed run)
    _lock = threading.Lock()

    def __init__(self) -> None:
        pass

    def _once(self, marker: str, text: str) -> bool:
        key = marker + "|" + text
        with self._lock:
            if key in self._seen:
                return False
            self._seen.add(key)
            return True

    def complete(self, *, system: str, user: str, schema: dict | None, model: str, effort: str,
                 max_output_tokens: int) -> CallResult:
        items = json.loads(user) if user.startswith("[") else [{"id": "single", "text": user}]
        if any("[[APIERROR_ONCE]]" in it["text"] and self._once("api", it["text"]) for it in items):
            raise TransientError("fake transient error")
        records = []
        malformed = False
        for it in items:
            text = it["text"]
            if "[[FAIL_ONCE]]" in text and self._once("fail", text):
                malformed = True
            if "[[DROP_ONCE]]" in text and self._once("drop", text):
                continue
            rec = label_text(re.sub(r"\[\[[A-Z_]+\]\]", "", text).strip() or text)
            if "[[BAD_QUOTE]]" in text:
                rec["evidence_quote"] = "this quote is not in the review"
            elif rec["evidence_quote"] not in text:
                rec["evidence_quote"] = text[:min(len(text), 120)]
            records.append({"id": it["id"], **rec})
        if "GROUPER" in system or '"name"' in system:
            out = json.dumps({"name": "fake issue name", "description": "fake description from examples"})
        elif "decision memo" in system:
            out = _fake_memo(user)
        elif malformed:
            out = '{"records": [ this is not json'
        else:
            out = json.dumps({"records": records})
        in_tokens = (len(system) + len(user)) // 4
        return CallResult(text=out, input_tokens=in_tokens, cached_input_tokens=0, cache_write_tokens=0,
                          output_tokens=len(out) // 4, usage_known=True, stop_reason="end_turn")
