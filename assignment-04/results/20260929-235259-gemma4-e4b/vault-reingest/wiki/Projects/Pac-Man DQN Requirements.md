---
title: Pac-Man DQN Requirements
aliases:
  - Assignment Overview and Requirements Pac-Man
  - assignment-overview-and-requirements-pac-man
topic: Projects
summary: This section outlines the structure and requirements for the assignment using a reference table.
sources:
  - raw/Pac-Man DQN README.md
source_id: pac-man-dqn-readme
source_sha256: cd469243a82e4f8b831e84de0e0e23277841ebb23499bde0585bb31c84a7fd69
sections_used:
  - Ms. Pac-Man DQN
  - Where to find each requirement
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: pac-man-dqn-readme/assignment-overview-and-requirements-pac-man
plan_origin: model-retry
---
# Pac-Man DQN Requirements

## Summary

This note details the process and results of training an agent for Assignment 2 of Fundamentals of Agentic AI using the Deep Q-Network notebook for Ms. Pac-Man. I trained the agent twice, noting that rerunning the notebook with 450 games yielded a significantly better result compared to the initial 500-game run. The note also provides a reference table mapping assignment requirements to specific sections within the notebook.

## Details

I trained this agent for Assignment 2 of Fundamentals of Agentic AI. It's the course's Deep Q-Network notebook for Ms. Pac-Man, run on my laptop with 10% exploration and a learning rate of 0.0001. I ran it twice, and the only difference between the two runs is the number of training games. My first run trained for 500 games, and its final agent averaged 400 on the five evaluation games against 492 for the untrained network. When I replayed every checkpoint that run saved on games the notebook never uses, the agent saved after 450 games turned out to be far better than the one the run ended with, so I reran the notebook with 450 games. The notebook in this folder is that second run, executed start to finish with every output saved, and its agent averaged 946 on the same five evaluation games against 492 for the untrained network.

The sections below follow the order of the assignment's README requirements. This table is the short version for anyone grading against the brief.

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

## Related

- [[Running the DQN Notebook]]: how to run the notebook these requirements point to

## Sources

- [[wiki/Sources/Pac-Man DQN README|Pac-Man DQN README]]: `raw/Pac-Man DQN README.md`, sections "Ms. Pac-Man DQN", "Where to find each requirement"
