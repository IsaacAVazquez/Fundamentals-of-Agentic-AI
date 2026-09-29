"""Chat mode: the personal assistant. Conversation context, a persona, and retrieval only when a turn needs it.

The harness decides whether to retrieve: deterministic rules first (slash commands,
capability questions, follow-ups, explicit notes cues), then a tiny routing call to the
model when the rules cannot tell. Retrieved passages are attached to the current turn as
evidence and are not kept in the stored history.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .ask import parse_citations
from .config import CHAT_HISTORY_CHARS, CHAT_HISTORY_TURNS, CHAT_PASSAGE_BUDGET, NUM_PREDICT, Settings, utc_now_iso
from .errors import BackendError, UsageError
from .evidence import Transcript, write_transcript
from .prompts import ROUTE_SCHEMA, build_chat_messages, build_route_messages, file_sha256, load_instruction_file
from .retrieval import format_passages, search, select_for_prompt
from .textutil import content_terms

CAPABILITY_RE = re.compile(r"what can you (do|help)|what do you do|who are you|what are you|which commands|what commands|"
                           r"how do i use|help me with\?$|what can we do|^(hi|hello|hey|thanks|thank you)\b", re.I)
FOLLOWUP_RE = re.compile(r"^(make|say|do|write|put) (that|it|this)\b|^(shorter|longer|simpler|again|rephrase|rewrite|expand|"
                         r"summari[sz]e (that|it)|as a list|in one sentence|tighten|condense)|"
                         r"(your|that|the) (last|previous) (answer|reply|plan|draft)", re.I)
NOTES_CUE_RE = re.compile(r"\bmy (notes|wiki|vault|readme|assignments?|projects?|runs?|agent|model|results?|write-?ups?)\b|"
                          r"according to (my|the) (notes|wiki)|\bdid i\b|\bin (my|the) (notes|wiki)\b|\bhave i\b|\bi (used|trained|built|chose|picked)\b", re.I)
WH_RE = re.compile(r"^(what|which|when|where|who|how|why)\b", re.I)


@dataclass
class Routing:
    decision: str      # retrieve | skip | search | command
    source: str        # rule | model | fallback
    reason: str
    query: str = ""

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def parse_script(path: Path) -> list:
    """Messages one per line. `# expect: retrieval=yes cite=946` attaches expectations to the next message."""
    if not path.exists():
        raise UsageError(f"--script file {path} not found.")
    items, pending = [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            m = re.match(r"#\s*expect:\s*(.*)$", line, re.I)
            if m:
                pending = dict(kv.split("=", 1) for kv in m.group(1).split() if "=" in kv)
            continue
        items.append((line, pending))
        pending = None
    return items


def trim_history(history: list, max_turns: int = CHAT_HISTORY_TURNS, max_chars: int = CHAT_HISTORY_CHARS) -> list:
    kept = history[-2 * max_turns:]
    while kept and sum(len(m["content"]) for m in kept) > max_chars:
        kept = kept[2:] if len(kept) >= 2 else []
    return kept


class ChatSession:
    def __init__(self, settings: Settings, backend, index, retrieval_enabled: bool = True):
        self.settings = settings
        self.backend = backend
        self.index = index
        self.retrieval_enabled = retrieval_enabled
        self.persona = load_instruction_file(settings.persona_file, "persona")
        self.persona_sha = file_sha256(settings.persona_file)
        self.history: list = []
        self.turns: list = []

    # routing ------------------------------------------------------------------------
    def route(self, message: str) -> Routing:
        text = message.strip()
        low = text.lower()
        if low in ("/quit", "/exit", "/reset", "/history", "/help"):
            return Routing("command", "rule", "command", "")
        if low.startswith("/search "):
            return Routing("search", "rule", "slash command /search", text[8:].strip())
        if low.startswith("/notes "):
            return Routing("retrieve", "rule", "slash command /notes", text[7:].strip())
        if not self.retrieval_enabled:
            return Routing("skip", "rule", "retrieval disabled with --no-retrieval")
        if CAPABILITY_RE.search(low):
            return Routing("skip", "rule", "capability or greeting question")
        cue = NOTES_CUE_RE.search(text)
        if self.history and len(text.split()) <= 12 and FOLLOWUP_RE.search(low) and not cue:
            return Routing("skip", "rule", "follow-up on the previous reply")
        if cue:
            return Routing("retrieve", "rule", f"notes cue \"{cue.group(0)}\"", text)
        last_reply = next((m["content"] for m in reversed(self.history) if m["role"] == "assistant"), "")
        try:
            completion = self.backend.generate(build_route_messages(text, last_reply), kind="route", json_schema=ROUTE_SCHEMA,
                                               temperature=0.0, num_predict=NUM_PREDICT["route"], num_ctx=self.settings.num_ctx,
                                               seed=self.settings.seed)
            data = json.loads(completion.text)
            retrieve = bool(data.get("retrieve"))
            query = str(data.get("query") or "").strip() or text
            return Routing("retrieve" if retrieve else "skip", "model", "routing call", query if retrieve else "")
        except (json.JSONDecodeError, TypeError, AttributeError, BackendError):
            wants = text.endswith("?") or bool(WH_RE.match(text))
            if wants and len(content_terms(text)) >= 3:
                return Routing("retrieve", "fallback", "routing call unusable; question with enough content words", text)
            return Routing("skip", "fallback", "routing call unusable; not a question about the notes")

    # one turn -----------------------------------------------------------------------
    def run_turn(self, message: str, expect: dict | None = None) -> dict:
        routing = self.route(message)
        turn = {"i": len(self.turns) + 1, "user": message, "routing": routing.to_dict(), "retrieved": [], "assistant": "",
                "citations": [], "timing": None, "memory": None, "expect": expect, "check": None}
        if routing.decision == "command":
            turn["assistant"] = self._command(message.strip().lower())
            self.turns.append(turn)
            return turn
        hits = []
        if routing.decision in ("retrieve", "search"):
            hits = select_for_prompt(search(self.index, routing.query, k=self.settings.k, scope=self.settings.scope), CHAT_PASSAGE_BUDGET)
            turn["retrieved"] = [h.to_dict(include_text=False) for h in hits]
        if routing.decision == "search":
            turn["assistant"] = format_passages(hits) if hits else "No passages matched."
            self.turns.append(turn)
            return turn
        messages = build_chat_messages(self.persona, trim_history(self.history), message, hits)
        completion = self.backend.generate(messages, kind="chat", temperature=0.2, num_predict=NUM_PREDICT["chat"],
                                           num_ctx=self.settings.num_ctx, seed=self.settings.seed)
        reply = completion.text.strip()
        by_rank = {h.rank: h for h in hits}
        for n in parse_citations(reply):
            h = by_rank.get(n)
            turn["citations"].append({"n": n, "valid": h is not None, "path": h.passage.path if h else None,
                                      "heading": h.passage.heading if h else None})
        turn["assistant"] = reply
        turn["timing"] = completion.timing.to_dict()
        turn["memory"] = completion.memory.to_dict()
        stored_user = message
        if hits:
            stored_user += "\n(notes consulted this turn: " + ", ".join(f"[{h.rank}] {h.passage.path}" for h in hits) + ")"
        self.history += [{"role": "user", "content": stored_user}, {"role": "assistant", "content": reply}]
        if expect:
            turn["check"] = self._check(expect, routing, reply, turn["citations"])
        self.turns.append(turn)
        return turn

    @staticmethod
    def _check(expect: dict, routing: Routing, reply: str, citations: list) -> dict:
        check: dict = {"retrieval_ok": None, "cite_ok": None}
        want = expect.get("retrieval")
        if want in ("yes", "no"):
            check["retrieval_ok"] = (routing.decision == "retrieve") == (want == "yes")
        if expect.get("cite"):
            check["cite_ok"] = expect["cite"] in reply and any(c["valid"] for c in citations)
        return check

    def _command(self, low: str) -> str:
        if low == "/reset":
            self.history.clear()
            return "Conversation cleared."
        if low == "/history":
            return "\n".join(f"{m['role']}: {m['content'][:120]}" for m in self.history) or "(no history)"
        if low == "/help":
            return ("/notes <question> looks it up in the notes; /search <words> prints matching passages; "
                    "/reset clears the conversation; /history shows it; /quit exits.")
        return "Bye."


def _print_turn(turn: dict, verbose: bool) -> None:
    r = turn["routing"]
    print(f"Assistant: {turn['assistant']}")
    if turn["retrieved"]:
        print("  [retrieved " + "; ".join(f"[{p['n']}] {p['path']} # {p['heading']}" for p in turn["retrieved"]) + "]")
    else:
        print(f"  [retrieval: {r['decision']} ({r['source']}: {r['reason']})]")
    if turn.get("timing"):
        t = turn["timing"]
        rate = f" at {t.get('tokens_per_s')} tok/s" if t.get("tokens_per_s") else ""
        print(f"  [{t['wall_s']:.1f} s, {t.get('eval_count') or 0} generated tokens{rate}]")
    print()


def run_chat(settings: Settings, backend, index, script: Path | None = None, name: str | None = None,
             retrieval_enabled: bool = True) -> Transcript:
    session = ChatSession(settings, backend, index, retrieval_enabled)
    info = backend.model_info()
    transcript = Transcript(settings.run_id, str(script) if script else None, info.to_dict(), session.persona_sha, utc_now_iso())
    print(f"wiki chat · model {info.tag} ({backend.name}, local) · type /help for commands, /quit to exit")
    print()
    items = parse_script(script) if script else None
    try:
        while True:
            if items is not None:
                if not items:
                    break
                message, expect = items.pop(0)
                print(f"You: {message}")
            else:
                try:
                    message = input("You: ").strip()
                except EOFError:
                    break
                expect = None
                if not message:
                    continue
            if message.strip().lower() in ("/quit", "/exit"):
                break
            turn = session.run_turn(message, expect)
            _print_turn(turn, settings.verbose)
    except KeyboardInterrupt:
        print("\nStopped.")
    transcript.turns = session.turns
    transcript.ended_at = utc_now_iso()
    checks = [v for t in session.turns for v in (t.get("check") or {}).values() if v is not None]
    transcript.checks = {"total": len(checks), "passed": sum(1 for v in checks if v)}
    if settings.save:
        tname = name or (Path(script).stem if script else "chat-" + transcript.started_at.replace(":", "").replace("-", ""))
        jp, mp = write_transcript(settings.run_dir, transcript, tname)
        print(f"Saved transcript: {mp}", file=sys.stderr)
    return transcript
