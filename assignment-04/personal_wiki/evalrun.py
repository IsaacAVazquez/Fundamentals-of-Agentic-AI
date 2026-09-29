"""Run the fixed ask-mode question set and score each evidence card against the expectations written before the run."""
from __future__ import annotations

import sys
from pathlib import Path

from .ask import run_ask
from .config import Settings
from .errors import UsageError
from .evidence import read_json, write_json


def load_questions(path: Path) -> dict:
    if not path.exists():
        raise UsageError(f"question file {path} not found.")
    data = read_json(path)
    questions = data.get("questions")
    if not isinstance(questions, list) or not questions:
        raise UsageError(f"{path} has no \"questions\" list.")
    for q in questions:
        for key in ("id", "question", "expected_behavior"):
            if key not in q:
                raise UsageError(f"question {q} is missing {key!r}")
    return data


def assess(card, q: dict) -> dict:
    expected = q.get("expected_behavior", "answer")
    passages = card.retrieval.get("passages", [])
    sent_paths = {p["path"] for p in passages if p.get("sent_to_model")}
    retrieved_paths = {p["path"] for p in passages}
    expected_sources = q.get("expected_sources", [])
    answer = (card.answer.get("text") or "").lower()
    keywords = q.get("expected_keywords", [])
    found = [k for k in keywords if k.lower() in answer]
    if expected == "insufficient":
        status_ok = card.status == "insufficient"
    else:
        status_ok = card.status in ("supported", "partial")
    hit = any(s in sent_paths for s in expected_sources) if expected_sources else None
    hit_all = all(s in sent_paths for s in expected_sources) if expected_sources else None
    if expected == "insufficient":
        verdict = "pass" if status_ok else "fail"
    elif status_ok and hit and (hit_all or not q.get("require_all_sources")) and len(found) == len(keywords):
        verdict = "pass"
    elif status_ok:
        verdict = "check"
    else:
        verdict = "fail"
    cited_ok = None
    if card.citations:
        cited_paths = {c["path"] for c in card.citations if c["valid"]}
        cited_ok = any(p in expected_sources for p in cited_paths) if expected_sources else None
    return {"expected_behavior": expected, "expected_sources": expected_sources, "retrieval_hit": hit, "retrieval_hit_all": hit_all,
            "retrieved_any": [s for s in expected_sources if s in retrieved_paths], "expected_keywords": keywords, "keywords_found": found,
            "status_matches_expected": status_ok, "cited_expected_source": cited_ok, "verdict": verdict, "notes": q.get("notes", ""),
            "human_assessment": q.get("human_assessment")}


def run_eval(settings: Settings, backend, index, questions_path: Path) -> list:
    data = load_questions(questions_path)
    defaults = data.get("defaults", {})
    cards = []
    print(f"wiki eval · {len(data['questions'])} questions from {questions_path} · model {backend.model_info().label()} ({backend.name}, local) · run {settings.run_id}")
    for q in data["questions"]:
        k = int(q.get("k") or defaults.get("k") or settings.k)
        scope = q.get("scope") or defaults.get("scope") or settings.scope
        print(f"\n[{q['id']}] {q['question']}")
        card = run_ask(settings, q["question"], backend, index, k=k, scope=scope, card_id=q["id"], mode="local")
        card.assessment = assess(card, q)
        if settings.save:
            from .evidence import write_card
            write_card(settings.run_dir, card)
        a = card.assessment
        print(f"  status {card.status} · verdict {a['verdict']} · retrieval hit {a['retrieval_hit']} · keywords {len(a['keywords_found'])}/{len(a['expected_keywords'])} · {card.timing['wall_s']:.1f} s")
        print("  answer: " + (card.answer.get("text") or "").replace("\n", " ")[:300])
        cards.append(card)
    summary = [{"id": c.id, "question": c.question, "status": c.status, "verdict": c.assessment["verdict"], "retrieval_hit": c.assessment["retrieval_hit"],
                "keywords_found": c.assessment["keywords_found"], "cited_paths": c.citation_check.get("cited_paths", []),
                "wall_s": c.timing.get("wall_s"), "tokens_per_s": c.timing.get("tokens_per_s"), "model": c.model.get("tag")} for c in cards]
    if settings.save:
        write_json(settings.run_dir / "ask" / "summary.json", {"schema": "eval-summary/1", "run_id": settings.run_id, "questions_file": str(questions_path), "results": summary})
        lines = ["# Ask-mode test summary", "", f"Run `{settings.run_id}`, questions from `{questions_path}`.", "",
                 "| id | status | verdict | retrieval hit | keywords found | cited paths | wall s | tok/s |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for s in summary:
            lines.append(f"| {s['id']} | {s['status']} | {s['verdict']} | {s['retrieval_hit']} | {s['keywords_found']} | {s['cited_paths']} | {s['wall_s']} | {s['tokens_per_s']} |")
        (settings.run_dir / "ask" / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nCards and summary: {settings.run_dir / 'ask'}", file=sys.stderr)
    return cards
