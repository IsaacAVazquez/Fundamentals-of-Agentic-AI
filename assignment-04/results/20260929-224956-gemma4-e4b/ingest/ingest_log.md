# Ingest log for run 20260929-224956-gemma4-e4b

Model `gemma4:e4b` (ollama, quantization Q4_K_M, 8.0B, digest `c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb`), started 2026-09-30T05:49:57Z, finished 2026-09-30T05:57:37Z.

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
| total_wall_s | 459.82 |
| prompt_tokens | 56073 |
| generated_tokens | 20955 |
| median_tokens_per_s | 53.2 |
| max_ollama_size_bytes | 3237478399 |
| max_ollama_process_rss_bytes | 605765632 |
| harness_max_rss_bytes | 33357824 |
| max_payload_chars | 12063 |
| payload_capped_calls | 5 |
| index_passages | 324 |
| index_wiki_passages | 92 |

## Text budget per call

The plan call receives the source outline capped at 6,000 characters; each note call receives its sections capped at 12,000 characters; every call asks Ollama for a 8,192-token context window. Largest payload sent: 12,063 characters; calls that hit the cap: 5.

## Sources

### raw/Class 5 Prompting and Retrieval Notes.md

- Action: ingested (); sha256 `535af3de2b0a`; plan origin: model-retry; wall 105.83 s
- Notes written: ['LLM Behavior and Probabilistic Nature', 'Model Customization Techniques Comparison', 'Prompting as Probability Steering', 'Structuring Prompts as Product Interfaces', 'Advanced Retrieval and Knowledge Hub']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | 1 | 3,605 (3,386) | False | 1,428 | 1393 | 1200 | 50.7 | 30.796 | True |
| plan | 2 | 3,740 (3,386) | False | 1,462 | 1430 | 554 | 50.8 | 11.253 | True |
| note | 1 | 6,197 (5,354) | False | 1,799 | 1745 | 289 | 46.2 | 7.919 | True |
| note | 1 | 6,543 (5,875) | False | 1,886 | 1854 | 774 | 49.6 | 17.241 | True |
| note | 1 | 3,310 (2,631) | False | 1,077 | 957 | 556 | 52.0 | 11.375 | True |
| note | 1 | 4,890 (4,165) | False | 1,472 | 1289 | 514 | 51.1 | 10.871 | True |
| note | 1 | 14,363 (11,850) | True | 3,841 | 3572 | 747 | 51.5 | 15.71 | True |

### raw/Custom LLM README.md

- Action: ingested (); sha256 `0293ff499fdd`; plan origin: model-retry; wall 118.93 s
- Notes written: ['Assignment Model Training Overview', 'Model Performance and Results', 'Training Budget and Hardware Details', 'Model Learning Mechanics Explained', 'Interacting with Trained Model']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | 1 | 5,398 (4,977) | False | 1,876 | 1910 | 1200 | 53.2 | 23.698 | True |
| plan | 2 | 5,533 (4,977) | False | 1,910 | 1947 | 343 | 53.3 | 7.78 | True |
| note | 1 | 12,311 (11,606) | True | 3,328 | 3231 | 617 | 53.5 | 12.54 | True |
| note | 1 | 12,482 (11,558) | True | 3,370 | 3163 | 1291 | 52.8 | 25.532 | True |
| note | 1 | 2,794 (2,201) | False | 948 | 1036 | 492 | 55.3 | 9.827 | True |
| note | 1 | 11,223 (10,621) | False | 3,056 | 3615 | 1400 | 53.2 | 27.578 | True |
| note | 1 | 10,994 (10,320) | False | 2,998 | 3053 | 528 | 50.2 | 11.437 | True |

### raw/Networking Tracker README.md

- Action: ingested (); sha256 `74a345428e79`; plan origin: model-retry; wall 128.3 s
- Notes written: ['Assignment Overview and Requirements', 'Web App Walkthrough Screenshots', 'Technology Stack and Architecture', 'Database Schema and Auth', 'Local Setup and Deployment Details']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | 1 | 6,003 (5,351) | False | 2,027 | 1973 | 1200 | 53.4 | 23.403 | True |
| plan | 2 | 6,138 (5,351) | False | 2,061 | 2010 | 302 | 53.6 | 6.991 | True |
| note | 1 | 2,428 (1,633) | False | 857 | 735 | 491 | 54.8 | 10.428 | True |
| note | 1 | 6,184 (5,231) | False | 1,796 | 1746 | 756 | 53.0 | 17.225 | True |
| note | 1 | 4,893 (4,119) | False | 1,473 | 1303 | 877 | 54.8 | 18.355 | True |
| note | 1 | 5,928 (5,132) | False | 1,732 | 1750 | 1164 | 53.8 | 24.6 | True |
| note | 1 | 13,006 (12,054) | True | 3,501 | 4877 | 955 | 53.0 | 26.709 | True |

### raw/Pac-Man DQN README.md

- Action: ingested (); sha256 `cd469243a82e`; plan origin: model-retry; wall 106.76 s
- Notes written: ['Assignment Overview and Requirements Pac-Man', 'Running the DQN Notebook', 'Agent Hyperparameter Tuning Choices', 'Performance Analysis Before Runs', 'Agent Training Results and Limitations']; drafted (reviewed notes kept): []; stale: []

| call | attempt | chars sent (payload) | capped | est. prompt tok | actual prompt tok | gen tok | tok/s | wall s | ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plan | 1 | 3,954 (3,089) | False | 1,515 | 1617 | 1200 | 54.5 | 25.553 | True |
| plan | 2 | 4,089 (3,089) | False | 1,549 | 1654 | 334 | 54.4 | 6.539 | True |
| note | 1 | 3,227 (2,240) | False | 1,057 | 939 | 629 | 55.3 | 13.171 | True |
| note | 1 | 4,117 (3,181) | False | 1,279 | 1260 | 988 | 54.6 | 20.571 | True |
| note | 1 | 2,293 (1,332) | False | 823 | 790 | 505 | 55.2 | 10.72 | True |
| note | 1 | 1,727 (762) | False | 682 | 603 | 308 | 54.2 | 6.917 | True |
| note | 1 | 13,317 (12,063) | True | 3,579 | 4621 | 741 | 51.8 | 22.666 | True |

