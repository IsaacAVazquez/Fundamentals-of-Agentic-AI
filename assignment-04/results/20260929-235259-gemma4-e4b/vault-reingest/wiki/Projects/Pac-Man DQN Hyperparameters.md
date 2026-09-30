---
title: Pac-Man DQN Hyperparameters
aliases:
  - Agent Hyperparameter Tuning Choices
  - agent-hyperparameter-tuning-choices
topic: Projects
summary: A comparison of starting and final values for key training settings like exploration and learning rate.
sources:
  - raw/Pac-Man DQN README.md
source_id: pac-man-dqn-readme
source_sha256: cd469243a82e4f8b831e84de0e0e23277841ebb23499bde0585bb31c84a7fd69
sections_used:
  - My three choices
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: pac-man-dqn-readme/agent-hyperparameter-tuning-choices
plan_origin: model-retry
---
# Pac-Man DQN Hyperparameters

## Summary

This note details my specific choices for key hyperparameters during the agent's training process, including exploration, episodes, and learning rate. The main point is that I adjusted these settings—setting exploration to 0.10, keeping the learning rate at 0.0001, and adjusting episodes to 450 for the final run—to better align the training with the evaluation environment.

## Details

| Setting | Starting value | First run | Final run |
| :--- | :--- | :--- | :--- |
| Exploration | 0.20 | 0.10 | 0.10 |
| Episodes | 100 | 500 | 450 |
| Learning rate | 0.0001 | 0.0001 | 0.0001 |

Everything else is exactly as the course ships it, including the five evaluation seeds, the 5% random moves during evaluation, and the cap of 3,000 decisions per game.

I set exploration to 0.10, so one training move in ten is random once the 1,000-move warm-up is over. The course's build-from-scratch prompt decays exploration toward 0.1, and a lower rate keeps practice closer to the way the agent gets scored, since evaluation uses 5% random moves.

I kept the learning rate at 0.0001. It's the notebook's reference value and the rate the course's build-from-scratch prompt starts Adam at, and with a replay memory of only 5,000 decisions I wanted steady updates more than fast ones.

For the first run I picked 500 episodes because a five-game run only checks the setup, and on this laptop 500 games looked like roughly 20 to 35 minutes, which I thought was long enough for learning to show up in the evaluation games the class leaderboard uses. For the final run I changed episodes to 450 and nothing else, because of what I found when I checked the first run's checkpoints, which is laid out under What happened.

## Related

- [[Pac-Man DQN Results and Limitations]]: the scores the agent reached with these settings

## Sources

- [[wiki/Sources/Pac-Man DQN README|Pac-Man DQN README]]: `raw/Pac-Man DQN README.md`, sections "My three choices"
