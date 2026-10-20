# What the code in this folder does, in plain language

This is the walkthrough for someone reading `assignment-05/` without a background in Python or in language-model APIs. The README has the setup commands and the evidence; this file explains the moving parts.

## The job

The assignment hands over a 97 MB spreadsheet of 660,622 public app store reviews of Spotify and asks one question: where should the next quarter of product effort go? Nobody can read that many reviews, so the program asks a language model to read each one and fill in a small fixed form (what the review is about, whether it is a complaint, how bad the problem is, a quote that proves it). Then ordinary code, not the model, adds up the forms, ranks the problems, and checks the memo that argues for a priority. The whole design is about keeping the judgment calls inside the model's narrow job and keeping the arithmetic and the bookkeeping in code where anyone can check them.

## The six stages

Stage 1, `prepare.py`, reads the spreadsheet one chunk at a time so it never holds the whole file in memory, gives every row a fingerprint (a SHA-256 hash of its six fields) so nothing can be swapped or lost without notice, counts the things the brief says to verify (13 empty reviews, 159,701 missing app versions, no repeated ids, 484,189 distinct texts), and stores every row in a small SQLite database with the status "pending". No model is involved.

Stage 2, `classify.py`, is the orchestrator. It takes pending reviews in batches of at most 50, sends each batch to the model with the labeling instructions in `prompts.py`, and checks every answer with `validate.py` before saving it. The checks are strict: the topic must be one of eight allowed words, the severity must be a whole number from 1 to 5, and the evidence quote must appear word for word in the original review. A record that fails is sent once more; if it fails again it is set aside with the reason written down ("quarantined"), never silently dropped. Before any batch goes out the orchestrator reserves its worst-case cost against a spending cap, and if the cap would be exceeded it stops and saves. If the same review text appears twice (very common in app store reviews), the second copy reuses the first answer and records which review it copied from. Every call to the model, successful or not, is logged with its token counts and price. If the process is interrupted it leaves a consistent database behind, and running the same command again continues from where it stopped without paying to relabel anything.

Stage 3, `verify.py`, picks a random sample of finished records (the random seed is written down so the sample can be reproduced) and asks the model to label those reviews again from scratch, without showing it the first answer. Code compares the two sets and writes down every disagreement. It also makes a separate test copy with one label deliberately changed to something wrong and checks that the verifier disagrees with it. That test copy never touches the real results.

Stage 4, `group.py`, puts every complaint and every cancellation threat into an issue. The grouping rule is just the topic label, so there are eight issues and every review lands in at most one, and the membership list is saved as a plain CSV. The model is allowed to suggest a human-readable name for each issue from a handful of example quotes, but it cannot change which reviews belong where.

Stage 5, `rank.py`, is only arithmetic: for each issue, the number of complaints times the mean severity, which equals the sum of the severities. Issues are sorted by that score, ties broken by issue id. It also writes a list of "claims", every number the memo is allowed to use, each with an id like C7 and a note on how it was computed. Running this stage twice on the same saved files produces byte-identical output, and `evals.py` checks exactly that.

Stage 6, `memo.py`, gives the model the claims table, a short pack of example quotes with their review ids, and the limitations, and asks for a memo that cites a claim id after every number. Code then reads the memo back: every claim id must exist, every number must match its claim, every issue id and review id must be real, and phrases the data cannot support (revenue at risk, churn rate) are rejected. The result is saved as `memo.md` with the check next to it.

## The roles and why this counts as multi-agent

Four different jobs talk to the model: the enricher, the verifier, the issue namer, and the memo writer. They have separate instructions, separate inputs, separate output formats, and separate saved outputs, and none of them sees another's context. The orchestrator that moves work between them is plain code with a fixed order. That is what the course means by a multi-agent pipeline: distinct bounded roles exchanging inspectable files, not an open-ended swarm.

## Backends

`backends/` holds three ways to reach a model. `anthropic_backend.py` calls Claude through the official SDK with structured JSON output, and `openai_backend.py` does the same for OpenAI. `fake.py` is not a model at all: it labels reviews by keyword rules, costs nothing, and exists so every other part of the system (validation, retries, caching, resume, the exports, the dashboard) can be tested on a laptop with no API key. Its results are marked synthetic wherever they appear. Special markers in a review text make the fake backend misbehave on purpose, which is how the tests exercise malformed output, dropped records, bad quotes, and a temporary outage.

## The cost calculator

`cost.py` runs the real pipeline on the fixed 100-review file with one worker and an empty cache, saves every call with its token usage, and runs again on the saved state to show that no enrichment call is repeated. The default `replay` command is offline: it multiplies the saved token counts by the prices in an editable `rates.csv` and projects the full 660,622-row run under editable assumptions, with and without exact-text reuse and in a base and a conservative scenario. Doubling the prices doubles the dollar figure and changes nothing else, and changing the projected volume changes nothing about the measured pilot, which is how the grader can tell the arithmetic is honest.

## The grading export

`export.py` writes the `grading/` folder the course checker reads: one line per review with its hash and final status, the issue membership, the ranking, the claims, every model call, and the checkpoint snapshots taken before and after a run. `check_submission.py` from the dataset ZIP recomputes the counts from these files without touching a model.

## The dashboard

`dashboard_load.py` copies a finished run's results (metrics, ranked issues, claims, example quotes, monthly trend, the memo and its check) into a database, either a local SQLite file or a hosted Postgres database. `dashboard/app.py` is a small web backend that reads only from that database and serves JSON, plus a single page, `dashboard/static/index.html`, that shows the overall metrics, the ranking with evidence behind each issue, and the AI-generated recommendation with its code-verified citations. The dashboard never reads the run folder and never calls a model, so the hosted version can be inspected without spending anything.

## Reading the tests

`tests/` runs the whole thing on a 300-row synthetic file in about two seconds. The names say what each one proves: every row is accounted for, cache copies point at a real classification, a bad record is retried once and then quarantined, a provider outage stops the run and the next run resumes, the spending cap stops admission, the ranking is reproducible, the memo checker rejects a wrong number, an injected instruction is labeled as content, and no completed id is ever sent again after a resume.
