from personal_wiki.chunking import split_sections
from personal_wiki.index import build_index
from personal_wiki.ingest import validate_plan
from personal_wiki.prompts import PLAN_SCHEMA, build_ask_messages, build_plan_messages, outline_for_plan
from personal_wiki.retrieval import search


def test_fake_plan_is_valid_json_plan(tmp_vault, fake_backend):
    text = (tmp_vault / "raw/Garden Sensor Log.md").read_text()
    sections = split_sections(text.split("\n"))
    messages = build_plan_messages("Garden Sensor Log.md", "Garden Sensor Log", outline_for_plan(sections, 6000), [], [], 5)
    reply = fake_backend.generate(messages, kind="plan", json_schema=PLAN_SCHEMA).text
    plan, problems = validate_plan(reply, sections, [], [], "Garden Sensor Log.md", 5, "garden-sensor-log", {})
    assert plan is not None and len(plan.notes) >= 2
    assert all(n.sections for n in plan.notes)


def test_fake_ask_supported_and_insufficient(tmp_vault, tmp_path, fake_backend):
    index = build_index(tmp_vault, tmp_path / "index")
    q = "When was the sensor installed in the raised bed?"
    reply = fake_backend.generate(build_ask_messages("rules", search(index, q, k=4), q), kind="ask").text
    assert "March 3" in reply and "[1]" in reply
    q2 = "What grade did the sensor project receive?"
    reply2 = fake_backend.generate(build_ask_messages("rules", search(index, q2, k=4), q2), kind="ask").text
    assert reply2.startswith("Insufficient evidence:")


def test_fake_is_deterministic(fake_backend):
    messages = [{"role": "system", "content": "s"}, {"role": "user", "content": "what can you help me with?"}]
    assert fake_backend.generate(messages, kind="chat").text == fake_backend.generate(messages, kind="chat").text
