"""Turn a Markdown file into retrieval passages that keep their source path, heading, and line range.

Sections start at H1 to H3 headings (a `#` line inside a fenced code block is not a
heading). Inside a section, blocks (paragraphs, whole tables, whole fenced or HTML
blocks) are packed into passages of at most PASSAGE_MAX_CHARS characters. A block that
is too long on its own is split at sentence, row, or line boundaries. The passage text
is the source text verbatim, so `wiki search` shows original passages.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from .config import PASSAGE_MAX_CHARS, PASSAGE_MIN_CHARS
from .frontmatter import split_frontmatter
from .textutil import split_sentences

HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
TABLE_LINE_RE = re.compile(r"^\s*\|")
LIST_LINE_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
HTML_OPEN_RE = re.compile(r"^\s*<(table|details|div|figure|blockquote|ul|ol)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Passage:
    id: str
    path: str                     # vault-relative POSIX path, e.g. "raw/Pac-Man DQN README.md"
    kind: str                     # "raw" or "wiki"
    heading_path: tuple           # e.g. ("Ms. Pac-Man DQN", "What happened", "The final run, 450 games")
    start_line: int               # 1-based, inclusive, in the source file
    end_line: int
    text: str                     # verbatim source lines
    extra_terms: tuple = ()       # indexed but never shown: a wiki note's title and summary

    @property
    def heading(self) -> str:
        return self.heading_path[-1] if self.heading_path else "(top of file)"

    def label(self) -> str:
        return f"{self.path} # {self.heading}"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "path": self.path, "kind": self.kind, "heading_path": list(self.heading_path),
            "start_line": self.start_line, "end_line": self.end_line, "text": self.text,
            "extra_terms": list(self.extra_terms),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Passage":
        return cls(d["id"], d["path"], d["kind"], tuple(d["heading_path"]), d["start_line"], d["end_line"],
                   d["text"], tuple(d.get("extra_terms", ())))


@dataclass
class Section:
    heading_path: tuple
    level: int
    start_line: int               # line of the heading (or 1 for text before the first heading)
    body_start_line: int
    body_lines: list

    @property
    def heading(self) -> str:
        return self.heading_path[-1] if self.heading_path else ""

    @property
    def end_line(self) -> int:
        return self.body_start_line + len(self.body_lines) - 1 if self.body_lines else self.start_line

    def body_text(self) -> str:
        return "\n".join(self.body_lines).strip("\n")


@dataclass(frozen=True)
class Block:
    start_line: int
    end_line: int
    text: str
    kind: str                     # paragraph | table | fence | html | list


def split_sections(lines: list, first_line_no: int = 1) -> list:
    """Split lines into sections at H1-H3 headings, ignoring headings inside fenced code."""
    sections: list = []
    stack: list = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    current = Section((), 0, first_line_no, first_line_no, [])
    for offset, line in enumerate(lines):
        line_no = first_line_no + offset
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence, fence_char, fence_len = True, marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len:
                in_fence = False
            current.body_lines.append(line)
            continue
        heading = None if in_fence else HEADING_RE.match(line)
        if heading:
            sections.append(current)
            level, title = len(heading.group(1)), heading.group(2).strip()
            stack = [s for s in stack if s[0] < level] + [(level, title)]
            current = Section(tuple(t for _, t in stack), level, line_no, line_no + 1, [])
        else:
            current.body_lines.append(line)
    sections.append(current)
    return sections


def group_blocks(body_lines: list, first_line_no: int) -> list:
    """Group a section's lines into blocks: paragraphs, tables, fenced code, HTML, and lists."""
    blocks: list = []
    i = 0
    n = len(body_lines)

    def emit(start: int, end: int, kind: str) -> None:
        text = "\n".join(body_lines[start:end + 1]).strip("\n")
        if text.strip():
            blocks.append(Block(first_line_no + start, first_line_no + end, text, kind))

    while i < n:
        line = body_lines[i]
        if not line.strip():
            i += 1
            continue
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            j = i + 1
            while j < n:
                close = FENCE_RE.match(body_lines[j])
                if close and close.group(1)[0] == marker[0] and len(close.group(1)) >= len(marker):
                    break
                j += 1
            emit(i, min(j, n - 1), "fence")
            i = j + 1
            continue
        if TABLE_LINE_RE.match(line):
            j = i
            while j + 1 < n and TABLE_LINE_RE.match(body_lines[j + 1]):
                j += 1
            emit(i, j, "table")
            i = j + 1
            continue
        if HTML_OPEN_RE.match(line):
            tag = HTML_OPEN_RE.match(line).group(1).lower()
            close_re = re.compile(rf"</{tag}\s*>", re.IGNORECASE)
            j = i
            while j < n and not close_re.search(body_lines[j]):
                j += 1
            emit(i, min(j, n - 1), "html")
            i = j + 1
            continue
        j = i
        while j + 1 < n and body_lines[j + 1].strip() and not FENCE_RE.match(body_lines[j + 1]) \
                and not TABLE_LINE_RE.match(body_lines[j + 1]) and not HTML_OPEN_RE.match(body_lines[j + 1]):
            j += 1
        kind = "list" if LIST_LINE_RE.match(line) else "paragraph"
        emit(i, j, kind)
        i = j + 1
    return blocks


def _split_lines_into_pieces(block: Block, keep_header: bool = False) -> list:
    """Split a block line by line into pieces of at most PASSAGE_MAX_CHARS, keeping a table header on each piece."""
    lines = block.text.split("\n")
    header = lines[:2] if keep_header and len(lines) > 2 else []
    body = lines[2:] if header else lines
    body_start = block.start_line + (2 if header else 0)
    pieces: list = []
    cur: list = []
    cur_start = body_start
    header_len = sum(len(h) + 1 for h in header)
    for offset, line in enumerate(body):
        if cur and header_len + sum(len(l) + 1 for l in cur) + len(line) > PASSAGE_MAX_CHARS:
            pieces.append(Block(cur_start, body_start + offset - 1, "\n".join(header + cur), block.kind))
            cur, cur_start = [], body_start + offset
        cur.append(line)
    if cur:
        pieces.append(Block(cur_start, body_start + len(body) - 1, "\n".join(header + cur), block.kind))
    return pieces


def _split_paragraph(block: Block) -> list:
    """Split a long paragraph at sentence boundaries; line numbers stay those of the paragraph."""
    sentences = split_sentences(block.text.replace("\n", " "))
    pieces: list = []
    cur: list = []
    for sentence in sentences:
        candidate = " ".join(cur + [sentence])
        if cur and len(candidate) > PASSAGE_MAX_CHARS:
            pieces.append(Block(block.start_line, block.end_line, " ".join(cur), block.kind))
            cur = []
        cur.append(sentence)
    if cur:
        pieces.append(Block(block.start_line, block.end_line, " ".join(cur), block.kind))
    return pieces


def split_oversize(block: Block) -> list:
    if len(block.text) <= PASSAGE_MAX_CHARS:
        return [block]
    if block.kind == "table":
        return _split_lines_into_pieces(block, keep_header=True)
    if block.kind in ("fence", "list", "html"):
        return _split_lines_into_pieces(block)
    return _split_paragraph(block)


def pack_blocks(blocks: list) -> list:
    """Pack pieces into passages of at most PASSAGE_MAX_CHARS characters; merge a short tail into the previous passage."""
    groups: list = []
    cur: list = []
    cur_len = 0
    for block in blocks:
        for piece in split_oversize(block):
            extra = len(piece.text) + (2 if cur else 0)
            if cur and cur_len + extra > PASSAGE_MAX_CHARS:
                groups.append(cur)
                cur, cur_len = [], 0
                extra = len(piece.text)
            cur.append(piece)
            cur_len += extra
    if cur:
        groups.append(cur)
    if len(groups) >= 2:
        last_len = sum(len(p.text) for p in groups[-1]) + 2 * (len(groups[-1]) - 1)
        prev_len = sum(len(p.text) for p in groups[-2]) + 2 * (len(groups[-2]) - 1)
        if last_len < PASSAGE_MIN_CHARS and prev_len + 2 + last_len <= PASSAGE_MAX_CHARS + PASSAGE_MIN_CHARS:
            groups[-2].extend(groups.pop())
    return groups


def _passage_id(path: str, start_line: int, text: str) -> str:
    return hashlib.sha1(f"{path}|{start_line}|{text}".encode("utf-8")).hexdigest()[:12]


def chunk_markdown(text: str, path: str, kind: str) -> list:
    """Chunk one file's text into passages. Wiki notes lose their frontmatter and their Sources section."""
    extra_terms: tuple = ()
    offset = 0
    if kind == "wiki":
        fm, body, offset = split_frontmatter(text)
        if offset:
            text = body
        extra_terms = tuple(str(fm[k]) for k in ("title", "summary") if fm.get(k))
    lines = text.split("\n")
    passages: list = []
    for section in split_sections(lines, first_line_no=offset + 1):
        if kind == "wiki" and section.heading.strip().lower() in ("sources", "source"):
            continue
        blocks = group_blocks(section.body_lines, section.body_start_line)
        for group in pack_blocks(blocks):
            body = "\n\n".join(p.text for p in group)
            start, end = group[0].start_line, group[-1].end_line
            passages.append(Passage(_passage_id(path, start, body), path, kind, section.heading_path,
                                    start, end, body, extra_terms))
    return passages


def collect_vault_files(vault: Path) -> list:
    """Vault-relative POSIX paths of every .md/.txt file under raw/ and wiki/, sorted."""
    files: list = []
    for sub in ("raw", "wiki"):
        base = vault / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            rel = p.relative_to(vault).as_posix()
            if any(part.startswith(".") for part in p.relative_to(vault).parts) or rel.startswith("wiki/Sources/"):
                continue  # hidden files, and the Sources catalog notes, which are navigation rather than evidence
            if p.suffix.lower() in (".md", ".txt") and p.is_file():
                files.append(rel)
    return files


def chunk_file(vault: Path, relpath: str) -> list:
    kind = "raw" if relpath.startswith("raw/") else "wiki"
    text = (vault / relpath).read_text(encoding="utf-8", errors="replace")
    return chunk_markdown(text, relpath, kind)
