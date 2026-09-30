# Ask-mode test summary

Run `smoke-online`, questions from `tests/questions.json`.

| id | status | verdict | retrieval hit | keywords found | cited paths | wall s | tok/s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | supported | check | True | ['CPU'] | ['raw/Custom LLM README.md'] | 10.28 | 51.7 |
| T2 | supported | pass | True | ['450', 'checkpoint'] | ['raw/Pac-Man DQN README.md'] | 4.777 | 51.8 |
| T3 | supported | pass | True | ['M4 Pro', 'MPS', 'CPU'] | ['raw/Custom LLM README.md', 'raw/Pac-Man DQN README.md', 'wiki/Projects/Assignment Model Training Overview.md', 'wiki/Projects/Training Budget and Hardware Details Pac-Man.md'] | 4.886 | 51.8 |
| T4 | partial | fail | None | [] | ['wiki/Projects/Assignment DQN Training Overview.md'] | 3.705 | 52.5 |
