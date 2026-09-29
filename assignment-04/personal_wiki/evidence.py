"""Saved outputs: evidence cards for ask, transcripts for chat, search records, and the run manifest.

Everything lands under results/<run-id>/ as JSON (for machines) and Markdown (for readers),
so a reader can inspect a run without rerunning the model.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .config import Settings, utc_now_iso


def write_json(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _fmt_bytes(n) -> str:
    if not n:
        return "n/a"
    return f"{n / 1e9:.2f} GB" if n >= 1e8 else f"{n / 1e6:.0f} MB"


def _fmt_secs(x) -> str:
    return "n/a" if x is None else f"{x:.2f} s"


@dataclass
class EvidenceCard:
    id: str
    run_id: str
    question: str
    mode: str
    backend: str
    model: dict
    options: dict
    retrieval: dict
    prompt: dict
    answer: dict
    citations: list
    citation_check: dict
    status: str
    timing: dict
    memory: dict
    offline: dict | None = None
    assessment: dict | None = None
    error: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    schema: str = "evidence-card/1"

    def to_dict(self) -> dict:
        return asdict(self)

    def to_markdown(self) -> str:
        m = self.model or {}
        lines = [f"# Evidence card {self.id}", "", "## Question", "", self.question, "", "## Setup", ""]
        lines.append(f"- Mode: {self.mode} (backend {self.backend}); run `{self.run_id}`; created {self.created_at}")
        lines.append(f"- Model: `{m.get('tag')}`, quantization {m.get('quantization_level') or 'n/a'}, parameters {m.get('parameter_size') or 'n/a'}, digest `{m.get('digest') or 'n/a'}`, Ollama {m.get('ollama_version') or 'n/a'}")
        lines.append(f"- Options: {json.dumps(self.options)}")
        if self.offline:
            state = "offline (no probe reached the internet)" if not self.offline.get("internet_reachable") else "ONLINE (a probe reached the internet)"
            lines.append(f"- Network at run time: {state}, checked {self.offline.get('checked_at')}")
        r = self.retrieval or {}
        lines += ["", "## Retrieved passages", "",
                  f"k={r.get('k')}, scope={r.get('scope')}, index of {r.get('index_passages')} passages built {r.get('index_built_at')}; query terms: {', '.join(r.get('query_terms', []))}", ""]
        for p in r.get("passages", []):
            sent = "sent to model" if p.get("sent_to_model") else "not sent (over the passage budget)"
            lines.append(f"**[{p['n']}]** `{p['path']}` # {p['heading']} (lines {p['lines'][0]}-{p['lines'][1]}, {p['kind']}, score {p['score']}, {sent})")
            lines.append("")
            text = p.get("text", "")
            shown = text if len(text) <= 700 else text[:700].rstrip() + " …(full text in the JSON card)"
            lines.extend("> " + l for l in shown.split("\n"))
            lines.append("")
        lines += ["## Answer", "", self.answer.get("text", "") or "(empty)", "", "## Citations", ""]
        if self.citations:
            lines.append("| n | valid | path | heading | lines |")
            lines.append("| --- | --- | --- | --- | --- |")
            for c in self.citations:
                ln = f"{c['lines'][0]}-{c['lines'][1]}" if c.get("lines") else ""
                lines.append(f"| {c['n']} | {'yes' if c['valid'] else 'no'} | {c.get('path') or ''} | {c.get('heading') or ''} | {ln} |")
        else:
            lines.append("(the answer cites nothing)")
        cc = self.citation_check or {}
        lines += ["", "## Citation check", "",
                  f"- Status: **{self.status}**",
                  f"- Valid citations: {cc.get('valid', 0)}; invalid: {cc.get('invalid', [])}; cited paths: {cc.get('cited_paths', [])}",
                  f"- Insufficient-evidence marker: {cc.get('insufficient_marker')}",
                  f"- Numbers in the answer not found in any cited passage: {cc.get('unverified_numbers', [])}"]
        t, mem = self.timing or {}, self.memory or {}
        lines += ["", "## Timing and memory", "", "| Measure | Value |", "| --- | --- |",
                  f"| Wall clock | {_fmt_secs(t.get('wall_s'))} |",
                  f"| Ollama total / load | {_fmt_secs(t.get('total_duration_s'))} / {_fmt_secs(t.get('load_duration_s'))} |",
                  f"| Prompt tokens (rate) | {t.get('prompt_eval_count')} ({t.get('prompt_tokens_per_s')} tok/s) |",
                  f"| Generated tokens (rate) | {t.get('eval_count')} ({t.get('tokens_per_s')} tok/s) |",
                  f"| Ollama model size / VRAM | {_fmt_bytes(mem.get('ollama_model_size_bytes'))} / {_fmt_bytes(mem.get('ollama_size_vram_bytes'))} |",
                  f"| Ollama process RSS | {_fmt_bytes(mem.get('ollama_process_rss_bytes'))} |",
                  f"| Harness peak RSS | {_fmt_bytes(mem.get('harness_max_rss_bytes'))} |"]
        if self.assessment:
            a = self.assessment
            lines += ["", "## Assessment", "",
                      f"- Expected behavior: {a.get('expected_behavior')}; status matches: {a.get('status_matches_expected')}",
                      f"- Expected sources: {a.get('expected_sources')}; retrieval hit: {a.get('retrieval_hit')} (all: {a.get('retrieval_hit_all')})",
                      f"- Expected keywords: {a.get('expected_keywords')}; found: {a.get('keywords_found')}",
                      f"- Automated verdict: **{a.get('verdict')}**",
                      f"- Notes written before the run: {a.get('notes')}",
                      f"- Human assessment: {a.get('human_assessment') or '(to be written after reading the cited passages)'}"]
        if self.error:
            lines += ["", "## Error", "", self.error]
        return "\n".join(lines) + "\n"


def write_card(run_dir: Path, card: EvidenceCard, subdir: str = "ask") -> tuple:
    folder = run_dir / subdir
    folder.mkdir(parents=True, exist_ok=True)
    jp = write_json(folder / f"{card.id}.json", card.to_dict())
    mp = folder / f"{card.id}.md"
    mp.write_text(card.to_markdown(), encoding="utf-8")
    return jp, mp


@dataclass
class Transcript:
    run_id: str
    script: str | None
    model: dict
    persona_sha256: str
    started_at: str
    ended_at: str = ""
    turns: list = field(default_factory=list)
    checks: dict = field(default_factory=dict)
    schema: str = "chat-transcript/1"

    def to_dict(self) -> dict:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [f"# Chat transcript ({'scripted: ' + self.script if self.script else 'interactive'})", "",
                 f"Run `{self.run_id}`, model `{self.model.get('tag')}` ({self.model.get('backend')}), persona sha256 `{self.persona_sha256[:12]}…`, "
                 f"started {self.started_at}, ended {self.ended_at}.", ""]
        if self.checks:
            lines.append(f"Expectation checks: {self.checks.get('passed', 0)} of {self.checks.get('total', 0)} held.")
            lines.append("")
        for t in self.turns:
            r = t.get("routing", {})
            head = f"### Turn {t['i']}, routing {r.get('decision')} ({r.get('source')}: {r.get('reason')})"
            if t.get("expect"):
                ok = t.get("check", {})
                verdict = "OK" if all(v is True for v in ok.values() if v is not None) and any(v is True for v in ok.values()) else ("FAILED" if any(v is False for v in ok.values()) else "n/a")
                head += f", expected {t['expect']}, {verdict}"
            lines += [head, "", f"**You:** {t['user']}", ""]
            if t.get("retrieved"):
                lines.append("**Retrieved:** " + "; ".join(f"[{p['n']}] {p['path']} # {p['heading']}" for p in t["retrieved"]))
                lines.append("")
            lines += [f"**Assistant:** {t.get('assistant', '')}", ""]
            if t.get("timing"):
                tm = t["timing"]
                lines.append(f"_{_fmt_secs(tm.get('wall_s'))}, {tm.get('eval_count')} generated tokens at {tm.get('tokens_per_s')} tok/s_")
                lines.append("")
        return "\n".join(lines) + "\n"


def write_transcript(run_dir: Path, transcript: Transcript, name: str) -> tuple:
    folder = run_dir / "chat"
    folder.mkdir(parents=True, exist_ok=True)
    jp = write_json(folder / f"{name}.json", transcript.to_dict())
    mp = folder / f"{name}.md"
    mp.write_text(transcript.to_markdown(), encoding="utf-8")
    return jp, mp


def write_search_record(run_dir: Path, query: str, hits: list, scope: str, k: int, index_stats: dict) -> tuple:
    from .textutil import slugify
    folder = run_dir / "search"
    folder.mkdir(parents=True, exist_ok=True)
    name = slugify(query)[:60] or "query"
    data = {"schema": "search/1", "query": query, "k": k, "scope": scope, "index": index_stats, "created_at": utc_now_iso(),
            "model_called": False, "hits": [h.to_dict() for h in hits]}
    jp = write_json(folder / f"{name}.json", data)
    lines = [f"# Search: {query}", "", f"k={k}, scope={scope}, no model call. {len(hits)} passages.", ""]
    for h in hits:
        p = h.passage
        lines += [f"## [{h.rank}] {p.path} # {p.heading} (lines {p.start_line}-{p.end_line}, score {h.score:.2f})", "", p.text, ""]
    tp = folder / f"{name}.md"
    tp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return jp, tp


def offline_status(settings: Settings) -> dict:
    """The run's network status: from doctor.json when the demo script wrote one, else a quick live probe."""
    for name in ("doctor-2.json", "doctor.json"):
        p = settings.run_dir / name
        if p.exists():
            try:
                d = read_json(p)
                return {"source": name, **(d.get("internet") or {})}
            except (json.JSONDecodeError, OSError):
                pass
    from .doctor import internet_reachable
    reachable, probes = internet_reachable(timeout=2.0)
    return {"source": "live probe", "internet_reachable": reachable, "probes": probes, "checked_at": utc_now_iso()}


def build_manifest(settings: Settings) -> dict:
    run = settings.run_dir
    manifest: dict = {"schema": "run-manifest/1", "run_id": settings.run_id, "created_at": utc_now_iso(),
                      "results_dir": str(run), "files": sorted(p.relative_to(run).as_posix() for p in run.rglob("*") if p.is_file())}
    for name in ("doctor.json", "doctor-2.json"):
        if (run / name).exists():
            d = read_json(run / name)
            manifest.setdefault("doctor", {})[name] = d
            manifest.setdefault("device", d.get("device"))
            manifest.setdefault("ollama", d.get("ollama"))
    steps = run / "steps.jsonl"
    if steps.exists():
        manifest["steps"] = [json.loads(l) for l in steps.read_text(encoding="utf-8").splitlines() if l.strip()]
    logs = sorted((run / "ingest").glob("ingest_log*.json")) if (run / "ingest").is_dir() else []
    if logs:
        runs = []
        for lg in logs:
            d = read_json(lg)
            runs.append({"file": lg.relative_to(run).as_posix(), "started_at": d.get("started_at"), "model": (d.get("model") or {}).get("tag"),
                         "totals": d.get("totals"), "budgets": d.get("budgets")})
        generation = max(runs, key=lambda r: (r["totals"] or {}).get("calls", 0))
        manifest["ingest"] = {"runs": runs, "generation": generation["totals"], "generation_log": generation["file"],
                              "idempotence_check": next((r["totals"] for r in runs if r is not generation and (r["totals"] or {}).get("calls", 0) == 0), None)}
    cards = sorted((run / "ask").glob("*.json")) if (run / "ask").is_dir() else []
    manifest["ask"] = []
    for c in cards:
        if c.name == "summary.json":
            continue
        d = read_json(c)
        manifest["ask"].append({"id": d.get("id"), "status": d.get("status"), "verdict": (d.get("assessment") or {}).get("verdict"),
                                "wall_s": (d.get("timing") or {}).get("wall_s"), "tokens_per_s": (d.get("timing") or {}).get("tokens_per_s"),
                                "model": (d.get("model") or {}).get("tag"), "card": c.relative_to(run).as_posix()})
    manifest["chat"] = []
    if (run / "chat").is_dir():
        for t in sorted((run / "chat").glob("*.json")):
            d = read_json(t)
            manifest["chat"].append({"transcript": t.relative_to(run).as_posix(), "turns": len(d.get("turns", [])), "checks": d.get("checks")})
    manifest["search"] = []
    if (run / "search").is_dir():
        for s in sorted((run / "search").glob("*.json")):
            d = read_json(s)
            manifest["search"].append({"query": d.get("query"), "hits": len(d.get("hits", [])), "file": s.relative_to(run).as_posix()})
    return manifest


def write_manifest(settings: Settings) -> Path:
    return write_json(settings.run_dir / "manifest.json", build_manifest(settings))
