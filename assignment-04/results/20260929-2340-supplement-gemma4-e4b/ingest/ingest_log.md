# Ingest log for run 20260929-2340-supplement-gemma4-e4b

Model `gemma4:e4b` (ollama, quantization Q4_K_M, 8.0B, digest `c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb`), started 2026-09-30T06:39:32Z, finished 2026-09-30T06:41:25Z.

## Totals

| Measure | Value |
| --- | --- |
| sources | 1 |
| ingested | 1 |
| up_to_date | 0 |
| notes_written | 5 |
| notes_drafted | 0 |
| notes_in_vault | 22 |
| calls | 6 |
| total_wall_s | 113.21 |
| prompt_tokens | 10090 |
| generated_tokens | 4351 |
| median_tokens_per_s | 46.9 |
| max_ollama_size_bytes | 3237478399 |
| max_ollama_process_rss_bytes | 4353392640 |
| harness_max_rss_bytes | 33013760 |
| max_payload_chars | 11902 |
| payload_capped_calls | 1 |
| index_passages | 333 |
| index_wiki_passages | 101 |

## Text budget per call

The plan call receives the source outline capped at 6,000 characters; each note call receives its sections capped at 12,000 characters; every call asks Ollama for a 8,192-token context window. Largest payload sent: 11,902 characters; calls that hit the cap: 1.

## Sources

### raw/Networking Tracker README.md

- Action: ingested (); sha256 `74a345428e79`; plan origin: model; wall 113.21 s
- Notes written: ['Assignment Overview and Requirements', 'Web App Walkthrough Screenshots', 'Core Functionality and Features', 'Technology Stack and Architecture', 'Data Persistence and Security Details']; drafted (reviewed notes kept): []; stale: ['Database Schema and Auth', 'Local Setup and Deployment Details']

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | 1 | 6,624 (5,351) | False | 2,183 | 2073 | 566 | 46.5 | 16.278 | True |
| note | 1 | 2,702 (1,633) | False | 925 | 779 | 440 | 49.6 | 10.438 | True |
| note | 1 | 5,497 (4,271) | False | 1,624 | 1565 | 766 | 47.2 | 19.554 | True |
| note | 1 | 1,978 (958) | False | 744 | 642 | 327 | 45.4 | 8.743 | True |
| note | 1 | 5,182 (4,119) | False | 1,545 | 1353 | 980 | 45.2 | 24.434 | True |
| note | 1 | 13,190 (11,902) | True | 3,547 | 3678 | 1272 | 48.6 | 33.298 | True |

