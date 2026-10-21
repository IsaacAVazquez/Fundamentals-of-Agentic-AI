"""Claude through the official anthropic SDK. Structured JSON output, the shared system prompt
cached as a stable prefix, and effort kept low for a bounded labeling task."""
from __future__ import annotations

import os

from .base import Backend, CallResult, TransientError


class AnthropicBackend(Backend):
    provider = "anthropic"

    def __init__(self) -> None:
        try:
            import anthropic
        except ImportError as exc:
            raise SystemExit("pip install anthropic (see requirements.txt)") from exc
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY is not set; copy .env.example to .env and load it")
        self._anthropic = anthropic
        # The orchestrator owns retries and logs each attempt. A user-scoped key (sk-ant-usr-...) must name
        # its workspace in a header; ANTHROPIC_WORKSPACE_ID carries it.
        ws = os.environ.get("ANTHROPIC_WORKSPACE_ID")
        self.client = anthropic.Anthropic(max_retries=0, default_headers={"anthropic-workspace-id": ws} if ws else None)

    def complete(self, *, system: str, user: str, schema: dict | None, model: str, effort: str,
                 max_output_tokens: int) -> CallResult:
        a = self._anthropic
        kwargs = dict(
            model=model,
            max_tokens=max_output_tokens,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user}],
            output_config={"effort": effort},
        )
        # Haiku 5.5 thinks by default and the thinking tokens count against max_tokens, which truncated a
        # 25-review batch at 4,000 tokens in the first pilot. Disabled thinking is supported on Haiku 5.5 at
        # effort high or below; Sonnet 5.5 rejects "disabled", so it keeps adaptive thinking at the given effort.
        if "haiku" in model:
            kwargs["thinking"] = {"type": "disabled"}
        if schema is not None:
            kwargs["output_config"]["format"] = {"type": "json_schema", "schema": schema}
        try:
            resp = self.client.messages.create(**kwargs)
        except (a.RateLimitError, a.APIConnectionError, a.APITimeoutError, a.InternalServerError) as exc:
            raise TransientError(str(exc)) from exc
        except a.APIStatusError as exc:
            if exc.status_code >= 500 or exc.status_code == 429:
                raise TransientError(str(exc)) from exc
            raise
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        u = resp.usage
        return CallResult(
            text=text,
            input_tokens=int(getattr(u, "input_tokens", 0) or 0),
            cached_input_tokens=int(getattr(u, "cache_read_input_tokens", 0) or 0),
            cache_write_tokens=int(getattr(u, "cache_creation_input_tokens", 0) or 0),
            output_tokens=int(getattr(u, "output_tokens", 0) or 0),
            usage_known=True,
            stop_reason=str(resp.stop_reason),
            extra={"request_id": getattr(resp, "_request_id", None)},
        )
