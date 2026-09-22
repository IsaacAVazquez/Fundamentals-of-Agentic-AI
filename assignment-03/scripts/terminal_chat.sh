#!/usr/bin/env bash
# Start chat.py on the corpus-extension model for a real Terminal session, the one behind
# results/chat/chat_terminal.png. chat.py seeds each turn from 2026 plus its index, so typing
# the same prompts in the same order reproduces results/chat/chat_transcript.json.
# Usage: scripts/terminal_chat.sh [transcript name, default terminal_session]
# chat.py refuses to overwrite a transcript, so pass a new name for any extra session.
set -euo pipefail
cd "$(dirname "$0")/.."
cat <<'PROMPTS'
Type these five prompts in order, pressing Enter after each, then /quit:
  the customer
  the opposite of cold is
  leo gave nora a lamp . nora thanked
  the cup is not white . it is black . the cup is
  what is the capital of france ?
PROMPTS
exec .venv/bin/python chat.py --model results/expanded/model.pt --transcript "results/chat/${1:-terminal_session}.json"
