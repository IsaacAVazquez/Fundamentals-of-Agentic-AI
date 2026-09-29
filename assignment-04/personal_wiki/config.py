"""Settings resolved from command-line flags, then environment variables, then defaults.

Nothing else in the package reads argparse or os.environ directly, so the places
that decide "which vault, which model, which run folder" are all here.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent  # the assignment-04 folder

DEFAULT_MODEL = "gemma4:e4b"
DEFAULT_HOST = "http://localhost:11434"
DEFAULT_BACKEND = "ollama"

# Text budgets. Every number here is documented in EXPLAINER.md and the README.
PASSAGE_MAX_CHARS = 1200      # a retrieval passage is at most this long
PASSAGE_MIN_CHARS = 200       # shorter tails are merged into the previous passage
ASK_PASSAGE_BUDGET = 5000     # characters of passages sent to the model in ask mode
CHAT_PASSAGE_BUDGET = 3500    # characters of passages appended to a chat turn
CHAT_HISTORY_TURNS = 10       # user+assistant pairs kept as conversation context
CHAT_HISTORY_CHARS = 12000    # about 3,000 tokens at 4 characters per token
PLAN_OUTLINE_BUDGET = 6000    # characters of outline sent to the ingest plan call
NOTE_TEXT_BUDGET = 12000      # characters of source text sent per note call
NUM_CTX = 8192                # context window requested from Ollama on every call
NUM_PREDICT = {"ask": 400, "chat": 500, "route": 60, "plan": 700, "note": 900}
FOLDERS = ("Projects", "Concepts", "Course")   # topic folders the plan may choose
SOURCES_FOLDER = "Sources"                     # catalog notes, one per raw file
DEFAULT_K = 6
DEFAULT_MAX_NOTES = 5


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def default_run_id(model: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{re.sub(r'[^A-Za-z0-9.-]+', '-', model)}"


@dataclass(frozen=True)
class Settings:
    vault: Path
    index_dir: Path
    results_dir: Path
    run_id: str
    backend: str = DEFAULT_BACKEND
    model: str = DEFAULT_MODEL
    host: str = DEFAULT_HOST
    instructions_file: Path = PACKAGE_ROOT / "wiki-instructions.md"
    persona_file: Path = PACKAGE_ROOT / "persona.md"
    k: int = DEFAULT_K
    scope: str = "all"
    num_ctx: int = NUM_CTX
    seed: int = 0
    verbose: bool = False
    save: bool = True
    extra: dict = field(default_factory=dict)

    @property
    def raw_dir(self) -> Path:
        return self.vault / "raw"

    @property
    def wiki_dir(self) -> Path:
        return self.vault / "wiki"

    @property
    def index_md(self) -> Path:
        return self.vault / "index.md"

    @property
    def run_dir(self) -> Path:
        return self.results_dir / self.run_id

    def with_overrides(self, **changes) -> "Settings":
        return replace(self, **changes)


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else default


def load_settings(args=None) -> Settings:
    """Build Settings from an argparse namespace (flags win), then the environment, then defaults."""
    get = (lambda key: getattr(args, key, None)) if args is not None else (lambda key: None)
    model = get("model") or os.environ.get("WIKI_MODEL") or DEFAULT_MODEL
    backend = get("backend") or os.environ.get("WIKI_BACKEND") or DEFAULT_BACKEND
    if backend == "fake" and not (get("model") or os.environ.get("WIKI_MODEL")):
        model = "fake-gemma"
    vault = Path(get("vault")).expanduser() if get("vault") else _env_path("WIKI_VAULT", PACKAGE_ROOT / "vault")
    index_dir = Path(get("index_dir")).expanduser() if get("index_dir") else _env_path("WIKI_INDEX_DIR", PACKAGE_ROOT / "index")
    results_dir = (Path(get("results_dir")).expanduser() if get("results_dir")
                   else _env_path("WIKI_RESULTS_DIR", PACKAGE_ROOT / "results"))
    run_id = get("run_id") or os.environ.get("WIKI_RUN_ID") or default_run_id(model)
    return Settings(
        vault=vault.resolve(),
        index_dir=index_dir.resolve(),
        results_dir=results_dir.resolve(),
        run_id=run_id,
        backend=backend,
        model=model,
        host=(get("host") or os.environ.get("WIKI_HOST") or DEFAULT_HOST).rstrip("/"),
        instructions_file=_env_path("WIKI_INSTRUCTIONS", PACKAGE_ROOT / "wiki-instructions.md"),
        persona_file=_env_path("WIKI_PERSONA", PACKAGE_ROOT / "persona.md"),
        k=int(get("k") or DEFAULT_K),
        scope=get("scope") or "all",
        num_ctx=int(os.environ.get("WIKI_NUM_CTX") or NUM_CTX),
        seed=int(os.environ.get("WIKI_SEED") or 0),
        verbose=bool(get("verbose")),
        save=not bool(get("no_save")),
    )
