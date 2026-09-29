# Personal Wiki CLI with Local Gemma

I built this for Assignment 4 of Fundamentals of Agentic AI. It is a command-line program, `wiki`, and the harness behind it, written in Python with nothing but the standard library at runtime, that turns four of my own course write-ups into a linked Obsidian wiki and lets me talk to that wiki through a Gemma model running on my laptop through Ollama. `wiki chat` is a personal assistant with a persona and conversation memory that looks things up in the notes only when a turn needs them, `wiki ask` gives a standalone, neutral answer with numbered citations or says "Insufficient evidence", `wiki search` shows the matching original passages without calling the model at all, and `wiki ingest` has the model plan and write the wiki pages, then the harness names them, links them, and keeps the index and the source catalog current. Retrieval is my own BM25 index over passages cut from both the raw sources and the generated notes, with the file path, heading, and line numbers kept on every passage so a citation can be opened and checked.

Where this stands as of this commit: the harness, the vault layout, the four test questions, the scripts, and a suite of 60 tests are done and pass in the Linux container where I wrote the code, using a deterministic stand-in for the model, because that container cannot download Ollama or Gemma weights. The real run happens on my laptop with Wi-Fi off, through `scripts/offline_demo.sh`, and that run is what generates the wiki notes, the four evidence cards, the chat and search transcripts, the terminal recording, and every timing and memory number. Every place below that needs a number from that run says so with a marker like `<<FILL ...>>` naming the results file it comes from, and I will replace the markers, not invent the numbers. The section "What is still to do on my laptop" at the end is the checklist and goes away when it is done.

## Where to find each requirement

| Requirement | Where it is |
| --- | --- |
| Purpose, sources, and how originals connect to generated pages | Purpose and sources, and The wiki in Obsidian |
| OS, chip, RAM, GPU or unified memory, available memory, free disk, dependencies, model and quantization, runtime, downloads, exact commands | Setup and device, and Running it |
| Model choice with RAM, runtime, measured memory, and response time | Why Gemma 4 E4B, and what it measured |
| Model, retrieval tool, RAG workflow, CLI, and harness, with one command traced | Architecture, and one question traced through the code |
| Passage size, retrieval method, research rules, persona, context limits, when chat retrieves, note naming and folders, source ids, re-ingestion, model settings | Design choices |
| Three answerable questions and one unsupported question with expected evidence, retrieved passages, answers, citations, and assessments | The four ask-mode tests |
| Chat capability check, follow-up, search, standalone ask, chat claims kept out of ask | Chat and search mode checks |
| Offline recording, device specs, model identity, saved evidence | The offline run |
| Obsidian screenshots, the source catalog, one note traced to its evidence, re-ingest without duplicates | The wiki in Obsidian |
| One real limitation and one concrete improvement | One limitation and one improvement |
| CLI and harness code, launch instructions | Running it, Files, and [EXPLAINER.md](EXPLAINER.md) |

## Purpose and sources

The wiki is my coursework memory: what I built, measured, and decided in this course, so that I can ask "what learning rate did I use for the DQN" or "which of my runs used the GPU" and get the answer with a pointer into my own write-up instead of scrolling through three READMEs. The sources are four files from this repository, copied byte for byte into `vault/raw/` with readable names, and their origin, copy date, and SHA-256 are recorded in [sources.json](sources.json), which `wiki doctor` checks against the files on every run.

| Raw file | Copied from | What it holds |
| --- | --- | --- |
| `vault/raw/Networking Tracker README.md` | `assignment-01/README.md` at commit `4e333d3` | The networking tracker on Next.js, Neon Postgres, managed Better Auth, and the Neon Data API |
| `vault/raw/Pac-Man DQN README.md` | `assignment-02/README.md` | The Ms. Pac-Man Deep Q-Network, the 500-game and 450-game runs, the checkpoint check, the evaluation scores |
| `vault/raw/Custom LLM README.md` | `assignment-03/README.md` | The word-token nanoGPT, its teaching corpus, the 48 language evals, the traced embedding and gradient, the chat sessions |
| `vault/raw/Class 5 Prompting and Retrieval Notes.md` | `class5.md` | The Class 5 deck: prompting, context, hallucination defenses, retrieval-augmented generation, embeddings, the Assignment 4 brief |

I left `COURSE.md` out on purpose. It holds my grades, which is private enough that I did not want it retrievable, and leaving it out also gives the fourth test question a clean answer, since no remaining source says what any assignment scored.

The generated pages live in `vault/wiki/` in three topic folders, `Projects/`, `Concepts/`, and `Course/`, plus `Sources/`, which holds one catalog note per raw file. Every wiki note's frontmatter records the raw file it came from, that file's hash, the sections it used, and the model that wrote it, and every note ends with a Sources section that links to the catalog note and names the raw path and sections. The catalog note links back to the raw file and forward to every note derived from it, so a reader can go index, note, related note, catalog, original in four clicks.

## Setup and device

The laptop is an Apple M4 Pro MacBook Pro with 12 CPU cores and 24 GB of unified memory, which the CPU and the Apple GPU share, running macOS 26.3, the same machine the Assignment 2 and 3 write-ups record. There is no discrete GPU and no separate VRAM. Available memory and free disk at the time of the run come from `results/<run-id>/device.txt` and `doctor.json`: `<<FILL from doctor.json, device.memory_available_bytes and device.disk_free_bytes>>`.

The software is Python 3.13 through Homebrew, uv to build the virtual environment, and Ollama as the local inference runtime. The harness has no runtime dependencies beyond the standard library; pytest is the only package in [requirements.txt](requirements.txt), for the tests. The model is Gemma 4 E4B as Ollama packages it under the tag `gemma4:e4b`, pulled once while online with `scripts/pull_model.sh`, which also pulls `gemma4:e2b` for the comparison run. The harness reads the exact identity from Ollama itself at run time, the tag, the digest, the quantization level, and the parameter size from `/api/tags` and `/api/show`, and writes them into every evidence card and into `doctor.json`, so the identity table below is copied from the run rather than typed from memory.

| Item | Value |
| --- | --- |
| Model tag | `gemma4:e4b` |
| Digest, quantization, parameter size | `<<FILL from doctor.json, ollama.model_info>>` |
| Ollama version | `<<FILL from doctor.json, ollama.version>>` |
| Context window requested per call | 8,192 tokens |
| Comparison model | `gemma4:e2b`, same run, results under `compare-gemma4-e2b/` |

The weights are not in the repository. Ollama's registry serves them under those tags, and Google's model page at https://ai.google.dev/gemma/docs/core is the source of the size and memory figures I used to choose.

## Running it

Everything below runs from `assignment-04/`. The first two steps need the internet once; nothing after them does.

```
git clone https://github.com/IsaacAVazquez/Fundamentals-of-Agentic-AI.git
cd Fundamentals-of-Agentic-AI/assignment-04
brew install ollama uv        # if they are missing; then start Ollama (the app, or `ollama serve`)
scripts/setup.sh              # builds .venv on Python 3.13 and installs the `wiki` command into it
scripts/pull_model.sh         # ollama pull gemma4:e4b and gemma4:e2b, then `wiki doctor`
```

`scripts/setup.sh` follows the same pattern as my earlier assignments: it builds `.venv` with uv on Python 3.13 and installs this folder as a package, which puts `wiki` on `.venv/bin`. Without installing, `python3 -m personal_wiki` runs the same program. The commands, with `.venv/bin/wiki` spelled out:

```
.venv/bin/wiki help                       # commands, configuration, required inputs; `wiki help ask` for one command
.venv/bin/wiki doctor                     # vault, sources.json hashes, index, Ollama, model identity, network, device
.venv/bin/wiki ingest                     # read vault/raw with Gemma, write vault/wiki, index.md, the catalog, the index
.venv/bin/wiki search "Pac-Man evaluation score"          # original passages and paths; no model call
.venv/bin/wiki ask "What learning rate did I use for the DQN?" --mode local   # cited answer or Insufficient evidence
.venv/bin/wiki chat                       # the assistant; /notes, /search, /reset, /help, /quit inside it
.venv/bin/wiki eval tests/questions.json  # the four fixed questions, scored against the expectations written beforehand
```

`--mode local` is the default and the only mode I built; `--mode online` stops with a message saying so and sends nothing anywhere. Flags win over environment variables: `--vault`, `--model`, `--host`, `--results-dir`, `--run-id`, and `--backend` have `WIKI_VAULT`, `WIKI_MODEL`, `WIKI_HOST`, `WIKI_RESULTS_DIR`, `WIKI_RUN_ID`, and `WIKI_BACKEND` equivalents. Errors are one line with an exit code: Ollama not running is exit 3 with the command to start it, a missing model is exit 4 with the pull command and the list of installed tags, a missing vault is exit 5, an empty vault is exit 6, and `wiki search` keeps working while Ollama is down because it never loads a backend.

The offline demonstration is one script:

```
# turn Wi-Fi off, quit and reopen Terminal, cd back here, then:
FRESH=1 COMPARE_MODEL=gemma4:e2b scripts/offline_demo.sh
```

It records the terminal with `script(1)`, writes the device report, runs `wiki doctor --require-offline` (which exits 11 if any probe reaches the internet), ingests the vault from scratch, ingests it a second time to show that nothing is duplicated, runs the four questions, runs the scripted chat checks, runs a search and a standalone ask, runs the doctor again, runs the four questions on the comparison model, and collects everything into `results/<run-id>/manifest.json`. Every step is a fresh `wiki` process started after the network went down.

The tests run with `.venv/bin/python -m pytest -q`. They use `--backend fake`, a deterministic stand-in in [personal_wiki/backends/fake.py](personal_wiki/backends/fake.py) that copies sentences out of the passages it is given and never invents anything, on a two-file fixture vault, so they exercise the harness without a model and never touch `vault/` or `results/`.

## Why Gemma 4 E4B, and what it measured

The brief's official loading estimates are about 2.9 GB for E2B at Q4_0, about 4.5 GB for E4B, and about 14.4 GB for the 26B A4B mixture of experts, which activates about 4B parameters per token but still loads all 26B. On 24 GB of unified memory the 26B model would fit, but it would leave under 10 GB for the 8,192-token context, Obsidian, the browser, and macOS itself, and this wiki is four documents, so I did not think it earned that. E2B is the model to start with when memory is tight, and 24 GB is not tight, so I made E4B the default and kept E2B as the comparison, since the brief asks for the smallest model that works and the honest way to say which that is on my wiki is to run the same four questions on both. The harness runs at temperature 0 with a fixed seed, so repeats on the same machine should agree in substance, though I would not promise byte-for-byte on Metal.

The measurements come from the Mac run. Memory is reported three ways because none of them alone is the whole story on Apple Silicon: what Ollama reports it has reserved for the model and its context through `/api/ps`, the resident memory of the Ollama processes from `ps`, and the harness's own peak resident memory, which is small because it is a client. Response time is wall-clock per call plus Ollama's own prompt and generation token counts and durations, so tokens per second is in every card.

| Measure | E4B | E2B |
| --- | --- | --- |
| Ingest, wall time for the fresh run | `<<FILL from manifest.json, ingest.generation.total_wall_s>>` | not run |
| Ingest, model calls, prompt tokens, generated tokens | `<<FILL from manifest.json, ingest.generation.calls, prompt_tokens, generated_tokens>>` | not run |
| Ingest, median generation speed | `<<FILL from manifest.json, ingest.generation.median_tokens_per_s>>` | not run |
| Ingest, peak Ollama memory (`/api/ps` size, process RSS) | `<<FILL from manifest.json, ingest.generation.max_ollama_size_bytes and max_ollama_process_rss_bytes>>` | not run |
| One answer (T1), wall time, generation speed, Ollama memory | `<<FILL from ask/T1.json, timing and memory>>` | `<<FILL from compare-gemma4-e2b/ask/T1.json>>` |
| Four questions, verdicts | `<<FILL from ask/summary.md>>` | `<<FILL from compare-gemma4-e2b/ask/summary.md>>` |

## Architecture, and one question traced through the code

The brief's four words map onto four different things here. The model is Gemma inside Ollama: it receives a system message and a user message from my program and returns text, and it has no idea my vault exists. The retrieval tool is [personal_wiki/index.py](personal_wiki/index.py) and [personal_wiki/retrieval.py](personal_wiki/retrieval.py): a BM25 index over passages cut from `vault/raw` and `vault/wiki` by [personal_wiki/chunking.py](personal_wiki/chunking.py), returning passages with their path, heading, and line range, which is exactly what `wiki search` prints. The RAG workflow is [personal_wiki/ask.py](personal_wiki/ask.py): retrieve, build the prompt with the research rules, call the model, check the citations, save the card. The CLI is [personal_wiki/cli.py](personal_wiki/cli.py), and the harness is the whole package: mode selection in `cli.py`, instruction loading and prompt assembly in [personal_wiki/prompts.py](personal_wiki/prompts.py), conversation context and the retrieval decision in [personal_wiki/chat.py](personal_wiki/chat.py), the Ollama client with its timing and memory capture in [personal_wiki/backends/ollama.py](personal_wiki/backends/ollama.py), errors in [personal_wiki/errors.py](personal_wiki/errors.py), saved outputs in [personal_wiki/evidence.py](personal_wiki/evidence.py), and the wiki writer in [personal_wiki/ingest.py](personal_wiki/ingest.py) with [personal_wiki/vault.py](personal_wiki/vault.py).

Take `wiki ask "What hardware did I train the nanoGPT model on for Assignment 3?"`. `cli.main` parses the flags and calls `cmd_ask`, which refuses `--mode online` before anything else, resolves the settings, opens the Ollama backend, and calls `index.ensure_index`, which compares a fingerprint of the vault's file names, sizes, and modification times with the one stored in `index/bm25.json` and rebuilds the index if anything changed. `ask.run_ask` then calls `retrieval.search`, which tokenizes the question, drops stopwords, stems what is left, adds a few synonyms, and scores every passage with BM25, boosting words that appear in a passage's headings. It keeps the top six, then `select_for_prompt` keeps as many of those as fit in 5,000 characters and numbers them from 1. `prompts.build_ask_messages` puts the text of [wiki-instructions.md](wiki-instructions.md) in the system message and the numbered passages plus the question in the user message. `OllamaBackend.generate` posts that to `/api/chat` with streaming off, temperature 0, seed 0, an 8,192-token context, and a 400-token output cap, strips any thinking block, and reads back the reply with Ollama's token counts and durations, then asks `/api/ps` for the model's memory and `ps` for the Ollama processes' resident size. Back in `run_ask`, every `[n]` in the reply is looked up in the numbered list: a number that was sent becomes a citation with its path, heading, and lines, a number that was not is marked invalid, a reply that starts with "Insufficient evidence" gets that status, and a reply with no valid citation and no such marker is flagged as unsupported, with a warning printed. Numbers in the answer that appear in no cited passage are listed too. The card, with the full prompt, every retrieved passage verbatim, whether it was sent, the model identity, the timings, the memory, and the network status, goes to `results/<run-id>/ask/<id>.json` and `.md`, and the terminal shows the answer, the sources by number, the status, and the timing. A `WikiError` anywhere along that path prints one line to stderr and exits with its code.

Chat is the same machinery with a different front. `chat.ChatSession.route` decides whether the turn needs the notes before any prompt is built: slash commands first, then a capability or greeting question skips retrieval, then a short follow-up such as "make that shorter" skips it when there is a previous reply to rewrite, then a message that mentions my notes, my runs, or "did I" retrieves, and only when none of those fire does the harness ask the model a tiny JSON question, retrieve or not and with what query, falling back to a rule if the JSON is unusable. Every transcript records the decision, its source (rule, model, or fallback), and the reason. When it retrieves, the passages are appended to the current user message inside a block labeled as evidence, not instructions, and after the turn that block is dropped from the stored history, which keeps only the last ten turns within about 3,000 tokens.

## Design choices

Passages are cut at H1 to H3 headings, with paragraphs, whole tables, and whole fenced or HTML blocks packed into passages of at most 1,200 characters, a paragraph longer than that split at sentence boundaries, and a tail shorter than 200 characters merged into the previous passage, so a passage can reach 1,400 characters in that one case. A `#` line inside a fenced block is not a heading, which matters because the networking tracker README has several. The four sources come out as 232 passages. Wiki notes are chunked the same way after their frontmatter is removed, with the title and summary indexed as extra terms, and their Sources sections and the catalog notes are not indexed at all, since they are navigation, not evidence.

Retrieval is keyword search on purpose. The class notes make the point that at personal-wiki scale the index file is the retrieval system and a vector database is the AI-era version of needing Hadoop, and BM25 with stemming and heading boosts was enough to put the right section at the top for the first three questions in my pre-run check. The one thing I added is a small synonym map at half weight, so "machine" also reaches "laptop" and "GPU" also reaches "MPS", and it is written down in `retrieval.py` rather than learned. Both `wiki search` and `wiki ask` take `-k` and `--scope raw|wiki|all`, and `--scope raw` is the strict recipe when I want only original passages as evidence.

The research rules for ask mode are in [wiki-instructions.md](wiki-instructions.md): use only the passages, end every factual sentence with its passage number, copy numbers exactly, and answer with one line starting "Insufficient evidence:" when the passages do not contain the answer, with a worked example. The persona for chat is in [persona.md](persona.md): a plain-spoken assistant that says what it runs on and what it cannot do, lists the actual commands, treats the retrieved block as evidence, treats things I say in chat as my words rather than notes, never invents facts about me, and starts any proposal with "Suggestion:". The harness loads each file for the mode that needs it and records the file's hash in every card and transcript.

The text budgets are all in [personal_wiki/config.py](personal_wiki/config.py). Ask sends the rules and up to 5,000 characters of passages, about 1,800 prompt tokens. Chat sends the persona, at most ten turns trimmed to 12,000 characters, and up to 3,500 characters of passages. Ingest sends the plan call an outline of the source, the headings with the first words of each section, capped at 6,000 characters, and each note call the sections that note covers, capped at 12,000 characters with a visible truncation marker when the cap is hit, and every call asks Ollama for an 8,192-token context so the biggest note prompt, around 3,500 tokens, never gets silently cut. The ingest log records characters sent, the cap flag, and the actual prompt token count for every call.

Notes are named by the plan the model returns, and the harness holds the line on names: two to six words, letters and digits, no hashes, dates, eight-digit numbers, file names, or sentences, validated by `vault.validate_title`, with the filename, the frontmatter title, and the first heading always identical. The folder comes from the plan, `Projects` for something I built or ran, `Course` for class material, `Concepts` for an idea explained on its own, and `Sources` is the catalog. Machine ids live in frontmatter: `source_id` is a slug of the raw file's name, `source_sha256` is the hash of the file the note was written from, `note_id` is source id plus title slug, and `sections_used` lists the headings. Re-ingesting a source whose hash has not changed is a no-op that says "up to date". A changed source is re-planned with its previous titles offered back to the model and reused when they still fit, so the same filenames are rewritten in place, `created` is kept and `updated` changes, and a note whose frontmatter says `reviewed: true` is never overwritten; its fresh draft goes to `results/<run-id>/ingest/drafts/` instead. A title that another source already owns is disambiguated with a word from the source's name. Links are real `[[wikilinks]]`, but only to notes that exist or are in the current plan, each with a clause saying why, and the Sources links use the path form `[[wiki/Sources/Name|Name]]` because the raw file and its catalog note share a basename.

The model settings that matter are temperature 0 for ask, plan, note, and routing, 0.2 for chat prose, seed 0 everywhere, `think` off, and JSON schema output for the plan and the routing call, with a fallback to plain JSON mode and then to a heuristic plan of one note per group of sections if the model's plan is unusable twice; the ingest log says which origin each plan had. `<<FILL: any setting changed after the first Mac run, with the reason and the rerun>>`

## The four ask-mode tests

I wrote the questions, the expected sources, and the expected behavior in [tests/questions.json](tests/questions.json) before the retrieval code existed, and that file stays outside `vault/` so the harness can never retrieve the answer key. `wiki eval` runs each one through the same `run_ask` as the command line and adds an automated assessment: whether the status matched the expected behavior, whether an expected source was among the passages sent to the model, whether the expected keywords appear in the answer, and a verdict of pass, check, or fail. The human assessment, whether each cited passage supports the claim it is attached to, is mine and goes in the cards after I read them.

| Test | Question | Expected source and passage | Expected behavior |
| --- | --- | --- | --- |
| T1 | What hardware did I train the nanoGPT model on for Assignment 3? | Custom LLM README, "Training budget and hardware": an Apple M4 Pro laptop with 12 CPU cores and 24 GB of memory running macOS 26.3, on the CPU | A cited answer naming the M4 Pro and the CPU |
| T2 | Why did the last Ms. Pac-Man run stop at fewer games than the first one? | Pac-Man DQN README, "My three choices", the checkpoint check, and "The final run, 450 games": 450 because that checkpoint was the best of 20 on 30 validation games, confirmed on 50 more | A cited answer with 450 and the checkpoint reason, from wording that differs from the source |
| T3 | What machine did I use for Assignments 2 and 3, and did either use the GPU? | Both READMEs' hardware paragraphs: the same M4 Pro, the DQN on the Apple GPU through MPS, the nanoGPT on the CPU | A cited answer that connects the two sources |
| T4 | What grade did I receive on Assignment 2? | None; no source states a grade | A reply starting "Insufficient evidence" |

Before any model ran I checked retrieval alone on the raw sources, which the brief says to do first. T1's top two passages were the two hardware paragraphs, the Pac-Man one first and the nanoGPT one second, so the model has to pick the right one. T2's top six held the passage that says I changed episodes to 450 and nothing else and the one that says I picked 450 using the extra games, but not the sentence that the 450-game checkpoint was the best of the 20, which sat just below the cutoff. T3 found the Pac-Man hardware paragraph and the nanoGPT README's opening sentence, which says the run was on my laptop's CPU, but not the nanoGPT hardware paragraph, since that paragraph never says "machine", "GPU", or "Assignment 3". T4's best match scored about half of what the other questions' top passages scored and was about the graded capstone in the class notes. I expected T1 and T2 to pass, T3 to come back as check because the second source's best passage is thin, and T4 to depend entirely on whether the model obeys the insufficient-evidence rule with score passages in front of it. The index the Mac run uses also has the generated notes in it, which changes the rankings, and the cards record what was actually retrieved.

The results on `gemma4:e4b`, from the offline run, with my reading of each cited passage: `<<FILL from results/<run-id>/ask/T1.md through T4.md and summary.md, one paragraph per test: retrieved paths, the answer, the citations, whether each cited passage supports each claim, and any failure>>`

The same four questions on `gemma4:e2b`: `<<FILL from results/<run-id>/compare-gemma4-e2b/ask/summary.md>>`

## Chat and search mode checks

The checks are in [tests/chat_checks.txt](tests/chat_checks.txt), run by `wiki chat --script`, and the transcript records the routing decision and reason for each turn beside the expectation I wrote in the file. "what can you help me with?" should be answered from the persona with no retrieval and no citations. "Write a three-sentence plan for the evening before next week's class." should be a suggestion, and "Make that shorter." should rewrite it from the conversation without touching the notes. "What learning rate did I use for the DQN?" should retrieve and cite 0.0001. "My Pac-Man agent scored 5,000 points on the leaderboard." is a claim that exists only in the chat, and the last turn, `/notes What did my final Pac-Man agent average on the five evaluation games?`, should cite 946 from the notes rather than repeat the 5,000. The demo then runs `wiki search "Pac-Man evaluation score"` and `wiki ask` with that same average question from fresh processes, which is the structural proof that ask never sees chat: `run_ask` has no history parameter, and the test suite checks that only a system message and one user message reach the model.

The transcript and the two saved outputs: `<<FILL: links to results/<run-id>/chat/chat_checks.md, search/pac-man-evaluation-score.md, and ask/S1.md, with what happened on each turn>>`

## The offline run

`<<FILL: the run id, the date, the terminal recording at results/<run-id>/terminal.txt, doctor.json and doctor-2.json showing every probe failed, device.txt, the ingest log, and the steps.jsonl exit codes>>`

Offline is proven by `wiki doctor --require-offline` at the start and the end of the recording, which tries TCP connections to two public addresses and an HTTPS request to example.com with three-second timeouts and exits 11 if any of them gets through; DNS is recorded but not counted because the Mac's resolver can answer from its cache. Every evidence card carries that network status too. Restarting the CLI is built into the script, since every step is its own `wiki` process started after Wi-Fi went off.

## The wiki in Obsidian

`<<FILL after the run: the three screenshots at docs/screenshots/01-open-note.png, 02-index-and-page-list.png, and 03-graph-view.png, the graph filter used (path:wiki/ with attachments off), the note chain I clicked through from index.md to a note to a related note to its catalog note to the raw file, and the second ingest's "up to date" lines as the duplicate check>>`

The layout is fixed regardless of what the model writes. `vault/` is the folder to open as the vault, `raw/` holds the unchanged originals, `wiki/Projects/`, `wiki/Concepts/`, and `wiki/Course/` hold the notes, `wiki/Sources/` holds the catalog, and `index.md` is the landing page the harness regenerates on every ingest, grouped by folder with each note's one-line summary and the sources listed last. Code, the retrieval index, logs, tests, and results all live outside `vault/`.

## One limitation and one improvement

The limitation I already know about is the paraphrase gap in keyword retrieval, and T3 is where it shows. The nanoGPT hardware paragraph is the best evidence that Assignment 3 ran on the CPU, but it says "laptop" and "CPU" where the question says "machine" and "GPU", so BM25 ranks it below passages that merely contain "Assignment" and "2". My synonym map patches the two words I noticed, which is not a method. `<<FILL: what actually failed on the Mac run, if anything, what caused it, and any setting I changed and reran>>`

The improvement I would try first is hybrid retrieval: keep BM25 and add a local embedding model through the same Ollama server, EmbeddingGemma at 300M parameters would fit alongside E4B with room to spare, merge the two rankings with reciprocal rank fusion, and rerun the same four questions so the cards show what changed. The class notes describe exactly that funnel, cheap keyword and dense stages narrowing the field before the expensive generation stage, and the harness already has the place for it, since `retrieval.search` is the one function everything calls.

## What is still to do on my laptop

1. `brew install ollama uv` if missing, start Ollama, run `scripts/setup.sh`, then `scripts/pull_model.sh` while online, and confirm `.venv/bin/wiki doctor` is all ok.
2. Turn Wi-Fi off, quit and reopen Terminal, `cd` back into `assignment-04/`, and run `FRESH=1 COMPARE_MODEL=gemma4:e2b scripts/offline_demo.sh`.
3. Read `results/<run-id>/ask/summary.md`, the four cards, `chat/chat_checks.md`, and `ingest/ingest_log.md`; open `vault/` in Obsidian, click through one note chain, and take the three screenshots into `docs/screenshots/`.
4. Review each generated note against its source, fix anything invented or misleading in the note (never in `raw/`), set `reviewed: true` on the notes I read, and if any note changed rerun `scripts/offline_demo.sh` without `FRESH` for a second offline result set.
5. Replace every `<<FILL ...>>` marker in this file with the numbers and links from the results, delete this section, and update the status paragraph at the top and the rows in the root `README.md` and `COURSE.md`.

## Files

| File | What it is |
| --- | --- |
| [personal_wiki/](personal_wiki/) | The harness package: `cli.py`, `config.py`, `errors.py`, `textutil.py`, `frontmatter.py`, `chunking.py`, `index.py`, `retrieval.py`, `vault.py`, `prompts.py`, `ask.py`, `chat.py`, `ingest.py`, `evidence.py`, `doctor.py`, `evalrun.py`, and `backends/` with the Ollama client and the fake |
| [wiki-instructions.md](wiki-instructions.md), [persona.md](persona.md) | The research rules for ask and the assistant's persona for chat |
| [vault/](vault/) | The Obsidian vault: `raw/` originals, `wiki/` notes and catalog, `index.md` |
| [sources.json](sources.json) | Where each raw file came from, when it was copied, and its SHA-256 |
| [tests/](tests/) | `questions.json`, `chat_checks.txt`, the fixture vault, and the pytest suite |
| [scripts/](scripts/) | `setup.sh`, `pull_model.sh`, `device_report.sh`, `offline_demo.sh` |
| [results/](results/) | One folder per run, described in [results/README.md](results/README.md) |
| [docs/screenshots/](docs/screenshots/) | The Obsidian screenshots and the checklist for taking them |
| [EXPLAINER.md](EXPLAINER.md) | A plain-language walkthrough of what the code does |
| [ASSIGNMENT.md](ASSIGNMENT.md) | My copy of the assignment brief |

## Where the code comes from

Every file in `personal_wiki/`, the scripts, and the tests are mine, written for this assignment on top of the Python standard library only; BM25, the chunker, the frontmatter reader, and the citation check are implemented here rather than imported, so there is no search or parsing library to trace through. Ollama is the inference runtime and Gemma 4 is Google's open-weight model, both installed on the laptop and not in the repository. The vault layout follows the raw, wiki, and index pattern from Karpathy's LLM wiki gist that the Class 5 deck points at. The four raw files are copies of my own earlier write-ups and of the course's Class 5 deck as converted to Markdown in this repository.
