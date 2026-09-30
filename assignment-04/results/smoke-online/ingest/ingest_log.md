# Ingest log for run smoke-online

Model `gemma4:e4b` (ollama, quantization Q4_K_M, 8.0B, digest `c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb`), started 2026-09-30T02:00:33Z, finished 2026-09-30T02:08:30Z.

## Totals

| Measure | Value |
| --- | --- |
| sources | 4 |
| ingested | 4 |
| up_to_date | 0 |
| notes_written | 20 |
| notes_drafted | 0 |
| notes_in_vault | 20 |
| calls | 28 |
| total_wall_s | 477.34 |
| prompt_tokens | 55222 |
| generated_tokens | 17083 |
| median_tokens_per_s | 48.2 |
| max_ollama_size_bytes | 3237478399 |
| max_ollama_process_rss_bytes | 4676812800 |
| harness_max_rss_bytes | 32702464 |
| max_payload_chars | 11902 |
| payload_capped_calls | 4 |
| index_passages | 319 |
| index_wiki_passages | 87 |

## Text budget per call

The plan call receives the source outline capped at 6,000 characters; each note call receives its sections capped at 12,000 characters; every call asks Ollama for a 8,192-token context window. Largest payload sent: 11,902 characters; calls that hit the cap: 4.

## Sources

### raw/Class 5 Prompting and Retrieval Notes.md

- Action: ingested (); sha256 `535af3de2b0a`; plan origin: model-retry; wall 105.6 s
- Notes written: ['LLM Behavior and Probabilistic Nature', 'Model Customization Techniques Comparison', 'Prompting as Probability Steering', 'Structuring Prompts as Product Interfaces', 'Advanced Retrieval and Knowledge Hub']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | 1 | 3,605 (3,386) | False | 1,428 | 1393 | 700 | 52.3 | 16.625 | True |
| plan | 2 | 3,740 (3,386) | False | 1,462 | 1430 | 554 | 52.0 | 10.927 | True |
| note | 1 | 6,197 (5,354) | False | 1,799 | 1745 | 289 | 52.6 | 8.917 | True |
| note | 1 | 6,543 (5,875) | False | 1,886 | 1854 | 774 | 51.5 | 18.944 | True |
| note | 1 | 3,310 (2,631) | False | 1,077 | 957 | 556 | 52.0 | 12.784 | True |
| note | 1 | 4,890 (4,165) | False | 1,472 | 1289 | 514 | 51.2 | 12.829 | True |
| note | 1 | 14,363 (11,850) | True | 3,841 | 3572 | 747 | 44.1 | 23.932 | True |

### raw/Custom LLM README.md

- Action: ingested (); sha256 `0293ff499fdd`; plan origin: model-retry; wall 151.88 s
- Notes written: ['Assignment Model Training Overview', 'Model Performance and Results', 'Training Budget and Hardware Details', 'Model Learning Mechanics Explained', 'Interacting with Trained Model']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | 1 | 5,398 (4,977) | False | 1,876 | 1910 | 700 | 40.9 | 21.851 | True |
| plan | 2 | 5,533 (4,977) | False | 1,910 | 1947 | 343 | 41.6 | 8.632 | True |
| note | 1 | 12,311 (11,606) | True | 3,328 | 3231 | 617 | 42.2 | 22.448 | True |
| note | 1 | 12,482 (11,558) | True | 3,370 | 3163 | 900 | 40.1 | 30.22 | True |
| note | 1 | 2,794 (2,201) | False | 948 | 1036 | 492 | 37.1 | 15.859 | True |
| note | 1 | 11,223 (10,621) | False | 3,056 | 3615 | 900 | 39.0 | 31.988 | True |
| note | 1 | 10,994 (10,320) | False | 2,998 | 3053 | 528 | 41.7 | 19.715 | True |

### raw/Networking Tracker README.md

- Action: ingested (); sha256 `74a345428e79`; plan origin: model-retry; wall 111.31 s
- Notes written: ['Assignment Overview and Requirements', 'Web App Walkthrough Screenshots', 'Core Functionality and Features', 'Technology Stack and Architecture', 'Database and Setup Details']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | 1 | 6,003 (5,351) | False | 2,027 | 1973 | 700 | 48.0 | 18.886 | True |
| plan | 2 | 6,138 (5,351) | False | 2,061 | 2010 | 269 | 38.2 | 7.331 | True |
| note | 1 | 2,425 (1,633) | False | 856 | 735 | 415 | 45.5 | 10.773 | True |
| note | 1 | 5,207 (4,271) | False | 1,552 | 1514 | 769 | 44.2 | 20.445 | True |
| note | 1 | 1,706 (958) | False | 676 | 598 | 289 | 38.1 | 8.508 | True |
| note | 1 | 4,892 (4,119) | False | 1,473 | 1303 | 900 | 50.1 | 20.51 | True |
| note | 1 | 12,914 (11,902) | True | 3,478 | 3634 | 900 | 51.9 | 23.959 | True |

### raw/Pac-Man DQN README.md

- Action: ingested (); sha256 `cd469243a82e`; plan origin: model-retry; wall 108.55 s
- Notes written: ['Assignment DQN Training Overview', 'Agent Performance Comparison Results', 'Training Budget and Hardware Details Pac-Man', 'Agent Observation and Reward System', 'Agent Limitations and Future Work']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | 1 | 3,953 (3,089) | False | 1,515 | 1617 | 654 | 50.4 | 16.003 | True |
| plan | 2 | 4,232 (3,089) | False | 1,585 | 1691 | 365 | 49.4 | 7.701 | True |
| note | 1 | 7,779 (6,757) | False | 2,195 | 2182 | 521 | 48.3 | 14.452 | True |
| note | 1 | 12,793 (11,703) | False | 3,448 | 4416 | 760 | 48.1 | 24.822 | True |
| note | 1 | 2,450 (1,502) | False | 862 | 919 | 616 | 49.8 | 13.965 | True |
| note | 1 | 2,799 (1,825) | False | 950 | 822 | 411 | 49.5 | 9.606 | True |
| note | 1 | 5,270 (4,260) | False | 1,567 | 1613 | 900 | 48.7 | 21.356 | True |

