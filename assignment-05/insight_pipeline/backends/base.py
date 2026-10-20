from __future__ import annotations

from dataclasses import dataclass, field


class TransientError(Exception):
    """Rate limit, timeout, or 5xx: retry with backoff, never quarantine for it."""


@dataclass
class CallResult:
    text: str
    input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0
    usage_known: bool = True
    stop_reason: str = ""
    extra: dict = field(default_factory=dict)

    def usage(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "cache_write_tokens": self.cache_write_tokens,
            "output_tokens": self.output_tokens,
        }


class Backend:
    provider = "base"

    def complete(self, *, system: str, user: str, schema: dict | None, model: str, effort: str,
                 max_output_tokens: int) -> CallResult:
        raise NotImplementedError


def get_backend(name: str) -> Backend:
    if name == "fake":
        from .fake import FakeBackend
        return FakeBackend()
    if name == "anthropic":
        from .anthropic_backend import AnthropicBackend
        return AnthropicBackend()
    if name == "openai":
        from .openai_backend import OpenAIBackend
        return OpenAIBackend()
    raise SystemExit(f"unknown backend {name!r}; choose fake, anthropic, or openai")
