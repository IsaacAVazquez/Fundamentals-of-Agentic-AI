"""Ask mode: a standalone, neutral, cited answer from retrieved evidence, or an insufficient-evidence reply.

This is the RAG workflow: retrieve passages, put them in the prompt with the research
rules, call the local model, then check the citations. `run_ask` takes no conversation
history at all, so nothing said in chat can reach it.
"""
from __future__ import annotations

import re

from .config import ASK_PASSAGE_BUDGET, NUM_PREDICT, Settings
from .evidence import EvidenceCard, offline_status, write_card
from .prompts import build_ask_messages, file_sha256, load_instruction_file
from .retrieval import expand_query, search, select_for_prompt

CITATION_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
NUMBER_RE = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?![\w])")


def parse_citations(answer: str) -> list:
    """Citation numbers in order of first appearance: [1], [1][3], [1, 3], [1,3]."""
    seen: list = []
    for group in CITATION_RE.findall(answer):
        for n in re.split(r"\s*,\s*", group):
            if n.isdigit() and int(n) not in seen:
                seen.append(int(n))
    return seen


def detect_insufficient(answer: str) -> bool:
    cleaned = re.sub(r"^[\s*_\"'`#>]+", "", answer.strip()).lower()
    return cleaned.startswith("insufficient evidence")


def strip_citation_markers(text: str) -> str:
    return CITATION_RE.sub("", text)


def unverified_numbers(answer: str, cited_texts: list) -> list:
    """Numbers in the answer that appear in none of the cited passages (commas ignored)."""
    haystack = " ".join(cited_texts).replace(",", "")
    found: list = []
    for raw in NUMBER_RE.findall(strip_citation_markers(answer)):
        plain = raw.replace(",", "")
        if plain not in haystack and plain not in found:
            found.append(raw)
    return found


def run_ask(settings: Settings, question: str, backend, index, *, k: int | None = None, scope: str | None = None,
            card_id: str | None = None, mode: str = "local", assessment: dict | None = None) -> EvidenceCard:
    k = k or settings.k
    scope = scope or settings.scope
    instructions = load_instruction_file(settings.instructions_file, "research rules")
    hits = search(index, question, k=k, scope=scope)
    sent = select_for_prompt(hits, ASK_PASSAGE_BUDGET)
    sent_ids = {h.passage.id for h in sent}
    messages = build_ask_messages(instructions, sent, question)
    options = {"temperature": 0.0, "num_ctx": settings.num_ctx, "num_predict": NUM_PREDICT["ask"], "seed": settings.seed}
    completion = backend.generate(messages, kind="ask", temperature=0.0, num_predict=NUM_PREDICT["ask"],
                                  num_ctx=settings.num_ctx, seed=settings.seed)
    answer = completion.text.strip()
    by_rank = {h.rank: h for h in sent}
    citations, invalid = [], []
    for n in parse_citations(answer):
        h = by_rank.get(n)
        if h is None:
            invalid.append(n)
            citations.append({"n": n, "valid": False, "path": None, "heading": None, "lines": None, "kind": None})
        else:
            p = h.passage
            citations.append({"n": n, "valid": True, "path": p.path, "heading": p.heading,
                              "lines": [p.start_line, p.end_line], "kind": p.kind})
    valid = [c for c in citations if c["valid"]]
    insufficient = detect_insufficient(answer)
    if insufficient and not valid:
        status = "insufficient"
    elif valid:
        status = "supported" if not insufficient else "partial"
    else:
        status = "unsupported"
    cited_texts = [by_rank[c["n"]].passage.text for c in valid]
    check = {"valid": len(valid), "invalid": invalid, "cited_paths": sorted({c["path"] for c in valid}),
             "insufficient_marker": insufficient, "unverified_numbers": unverified_numbers(answer, cited_texts) if valid else []}
    retrieval = {"k": k, "scope": scope, "index_built_at": index.built_at, "index_passages": index.n_docs,
                 "query_terms": sorted(expand_query(question)),
                 "passages": [{**h.to_dict(), "sent_to_model": h.passage.id in sent_ids} for h in hits]}
    # ranks in the card follow the numbering the model saw (the sent subset), then the rest
    renumber = {h.passage.id: h.rank for h in sent}
    for p in retrieval["passages"]:
        p["n"] = renumber.get(p["id"], p["n"])
    prompt = {"system_file": settings.instructions_file.name, "system_sha256": file_sha256(settings.instructions_file),
              "system_chars": len(messages[0]["content"]), "user_chars": len(messages[1]["content"]),
              "passage_chars": sum(len(h.passage.text) for h in sent), "passages_sent": len(sent),
              "estimated_tokens": (len(messages[0]["content"]) + len(messages[1]["content"])) // 4,
              "user_message": messages[1]["content"]}
    card = EvidenceCard(
        id=card_id or f"ask-{completion.timing.wall_s:.0f}s-{abs(hash(question)) % 100000:05d}", run_id=settings.run_id,
        question=question, mode=mode, backend=backend.name, model=completion.model.to_dict(), options=options,
        retrieval=retrieval, prompt=prompt, answer={"text": answer, "raw": completion.text}, citations=citations,
        citation_check=check, status=status, timing=completion.timing.to_dict(), memory=completion.memory.to_dict(),
        offline=offline_status(settings), assessment=assessment,
    )
    if settings.save:
        write_card(settings.run_dir, card)
    return card


def render_answer(card: EvidenceCard) -> str:
    m = card.model
    lines = [f"model {m.get('tag')} ({card.backend}, {card.mode}) · k={card.retrieval.get('k')} · scope={card.retrieval.get('scope')}", ""]
    lines.append(card.answer.get("text") or "(the model returned nothing)")
    lines.append("")
    if card.citations:
        lines.append("Sources:")
        for c in card.citations:
            if c["valid"]:
                lines.append(f"  [{c['n']}] {c['path']} # {c['heading']} (lines {c['lines'][0]}-{c['lines'][1]})")
            else:
                lines.append(f"  [{c['n']}] (not one of the retrieved passages)")
    if card.status == "unsupported":
        lines.append("warning: the answer cites nothing from the retrieved passages; treat it as unverified.")
    if card.citation_check.get("unverified_numbers"):
        lines.append(f"note: numbers not found in the cited passages: {', '.join(card.citation_check['unverified_numbers'])}")
    t, mem = card.timing, card.memory
    rate = f" at {t.get('tokens_per_s')} tok/s" if t.get("tokens_per_s") else ""
    memo = f"; ollama {mem['ollama_model_size_bytes'] / 1e9:.1f} GB" if mem.get("ollama_model_size_bytes") else ""
    lines.append(f"status: {card.status} · {t.get('wall_s'):.1f} s, {t.get('eval_count') or 0} generated tokens{rate}{memo}")
    return "\n".join(lines)
