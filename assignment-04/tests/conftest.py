import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from personal_wiki.config import Settings  # noqa: E402

FIXTURE_VAULT = Path(__file__).parent / "fixtures" / "vault"


@pytest.fixture
def tmp_vault(tmp_path):
    vault = tmp_path / "vault"
    shutil.copytree(FIXTURE_VAULT, vault)
    for folder in ("Projects", "Concepts", "Course", "Sources"):
        (vault / "wiki" / folder).mkdir(parents=True, exist_ok=True)
    return vault


@pytest.fixture
def fake_settings(tmp_vault, tmp_path):
    return Settings(vault=tmp_vault, index_dir=tmp_path / "index", results_dir=tmp_path / "results", run_id="test-run",
                    backend="fake", model="fake-gemma", instructions_file=ROOT / "wiki-instructions.md", persona_file=ROOT / "persona.md")


@pytest.fixture
def fake_backend():
    from personal_wiki.backends.fake import FakeBackend
    return FakeBackend()
