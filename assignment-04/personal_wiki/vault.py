"""Everything that reads or writes the Obsidian vault: notes, titles, links, the Sources catalog, index.md.

The vault has three parts. raw/ holds unchanged originals. wiki/<Folder>/<Title>.md holds
notes whose filename is a short descriptive title that matches the note's first heading.
wiki/Sources/<Name>.md is one catalog note per raw file. index.md is the landing page.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import FOLDERS, SOURCES_FOLDER
from .frontmatter import render_frontmatter, split_frontmatter
from .textutil import content_terms, slugify

NOTE_WORD = r"[A-Za-z0-9][A-Za-z0-9'&+.-]*"
TITLE_RE = re.compile(rf"^{NOTE_WORD}( (?:{NOTE_WORD}|-)){{1,5}}$")  # a lone hyphen allows qualifiers like "Memory - Computers"
ILLEGAL_CHARS = set('/\\:*?"<>|#^[]')
RESERVED = {"index", "readme", "sources", "source", "untitled", "note", "notes"}
HASH_WORD = re.compile(r"^[0-9a-f]{7,}$")
DATE_WORD = re.compile(r"^\d{4}-\d{2}(-\d{2})?$|^\d{8}$|^\d{4,}$")


@dataclass
class Note:
    path: Path
    frontmatter: dict
    body: str

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title") or self.path.stem)

    @property
    def folder(self) -> str:
        return self.path.parent.name

    @property
    def summary(self) -> str:
        return str(self.frontmatter.get("summary") or "")


@dataclass
class SourceSpec:
    name: str                     # "Pac-Man DQN README"
    relpath: str                  # "raw/Pac-Man DQN README.md"
    source_id: str                # "pac-man-dqn-readme"
    sha256: str
    copied_from: str = "unknown"
    copied_on: str = "unknown"
    description: str = ""
    ingested: str = ""
    generated_by: str = ""
    generated_by_digest: str = ""
    notes: list = field(default_factory=list)      # [(title, summary)]
    sections: list = field(default_factory=list)   # [(heading, start_line, end_line, note_title or None)]


def ensure_layout(vault: Path) -> None:
    from .errors import VaultMissing
    if not (vault / "raw").is_dir():
        raise VaultMissing(f"no vault at {vault} (expected raw/ and wiki/ inside it). Run from assignment-04/ or pass --vault PATH.")
    for folder in FOLDERS + (SOURCES_FOLDER,):
        (vault / "wiki" / folder).mkdir(parents=True, exist_ok=True)


def read_note(path: Path) -> Note:
    fm, body, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    return Note(path, fm, body)


def write_note(path: Path, frontmatter: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = render_frontmatter(frontmatter) + body.strip("\n") + "\n"
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def list_notes(vault: Path, include_sources: bool = False) -> list:
    wiki = vault / "wiki"
    if not wiki.is_dir():
        return []
    notes = []
    for p in sorted(wiki.rglob("*.md")):
        rel = p.relative_to(wiki).parts
        if any(part.startswith(".") for part in rel):
            continue
        if not include_sources and rel[0] == SOURCES_FOLDER:
            continue
        if include_sources is None:
            pass
        notes.append(read_note(p))
    return notes


def list_source_notes(vault: Path) -> list:
    folder = vault / "wiki" / SOURCES_FOLDER
    if not folder.is_dir():
        return []
    return [read_note(p) for p in sorted(folder.glob("*.md"))]


def normalize_title(title: str) -> str:
    t = str(title).strip().strip("`\"'").strip()
    t = re.sub(r"^#+\s*", "", t)
    t = t.replace(":", " ").replace("/", " ").replace("\\", " ").replace("|", " ")
    t = re.sub(r"[\"“”‘’*_`\[\]{}()<>?#^]", "", t)
    t = re.sub(r"[\s,;]+", " ", t).strip(" .-")
    if t.lower().endswith(".md"):
        t = t[:-3]
    return t


def validate_title(title: str) -> tuple:
    """Return (ok, reason). Titles are 2 to 6 words, readable, and never hashes, dates, or sentences."""
    if not title or not title.strip():
        return False, "empty title"
    if len(title) > 60:
        return False, "longer than 60 characters"
    if any(ch in ILLEGAL_CHARS for ch in title):
        return False, "contains a character that cannot be in a filename"
    if not TITLE_RE.match(title):
        return False, "must be 2 to 6 words of letters, digits, apostrophes, or hyphens"
    words = [w for w in title.split(" ") if w != "-"]
    if len(words) < 2 or not any(any(c.isalpha() for c in w) for w in words):
        return False, "needs at least one word with letters"
    for w in words:
        if HASH_WORD.match(w.lower()) or DATE_WORD.match(w):
            return False, f"'{w}' looks like an id, hash, or date"
    if title.lower() in RESERVED or title.lower().split(" ")[0] in RESERVED and len(words) == 1:
        return False, "reserved name"
    return True, ""


def title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def find_existing_title(title: str, existing) -> str | None:
    """Exact match ignoring case and punctuation, else a stemmed-word overlap (Jaccard >= 0.75)."""
    key = title_key(title)
    for e in existing:
        if title_key(e) == key:
            return e
    mine = set(content_terms(title))
    if not mine:
        return None
    best, best_score = None, 0.0
    for e in existing:
        theirs = set(content_terms(e))
        if not theirs:
            continue
        score = len(mine & theirs) / len(mine | theirs)
        if score > best_score:
            best, best_score = e, score
    return best if best_score >= 0.75 else None


def disambiguate_title(title: str, source_name: str, taken) -> str:
    """Make a title unique by adding a distinguishing word from the source name, then a counter."""
    taken_keys = {title_key(t) for t in taken}
    if title_key(title) not in taken_keys:
        return title
    for word in [w for w in re.findall(NOTE_WORD, source_name) if w.lower() not in {"readme", "notes", "md"}]:
        candidate = normalize_title(f"{title} {word}")
        ok, _ = validate_title(candidate)
        if ok and title_key(candidate) not in taken_keys:
            return candidate
    for i in range(2, 20):
        candidate = f"{title} {i}"
        if validate_title(candidate)[0] and title_key(candidate) not in taken_keys:
            return candidate
    return title


def note_path(vault: Path, folder: str, title: str) -> Path:
    return vault / "wiki" / folder / f"{title}.md"


def find_note_by_title(vault: Path, title: str):
    key = title_key(title)
    for note in list_notes(vault):
        if title_key(note.title) == key or title_key(note.path.stem) == key:
            return note
    return None


def linkify_related(items, allowed) -> list:
    """Turn (title, why) pairs into '- [[Title]]: why' lines, keeping only allowed titles."""
    by_key = {title_key(t): t for t in allowed}
    lines, seen = [], set()
    for title, why in items:
        target = by_key.get(title_key(normalize_title(title)))
        if not target or target in seen:
            continue
        seen.add(target)
        why = (why or "").strip().rstrip(".")
        lines.append(f"- [[{target}]]: {why}" if why else f"- [[{target}]]")
    return lines


def source_id_for(filename: str) -> str:
    return slugify(Path(filename).stem)


def source_note_name(filename: str) -> str:
    return Path(filename).stem


def source_link(name: str) -> str:
    return f"[[wiki/{SOURCES_FOLDER}/{name}|{name}]]"


def raw_link(relpath: str) -> str:
    stem = relpath[:-3] if relpath.lower().endswith(".md") else relpath
    return f"[[{stem}|{relpath}]]"


def write_source_note(vault: Path, spec: SourceSpec) -> Path:
    fm = {
        "title": spec.name, "topic": SOURCES_FOLDER, "source_path": spec.relpath, "source_id": spec.source_id,
        "source_sha256": spec.sha256, "copied_from": spec.copied_from, "copied_on": spec.copied_on,
        "ingested": spec.ingested, "generated_by": spec.generated_by, "generated_by_digest": spec.generated_by_digest,
        "notes": [t for t, _ in spec.notes],
    }
    lines = [f"# {spec.name}", ""]
    lines.append(f"Catalog entry for one raw source. The original is unchanged at {raw_link(spec.relpath)} "
                 f"(sha256 `{spec.sha256[:12]}…`), copied from `{spec.copied_from}` in the course repository on {spec.copied_on}.")
    if spec.description:
        lines += ["", spec.description]
    lines += ["", "## Notes derived from this source"]
    if spec.notes:
        lines += [f"- [[{t}]]: {s}" if s else f"- [[{t}]]" for t, s in spec.notes]
    else:
        lines.append("_No notes yet._")
    if spec.sections:
        lines += ["", "## Sections of the source"]
        for heading, start, end, target in spec.sections:
            where = f", in [[{target}]]" if target else ", not used by a note"
            lines.append(f"- {heading or '(top of file)'} (lines {start}-{end}){where}")
    path = vault / "wiki" / SOURCES_FOLDER / f"{spec.name}.md"
    write_note(path, fm, "\n".join(lines))
    return path


def write_index_md(vault: Path, notes, source_notes, model_tag: str, when: str) -> Path:
    lines = ["# Wiki index", "",
             f"Landing page for the notes in `wiki/`, regenerated by `wiki ingest` on {when} with {model_tag}. "
             "One line per note, taken from the note's summary. Raw sources are listed last and are never edited.", ""]
    for folder in FOLDERS:
        lines.append(f"## {folder}")
        group = sorted((n for n in notes if n.folder == folder), key=lambda n: n.title.lower())
        if group:
            lines += [f"- [[{n.title}]]: {n.summary}" if n.summary else f"- [[{n.title}]]" for n in group]
        else:
            lines.append("_No notes yet._")
        lines.append("")
    lines.append("## Sources")
    if source_notes:
        for n in sorted(source_notes, key=lambda n: n.title.lower()):
            count = len(n.frontmatter.get("notes") or [])
            copied = n.frontmatter.get("copied_from", "unknown")
            lines.append(f"- {source_link(n.title)}: copied from `{copied}`, {count} note{'s' if count != 1 else ''}")
    else:
        lines.append("_No sources ingested yet._")
    lines.append("")
    path = vault / "index.md"
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def resolve_links(vault: Path, body: str) -> tuple:
    """Return (resolved, dangling) lists of [[link]] targets in a note body."""
    targets = re.findall(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", body)
    all_stems = {}
    for p in (vault / "wiki").rglob("*.md"):
        all_stems.setdefault(p.stem.lower(), []).append(p)
        all_stems.setdefault(p.relative_to(vault).with_suffix("").as_posix().lower(), []).append(p)
    for p in (vault / "raw").glob("*"):
        all_stems.setdefault(p.stem.lower(), []).append(p)
        all_stems.setdefault(p.relative_to(vault).with_suffix("").as_posix().lower(), []).append(p)
    resolved, dangling = [], []
    for t in targets:
        (resolved if t.strip().lower() in all_stems else dangling).append(t.strip())
    return resolved, dangling
