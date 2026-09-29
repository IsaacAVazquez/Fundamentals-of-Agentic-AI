# What this CLI is doing

This is a plain-language walkthrough of the personal wiki command in this folder. The README is the graded document and holds the device, the model, the measurements, the evidence, and the explanation. This file is for anyone who opens `personal_wiki/` and wants to know what each part does, including people who have not built anything with a language model before.

The short version is that a small program on my laptop keeps a folder of my own notes, cuts them into passages it can search, and, when I ask a question, finds the handful of passages that match, pastes them into a prompt along with a short set of rules, and hands that prompt to a Gemma model running on the same laptop through Ollama. The model writes an answer from those passages and marks each fact with the number of the passage it came from, and the program checks that every number points at a passage it actually sent. Nothing leaves the machine, and the model never reads a file on its own.

## Four words that mean four different things

The model is Gemma. It only ever sees the text my program sends it, a system message and a user message, and it sends text back. It does not know my folder exists.

The retrieval tool is `personal_wiki/retrieval.py` with the index in `personal_wiki/index.py`. Given a few words it returns the best-matching passages, each with its file path, its heading, and its line numbers. `wiki search` prints exactly what this tool returns, so I can check whether the right evidence is being found before I judge anything the model says.

The RAG workflow is retrieve, then prompt, then generate, then check. `wiki ask` does that once per question, from scratch, with no memory of any conversation.

The harness is everything else in `personal_wiki/`: choosing the mode, loading the right instruction file, keeping the chat's recent turns, deciding whether a chat message needs the notes, building the prompt, calling Ollama, checking citations, turning errors into a one-line message with an exit code, and saving every result under `results/`.

## What each piece does

| File | What it does |
| --- | --- |
| `cli.py` | Reads the command line and calls one mode. `search` never loads a model, so it works with Ollama stopped |
| `config.py` | Decides which vault, model, and results folder to use, from flags, then environment variables, then defaults, and holds every size budget |
| `chunking.py` | Cuts a Markdown file into passages at headings, keeping tables and code blocks whole, ignoring `#` lines inside code blocks, and remembering line numbers |
| `index.py` | Builds the BM25 keyword index over every passage from `vault/raw` and `vault/wiki` and rebuilds it when the vault changes |
| `retrieval.py` | Scores passages for a query, with a small synonym map so "machine" also finds "laptop", and trims the list to a character budget |
| `prompts.py` | Assembles every prompt: the ask prompt from `wiki-instructions.md`, the chat prompt from `persona.md`, and the routing, plan, and note prompts used by chat and ingest |
| `backends/ollama.py` | Talks to Ollama over HTTP, records the model's tag, digest, and quantization, and captures timing and memory for every call |
| `backends/fake.py` | A stand-in model for the tests. It copies sentences from the passages it is given and never invents anything, which is enough to test the harness without a real model |
| `ask.py` | The RAG workflow with the citation check and the "Insufficient evidence" detection |
| `chat.py` | The assistant: conversation memory, the retrieval decision, and the scripted mode-check runs |
| `ingest.py` | Reads a raw source, asks the model for a plan of notes, asks for each note's body, then writes the notes, the catalog page, and the index page |
| `vault.py` | Reads and writes notes, validates titles, builds links only to notes that exist, and regenerates `wiki/Sources/` and `index.md` |
| `evidence.py` | Writes the evidence cards, transcripts, search records, and the run manifest |
| `doctor.py` | Checks the setup, probes whether the internet is reachable, and reads the device's specs |
| `evalrun.py` | Runs the four fixed questions and compares each card with the expectation written before the run |

## How one question travels through the code

Take `wiki ask "What hardware did I train the nanoGPT model on for Assignment 3?"`. `cli.py` reads the flags and calls `cmd_ask`, which refuses `--mode online` before doing anything else, builds the settings, opens the Ollama backend, and loads the index, rebuilding it first if any file in the vault changed since the last build. Then `ask.run_ask` tokenizes the question, drops words like "what" and "did", stems the rest, adds the synonyms, and scores every passage with BM25. It keeps the top six, then keeps as many of those as fit in 5,000 characters, and numbers them 1 to k. `prompts.build_ask_messages` puts the research rules from `wiki-instructions.md` in the system message and the numbered passages plus the question in the user message. `backends/ollama.py` posts that to `/api/chat` at temperature 0 with an 8,192-token context and reads back the text, the token counts, and the durations, then asks `/api/ps` how much memory the model is using. Back in `ask.py`, every `[n]` in the answer is looked up in the numbered list, a citation to a number that was not sent is marked invalid, an answer that starts with "Insufficient evidence" gets that status, and an answer with no valid citation is flagged as unsupported. The card with all of that, including the full prompt and the verbatim passages, is written to `results/<run>/ask/`, and the terminal shows the answer, the sources, the status, and the timing.

## What the model sees and what it never sees

In ask mode the model sees the rules, at most 5,000 characters of passages, and the question. It does not see the chat history, because `run_ask` has no parameter for it. In chat mode the model sees the persona, the last ten turns trimmed to about 3,000 tokens, and, only when the harness decided the turn needs the notes, at most 3,500 characters of passages inside a block that the persona tells it to treat as evidence rather than instructions. After the turn, that block is dropped from the stored history so a stale passage cannot drift into later turns as if it were a fact the user stated. The test questions and their expected answers live in `tests/`, outside the vault, so retrieval can never find the answer key.

The decision to retrieve in chat is made by the harness, in `chat.route`. Slash commands win first, then a few rules: a question about what the assistant can do skips retrieval, a short follow-up like "make that shorter" skips it when there is a previous reply to rewrite, and a message that mentions my notes, my runs, or "did I" retrieves. When none of the rules fire, the harness asks the model a tiny yes-or-no question in JSON, and if that reply is unusable it falls back to retrieving only for questions with enough content words. Every transcript records which of these made the decision and why.

## How the wiki gets written

`wiki ingest` reads each file in `vault/raw`, hashes it, and skips it if notes for that hash already exist. Otherwise it sends the model an outline of the file, the headings with the first words of each section, capped at 6,000 characters, plus the titles of every note that already exists, and asks for a plan in JSON: two to five notes, each with a short title, a folder, a one-line summary, the sections it covers, and up to three related notes with a reason. The harness checks every title against its naming rules, reuses an existing title when the plan proposes something that already exists, and falls back to one note per group of sections if the model's plan is unusable twice. For each planned note it sends the model that note's sections, capped at 12,000 characters, and asks for a Summary, Details, and Related section in the owner's own voice with nothing added. The harness then writes the frontmatter, keeps only links to notes that exist, adds the Sources section, and saves the file as `vault/wiki/<Folder>/<Title>.md` with the title as the first heading. Finally it regenerates one catalog note per source under `wiki/Sources/`, regenerates `index.md`, and rebuilds the search index. A note that I have marked `reviewed: true` is never overwritten; a fresh draft goes to `results/` instead.

## The files I added

| File | What it does |
| --- | --- |
| `personal_wiki/` | The harness, described above |
| `wiki-instructions.md` and `persona.md` | The research rules for ask and the assistant's voice and capabilities for chat, loaded by the harness for the mode that needs them |
| `vault/raw/` | Byte-identical copies of four files from this repository, listed with their hashes in `sources.json` |
| `vault/wiki/` and `vault/index.md` | The generated notes, the catalog notes, and the landing page |
| `tests/questions.json` and `tests/chat_checks.txt` | The four ask-mode tests with their expected sources, and the scripted chat checks |
| `tests/test_*.py` | The pytest suite, which runs on the fake backend with a small fixture vault |
| `scripts/setup.sh`, `scripts/pull_model.sh` | The environment and the one-time model download |
| `scripts/offline_demo.sh`, `scripts/device_report.sh` | The recorded offline run that produces everything under `results/` |
| `results/` | One folder per run: device report, doctor checks, ingest log, evidence cards, transcripts, search records, terminal recording, manifest |

## Where the results are explained

The README links every evidence card, the chat and search transcripts, the terminal recording, and the Obsidian screenshots, and it says which claims in each answer the cited passages support. This file stops at what the code does.
