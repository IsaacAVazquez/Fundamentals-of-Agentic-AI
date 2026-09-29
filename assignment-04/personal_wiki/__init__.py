"""personal_wiki: the CLI and harness behind the `wiki` command.

The harness manages modes (chat, ask, search, ingest), instructions, conversation
context, retrieval, prompt assembly, local model calls, citation checks, errors,
and saved outputs. The model (local Gemma through Ollama) only ever sees the text
this package sends it.
"""

__version__ = "0.1.0"
