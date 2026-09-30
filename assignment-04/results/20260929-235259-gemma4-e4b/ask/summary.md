# Ask-mode test summary

Run `20260929-235259-gemma4-e4b`, questions from `tests/questions.json`.

| id | status | verdict | retrieval hit | keywords found | cited paths | wall s | tok/s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | supported | pass | True | ['M4 Pro', 'CPU'] | ['raw/Custom LLM README.md', 'wiki/Projects/Custom LLM Training Hardware.md'] | 3.196 | 53.6 |
| T2 | supported | pass | True | ['450', 'checkpoint'] | ['raw/Pac-Man DQN README.md'] | 1.743 | 55.5 |
| T3 | supported | check | True | ['CPU'] | ['raw/Custom LLM README.md', 'raw/Pac-Man DQN README.md', 'wiki/Projects/Custom LLM Training Runs.md', 'wiki/Projects/Pac-Man DQN Requirements.md'] | 1.6 | 55.7 |
| T4 | insufficient | pass | None | [] | [] | 0.692 | 56.1 |
