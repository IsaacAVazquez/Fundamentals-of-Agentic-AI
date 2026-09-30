---
title: Performance Analysis Before Runs
aliases:
  - performance-analysis-before-runs
topic: Projects
summary: Recording and comparing expected performance metrics before the agent's training runs began.
sources:
  - raw/Pac-Man DQN README.md
source_id: pac-man-dqn-readme
source_sha256: cd469243a82e4f8b831e84de0e0e23277841ebb23499bde0585bb31c84a7fd69
sections_used:
  - What I expected before each run
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: pac-man-dqn-readme/performance-analysis-before-runs
plan_origin: model-retry
---
# Performance Analysis Before Runs

## Summary

This note details the expected performance metrics recorded before the agent's training runs. The initial expectation was a significant improvement over the untrained network, which showed high variance across five-game checks. For the final run, I anticipated the agent's score to be near the 1,033 average achieved by the 450-game checkpoint on 50 test games.

## Details

I recorded both predictions before the runs started.

Before the first run, I expected a clear gain over the untrained network, whose five-game average had been 492 in the 9/8 and 9/9 setup checks, but with a lot of swing from one game to the next. My reasoning was that 500 games is a hundred times the five-game check, where the trained agent actually scored worse than the untrained one, and that 10% exploration keeps training closer to the way the agent gets scored.

Before the final run, I expected its agent to land near the 1,033 average that the 450-game checkpoint had scored on 50 test games, described below, but five games is a small sample, so I wouldn't have been surprised by anything from roughly 500 to 1,500.

## Related

- [[Assignment Model Training Overview]]: This note discusses performance expectations before training runs
- [[Model Performance and Results]]: The note compares expected performance to previous checkpoint scores

## Sources

- [[wiki/Sources/Pac-Man DQN README|Pac-Man DQN README]]: `raw/Pac-Man DQN README.md`, sections "What I expected before each run"
