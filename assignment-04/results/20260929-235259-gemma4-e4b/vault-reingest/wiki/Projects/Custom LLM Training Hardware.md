---
title: Custom LLM Training Hardware
aliases:
  - Training Budget and Hardware Details
  - training-budget-and-hardware-details
topic: Projects
summary: Documents the computational resources and steps used during model training.
sources:
  - raw/Custom LLM README.md
source_id: custom-llm-readme
source_sha256: 0293ff499fdd970bee6aeb0310c48a81919cb8028af1272b13bf71c8ae71110e
sections_used:
  - Training budget and hardware
created: 2026-09-30
updated: 2026-09-30
reviewed: true
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: custom-llm-readme/training-budget-and-hardware-details
plan_origin: model-retry
---
# Custom LLM Training Hardware

## Summary

This note details the computational resources and steps used during model training, presenting a table summarizing four distinct runs. The main point is that I trained on an Apple M4 Pro laptop using specific software versions, and the results for the expanded runs were reproducible.

## Details

I trained on an Apple M4 Pro laptop with 12 CPU cores and 24 GB of memory running macOS 26.3, on the CPU, which is the notebook's default and caps PyTorch at four threads. The software was Python 3.13.15, PyTorch 2.14.0, NumPy 2.5.3, and pypdf 6.19.0. The course's reference run was on a Mac with the same PyTorch version, which is probably why the starter run reproduced it exactly.

The training runs were:
*   Setup check: completed, 10 steps, 0.1 s, 9.7 s, 111,872 parameters, 136 vocabulary.
*   Starter corpus: completed, 3,000 steps, 7.6 s, 11.7 s, 111,872 parameters, 136 vocabulary.
*   Corpus extension: completed, 3,000 steps, 12.2 s, 17.3 s, 130,496 parameters, 427 vocabulary.
*   Optional, 6,000 steps: completed, 6,000 steps, 23.0 s, 27.8 s, 130,496 parameters, 427 vocabulary.

No run was interrupted or failed. The training loop time is `elapsed_seconds` from each run's `training_summary.json`, and the whole-notebook time is the wall-clock time my shell reported for the run script. For the two expanded runs a repeat of each at the same settings produced the same weights.

## Related

- [[Custom LLM Training Runs]]: The setup check is the 10-step run the assignment suggests, whose summary, config, loss table, samples, and eval comparison are in `results/setup-check/`

## Sources

- [[wiki/Sources/Custom LLM README|Custom LLM README]]: `raw/Custom LLM README.md`, sections "Training budget and hardware"
