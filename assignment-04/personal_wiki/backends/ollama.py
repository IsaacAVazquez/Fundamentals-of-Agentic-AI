"""The Ollama backend: HTTP calls to a local Ollama server, with identity, timing, and memory capture."""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

from ..config import utc_now_iso
from ..errors import BackendError, ModelMissing, OllamaUnreachable
from .base import Backend, Completion, MemorySnapshot, ModelInfo, Timing, harness_max_rss_bytes, strip_thinking


def _ns_to_s(value) -> float | None:
    return round(value / 1e9, 4) if isinstance(value, (int, float)) else None


class OllamaBackend(Backend):
    name = "ollama"

    def __init__(self, host: str, model: str):
        self.host = host.rstrip("/")
        self.model = model
        self._info: ModelInfo | None = None

    # HTTP plumbing -------------------------------------------------------------------
    def _request(self, method: str, path: str, payload: dict | None = None, timeout: float = 5.0) -> dict:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(self.host + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 404 and "not found" in body.lower():
                raise ModelMissing(self._missing_message()) from None
            raise BackendError(f"Ollama returned HTTP {e.code} for {path}: {body[:300]}") from None
        except urllib.error.URLError as e:
            raise OllamaUnreachable(f"cannot reach Ollama at {self.host} ({e.reason}). Start it with \"ollama serve\" "
                                    "or open the Ollama app, then retry. \"wiki search\" works without it.") from None
        except (TimeoutError, OSError) as e:
            raise OllamaUnreachable(f"cannot reach Ollama at {self.host} ({e}). Start it with \"ollama serve\" "
                                    "or open the Ollama app, then retry. \"wiki search\" works without it.") from None
        try:
            return json.loads(body) if body.strip() else {}
        except json.JSONDecodeError:
            raise BackendError(f"Ollama returned something that is not JSON for {path}: {body[:200]}") from None

    def _missing_message(self) -> str:
        installed = ", ".join(self.installed_models()) or "none"
        return (f"model \"{self.model}\" is not installed in Ollama. Pull it once while online with "
                f"scripts/pull_model.sh {self.model} (or: ollama pull {self.model}). Installed: {installed}.")

    def installed_models(self) -> list:
        try:
            tags = self._request("GET", "/api/tags")
        except OllamaUnreachable:
            return []
        return [m.get("name", "") for m in tags.get("models", [])]

    def version(self) -> str | None:
        try:
            return self._request("GET", "/api/version").get("version")
        except (BackendError, ModelMissing):
            return None

    def _tag_entry(self, models: list) -> dict | None:
        candidates = {self.model, self.model + ":latest"}
        for m in models:
            if m.get("name") in candidates or m.get("model") in candidates:
                return m
        return None

    # Identity ------------------------------------------------------------------------
    def model_info(self) -> ModelInfo:
        if self._info is not None:
            return self._info
        version = self.version()
        tags = self._request("GET", "/api/tags")
        entry = self._tag_entry(tags.get("models", []))
        if entry is None:
            raise ModelMissing(self._missing_message())
        details = entry.get("details", {})
        context_length = None
        try:
            show = self._request("POST", "/api/show", {"model": self.model})
            for key, value in (show.get("model_info") or {}).items():
                if key.endswith(".context_length") and isinstance(value, int):
                    context_length = value
                    break
            details = {**details, **(show.get("details") or {})}
        except (BackendError, ModelMissing):
            pass
        self._info = ModelInfo(
            backend="ollama", tag=self.model, digest=entry.get("digest"),
            parameter_size=details.get("parameter_size"), quantization_level=details.get("quantization_level"),
            family=details.get("family"), context_length=context_length, ollama_version=version,
            size_bytes=entry.get("size"),
        )
        return self._info

    def check(self) -> tuple:
        try:
            version = self.version()
        except OllamaUnreachable as e:
            return False, str(e)
        try:
            info = self.model_info()
        except ModelMissing as e:
            return False, str(e)
        return True, f"Ollama {version}: model {info.label()} present (digest {str(info.digest)[:19]}…)"

    # Memory --------------------------------------------------------------------------
    def memory_snapshot(self) -> MemorySnapshot:
        size = vram = None
        try:
            ps = self._request("GET", "/api/ps")
            entry = self._tag_entry(ps.get("models", []))
            if entry:
                size, vram = entry.get("size"), entry.get("size_vram")
        except (BackendError, ModelMissing, OllamaUnreachable):
            pass
        rss = None
        try:
            out = subprocess.run(["ps", "-axo", "rss=,command="], capture_output=True, text=True, timeout=5).stdout
            total = 0
            for line in out.splitlines():
                parts = line.strip().split(None, 1)
                if len(parts) == 2 and "ollama" in parts[1].lower() and "python" not in parts[1].lower():
                    total += int(parts[0]) * 1024
            rss = total or None
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
        return MemorySnapshot(size, vram, rss, harness_max_rss_bytes(), utc_now_iso())

    # Generation ----------------------------------------------------------------------
    def generate(self, messages: list, *, kind: str, json_schema: dict | None = None, temperature: float = 0.0,
                 num_predict: int = 400, num_ctx: int = 8192, seed: int = 0, timeout_s: float = 600) -> Completion:
        payload = {
            "model": self.model, "messages": messages, "stream": False, "keep_alive": "10m", "think": False,
            "options": {"temperature": temperature, "num_ctx": num_ctx, "num_predict": num_predict, "seed": seed},
        }
        if json_schema is not None:
            payload["format"] = json_schema
        start = time.perf_counter()
        response = None
        for attempt in range(3):
            try:
                response = self._request("POST", "/api/chat", payload, timeout=timeout_s)
                break
            except BackendError as e:
                text = str(e)
                if "HTTP 400" in text and "think" in text.lower() and "think" in payload:
                    payload.pop("think", None)
                    continue
                if "HTTP 400" in text and json_schema is not None and payload.get("format") != "json":
                    payload["format"] = "json"
                    continue
                raise
        if response is None:
            raise BackendError("Ollama refused the request three times")
        wall = time.perf_counter() - start
        content = strip_thinking((response.get("message") or {}).get("content", ""))
        timing = Timing(
            wall_s=wall, total_duration_s=_ns_to_s(response.get("total_duration")),
            load_duration_s=_ns_to_s(response.get("load_duration")), prompt_eval_count=response.get("prompt_eval_count"),
            prompt_eval_duration_s=_ns_to_s(response.get("prompt_eval_duration")), eval_count=response.get("eval_count"),
            eval_duration_s=_ns_to_s(response.get("eval_duration")),
        )
        return Completion(content, response, self.model_info(), timing, self.memory_snapshot(), kind, json_schema is not None)
