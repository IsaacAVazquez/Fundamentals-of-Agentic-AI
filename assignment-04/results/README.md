# Results

Every run of the harness writes into one folder here, named `<timestamp>-<model tag>` unless `WIKI_RUN_ID` or `--run-id` says otherwise. Nothing in this folder is inside the Obsidian vault, so the model can never retrieve its own test answers.

A full run from `scripts/offline_demo.sh` holds:

| File | What it is |
| --- | --- |
| `terminal.txt` | The terminal recording of the whole run, made with `script(1)` |
| `device.txt` | The raw device report (`sw_vers`, `sysctl`, `system_profiler`, `vm_stat`, `ollama list`, `ollama ps`) |
| `doctor.json`, `doctor-2.json` | `wiki doctor --require-offline --save` at the start and at the end: vault, index, Ollama, model identity, the network probes, the parsed device info |
| `steps.jsonl` | One line per step with its command, start and end time, and exit code |
| `ingest/ingest_log.json`, `ingest/ingest_log.md` | The first ingest of the run: per-source actions, the plan origin, every model call with characters sent, tokens, tokens per second, and memory. The second ingest, the duplicate check, writes `ingest_log-2.json` and `.md` |
| `ingest/calls/*.json` | The full messages and the raw reply of every ingest model call |
| `ingest/drafts/` | Fresh drafts for notes that were left alone because they are marked `reviewed: true` |
| `ask/T1.json` … `ask/T4.json`, and `.md` | The four ask-mode evidence cards: question, retrieved passages and paths, prompt, model identity, answer, citations, citation check, timing, memory, offline status, assessment |
| `ask/S1.json`, `ask/summary.md` | The standalone ask from the mode checks, and the summary table |
| `chat/chat_checks.json`, `.md` | The scripted chat transcript with the routing decision and reason for every turn |
| `search/*.json`, `.md` | The saved `wiki search` output: original passages, no model call |
| `compare-<model>/ask/` | The same four questions on the comparison model, when `COMPARE_MODEL` was set |
| `manifest.json` | Everything above collected into one file |

Runs made in the Linux container with the fake backend, if any are kept, are named with `fake` in the run id and are not the required evidence; the required evidence is the run made on my laptop with the internet disconnected.
