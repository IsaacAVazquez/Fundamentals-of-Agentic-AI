"""The command-line interface: `wiki help|ingest|index|search|ask|chat|eval|doctor|manifest`.

Each subcommand is thin: it resolves settings, opens the index or the backend it needs,
and hands off to the module that implements the mode. `search` never touches a backend,
so it works with Ollama stopped. Every WikiError becomes one line on stderr and an exit code.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import DEFAULT_K, DEFAULT_MAX_NOTES, load_settings
from .errors import UsageError, WikiError

DESCRIPTION = """wiki: a personal wiki CLI that talks to your own notes with a local Gemma model.

modes
  chat    the personal assistant: conversation context, persona, retrieval only when a turn needs notes
  ask     a standalone factual answer with citations from retrieved evidence, or "Insufficient evidence"
  search  matching original passages with source paths; no model call, works with Ollama stopped
  ingest  read vault/raw with local Gemma, write linked wiki notes, update index.md and the retrieval index
  doctor  check the vault, the index, Ollama, the model, the network (offline?) and the device

configuration (flags win over environment variables)
  --vault PATH        WIKI_VAULT        the Obsidian vault (default: assignment-04/vault)
  --model TAG         WIKI_MODEL        Ollama model tag (default: gemma4:e4b)
  --host URL          WIKI_HOST         Ollama server (default: http://localhost:11434)
  --backend NAME      WIKI_BACKEND      ollama (default) or fake (tests only)
  --results-dir PATH  WIKI_RESULTS_DIR  where evidence is saved (default: assignment-04/results)
  --run-id ID         WIKI_RUN_ID       results subfolder for this run (default: timestamp-model)
  --index-dir PATH    WIKI_INDEX_DIR    retrieval index location (default: assignment-04/index)

required inputs: Markdown or text sources in vault/raw, wiki-instructions.md and persona.md next to the package,
and, for ask/chat/ingest, a running Ollama with the model pulled (scripts/pull_model.sh)."""


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--vault", default=argparse.SUPPRESS, help="path to the Obsidian vault")
    common.add_argument("--results-dir", dest="results_dir", default=argparse.SUPPRESS, help="where results are saved")
    common.add_argument("--run-id", dest="run_id", default=argparse.SUPPRESS, help="results subfolder name")
    common.add_argument("--index-dir", dest="index_dir", default=argparse.SUPPRESS, help="retrieval index folder")
    common.add_argument("--backend", choices=["ollama", "fake"], default=argparse.SUPPRESS, help="model backend")
    common.add_argument("--model", default=argparse.SUPPRESS, help="Ollama model tag")
    common.add_argument("--host", default=argparse.SUPPRESS, help="Ollama server URL")
    common.add_argument("-v", "--verbose", action="store_true", default=argparse.SUPPRESS)
    common.add_argument("--no-save", dest="no_save", action="store_true", default=argparse.SUPPRESS, help="do not write results files")

    parser = argparse.ArgumentParser(prog="wiki", description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[common])
    parser.add_argument("--version", action="version", version=f"wiki {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="command")

    p = sub.add_parser("help", parents=[common], help="show this help, or help for one command")
    p.add_argument("topic", nargs="?")

    p = sub.add_parser("ingest", parents=[common], help="turn sources in vault/raw into linked wiki notes with local Gemma")
    p.add_argument("paths", nargs="*", help="source files or folders inside vault/raw (default: vault/raw)")
    p.add_argument("--force", action="store_true", help="regenerate even when the source is unchanged")
    p.add_argument("--overwrite-reviewed", action="store_true", help="also overwrite notes marked reviewed: true")
    p.add_argument("--max-notes", type=int, default=DEFAULT_MAX_NOTES, help="notes per source the plan may propose (2-6)")
    p.add_argument("--dry-run", action="store_true", help="plan only; write nothing")

    p = sub.add_parser("index", parents=[common], help="rebuild the retrieval index from the vault")
    p.add_argument("--check", action="store_true", help="report whether the index is fresh; exit 1 if stale")

    p = sub.add_parser("search", parents=[common], help="show matching original passages and paths; no model call")
    p.add_argument("query")
    p.add_argument("-k", type=int, default=argparse.SUPPRESS, help=f"passages to return (default {DEFAULT_K})")
    p.add_argument("--scope", choices=["raw", "wiki", "all"], default=argparse.SUPPRESS)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("ask", parents=[common], help="a standalone cited answer from retrieved evidence")
    p.add_argument("question")
    p.add_argument("--mode", choices=["local", "online"], default="local", help="local is the default and the only mode built")
    p.add_argument("-k", type=int, default=argparse.SUPPRESS)
    p.add_argument("--scope", choices=["raw", "wiki", "all"], default=argparse.SUPPRESS)
    p.add_argument("--id", dest="card_id", help="evidence card id (default: generated)")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("chat", parents=[common], help="the personal assistant with conversation context")
    p.add_argument("--script", help="file of messages, one per line, run instead of interactive input")
    p.add_argument("--name", help="transcript name (default: script name or timestamp)")
    p.add_argument("--no-retrieval", action="store_true", help="never consult the notes (persona and conversation only)")
    p.add_argument("-k", type=int, default=argparse.SUPPRESS)
    p.add_argument("--scope", choices=["raw", "wiki", "all"], default=argparse.SUPPRESS)

    p = sub.add_parser("eval", parents=[common], help="run the fixed ask-mode question set and write evidence cards")
    p.add_argument("questions", nargs="?", default="tests/questions.json")

    p = sub.add_parser("doctor", parents=[common], help="check the setup, the model, the network, and the device")
    p.add_argument("--require-offline", action="store_true", help="exit 11 if the internet is reachable")
    p.add_argument("--json", action="store_true")
    p.add_argument("--save", action="store_true", help="write doctor.json into the run folder")

    sub.add_parser("manifest", parents=[common], help="collect this run's results into manifest.json")
    return parser


def cmd_ingest(args) -> int:
    from .backends import get_backend
    from .ingest import run_ingest
    settings = load_settings(args)
    backend = get_backend(settings)
    log = run_ingest(settings, backend, [Path(p) for p in args.paths], force=args.force, overwrite_reviewed=args.overwrite_reviewed,
                     max_notes=args.max_notes, dry_run=args.dry_run)
    usable = [s for s in log["sources"] if s["action"] in ("ingested", "up-to-date", "dry-run")]
    return 0 if usable else 1


def cmd_index(args) -> int:
    from .index import build_index, index_is_fresh
    settings = load_settings(args)
    if args.check:
        fresh = index_is_fresh(settings)
        print("index is fresh" if fresh else "index is missing or stale")
        return 0 if fresh else 1
    index = build_index(settings.vault, settings.index_dir)
    s = index.stats()
    print(f"Indexed {s['passages']} passages from {s['files']} files ({s['raw_passages']} raw, {s['wiki_passages']} wiki) into {settings.index_dir}")
    return 0


def cmd_search(args) -> int:
    from .evidence import write_search_record
    from .index import ensure_index
    from .retrieval import search
    settings = load_settings(args)
    index = ensure_index(settings)
    hits = search(index, args.query, k=settings.k, scope=settings.scope)
    if args.json:
        print(json.dumps({"query": args.query, "k": settings.k, "scope": settings.scope, "model_called": False, "hits": [h.to_dict() for h in hits]}, indent=2, ensure_ascii=False))
    else:
        print(f"search · {len(hits)} passage(s) for \"{args.query}\" · k={settings.k} · scope={settings.scope} · no model call")
        for h in hits:
            p = h.passage
            print(f"\n[{h.rank}] {p.path} # {p.heading} (lines {p.start_line}-{p.end_line}, {p.kind}, score {h.score:.2f}, matched: {', '.join(h.matched_terms)})")
            print("\n".join("    " + l for l in p.text.split("\n")))
        if not hits:
            print("No passages matched. Try other words, or check that vault/raw has sources and the index is built (wiki index).")
    if settings.save:
        jp, mp = write_search_record(settings.run_dir, args.query, hits, settings.scope, settings.k, index.stats())
        print(f"\nSaved: {mp}", file=sys.stderr)
    return 0


def cmd_ask(args) -> int:
    if args.mode == "online":
        raise UsageError("online mode is not built in this version; only --mode local (the default) works. Nothing was sent anywhere.")
    from .ask import render_answer, run_ask
    from .backends import get_backend
    from .index import ensure_index
    settings = load_settings(args)
    backend = get_backend(settings)
    index = ensure_index(settings)
    card = run_ask(settings, args.question, backend, index, card_id=args.card_id, mode=args.mode)
    if args.json:
        print(json.dumps(card.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(render_answer(card))
        if settings.save:
            print(f"Evidence card: {settings.run_dir / 'ask' / (card.id + '.md')}", file=sys.stderr)
    return 0


def cmd_chat(args) -> int:
    from .backends import get_backend
    from .chat import run_chat
    from .index import ensure_index
    settings = load_settings(args)
    backend = get_backend(settings)
    index = ensure_index(settings)
    run_chat(settings, backend, index, script=Path(args.script) if args.script else None, name=args.name, retrieval_enabled=not args.no_retrieval)
    return 0


def cmd_eval(args) -> int:
    from .backends import get_backend
    from .evalrun import run_eval
    from .index import ensure_index
    settings = load_settings(args)
    backend = get_backend(settings)
    index = ensure_index(settings)
    run_eval(settings, backend, index, Path(args.questions))
    return 0


def cmd_doctor(args) -> int:
    from .doctor import render_report, run_doctor, save_report
    settings = load_settings(args)
    report = run_doctor(settings, require_offline=args.require_offline)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_report(report))
    if args.save:
        path = save_report(settings, report)
        print(f"Saved: {path}", file=sys.stderr)
    return report["exit_code"]


def cmd_manifest(args) -> int:
    from .evidence import write_manifest
    settings = load_settings(args)
    path = write_manifest(settings)
    print(f"Wrote {path}")
    return 0


HANDLERS = {"ingest": cmd_ingest, "index": cmd_index, "search": cmd_search, "ask": cmd_ask, "chat": cmd_chat,
            "eval": cmd_eval, "doctor": cmd_doctor, "manifest": cmd_manifest}


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in (None, "help"):
        topic = getattr(args, "topic", None)
        if topic and topic in HANDLERS:
            parser.parse_args([topic, "--help"])
        elif topic:
            print(f"wiki: unknown command {topic!r}; try \"wiki help\"", file=sys.stderr)
            return 2
        parser.print_help()
        return 0
    try:
        return HANDLERS[args.command](args)
    except WikiError as e:
        print(f"wiki: {e}", file=sys.stderr)
        return e.exit_code
    except KeyboardInterrupt:
        print("\nwiki: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
