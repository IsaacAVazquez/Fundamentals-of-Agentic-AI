# Ingest log for run 20260929-235259-gemma4-e4b/reingest

Model `gemma4:e4b` (ollama, quantization Q4_K_M, 8.0B, digest `c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb`), started 2026-09-30T06:53:42Z, finished 2026-09-30T06:55:24Z.

## Totals

| Measure | Value |
| --- | --- |
| sources | 1 |
| ingested | 1 |
| up_to_date | 0 |
| notes_written | 5 |
| notes_drafted | 0 |
| notes_in_vault | 20 |
| calls | 5 |
| total_wall_s | 101.99 |
| prompt_tokens | 10586 |
| generated_tokens | 3894 |
| median_tokens_per_s | 52.9 |
| max_ollama_size_bytes | 3237478399 |
| max_ollama_process_rss_bytes | 5058756608 |
| harness_max_rss_bytes | 33390592 |
| max_payload_chars | 12054 |
| payload_capped_calls | 1 |
| index_passages | 320 |
| index_wiki_passages | 88 |

## Text budget per call

The plan call receives the source outline capped at 6,000 characters; each note call receives its sections capped at 12,000 characters; every call asks Ollama for a 8,192-token context window. Largest payload sent: 12,054 characters; calls that hit the cap: 1.

## Sources

### raw/Networking Tracker README.md

- Action: ingested (); sha256 `74a345428e79`; plan origin: stored; wall 101.99 s
- Notes written: ['Database Schema and Auth', 'Local Setup and Deployment Details', 'Networking Tracker Requirements', 'Technology Stack and Architecture', 'Web App Walkthrough Screenshots']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| note | 1 | 6,023 (5,132) | False | 1,756 | 1785 | 616 | 54.4 | 18.221 | True |
| note | 1 | 13,101 (12,054) | True | 3,525 | 4912 | 1113 | 53.0 | 30.122 | True |
| note | 1 | 2,523 (1,633) | False | 881 | 770 | 481 | 52.9 | 10.753 | True |
| note | 1 | 4,988 (4,119) | False | 1,497 | 1338 | 873 | 44.1 | 22.477 | True |
| note | 1 | 6,279 (5,231) | False | 1,820 | 1781 | 811 | 48.9 | 20.026 | True |

