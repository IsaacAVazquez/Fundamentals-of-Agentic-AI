import time

from personal_wiki.chunking import Passage
from personal_wiki.index import build_index, ensure_index, load_index, vault_fingerprint
from personal_wiki.retrieval import Hit, expand_query, search, select_for_prompt


def test_bm25_ranks_matching_passage_first(tmp_vault, tmp_path):
    index = build_index(tmp_vault, tmp_path / "index")
    hits = search(index, "capacitive probe microcontroller", k=3)
    assert hits[0].passage.path == "raw/Garden Sensor Log.md" and hits[0].passage.heading == "Setup"
    assert hits[0].rank == 1 and "probe" in hits[0].matched_terms


def test_heading_boost(tmp_vault, tmp_path):
    (tmp_vault / "raw/A.md").write_text("# A\n\n## Evaluation scores\n\nThe agent did well on the games.\n")
    (tmp_vault / "raw/B.md").write_text("# B\n\n## Other things\n\nThe agent did well on the games.\n")
    index = build_index(tmp_vault, tmp_path / "index")
    hits = search(index, "evaluation scores", k=2)
    assert hits[0].passage.path == "raw/A.md"


def test_scope_filter_and_synonyms(tmp_vault, tmp_path):
    (tmp_vault / "wiki/Projects/Note.md").write_text("---\ntitle: Note\n---\n# Note\n\n## Summary\n\nThe laptop ran the probe.\n")
    index = build_index(tmp_vault, tmp_path / "index")
    assert all(h.passage.kind == "wiki" for h in search(index, "laptop probe", k=5, scope="wiki"))
    assert all(h.passage.kind == "raw" for h in search(index, "laptop probe", k=5, scope="raw"))
    weights = expand_query("Which machine ran the GPU?")
    assert weights["laptop"] == 0.5 and weights["mps"] == 0.5 and weights["machine"] == 1.0


def test_index_roundtrip_and_staleness(tmp_vault, tmp_path, fake_settings):
    index = build_index(tmp_vault, tmp_path / "index")
    loaded = load_index(tmp_path / "index")
    assert loaded.n_docs == index.n_docs and loaded.fingerprint == index.fingerprint
    assert [p.id for p in loaded.passages] == [p.id for p in index.passages]
    before = vault_fingerprint(tmp_vault)
    time.sleep(0.01)
    (tmp_vault / "raw/Bike Commute Notes.md").write_text((tmp_vault / "raw/Bike Commute Notes.md").read_text() + "\n\nA new paragraph about pedals.\n")
    assert vault_fingerprint(tmp_vault) != before
    rebuilt = ensure_index(fake_settings, quiet=True)
    assert rebuilt.fingerprint == vault_fingerprint(tmp_vault)
    assert any("pedals" in p.text for p in rebuilt.passages)


def test_select_for_prompt_budget():
    hits = [Hit(Passage(str(i), "raw/x.md", "raw", ("H",), 1, 2, "x" * 1100), 1.0, i + 1, []) for i in range(6)]
    chosen = select_for_prompt(hits, 5000)
    assert len(chosen) == 4 and [h.rank for h in chosen] == [1, 2, 3, 4]
    assert select_for_prompt(hits[:1], 10)  # a single passage is always sent
