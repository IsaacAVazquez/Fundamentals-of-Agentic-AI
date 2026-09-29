"""A minimal YAML-frontmatter reader and writer for the keys this harness writes.

Supported: `key: scalar` (string, integer, true/false, quoted string), block lists
(`key:` followed by `  - item` lines), and flow lists (`[a, b]`) on read. Unknown
keys are kept as strings so a note edited in Obsidian survives a rewrite.
"""
from __future__ import annotations

import re

_INT = re.compile(r"^-?\d+$")
_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s+(.*))?$")


def _parse_scalar(raw: str):
    raw = raw.strip()
    if raw == "":
        return ""
    if raw in ("true", "True"):
        return True
    if raw in ("false", "False"):
        return False
    if _INT.match(raw):
        return int(raw)
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(raw) >= 2 and raw[0] == raw[-1] == "'":
        return raw[1:-1].replace("''", "'")
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [_parse_scalar(p) for p in _split_flow(inner)] if inner else []
    return raw


def _split_flow(inner: str) -> list[str]:
    parts, cur, quote = [], "", None
    for ch in inner:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            cur += ch
        elif ch == ",":
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def parse_frontmatter(lines: list[str]) -> dict:
    """Parse the lines between the `---` markers."""
    data: dict = {}
    key = None
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and key is not None and line.strip().startswith("- "):
            item = line.strip()[2:]
            if not isinstance(data.get(key), list):
                data[key] = []
            data[key].append(_parse_scalar(item))
            continue
        m = _KEY.match(line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2)
        data[key] = _parse_scalar(raw) if raw is not None and raw.strip() != "" else ""
    for k, v in list(data.items()):
        if v == "" and k in data and isinstance(v, str):
            pass
    return data


def split_frontmatter(text: str) -> tuple[dict, str, int]:
    """Return (frontmatter dict, body text, number of leading lines that belong to the frontmatter)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text, 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return parse_frontmatter(lines[1:i]), "\n".join(lines[i + 1:]), i + 1
    return {}, text, 0


def _render_scalar(value) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if value is None:
        return ""
    s = str(value)
    needs_quotes = (
        s == "" or ": " in s or s.endswith(":") or "#" in s or s.startswith(("[", "{", "'", '"', "-", "*", "&", "!", "%", "@", "`"))
        or s in ("true", "false", "True", "False", "null", "~") or _INT.match(s) or s != s.strip()
    )
    if needs_quotes:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def render_frontmatter(data: dict) -> str:
    out = ["---"]
    for key, value in data.items():
        if isinstance(value, (list, tuple)):
            if not value:
                out.append(f"{key}: []")
            else:
                out.append(f"{key}:")
                out.extend(f"  - {_render_scalar(v)}" for v in value)
        else:
            out.append(f"{key}: {_render_scalar(value)}")
    out.append("---")
    return "\n".join(out) + "\n"
