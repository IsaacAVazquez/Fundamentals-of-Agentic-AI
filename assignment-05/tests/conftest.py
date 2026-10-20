import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def synthetic_csv(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("data") / "syn.csv"
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_synthetic_reviews.py"), "--out", str(out), "--rows", "300", "--seed", "3"], check=True)
    return out


@pytest.fixture()
def fake_controls():
    from insight_pipeline.classify import Controls
    return Controls(backend="fake", batch_size=20, workers=2, max_spend_usd=1.0)
