---
title: Agent Training Results and Limitations
aliases:
  - agent-training-results-and-limitations
topic: Projects
summary: Presenting the results from the first and final training runs, along with observed agent limitations.
sources:
  - raw/Pac-Man DQN README.md
source_id: pac-man-dqn-readme
source_sha256: cd469243a82e4f8b831e84de0e0e23277841ebb23499bde0585bb31c84a7fd69
sections_used:
  - What happened
  - The first run, 500 games
  - Checking the checkpoints on games the notebook never plays
  - The final run, 450 games
  - Training budget and hardware
  - What the agent sees, does, and gets rewarded for
  - One limitation and the next experiment
  - Files and checkpoints
  - Where the code comes from
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: pac-man-dqn-readme/agent-training-results-and-limitations
plan_origin: model-retry
---
# Agent Training Results and Limitations

## Summary

This note details the results and limitations observed during two agent training runs for Pac-Man: one with 500 games and a final one with 450 games. The final 450-game run showed a significant improvement, achieving an average score of 946 against the untrained network's 492. However, the analysis also highlights the instability of performance, noting that the best checkpoint from the 450-game run significantly outperformed the final agent on a separate set of 50 test games.

## Details

### The first run, 500 games
The trained agent beat the untrained network on two of the five games and lost on three, with an average score 92 points lower than the untrained network. The 25-game average stayed between about 580 and 1,020 from the fifth game to the last, and the loss rose from about 0.02 to about 0.13. The untrained network pushed the joystick up and to the left on 96% of its moves across the five evaluation games. The final 500-game agent mostly chose no move at all, on 70% of its moves across the five games.

### Checking the checkpoints on games the notebook never plays
I wrote `scripts/check_checkpoints.py` to replay saved agents on more games. Averaged over the same 30 validation games, the untrained network scored 449 and the 20 checkpoints ranged from 418 to 1,182. On 50 more games, the 450-game checkpoint averaged 1,033 against 454 for the untrained network, which is 579 points higher. The final 500-game agent averaged 499 on those same 50 games, 45 points above the untrained network.

### The final run, 450 games
On the five evaluation games, the final agent beat the untrained network on three and lost on two, with an average of 946 against 492, a gain of 454 points. The final agent's best evaluation game was seed 303, which scored 1,770. The progress samples showed scores bouncing between 350 and 1,410 with no steady climb.

### Training budget and hardware
| Run | Status | Completed games | Decisions | Learning updates | Training loop time | Whole notebook |
| --- | --- | --- | --- | --- | --- | --- |
| First, 500 games | completed | 500 | 303,666 | 75,667 | 837.5 s, about 14.0 minutes | 852 s, about 14.2 minutes |
| Final, 450 games | completed | 450 | 274,814 | 68,454 | 761.9 s, about 12.7 minutes | 777 s, about 13.0 minutes |

- Model Performance and Results: This note presents the results from the first and final training runs, along with observed agent limitations.
- Assignment Model Training Overview: The note details the process of checking checkpoints and comparing the 450-game run to the 500-game run.

## Related

- [[Model Performance and Results]]: This note details the specific performance metrics observed

## Sources

- [[wiki/Sources/Pac-Man DQN README|Pac-Man DQN README]]: `raw/Pac-Man DQN README.md`, sections "What happened", "The first run, 500 games", "Checking the checkpoints on games the notebook never plays", "The final run, 450 games", "Training budget and hardware", "What the agent sees, does, and gets rewarded for" and more
