# Ingest log for run 20260929-2344-reingest-fixed-gemma4-e4b

Model `gemma4:e4b` (ollama, quantization Q4_K_M, 8.0B, digest `c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb`), started 2026-09-30T06:43:06Z, finished 2026-09-30T06:45:09Z.

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
| total_wall_s | 123.4 |
| prompt_tokens | 10561 |
| generated_tokens | 4696 |
| median_tokens_per_s | 46.2 |
| max_ollama_size_bytes | 3237478399 |
| max_ollama_process_rss_bytes | 4276338688 |
| harness_max_rss_bytes | 35438592 |
| max_payload_chars | 12054 |
| payload_capped_calls | 1 |
| index_passages | 325 |
| index_wiki_passages | 93 |

## Text budget per call

The plan call receives the source outline capped at 6,000 characters; each note call receives its sections capped at 12,000 characters; every call asks Ollama for a 8,192-token context window. Largest payload sent: 12,054 characters; calls that hit the cap: 1.

## Sources

### raw/Networking Tracker README.md

- Action: ingested (); sha256 `74a345428e79`; plan origin: stored; wall 123.4 s
- Notes written: ['Assignment Overview and Requirements', 'Database Schema and Auth', 'Local Setup and Deployment Details', 'Technology Stack and Architecture', 'Web App Walkthrough Screenshots']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| note | 1 | 2,611 (1,633) | False | 903 | 765 | 480 | 46.2 | 11.986 | True |
| note | 1 | 6,111 (5,132) | False | 1,778 | 1780 | 1298 | 48.1 | 30.186 | True |
| note | 1 | 13,189 (12,054) | True | 3,547 | 4907 | 1136 | 44.6 | 34.486 | True |
| note | 1 | 5,076 (4,119) | False | 1,519 | 1333 | 1012 | 43.5 | 26.19 | True |
| note | 1 | 6,367 (5,231) | False | 1,842 | 1776 | 770 | 47.2 | 19.892 | True |

