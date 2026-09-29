import json

from personal_wiki.backends.fake import FakeBackend
from personal_wiki.chat import ChatSession, parse_script, run_chat, trim_history
from personal_wiki.index import build_index


def make_session(fake_settings, fake_backend):
    index = build_index(fake_settings.vault, fake_settings.index_dir)
    return ChatSession(fake_settings, fake_backend, index)


def test_route_capability_skips(fake_settings, fake_backend):
    r = make_session(fake_settings, fake_backend).route("what can you help me with?")
    assert r.decision == "skip" and r.source == "rule"
    assert make_session(fake_settings, fake_backend).route("What can we do?").decision == "skip"


def test_route_followup_skips_only_with_history(fake_settings, fake_backend):
    s = make_session(fake_settings, fake_backend)
    assert "follow-up" not in s.route("Make that shorter.").reason
    s.history = [{"role": "user", "content": "plan"}, {"role": "assistant", "content": "a plan"}]
    r = s.route("Make that shorter.")
    assert r.decision == "skip" and "follow-up" in r.reason


def test_route_notes_cue_retrieves(fake_settings, fake_backend):
    r = make_session(fake_settings, fake_backend).route("What learning rate did I use for the DQN?")
    assert r.decision == "retrieve" and "did i" in r.reason.lower()


def test_route_slash_commands(fake_settings, fake_backend):
    s = make_session(fake_settings, fake_backend)
    assert s.route("/notes sensor install").decision == "retrieve"
    assert s.route("/search sensor").decision == "search"
    assert s.route("/quit").decision == "command"


def test_route_model_and_fallback(fake_settings, fake_backend):
    s = make_session(fake_settings, fake_backend)
    r = s.route("Where does the probe report its readings?")
    assert r.decision == "retrieve" and r.source == "model"

    class BadJson(FakeBackend):
        def generate(self, messages, *, kind, **kw):
            c = super().generate(messages, kind=kind, **kw)
            if kind == "route":
                c.text = "not json at all"
            return c

    s2 = ChatSession(fake_settings, BadJson(), s.index)
    r2 = s2.route("Where does the probe report its readings?")
    assert r2.source == "fallback" and r2.decision == "retrieve"
    assert s2.route("Nothing to ask here").decision == "skip"


def test_passage_block_not_stored_in_history_and_cited(fake_settings, fake_backend):
    s = make_session(fake_settings, fake_backend)
    turn = s.run_turn("/notes When was the sensor installed?")
    assert turn["retrieved"] and turn["citations"] and turn["citations"][0]["valid"]
    assert "March" in turn["assistant"]
    assert not any("=== Retrieved notes" in m["content"] for m in s.history)
    assert s.history[0]["content"].endswith(")") and "(notes consulted this turn:" in s.history[0]["content"]


def test_history_trimmed():
    history = []
    for i in range(15):
        history += [{"role": "user", "content": "u" * 2000}, {"role": "assistant", "content": "a" * 2000}]
    kept = trim_history(history)
    assert len(kept) <= 20 and sum(len(m["content"]) for m in kept) <= 12000 and kept[-1]["role"] == "assistant"


def test_script_expectations_recorded(tmp_path, fake_settings, fake_backend, capsys):
    script = tmp_path / "checks.txt"
    script.write_text("# expect: retrieval=no\nwhat can you help me with?\n# expect: retrieval=no\nWrite a plan for tomorrow.\n"
                      "# expect: retrieval=no\nMake that shorter.\n# expect: retrieval=yes cite=March\n/notes When was the sensor installed?\n")
    assert len(parse_script(script)) == 4
    index = build_index(fake_settings.vault, fake_settings.index_dir)
    transcript = run_chat(fake_settings, fake_backend, index, script=script, name="checks")
    assert len(transcript.turns) == 4
    assert all(t["expect"] for t in transcript.turns)
    assert all(t["check"]["retrieval_ok"] for t in transcript.turns)
    assert transcript.turns[3]["check"]["cite_ok"] is True
    assert transcript.turns[2]["assistant"].startswith("Suggestion:") and len(transcript.turns[2]["assistant"]) < len(transcript.turns[1]["assistant"])
    data = json.loads((fake_settings.run_dir / "chat" / "checks.json").read_text())
    assert data["checks"] == {"total": 5, "passed": 5}
    assert (fake_settings.run_dir / "chat" / "checks.md").exists()
    out = capsys.readouterr().out
    assert "You: what can you help me with?" in out and "[retrieval: skip" in out
