# Ask-mode test summary

Run `20260929-224956-gemma4-e4b/compare-gemma4-e2b`, questions from `tests/questions.json`.

| id | status | verdict | retrieval hit | keywords found | cited paths | wall s | tok/s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | supported | pass | True | ['M4 Pro', 'CPU'] | ['raw/Custom LLM README.md', 'raw/Pac-Man DQN README.md', 'wiki/Projects/Training Budget and Hardware Details.md'] | 8.526 | 80.7 |
| T2 | insufficient | fail | True | [] | [] | 1.879 | 96.1 |
| T3 | supported | pass | True | ['M4 Pro', 'MPS', 'CPU'] | ['raw/Pac-Man DQN README.md'] | 1.973 | 92.7 |
| T4 | insufficient | pass | None | [] | [] | 1.446 | 99.4 |
