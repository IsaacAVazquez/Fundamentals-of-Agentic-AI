# Search: Pac-Man evaluation score

k=6, scope=all, no model call. 6 passages.

## [1] raw/Pac-Man DQN README.md # The final run, 450 games (lines 145-149, score 13.56)

The final agent's best evaluation game was seed 303, which scored 1,770. Across the five evaluation games it chose down-left on 47% of its moves and up-right on 39%, and in this game it reached 1,150 points in the first 20 seconds without losing a life, including a jump from 610 to 1,070 in a couple of seconds right after the ghosts turned blue. It lost its first life at decision 488 of 872, well after the GIF ends. The move counts, and the per-game scores and life losses behind them, are in [results/450-games/move_shares.json](results/450-games/move_shares.json), which `scripts/eval_move_shares.py` wrote by replaying the saved agents on the same five games and reproducing every score in `comparison.json`.

![The final agent in its best evaluation game, seed 303, which scored 1,770](results/450-games/demos/final_best.gif)

The progress samples below all play evaluation seed 101, one every 25 training games, and they're identical to the first run's samples up to game 450. Their scores bounce between 350 and 1,410 with no steady climb, which is the same instability the checkpoint check measured on more games.

## [2] raw/Pac-Man DQN README.md # The first run, 500 games (lines 90-92, score 12.69)

Looking at which moves the agents chose explained more than the scores did. The untrained network pushes the joystick up and to the left on 96% of its moves across the five evaluation games, so the 492 baseline is really what holding one diagonal gets you. The final 500-game agent mostly chose no move at all, on 70% of its moves across the five games and on 80 to 88% of them in four of the five. Its best game, the 730 on seed 101, is also the game where it held up and to the left the most, and that's the game both of the run's final GIFs show, because the best-of-five GIF and the 500-game progress sample came out as the same file.

![The first run's final agent in its best evaluation game, seed 101, which scored 730](results/500-games/demos/final_best.gif)

## [3] wiki/Projects/Assignment Overview and Requirements Pac-Man.md # Details (lines 34-45, score 12.51)

| Requirement | Where it is |
| :--- | :--- |
| Overview and how to open and run the notebook | The paragraph above, and Open and run the notebook |
| Exploration, episodes, and learning rate, with a reason for each | My three choices |
| What I expected before training, then what I observed | What I expected before each run, and What happened |
| Completed episodes, decisions, learning updates, elapsed time, and hardware | Training budget and hardware |
| Observations, actions, and rewards in plain language | What the agent sees, does, and gets rewarded for |
| One observed limitation and one next experiment | One limitation and the next experiment |
| Untrained, best trained, and intermediate GIFs | Gameplay, under The final run |
| `training_dashboard.png` | Training dashboard, under The final run, with the first run's under The first run |
| All five baseline and trained scores, both means, and `comparison.json` | Evaluation scores, under The final run, with the first run's table under The first run |
| Links to the notebook, `config.json`, `training.csv`, and `training_summary.json`, and whether a run was interrupted | Training budget and hardware, and Files and checkpoints |

## [4] raw/Pac-Man DQN README.md # The final run, 450 games (lines 137-143, score 12.43)

The full record is in [results/450-games/comparison.json](results/450-games/comparison.json). None of the ten games hit the 3,000-decision time limit.

#### Gameplay

Every GIF shows only the first 20 seconds of a game at four times speed, while the score beside it counts the whole game. Before training, the network holds the joystick up and to the left on almost every move.

![The untrained network playing evaluation game 1, seed 101, which scored 350](results/450-games/demos/episode_0000.gif)

## [5] raw/Pac-Man DQN README.md # Where to find each requirement (lines 9-20, score 12.08)

| Requirement | Where it is |
| --- | --- |
| Overview and how to open and run the notebook | The paragraph above, and Open and run the notebook |
| Exploration, episodes, and learning rate, with a reason for each | My three choices |
| What I expected before training, then what I observed | What I expected before each run, and What happened |
| Completed episodes, decisions, learning updates, elapsed time, and hardware | Training budget and hardware |
| Observations, actions, and rewards in plain language | What the agent sees, does, and gets rewarded for |
| One observed limitation and one next experiment | One limitation and the next experiment |
| Untrained, best trained, and intermediate GIFs | Gameplay, under The final run |
| `training_dashboard.png` | Training dashboard, under The final run, with the first run's under The first run |
| All five baseline and trained scores, both means, and `comparison.json` | Evaluation scores, under The final run, with the first run's table under The first run |
| Links to the notebook, `config.json`, `training.csv`, and `training_summary.json`, and whether a run was interrupted | Training budget and hardware, and Files and checkpoints |

## [6] raw/Pac-Man DQN README.md # Ms. Pac-Man DQN (lines 3-3, score 11.49)

I trained this agent for Assignment 2 of Fundamentals of Agentic AI. It's the course's Deep Q-Network notebook for Ms. Pac-Man, run on my laptop with 10% exploration and a learning rate of 0.0001. I ran it twice, and the only difference between the two runs is the number of training games. My first run trained for 500 games, and its final agent averaged 400 on the five evaluation games against 492 for the untrained network. When I replayed every checkpoint that run saved on games the notebook never uses, the agent saved after 450 games turned out to be far better than the one the run ended with, so I reran the notebook with 450 games. The notebook in this folder is that second run, executed start to finish with every output saved, and its agent averaged 946 on the same five evaluation games against 492 for the untrained network.

