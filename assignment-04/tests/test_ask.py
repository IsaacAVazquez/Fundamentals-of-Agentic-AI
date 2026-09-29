import inspect
import json

from personal_wiki import cli
from personal_wiki.ask import detect_insufficient, parse_citations, run_ask, unverified_numbers
from personal_wiki.index import build_index


def test_parse_citations_forms():
    assert parse_citations("a [1]. b [2][3]. c [4, 5] and [1,6]") == [1, 2, 3, 4, 5, 6]
    assert parse_citations("no citations here") == []


def test_detect_insufficient():
    assert detect_insufficient("**Insufficient evidence:** nothing says so.")
    assert detect_insufficient("Insufficient Evidence: the passages do not mention it")
    assert not detect_insufficient("Evidence is insufficient for this.")


def test_unverified_numbers():
    assert unverified_numbers("averaged 946 against 492 [1]", ["it scored 492 points"]) == ["946"]
    assert unverified_numbers("1,033 games [1]", ["1033 games"]) == []


def test_ask_ignores_history_by_construction():
    assert "history" not in inspect.signature(run_ask).parameters


def test_status_rules_and_card_files(tmp_vault, tmp_path, fake_settings, fake_backend):
    index = build_index(tmp_vault, fake_settings.index_dir)
    card = run_ask(fake_settings, "When was the sensor installed in the raised bed?", fake_backend, index, card_id="Q1")
    assert card.status == "supported" and card.citations and card.citations[0]["valid"]
    assert card.citations[0]["path"] == "raw/Garden Sensor Log.md"
    assert card.mode == "local" and card.model["tag"] == "fake-gemma"
    jp = fake_settings.run_dir / "ask" / "Q1.json"
    mp = fake_settings.run_dir / "ask" / "Q1.md"
    assert jp.exists() and mp.exists()
    data = json.loads(jp.read_text())
    for key in ("question", "retrieval", "prompt", "answer", "citations", "citation_check", "status", "timing", "memory", "offline"):
        assert key in data
    assert "## Citation check" in mp.read_text()
    assert data["prompt"]["passages_sent"] >= 1 and data["retrieval"]["passages"][0]["sent_to_model"]
    card2 = run_ask(fake_settings, "What grade did the sensor project receive?", fake_backend, index, card_id="Q2")
    assert card2.status == "insufficient" and card2.citations == []


def test_only_system_and_one_user_message_reach_the_model(tmp_vault, fake_settings, fake_backend):
    index = build_index(tmp_vault, fake_settings.index_dir)
    seen = {}
    original = fake_backend.generate

    def spy(messages, **kw):
        seen["messages"] = messages
        return original(messages, **kw)

    fake_backend.generate = spy
    run_ask(fake_settings, "When was the sensor installed?", fake_backend, index, card_id="Q3")
    assert [m["role"] for m in seen["messages"]] == ["system", "user"]


def test_online_mode_refused(tmp_vault, tmp_path, capsys):
    code = cli.main(["--backend", "fake", "--vault", str(tmp_vault), "--results-dir", str(tmp_path / "r"), "--index-dir", str(tmp_path / "i"),
                     "ask", "--mode", "online", "anything"])
    assert code == 2
    assert "not built" in capsys.readouterr().err
