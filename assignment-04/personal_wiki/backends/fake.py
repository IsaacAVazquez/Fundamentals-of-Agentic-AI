"""A deterministic stand-in for Gemma so the harness can be tested without a model.

It answers extractively from the text it is given, never from outside knowledge, and it
returns valid JSON for the plan and routing prompts. It exists for pytest and for dry
runs in an environment without Ollama; it is never the graded model.
"""
from __future__ import annotations

import json
import math
import re
import time

from ..config import utc_now_iso
from ..errors import BackendError
from ..textutil import STOPWORDS, estimate_tokens, split_sentences, stem, tokenize
from .base import Backend, Completion, MemorySnapshot, ModelInfo, Timing, harness_max_rss_bytes

PASSAGE_HEADER = re.compile(r"^\[(\d+)\] (.+?) # (.*?) \(lines (\d+)-(\d+)\)$", re.MULTILINE)
CAPABILITY = re.compile(r"what can you (do|help)|what do you do|who are you|what are you|which commands|what commands|how do i use", re.I)
CAPABILITY_TEXT = ("I am the wiki assistant for your course notes. I can brainstorm, draft, and plan with you, look things up "
                   "in your notes when a question needs them (or when you use /notes), and show original passages with /search; "
                   "wiki ask gives standalone cited answers and wiki search shows passages without the model. "
                   "Suggestion: start with /notes and a question about one of your assignments.")
PLAN_TEXT = ("Suggestion: 1) Reread the assignment brief and list what is missing. 2) Run the offline demo and read every "
             "evidence card. 3) Fill the README numbers from the results files before pushing.")


def _content_stems(text: str) -> list:
    return [stem(t) for t in tokenize(text) if t not in STOPWORDS and not t[0].isdigit() and len(t) >= 3]


def _sanitize_words(text: str) -> list:
    words = []
    for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9'&+.-]*", text):
        w = w.strip(".-'")
        if w and not w.isdigit():
            words.append(w)
    return words


class FakeBackend(Backend):
    name = "fake"

    def __init__(self, model: str = "fake-gemma"):
        self.model = model

    def model_info(self) -> ModelInfo:
        return ModelInfo("fake", self.model, "sha256:" + "0" * 64, "0B", "none", "fake", 8192, None, 0)

    def check(self) -> tuple:
        return True, "fake backend: deterministic, no model loaded"

    def generate(self, messages: list, *, kind: str, json_schema: dict | None = None, temperature: float = 0.0,
                 num_predict: int = 400, num_ctx: int = 8192, seed: int = 0, timeout_s: float = 600) -> Completion:
        start = time.perf_counter()
        user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        handlers = {"ask": self._ask, "chat": self._chat, "route": self._route, "plan": self._plan, "note": self._note}
        if kind not in handlers:
            raise BackendError(f"fake backend has no handler for kind {kind!r}")
        text = handlers[kind](user, messages)
        wall = max(time.perf_counter() - start, 0.001)
        prompt_chars = sum(len(m["content"]) for m in messages)
        timing = Timing(wall, wall, 0.0, estimate_tokens("x" * prompt_chars), wall / 2, estimate_tokens(text), wall / 2)
        memory = MemorySnapshot(None, None, None, harness_max_rss_bytes(), utc_now_iso())
        return Completion(text, {"fake": True, "kind": kind}, self.model_info(), timing, memory, kind, json_schema is not None)

    # ask ------------------------------------------------------------------------------
    @staticmethod
    def _parse_passages(user: str) -> list:
        headers = list(PASSAGE_HEADER.finditer(user))
        passages = []
        end_of_block = user.find("\nQuestion:")
        for i, m in enumerate(headers):
            stop = headers[i + 1].start() if i + 1 < len(headers) else (end_of_block if end_of_block > 0 else len(user))
            passages.append({"n": int(m.group(1)), "path": m.group(2), "heading": m.group(3),
                             "text": user[m.end():stop].strip()})
        return passages

    def _ask(self, user: str, messages: list) -> str:
        passages = self._parse_passages(user)
        qm = re.search(r"^Question: (.*)$", user, re.M)
        question = qm.group(1) if qm else ""
        q_stems = sorted(set(_content_stems(question)))
        if not passages or not q_stems:
            return "Insufficient evidence: no passages were retrieved for this question."
        scored = []
        for p in passages:
            stems = set(_content_stems(p["heading"] + " " + p["text"]))
            hits = [s for s in q_stems if s in stems]
            scored.append((len(hits), -p["n"], p, hits))
        scored.sort(reverse=True)
        best_count, _, best, _ = scored[0]
        if best_count < 2:
            counts = {s: sum(1 for p in passages if s in set(_content_stems(p["text"]))) for s in q_stems}
            rare = sorted(q_stems, key=lambda s: (counts[s], s))[:2]
            return f"Insufficient evidence: none of the retrieved passages mention {' or '.join(rare)}."
        answer = self._best_sentences(best["text"], q_stems, 2) + f" [{best['n']}]"
        for count, _, other, _ in scored[1:]:
            if count >= 2 and other["path"] != best["path"]:
                answer += " " + self._best_sentences(other["text"], q_stems, 1) + f" [{other['n']}]"
                break
        return answer

    @staticmethod
    def _best_sentences(text: str, q_stems: list, n: int) -> str:
        sentences = split_sentences(text.replace("\n", " ")) or [text]
        ranked = sorted(sentences, key=lambda s: (-len(set(_content_stems(s)) & set(q_stems)), sentences.index(s)))
        chosen = sorted(ranked[:n], key=sentences.index)
        return " ".join(chosen)[:400].strip()

    # chat -----------------------------------------------------------------------------
    def _chat(self, user: str, messages: list) -> str:
        if "=== Retrieved notes" in user:
            passages = self._parse_passages(user.split("=== Retrieved notes", 1)[1])
            if passages:
                first = split_sentences(passages[0]["text"].replace("\n", " "))
                return f"From your notes: {(first[0] if first else passages[0]['text'])[:300]} [{passages[0]['n']}]"
            return "The retrieved notes do not cover that."
        if CAPABILITY.search(user):
            return CAPABILITY_TEXT
        if re.match(r"^\s*(make|say) (that|it) shorter", user, re.I):
            last = next((m["content"] for m in reversed(messages) if m["role"] == "assistant"), "")
            sentences = split_sentences(last)
            return sentences[0] if sentences else "There is no previous reply to shorten."
        if "plan" in user.lower():
            return PLAN_TEXT
        return "Noted. I have not checked that against your notes, so I am treating it as something you told me."

    # routing --------------------------------------------------------------------------
    def _route(self, user: str, messages: list) -> str:
        m = re.search(r'^Message: "(.*)"$', user, re.M | re.S)
        message = m.group(1) if m else user
        retrieve = message.strip().endswith("?") and len(_content_stems(message)) >= 2
        return json.dumps({"retrieve": retrieve, "query": message if retrieve else ""})

    # ingest plan ----------------------------------------------------------------------
    def _plan(self, user: str, messages: list) -> str:
        source = re.search(r"^Source file: (.*)$", user, re.M)
        source_name = source.group(1) if source else "Source"
        doc_title = re.search(r"^Document title: (.*)$", user, re.M)
        doc_title = doc_title.group(1) if doc_title else source_name
        max_m = re.search(r"^Maximum notes: (\d+)$", user, re.M)
        max_notes = int(max_m.group(1)) if max_m else 5
        outline = user.split("Outline:", 1)[1] if "Outline:" in user else ""
        headings = [(len(m.group(1)), m.group(2).strip()) for m in re.finditer(r"^(#{1,3}) (.+?)(?: — .*)?$", outline, re.M)]
        h2 = [h for lvl, h in headings if lvl == 2]
        if not h2:
            h2 = [h for lvl, h in headings if lvl in (1, 3)] or [doc_title]
        n_groups = min(max_notes, max(2, math.ceil(len(h2) / 3)))
        size = math.ceil(len(h2) / n_groups)
        groups = [h2[i:i + size] for i in range(0, len(h2), size)][:n_groups]
        h1 = [h for lvl, h in headings if lvl == 1]
        titles, notes = [], []
        for gi, group in enumerate(groups):
            words = _sanitize_words(doc_title)[:3] + _sanitize_words(group[0])[:3]
            title = " ".join(words[:6])
            if len(title.split()) < 2:
                title = f"{title} Notes"
            if title in titles:
                title = f"{title} {gi + 1}"
            titles.append(title)
            sections = list(group)
            if gi == 0 and h1:
                sections = h1[:1] + sections
            for lvl, h in headings:
                if lvl == 3 and any(h.startswith(g) for g in []):
                    sections.append(h)
            folder = "Course" if "class" in source_name.lower() else "Projects"
            if len(groups) >= 3 and gi == len(groups) - 1:
                folder = "Concepts"
            summary = " ".join(("Covers " + ", ".join(group[:3]) + ".").split()[:25])
            related = [{"title": titles[gi - 1], "why": "adjacent sections of the same source"}] if gi > 0 else []
            notes.append({"title": title, "folder": folder, "summary": summary, "sections": sections, "related": related})
        return json.dumps({"notes": notes})

    # ingest note ----------------------------------------------------------------------
    def _note(self, user: str, messages: list) -> str:
        allowed_m = re.search(r"^Allowed related titles: (.*)$", user, re.M)
        allowed = [] if not allowed_m or allowed_m.group(1).strip() == "(none)" else [t.strip() for t in allowed_m.group(1).split(";") if t.strip()]
        text = user.split("Source text:\n", 1)[1] if "Source text:\n" in user else user
        paragraphs, in_fence = [], False
        for para in re.split(r"\n\s*\n", text):
            lines = [l for l in para.split("\n")]
            if any(l.startswith("```") for l in lines):
                in_fence = not in_fence if sum(l.startswith("```") for l in lines) % 2 else in_fence
                continue
            if in_fence:
                continue
            keep = [l for l in lines if l.strip() and not l.lstrip().startswith(("|", "<", "#", "![", "```"))]
            if keep:
                paragraphs.append(" ".join(keep).strip())
        first = paragraphs[0] if paragraphs else "This note has no prose paragraphs in its source sections."
        summary = " ".join(split_sentences(first)[:2]) or first
        details, used = [], 0
        for para in paragraphs:
            if used + len(para) > 1500:
                break
            details.append(para)
            used += len(para)
        body = "## Summary\n" + summary + "\n\n## Details\n" + "\n\n".join(details or [first]) + "\n\n## Related\n"
        if allowed:
            body += f"- {allowed[0]}: adjacent sections of the same source\n"
        return body
