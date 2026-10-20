"""OpenAI through the official openai SDK, chat completions with a JSON schema response format.

Untested in this repository: no OpenAI key was available while it was written. Check the
model page named in rates.csv for the current reasoning-effort values before a paid run.
"""
from __future__ import annotations

import os

from .base import Backend, CallResult, TransientError


class OpenAIBackend(Backend):
    provider = "openai"

    def __init__(self) -> None:
        try:
            import openai
        except ImportError as exc:
            raise SystemExit("pip install openai (see requirements.txt)") from exc
        if not os.environ.get("OPENAI_API_KEY"):
            raise SystemExit("OPENAI_API_KEY is not set; copy .env.example to .env and load it")
        self._openai = openai
        self.client = openai.OpenAI(max_retries=0)

    def complete(self, *, system: str, user: str, schema: dict | None, model: str, effort: str,
                 max_output_tokens: int) -> CallResult:
        o = self._openai
        kwargs = dict(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_completion_tokens=max_output_tokens,
            reasoning_effort="none" if effort == "none" else effort,
        )
        if schema is not None:
            kwargs["response_format"] = {"type": "json_schema", "json_schema": {"name": "records", "schema": schema, "strict": True}}
        try:
            resp = self.client.chat.completions.create(**kwargs)
        except (o.RateLimitError, o.APIConnectionError, o.APITimeoutError, o.InternalServerError) as exc:
            raise TransientError(str(exc)) from exc
        choice = resp.choices[0]
        u = resp.usage
        cached = 0
        details = getattr(u, "prompt_tokens_details", None)
        if details is not None:
            cached = int(getattr(details, "cached_tokens", 0) or 0)
        prompt = int(getattr(u, "prompt_tokens", 0) or 0)
        return CallResult(
            text=choice.message.content or "",
            input_tokens=prompt - cached,
            cached_input_tokens=cached,
            cache_write_tokens=0,
            output_tokens=int(getattr(u, "completion_tokens", 0) or 0),
            usage_known=u is not None,
            stop_reason=str(choice.finish_reason),
        )
