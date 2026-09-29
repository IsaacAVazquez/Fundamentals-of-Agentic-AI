from personal_wiki.chunking import chunk_file, chunk_markdown, collect_vault_files, split_sections
from personal_wiki.config import PASSAGE_MAX_CHARS, PASSAGE_MIN_CHARS
from personal_wiki.vault import write_note


def test_headings_split_and_heading_path(tmp_vault):
    passages = chunk_file(tmp_vault, "raw/Garden Sensor Log.md")
    headings = {p.heading_path for p in passages}
    assert ("Garden Sensor Log", "Setup") in headings
    setup = next(p for p in passages if p.heading == "Setup")
    lines = (tmp_vault / "raw/Garden Sensor Log.md").read_text().split("\n")
    assert lines[setup.start_line - 1].startswith("The sensor is a capacitive probe")
    assert setup.end_line >= setup.start_line
    assert all(p.path == "raw/Garden Sensor Log.md" and p.kind == "raw" for p in passages)


def test_hash_lines_in_fences_are_not_headings(tmp_vault):
    passages = chunk_file(tmp_vault, "raw/Garden Sensor Log.md")
    assert not any("not a heading" in p.heading for p in passages)
    problems = [p for p in passages if p.heading == "Problems"]
    assert problems and any("# not a heading" in p.text for p in problems)


def test_long_paragraph_is_sentence_split(tmp_vault):
    passages = [p for p in chunk_file(tmp_vault, "raw/Garden Sensor Log.md") if p.heading == "Next steps"]
    assert len(passages) >= 2
    assert all(len(p.text) <= PASSAGE_MAX_CHARS for p in passages)
    joined = " ".join(p.text for p in passages)
    assert "second probe" in joined and "hard to reproduce two weeks later" in joined


def test_table_kept_whole(tmp_vault):
    readings = [p for p in chunk_file(tmp_vault, "raw/Garden Sensor Log.md") if p.heading == "Readings"]
    assert len(readings) == 1
    assert "| 3 | 52% | 1 |" in readings[0].text and "| Week |" in readings[0].text


def test_short_tail_merges():
    text = "# T\n\n## S\n\n" + ("A sentence of text here. " * 30).strip() + "\n\nShort tail.\n"
    passages = chunk_markdown(text, "raw/x.md", "raw")
    assert len(passages) == 1
    assert passages[0].text.endswith("Short tail.")
    assert len(passages[0].text) <= PASSAGE_MAX_CHARS + PASSAGE_MIN_CHARS


def test_verbatim_text_and_line_numbers(tmp_vault):
    lines = (tmp_vault / "raw/Bike Commute Notes.md").read_text().split("\n")
    for p in chunk_file(tmp_vault, "raw/Bike Commute Notes.md"):
        original = "\n".join(lines[p.start_line - 1:p.end_line])
        assert p.text in original


def test_wiki_note_frontmatter_stripped_and_sources_dropped(tmp_vault):
    fm = {"title": "Sensor Setup", "summary": "How the probe was installed.", "topic": "Projects"}
    body = "# Sensor Setup\n\n## Summary\n\nThe probe went into the raised bed.\n\n## Sources\n\n- [[wiki/Sources/Garden Sensor Log|Garden Sensor Log]]\n"
    write_note(tmp_vault / "wiki/Projects/Sensor Setup.md", fm, body)
    passages = chunk_file(tmp_vault, "wiki/Projects/Sensor Setup.md")
    assert passages and all(p.kind == "wiki" for p in passages)
    assert not any("title:" in p.text for p in passages)
    assert not any(p.heading == "Sources" for p in passages)
    assert "How the probe was installed." in passages[0].extra_terms
    assert "wiki/Projects/Sensor Setup.md" in collect_vault_files(tmp_vault)


def test_split_sections_levels():
    sections = split_sections("intro\n# A\ntext\n## B\nmore\n### C\ndeep\n#### D stays in body\n## E\n".split("\n"))
    paths = [s.heading_path for s in sections]
    assert paths == [(), ("A",), ("A", "B"), ("A", "B", "C"), ("A", "E")]
    assert "#### D stays in body" in sections[3].body_lines
