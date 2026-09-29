"""Ingest: read a raw source, have the model plan and write linked wiki notes, keep the catalog and index current.

Two model calls per source shape the notes: a PLAN call (JSON, which notes to write and
from which sections) and one NOTE call per planned note (the body). The harness owns
everything else: chunking the source, budgeting the text sent, validating titles and
links, frontmatter, the Sources catalog note, index.md, and the retrieval index.
Re-ingesting an unchanged source is a no-op; a changed source rewrites the same
filenames; a note marked `reviewed: true` is never overwritten without --overwrite-reviewed.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .chunking import Section, split_sections
from .config import FOLDERS, NOTE_TEXT_BUDGET, NUM_PREDICT, PACKAGE_ROOT, PLAN_OUTLINE_BUDGET, Settings, today_iso, utc_now_iso
from .errors import UsageError
from .evidence import read_json, write_json
from .index import build_index
from .prompts import PLAN_SCHEMA, build_note_messages, build_plan_messages, outline_for_plan
from .textutil import content_terms, estimate_tokens, slugify
from .vault import (SourceSpec, disambiguate_title, ensure_layout, find_existing_title, find_note_by_title, linkify_related,
                    list_notes, list_source_notes, normalize_title, note_path, read_note, source_id_for, source_link,
                    source_note_name, title_key, validate_title, write_index_md, write_note, write_source_note)


@dataclass
class RelatedRef:
    title: str
    why: str


@dataclass
class NotePlanItem:
    title: str
    folder: str
    summary: str
    sections: list
    related: list = field(default_factory=list)


@dataclass
class NotePlan:
    source_id: str
    source_name: str
    notes: list
    origin: str          # model | model-retry | heuristic


@dataclass
class CallRecord:
    kind: str
    attempt: int
    system_chars: int
    user_chars: int
    payload_chars: int
    payload_capped: bool
    est_prompt_tokens: int
    timing: dict
    memory: dict
    response_chars: int
    ok: bool
    error: str | None
    dump_file: str


@dataclass
class IngestResult:
    source: str
    source_id: str
    sha256: str
    action: str                     # up-to-date | ingested | dry-run | unsupported | error
    notes_written: list = field(default_factory=list)
    notes_drafted: list = field(default_factory=list)
    notes_stale: list = field(default_factory=list)
    calls: list = field(default_factory=list)
    wall_s: float = 0.0
    plan_origin: str | None = None
    errors: list = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def load_source_catalog() -> dict:
    path = PACKAGE_ROOT / "sources.json"
    if not path.exists():
        return {}
    data = read_json(path)
    return {s["file"]: {**s, "copied_on": data.get("copied_on", s.get("copied_on", "unknown")),
                        "commit": data.get("copied_from_commit")} for s in data.get("sources", [])}


def discover_sources(paths: list, settings: Settings) -> list:
    raw = settings.raw_dir
    if not paths:
        paths = [raw]
    found: list = []
    for p in paths:
        p = Path(p).expanduser().resolve()
        if p.is_dir():
            found.extend(sorted(x for x in p.iterdir() if x.is_file() and not x.name.startswith(".")))
        elif p.is_file():
            found.append(p)
        else:
            raise UsageError(f"source path {p} does not exist. Put Markdown or text files in {raw} and run \"wiki ingest\".")
    for p in found:
        try:
            p.relative_to(raw)
        except ValueError:
            raise UsageError(f"{p} is outside the vault's raw folder ({raw}). Copy it there first so notes can reference it.") from None
    return found


def _extract_json(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        return json.loads(m.group(0))
    raise json.JSONDecodeError("no JSON object found", text, 0)


def _match_heading(name: str, headings: list) -> str | None:
    key = title_key(re.sub(r"^#+\s*", "", name).split(" — ")[0])
    if not key:
        return None
    for h in headings:
        if title_key(h) == key:
            return h
    for h in headings:
        hk = title_key(h)
        if hk and (hk.startswith(key) or key.startswith(hk)) and min(len(hk), len(key)) >= 6:
            return h
    mine = set(content_terms(name))
    best, best_score = None, 0.0
    for h in headings:
        theirs = set(content_terms(h))
        if not mine or not theirs:
            continue
        score = len(mine & theirs) / len(mine | theirs)
        if score > best_score:
            best, best_score = h, score
    return best if best_score >= 0.6 else None


def default_folder(source_name: str) -> str:
    return "Course" if re.search(r"\bclass\b|\blecture\b|\bsyllabus\b|\bcourse\b", source_name, re.I) else "Projects"


def validate_plan(raw_text: str, sections: list, existing_titles: list, previous_titles: list, source_name: str,
                  max_notes: int, source_id: str, owners: dict) -> tuple:
    """Turn the model's JSON into a NotePlan. Returns (plan or None, list of problems)."""
    problems: list = []
    try:
        data = _extract_json(raw_text)
    except (json.JSONDecodeError, ValueError) as e:
        return None, [f"the reply was not valid JSON ({e})"]
    raw_notes = data.get("notes") if isinstance(data, dict) else None
    if not isinstance(raw_notes, list) or not raw_notes:
        return None, ["the JSON has no \"notes\" list"]
    headings = [s.heading for s in sections if s.heading_path]
    other_titles = [t for t, _ in existing_titles if owners.get(title_key(t)) not in (None, source_id)]
    items: list = []
    taken: list = []
    for i, n in enumerate(raw_notes[:max_notes]):
        if not isinstance(n, dict):
            problems.append(f"note {i + 1} is not an object")
            continue
        title = normalize_title(str(n.get("title", "")))
        ok, why = validate_title(title)
        if not ok:
            problems.append(f"title {n.get('title')!r}: {why}")
            continue
        reuse = find_existing_title(title, previous_titles)
        if reuse:
            title = reuse
        elif find_existing_title(title, other_titles):
            title = disambiguate_title(title, source_name, other_titles + taken)
        if title_key(title) in {title_key(t) for t in taken}:
            problems.append(f"duplicate title {title!r}")
            continue
        folder = n.get("folder") if n.get("folder") in FOLDERS else default_folder(source_name)
        summary = re.sub(r"\s+", " ", str(n.get("summary", ""))).strip()[:220] or f"Notes from {source_name}."
        matched: list = []
        for s in n.get("sections") or []:
            h = _match_heading(str(s), headings)
            if h and h not in matched:
                matched.append(h)
            elif not h:
                problems.append(f"note {title!r} names a section that is not in the outline: {s!r}")
        related = [RelatedRef(str(r.get("title", "")), str(r.get("why", ""))) for r in (n.get("related") or []) if isinstance(r, dict)]
        if not matched:
            problems.append(f"note {title!r} has no sections from the outline; dropped")
            continue
        taken.append(title)
        items.append(NotePlanItem(title, folder, summary, matched, related))
    if len(items) < 1 or (len(items) < 2 and len(headings) >= 4):
        problems.append(f"only {len(items)} usable note(s); need at least 2 for a document with {len(headings)} sections")
        return None, problems
    return NotePlan(source_id, source_name, items, "model"), problems


def heuristic_plan(source_name: str, doc_title: str, sections: list, max_notes: int, previous_titles: list) -> NotePlan:
    """Fallback when the model's plan is unusable: one note per group of H2 sections."""
    h2 = [s for s in sections if s.level == 2]
    if not h2:
        h2 = [s for s in sections if s.heading_path]
    groups_n = max(1, min(max_notes, math.ceil(len(h2) / 3))) if h2 else 1
    size = math.ceil(len(h2) / groups_n) if h2 else 1
    groups = [h2[i:i + size] for i in range(0, len(h2), size)] or [[]]
    base_words = [w for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9'&+.-]*", doc_title) if w.lower() not in ("readme", "notes", "the", "a", "an", "of")]
    items: list = []
    taken: list = []
    for gi, group in enumerate(groups):
        head_words = [w for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9'&+.-]*", group[0].heading)] if group else ["Overview"]
        title = normalize_title(" ".join((base_words[:2] + head_words)[:5]))
        if not validate_title(title)[0] or title_key(title) in {title_key(t) for t in taken}:
            title = normalize_title(" ".join((base_words[:2] + ["Part", str(gi + 1)])[:5]))
        reuse = find_existing_title(title, previous_titles)
        title = reuse or disambiguate_title(title, source_name, taken)
        taken.append(title)
        headings = [s.heading for s in group]
        if gi == 0:
            headings = [s.heading for s in sections if s.level == 1][:1] + headings
        summary = "Covers " + ", ".join(headings[:3]) + "." if headings else f"Notes from {source_name}."
        related = [RelatedRef(taken[gi - 1], "adjacent sections of the same source")] if gi > 0 else []
        items.append(NotePlanItem(title, default_folder(source_name), summary[:220], headings, related))
    return NotePlan(source_id_for(source_name), source_name, items, "heuristic")


def assign_sections(plan: NotePlan, sections: list) -> dict:
    """Map every section (in document order) to a planned note; unclaimed sections go to the nearest claimed note."""
    claimed: dict = {}
    for item in plan.notes:
        for h in item.sections:
            claimed.setdefault(title_key(h), item.title)
    ordered = [s for s in sections if s.body_text().strip() or s.heading_path]
    assigned: dict = {item.title: [] for item in plan.notes}
    last_owner = None
    pending: list = []
    for s in ordered:
        owner = claimed.get(title_key(s.heading)) if s.heading_path else None
        if owner is None:
            for depth in range(len(s.heading_path) - 1, 0, -1):
                owner = claimed.get(title_key(s.heading_path[depth - 1]))
                if owner:
                    break
        if owner is None:
            if last_owner is None:
                pending.append(s)
            else:
                assigned[last_owner].append(s)
            continue
        if pending:
            assigned[owner].extend(pending)
            pending = []
        assigned[owner].append(s)
        last_owner = owner
    if pending:
        assigned[plan.notes[0].title].extend(pending)
    return assigned


def sections_text(secs: list, budget: int) -> tuple:
    parts: list = []
    used = 0
    capped = False
    for s in secs:
        body = s.body_text()
        header = ("#" * max(s.level, 2) + " " + s.heading + "\n") if s.heading_path else ""
        block = header + body
        if not block.strip():
            continue
        if used + len(block) + 2 > budget:
            room = budget - used - 2
            if room > 200:
                cut = block[:room]
                cut = cut[: cut.rfind("\n\n")] if cut.rfind("\n\n") > room // 2 else cut
                parts.append(cut.rstrip() + f"\n[... section text truncated by the harness at {budget:,} characters]")
            capped = True
            break
        parts.append(block)
        used += len(block) + 2
    return "\n\n".join(parts), capped


def clean_note_body(text: str) -> tuple:
    """Keep exactly Summary, Details, Related. Returns (summary, details, related lines)."""
    text = re.sub(r"^```[a-z]*\n(.*?)\n```$", r"\1", text.strip(), flags=re.S)
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    lines = text.split("\n")
    parts: dict = {"summary": [], "details": [], "related": []}
    current = None
    for line in lines:
        m = re.match(r"^\s*#{1,4}\s*(summary|details|related|sources?)\b.*$", line, re.I)
        if m:
            name = m.group(1).lower()
            current = None if name.startswith("source") else name
            continue
        if re.match(r"^\s*#\s+\S", line) and current is None and not parts["summary"]:
            continue
        if current is not None:
            parts[current].append(line)
        elif not parts["summary"] and line.strip() and current is None and not any(parts.values()):
            parts["summary"].append(line)
    summary = "\n".join(parts["summary"]).strip()
    details = "\n".join(parts["details"]).strip()
    related = [l.strip() for l in parts["related"] if l.strip().startswith(("-", "*"))]
    if not details and summary:
        chunks = summary.split("\n\n", 1)
        if len(chunks) == 2:
            summary, details = chunks[0].strip(), chunks[1].strip()
    return summary, details, related


def parse_related_lines(lines: list) -> list:
    out: list = []
    for l in lines:
        body = l.lstrip("-* ").strip()
        if body.lower() in ("none", "none.", "(none)"):
            continue
        m = re.match(r"^\[\[([^\]|]+)(?:\|[^\]]*)?\]\]\s*[—:–-]?\s*(.*)$", body) or re.match(r"^([^:—–]+?)\s*[:—–]\s*(.*)$", body) or re.match(r"^(.+?)$", body)
        if m:
            out.append((m.group(1).strip().strip("*_`\""), (m.group(2) if m.lastindex and m.lastindex >= 2 else "").strip()))
    return out


class Ingester:
    def __init__(self, settings: Settings, backend, *, force=False, overwrite_reviewed=False, max_notes=5, dry_run=False):
        self.settings = settings
        self.backend = backend
        self.force = force
        self.overwrite_reviewed = overwrite_reviewed
        self.max_notes = max(2, min(6, int(max_notes)))
        self.dry_run = dry_run
        self.catalog = load_source_catalog()
        self.call_no = 0
        self.info = backend.model_info()
        self.run_dir = settings.run_dir
        self.started = utc_now_iso()
        self.stamp = time.strftime("%H%M%S")
        # one log per invocation, so a second ingest (the idempotence check) never overwrites the first run's record
        self.log_name = "ingest_log"
        n = 1
        while (self.run_dir / "ingest" / f"{self.log_name}.json").exists():
            n += 1
            self.log_name = f"ingest_log-{n}"

    # model calls ----------------------------------------------------------------------
    def _call(self, kind: str, messages: list, source_id: str, label: str, *, json_schema=None, payload_chars=0, capped=False) -> tuple:
        self.call_no += 1
        stamp = time.perf_counter()
        error = None
        text = ""
        completion = None
        try:
            completion = self.backend.generate(messages, kind=kind, json_schema=json_schema, temperature=0.0,
                                               num_predict=NUM_PREDICT[kind], num_ctx=self.settings.num_ctx, seed=self.settings.seed)
            text = completion.text
        except Exception as e:  # recorded, then re-raised by the caller's policy
            error = f"{type(e).__name__}: {e}"
        name = f"{self.stamp}-{self.call_no:03d}-{kind}-{source_id}" + (f"-{slugify(label)[:40]}" if label else "") + ".json"
        dump = self.run_dir / "ingest" / "calls" / name
        system_chars = sum(len(m["content"]) for m in messages if m["role"] == "system")
        user_chars = sum(len(m["content"]) for m in messages if m["role"] == "user")
        record = CallRecord(kind, 1, system_chars, user_chars, payload_chars, capped, estimate_tokens("x" * (system_chars + user_chars)),
                            completion.timing.to_dict() if completion else {"wall_s": round(time.perf_counter() - stamp, 3)},
                            completion.memory.to_dict() if completion else {}, len(text), error is None, error, str(dump.relative_to(self.run_dir)))
        if self.settings.save:
            write_json(dump, {"kind": kind, "label": label, "messages": messages, "response": text, "error": error,
                              "model": self.info.to_dict(), "record": asdict(record)})
        rate = record.timing.get("tokens_per_s")
        line = (f"  {kind:<5} {self.info.tag} {record.timing.get('wall_s', 0):.1f} s | ~{record.est_prompt_tokens:,} prompt tok"
                + (f" | {record.timing.get('eval_count')} gen tok @ {rate} tok/s" if rate else "")
                + (f" | {record.memory.get('ollama_model_size_bytes') / 1e9:.1f} GB in Ollama" if record.memory.get("ollama_model_size_bytes") else ""))
        print(line + (f" | ERROR {error}" if error else ""))
        if error:
            raise RuntimeError(error)
        return text, record

    # one source -----------------------------------------------------------------------
    def ingest_source(self, path: Path) -> IngestResult:
        started = time.perf_counter()
        relpath = path.relative_to(self.settings.vault).as_posix()
        name = source_note_name(path.name)
        source_id = source_id_for(path.name)
        if path.suffix.lower() not in (".md", ".txt"):
            msg = f"skipping {relpath}: only .md and .txt sources are supported; convert it to Markdown first."
            print(f"- {msg}")
            return IngestResult(relpath, source_id, "", "unsupported", message=msg)
        text = path.read_text(encoding="utf-8", errors="replace")
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        all_notes = list_notes(self.settings.vault)
        mine = [n for n in all_notes if n.frontmatter.get("source_id") == source_id]
        owners = {title_key(n.title): n.frontmatter.get("source_id") for n in all_notes}
        result = IngestResult(relpath, source_id, sha, "ingested")
        if mine and all(n.frontmatter.get("source_sha256") == sha for n in mine) and not self.force:
            result.action = "up-to-date"
            result.notes_written = [n.title for n in mine]
            result.message = f"up to date ({len(mine)} notes, source unchanged; use --force to regenerate)"
            print(f"- {relpath}: {result.message}")
            result.wall_s = round(time.perf_counter() - started, 2)
            return result
        print(f"- {relpath}: {'regenerating' if mine else 'ingesting'} ({len(text):,} chars, sha256 {sha[:12]}…)")
        sections = split_sections(text.split("\n"))
        doc_title = next((s.heading for s in sections if s.level == 1), name)
        existing_titles = [(n.title, n.folder) for n in all_notes]
        previous_titles = [n.title for n in mine]
        outline = outline_for_plan(sections, PLAN_OUTLINE_BUDGET)
        # PLAN ---------------------------------------------------------------------------
        plan = None
        problems: list = []
        for attempt in (1, 2):
            messages = build_plan_messages(name, doc_title, outline, existing_titles, previous_titles, self.max_notes)
            if attempt == 2 and problems:
                messages[-1]["content"] += "\n\nYour previous plan had these problems, fix them: " + "; ".join(problems[:8])
            try:
                reply, record = self._call("plan", messages, source_id, "", json_schema=PLAN_SCHEMA, payload_chars=len(outline))
            except RuntimeError as e:
                result.errors.append(str(e))
                record = None
                reply = ""
            if record:
                record.attempt = attempt
                result.calls.append(asdict(record))
            plan, problems = validate_plan(reply, sections, existing_titles, previous_titles, name, self.max_notes, source_id, owners)
            if plan:
                plan.origin = "model" if attempt == 1 else "model-retry"
                break
        if plan is None:
            plan = heuristic_plan(name, doc_title, sections, self.max_notes, previous_titles)
            result.errors.append("plan fell back to the heuristic (one note per group of sections): " + "; ".join(problems[:5]))
            print(f"  plan: model plan unusable ({'; '.join(problems[:3])}); using the heuristic plan")
        result.plan_origin = plan.origin
        print(f"  plan ({plan.origin}): " + "; ".join(f"{i.title} [{i.folder}]" for i in plan.notes))
        if self.dry_run:
            result.action = "dry-run"
            result.notes_written = [i.title for i in plan.notes]
            result.wall_s = round(time.perf_counter() - started, 2)
            return result
        # NOTES --------------------------------------------------------------------------
        assigned = assign_sections(plan, sections)
        planned_titles = [i.title for i in plan.notes]
        all_titles = planned_titles + [t for t, _ in existing_titles if t not in planned_titles]
        written: list = []
        for item in plan.notes:
            secs = assigned.get(item.title, [])
            body_text, capped = sections_text(secs, NOTE_TEXT_BUDGET)
            allowed = [t for t in all_titles if t != item.title]
            section_names = [s.heading for s in secs if s.heading_path]
            messages = build_note_messages(item.title, item.summary, allowed, name, section_names, body_text)
            try:
                reply, record = self._call("note", messages, source_id, item.title, payload_chars=len(body_text), capped=capped)
            except RuntimeError as e:
                result.errors.append(f"note {item.title!r}: {e}")
                continue
            result.calls.append(asdict(record))
            summary, details, related_lines = clean_note_body(reply)
            related = parse_related_lines(related_lines) + [(r.title, r.why) for r in item.related]
            related_md = linkify_related(related, allowed)
            sec_labels = ", ".join(f'"{h}"' for h in section_names[:6]) + (" and more" if len(section_names) > 6 else "")
            body = "\n".join([
                f"# {item.title}", "", "## Summary", "", summary or item.summary, "", "## Details", "",
                details or "(the model returned no details; see the source sections listed below)", "", "## Related", "",
                *(related_md or ["_No related notes yet._"]), "", "## Sources", "",
                f"- {source_link(name)}: `{relpath}`, sections {sec_labels or '(top of file)'}", ""])
            existing = find_note_by_title(self.settings.vault, item.title)
            target = existing.path if existing else note_path(self.settings.vault, item.folder, item.title)
            fm = {
                "title": item.title, "aliases": [slugify(item.title)], "topic": target.parent.name, "summary": item.summary,
                "sources": [relpath], "source_id": source_id, "source_sha256": sha, "sections_used": section_names,
                "created": today_iso(), "updated": today_iso(), "reviewed": False,
                "generated_by": self.info.tag, "generated_by_digest": self.info.digest or "", "note_id": f"{source_id}/{slugify(item.title)}",
                "plan_origin": plan.origin,
            }
            if existing:
                old = existing.frontmatter
                merged = {**old, **fm}
                merged["created"] = old.get("created") or fm["created"]
                if old.get("reviewed") is True and not self.overwrite_reviewed:
                    draft = self.run_dir / "ingest" / "drafts" / target.parent.name / target.name
                    merged["reviewed"] = True
                    write_note(draft, merged, body)
                    result.notes_drafted.append(item.title)
                    print(f"  kept reviewed note {target.relative_to(self.settings.vault)}; new draft saved to {draft.relative_to(self.run_dir)}")
                    continue
                fm = merged
                fm["reviewed"] = False
            write_note(target, fm, body)
            written.append(item.title)
            print(f"  wrote {target.relative_to(self.settings.vault)} ({len(body):,} chars)")
        result.notes_written = written
        result.notes_stale = [n.title for n in mine if n.title not in planned_titles]
        for stale in result.notes_stale:
            print(f"  note {stale!r} came from an earlier version of this source and is not in the new plan; left in place, review it")
        result.wall_s = round(time.perf_counter() - started, 2)
        return result

    # catalog, index, log --------------------------------------------------------------
    def finish(self, results: list) -> dict:
        vault = self.settings.vault
        for r in results:
            if r.action in ("unsupported", "dry-run"):
                continue
            path = vault / r.source
            text = path.read_text(encoding="utf-8", errors="replace")
            sections = split_sections(text.split("\n"))
            notes = [n for n in list_notes(vault) if n.frontmatter.get("source_id") == r.source_id]
            by_section: dict = {}
            for n in notes:
                for h in n.frontmatter.get("sections_used") or []:
                    by_section.setdefault(title_key(h), n.title)
            meta = self.catalog.get(r.source, {})
            spec = SourceSpec(
                name=source_note_name(path.name), relpath=r.source, source_id=r.source_id, sha256=r.sha256,
                copied_from=meta.get("copied_from", "unknown"), copied_on=meta.get("copied_on", "unknown"),
                description=meta.get("description", ""), ingested=self.started, generated_by=self.info.tag,
                generated_by_digest=self.info.digest or "",
                notes=[(n.title, n.summary) for n in sorted(notes, key=lambda n: n.title.lower())],
                sections=[(s.heading, s.start_line, s.end_line, by_section.get(title_key(s.heading))) for s in sections if s.heading_path],
            )
            write_source_note(vault, spec)
        notes = list_notes(vault)
        write_index_md(vault, notes, list_source_notes(vault), self.info.tag, self.started)
        index = build_index(vault, self.settings.index_dir)
        calls = [c for r in results for c in r.calls]
        totals = {
            "sources": len(results), "ingested": sum(r.action == "ingested" for r in results),
            "up_to_date": sum(r.action == "up-to-date" for r in results), "notes_written": sum(len(r.notes_written) for r in results if r.action == "ingested"),
            "notes_drafted": sum(len(r.notes_drafted) for r in results), "notes_in_vault": len(notes), "calls": len(calls),
            "total_wall_s": round(sum(r.wall_s for r in results), 2),
            "prompt_tokens": sum((c["timing"].get("prompt_eval_count") or 0) for c in calls),
            "generated_tokens": sum((c["timing"].get("eval_count") or 0) for c in calls),
            "median_tokens_per_s": _median([c["timing"].get("tokens_per_s") for c in calls if c["timing"].get("tokens_per_s")]),
            "max_ollama_size_bytes": max([c["memory"].get("ollama_model_size_bytes") or 0 for c in calls] + [0]) or None,
            "max_ollama_process_rss_bytes": max([c["memory"].get("ollama_process_rss_bytes") or 0 for c in calls] + [0]) or None,
            "harness_max_rss_bytes": max([c["memory"].get("harness_max_rss_bytes") or 0 for c in calls] + [0]) or None,
            "max_payload_chars": max([c["payload_chars"] for c in calls] + [0]), "payload_capped_calls": sum(c["payload_capped"] for c in calls),
            "index_passages": index.n_docs, "index_wiki_passages": index.stats()["wiki_passages"],
        }
        log = {"schema": "ingest-log/1", "run_id": self.settings.run_id, "started_at": self.started, "finished_at": utc_now_iso(),
               "model": self.info.to_dict(), "budgets": {"plan_outline_chars": PLAN_OUTLINE_BUDGET, "note_text_chars": NOTE_TEXT_BUDGET,
               "num_ctx": self.settings.num_ctx, "num_predict": NUM_PREDICT}, "totals": totals, "sources": [r.to_dict() for r in results]}
        log["log_file"] = f"ingest/{self.log_name}.json"
        if self.settings.save:
            write_json(self.run_dir / "ingest" / f"{self.log_name}.json", log)
            (self.run_dir / "ingest" / f"{self.log_name}.md").write_text(render_ingest_log(log), encoding="utf-8")
        return log


def _median(values: list):
    values = sorted(v for v in values if v is not None)
    if not values:
        return None
    mid = len(values) // 2
    return values[mid] if len(values) % 2 else round((values[mid - 1] + values[mid]) / 2, 1)


def render_ingest_log(log: dict) -> str:
    t = log["totals"]
    m = log["model"]
    lines = [f"# Ingest log for run {log['run_id']}", "",
             f"Model `{m.get('tag')}` ({m.get('backend')}, quantization {m.get('quantization_level')}, {m.get('parameter_size')}, digest `{m.get('digest')}`), "
             f"started {log['started_at']}, finished {log['finished_at']}.", "",
             "## Totals", "", "| Measure | Value |", "| --- | --- |"]
    for k, v in t.items():
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Text budget per call", "",
              f"The plan call receives the source outline capped at {log['budgets']['plan_outline_chars']:,} characters; each note call receives its sections capped at "
              f"{log['budgets']['note_text_chars']:,} characters; every call asks Ollama for a {log['budgets']['num_ctx']:,}-token context window. "
              f"Largest payload sent: {t['max_payload_chars']:,} characters; calls that hit the cap: {t['payload_capped_calls']}.", "",
              "## Sources", ""]
    for s in log["sources"]:
        lines.append(f"### {s['source']}")
        lines.append("")
        lines.append(f"- Action: {s['action']} ({s.get('message') or ''}); sha256 `{s['sha256'][:12]}`; plan origin: {s.get('plan_origin')}; wall {s['wall_s']} s")
        lines.append(f"- Notes written: {s['notes_written']}; drafted (reviewed notes kept): {s['notes_drafted']}; stale: {s['notes_stale']}")
        if s["errors"]:
            lines.append(f"- Problems: {s['errors']}")
        if s["calls"]:
            lines.append("")
            lines.append("| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |")
            lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
            for c in s["calls"]:
                tm = c["timing"]
                lines.append(f"| {c['kind']} | {c['attempt']} | {c['user_chars']:,} ({c['payload_chars']:,}) | {c['payload_capped']} | {c['est_prompt_tokens']:,} | "
                             f"{tm.get('prompt_eval_count') or ''} | {tm.get('eval_count') or ''} | {tm.get('tokens_per_s') or ''} | {tm.get('wall_s')} | {c['ok']} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def run_ingest(settings: Settings, backend, paths: list, *, force=False, overwrite_reviewed=False, max_notes=5, dry_run=False) -> dict:
    ensure_layout(settings.vault)
    sources = discover_sources(paths, settings)
    if not sources:
        raise UsageError(f"no source files found in {settings.raw_dir}. Copy Markdown or text files there first.")
    ingester = Ingester(settings, backend, force=force, overwrite_reviewed=overwrite_reviewed, max_notes=max_notes, dry_run=dry_run)
    print(f"wiki ingest · model {ingester.info.label()} ({backend.name}, local) · {len(sources)} source file(s) · run {settings.run_id}")
    results = [ingester.ingest_source(p) for p in sources]
    log = ingester.finish(results)
    t = log["totals"]
    print(f"\nDone: {t['ingested']} ingested, {t['up_to_date']} up to date, {t['notes_written']} notes written, {t['notes_in_vault']} notes in the vault, "
          f"{t['calls']} model calls, {t['total_wall_s']} s. Index: {t['index_passages']} passages.")
    if settings.save:
        print(f"Ingest log: {settings.run_dir / log['log_file'].replace('.json', '.md')}", file=sys.stderr)
    return log
