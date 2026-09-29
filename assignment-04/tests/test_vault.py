from personal_wiki.frontmatter import render_frontmatter, split_frontmatter
from personal_wiki.vault import (disambiguate_title, find_existing_title, linkify_related, list_notes, list_source_notes, normalize_title,
                                 resolve_links, validate_title, write_index_md, write_note, write_source_note, SourceSpec)


def test_frontmatter_roundtrip():
    data = {"title": "Memory: Computers", "reviewed": False, "count": 3, "created": "2026-09-29", "sources": ["raw/x.md", "raw/y.md"],
            "custom": "keep me", "empty": [], "hash": "a value with # in it"}
    text = render_frontmatter(data) + "body\n"
    parsed, body, n = split_frontmatter(text)
    assert parsed == data and body == "body\n" and n == text.count("\n") - 1


def test_validate_title():
    for good in ("Pac-Man DQN Training", "Next.js Auth Proxy", "Memory - Computers", "Class 5 Retrieval Notes"):
        assert validate_title(good)[0], good
    for bad in ("a1b2c3d4e5f6 notes", "2026-09-29 notes", "Note 20260929", "Everything I learned about training the agent this week",
                "Training", "index", "Pac/Man DQN", "", "Notes: on things"):
        assert not validate_title(bad)[0], bad


def test_normalize_title():
    assert normalize_title("Pac-Man DQN: Training.") == "Pac-Man DQN Training"
    assert normalize_title('"Networking Tracker Security"') == "Networking Tracker Security"
    assert normalize_title("# Custom LLM Evals.md") == "Custom LLM Evals"


def test_find_existing_title_fuzzy():
    existing = ["Pac-Man DQN Training", "Networking Tracker Security"]
    assert find_existing_title("pac man dqn training", existing) == "Pac-Man DQN Training"
    assert find_existing_title("Pac-Man DQN Training Run", existing) == "Pac-Man DQN Training"
    assert find_existing_title("Custom LLM Evals", existing) is None


def test_disambiguate_title():
    assert disambiguate_title("Training Budget", "Custom LLM README", ["Training Budget"]) == "Training Budget Custom"
    assert disambiguate_title("Fresh Title", "Custom LLM README", ["Training Budget"]) == "Fresh Title"


def test_linkify_related_only_allowed():
    lines = linkify_related([("Known Note", "why one"), ("Ghost Note", "why two"), ("known note", "again")], {"Known Note"})
    assert lines == ["- [[Known Note]]: why one"]


def test_write_index_md_grouping_and_order(tmp_vault):
    write_note(tmp_vault / "wiki/Projects/Zeta Project.md", {"title": "Zeta Project", "summary": "Last by name."}, "# Zeta Project\n")
    write_note(tmp_vault / "wiki/Projects/Alpha Project.md", {"title": "Alpha Project", "summary": "First by name."}, "# Alpha Project\n")
    write_note(tmp_vault / "wiki/Course/Class Notes Here.md", {"title": "Class Notes Here", "summary": "Course stuff."}, "# Class Notes Here\n")
    spec = SourceSpec("Garden Sensor Log", "raw/Garden Sensor Log.md", "garden-sensor-log", "ab" * 32, "notes/garden.md", "2026-09-29",
                      notes=[("Alpha Project", "First by name.")], sections=[("Setup", 5, 7, "Alpha Project")])
    write_source_note(tmp_vault, spec)
    write_index_md(tmp_vault, list_notes(tmp_vault), list_source_notes(tmp_vault), "fake-gemma", "2026-09-29T00:00:00Z")
    text = (tmp_vault / "index.md").read_text()
    assert text.index("## Projects") < text.index("## Concepts") < text.index("## Course") < text.index("## Sources")
    assert text.index("[[Alpha Project]]") < text.index("[[Zeta Project]]")
    assert "_No notes yet._" in text.split("## Concepts")[1].split("## Course")[0]
    assert "[[wiki/Sources/Garden Sensor Log|Garden Sensor Log]]: copied from `notes/garden.md`, 1 note" in text
    source_text = (tmp_vault / "wiki/Sources/Garden Sensor Log.md").read_text()
    assert "[[raw/Garden Sensor Log|raw/Garden Sensor Log.md]]" in source_text and "Setup (lines 5-7), in [[Alpha Project]]" in source_text
    resolved, dangling = resolve_links(tmp_vault, source_text)
    assert dangling == [] and "Alpha Project" in resolved
