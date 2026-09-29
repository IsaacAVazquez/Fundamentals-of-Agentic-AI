"""The backend interface: one `generate` call in, text plus identity, timing, and memory out."""
from __future__ import annotations

import re
import resource
import sys
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

THINK_RE = re.compile(r"<(think|thought|thinking)>.*?</\1>\s*", re.DOTALL | re.IGNORECASE)


@dataclass
class ModelInfo:
    backend: str
    tag: str
    digest: str | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None
    family: str | None = None
    context_length: int | None = None
    ollama_version: str | None = None
    size_bytes: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    def label(self) -> str:
        bits = [self.tag]
        if self.quantization_level:
            bits.append(self.quantization_level)
        if self.parameter_size:
            bits.append(self.parameter_size)
        return " ".join(bits)


@dataclass
class Timing:
    wall_s: float
    total_duration_s: float | None = None
    load_duration_s: float | None = None
    prompt_eval_count: int | None = None
    prompt_eval_duration_s: float | None = None
    eval_count: int | None = None
    eval_duration_s: float | None = None

    @property
    def tokens_per_s(self) -> float | None:
        if self.eval_count and self.eval_duration_s:
            return round(self.eval_count / self.eval_duration_s, 1)
        return None

    @property
    def prompt_tokens_per_s(self) -> float | None:
        if self.prompt_eval_count and self.prompt_eval_duration_s:
            return round(self.prompt_eval_count / self.prompt_eval_duration_s, 1)
        return None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["wall_s"] = round(self.wall_s, 3)
        d["tokens_per_s"] = self.tokens_per_s
        d["prompt_tokens_per_s"] = self.prompt_tokens_per_s
        return d

    def summary(self) -> str:
        parts = [f"{self.wall_s:.1f} s"]
        if self.prompt_eval_count:
            rate = f" @ {self.prompt_tokens_per_s} tok/s" if self.prompt_tokens_per_s else ""
            parts.append(f"{self.prompt_eval_count:,} prompt tok{rate}")
        if self.eval_count:
            rate = f" @ {self.tokens_per_s} tok/s" if self.tokens_per_s else ""
            parts.append(f"{self.eval_count:,} gen tok{rate}")
        if self.load_duration_s and self.load_duration_s > 0.5:
            parts.append(f"load {self.load_duration_s:.1f} s")
        return " | ".join(parts)


@dataclass
class MemorySnapshot:
    ollama_model_size_bytes: int | None
    ollama_size_vram_bytes: int | None
    ollama_process_rss_bytes: int | None
    harness_max_rss_bytes: int
    sampled_at: str

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        bits = []
        if self.ollama_model_size_bytes:
            bits.append(f"ollama {self.ollama_model_size_bytes / 1e9:.1f} GB")
        if self.ollama_process_rss_bytes:
            bits.append(f"rss {self.ollama_process_rss_bytes / 1e9:.1f} GB")
        bits.append(f"harness {self.harness_max_rss_bytes / 1e6:.0f} MB")
        return ", ".join(bits)


@dataclass
class Completion:
    text: str
    raw: dict
    model: ModelInfo
    timing: Timing
    memory: MemorySnapshot
    kind: str
    json_mode: bool


def harness_max_rss_bytes() -> int:
    """Peak resident memory of this process. ru_maxrss is bytes on macOS and kilobytes elsewhere."""
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(rss) if sys.platform == "darwin" else int(rss) * 1024


def strip_thinking(text: str) -> str:
    return THINK_RE.sub("", text).strip()


class Backend(ABC):
    name = "base"

    @abstractmethod
    def model_info(self) -> ModelInfo: ...

    @abstractmethod
    def check(self) -> tuple: ...

    @abstractmethod
    def generate(self, messages: list, *, kind: str, json_schema: dict | None = None, temperature: float = 0.0,
                 num_predict: int = 400, num_ctx: int = 8192, seed: int = 0, timeout_s: float = 600) -> Completion: ...
