"""Model backends. `get_backend` picks Ollama (the real thing) or the deterministic fake used by tests."""
from __future__ import annotations

from ..config import Settings
from ..errors import UsageError
from .base import Backend


def get_backend(settings: Settings) -> Backend:
    if settings.backend == "ollama":
        from .ollama import OllamaBackend
        return OllamaBackend(settings.host, settings.model)
    if settings.backend == "fake":
        from .fake import FakeBackend
        return FakeBackend(settings.model if settings.model != "gemma4:e4b" else "fake-gemma")
    raise UsageError(f"unknown backend {settings.backend!r}; use ollama or fake")
