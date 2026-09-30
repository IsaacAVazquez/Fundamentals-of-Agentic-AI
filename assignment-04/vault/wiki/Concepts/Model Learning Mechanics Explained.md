---
title: Model Learning Mechanics Explained
aliases:
  - model-learning-mechanics-explained
topic: Concepts
summary: Explains how the model learns using specific run numbers and files.
sources:
  - raw/Custom LLM README.md
source_id: custom-llm-readme
source_sha256: 0293ff499fdd970bee6aeb0310c48a81919cb8028af1272b13bf71c8ae71110e
sections_used:
  - How the model learns, with this run's numbers
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: custom-llm-readme/model-learning-mechanics-explained
plan_origin: model-retry
---
# Model Learning Mechanics Explained

## Summary

This note explains the mechanics of how the model learns during training, detailing the process from tokenization to parameter updates. The core mechanism involves predicting the next token in a sequence using learned embeddings and transformer blocks, with the loss function guiding the adjustment of the model's parameters. The main result shown is that training significantly alters word representations, causing related words to cluster together in the embedding space.

## Details

Everything in this section is from the corpus-extension run unless it says otherwise, and the files are [results/expanded/tokenization.json](results/expanded/tokenization.json) and [results/expanded/inspection.json](results/expanded/inspection.json).

The corpus is a collection of short passages, and the network only ever sees passages, one at a time in batches of 32, each one as a sequence of tokens. A token here is a whole word or a punctuation mark, and the vocabulary is the list of every token type that occurred in the training passages, 424 of them plus three special tokens, so the tokenizer turns text into a list of integers by looking each word up in that list. The notebook's own example is the first training passage, `today the station focused on traffic and the important truck .`, which becomes the IDs `1, 376, 366, 343, 133, 254, 379, 8, 366, 173, 383, 3, 2`, where 1 is the start token, 2 is the end token, 3 is the period, and 366 is the both times it appears. An ID is a row number and nothing more. The training example the network gets from that passage is the sequence shifted by one, every token as the input and the following token as the target, so from `today the station` it should predict focused, and so on through the passage.

The embedding is what a row holds. The token embedding table has 427 rows of 64 numbers, one row per vocabulary entry, and the word customer is row 93 in this run's vocabulary. Those 64 numbers are parameters, which is to say they start random and training changes them, and they are the word as the network sees it. Row 93 started as
```
0.016, -0.040, 0.008, 0.005, 0.033, -0.019, -0.001, -0.002, 0.004, 0.015, 0.006, 0.017, -0.007, -0.015, -0.041, -0.016,
0.013, -0.026, -0.005, 0.004, -0.017, 0.004, 0.004, 0.000, -0.021, -0.052, -0.014, -0.026, -0.025, -0.026, -0.017, -0.009,
0.010, -0.037, -0.006, 0.016, 0.017, 0.001, 0.010, 0.012, 0.016, -0.006, 0.038, 0.008, -0.006, -0.003, 0.028, -0.019,
0.025, -0.036, 0.017, 0.061, 0.039, -0.014, -0.016, 0.014, -0.016, -0.001, -0.024, -0.013, 0.021, -0.043, 0.035, 0.001
```
and finished, after 3,000 updates, as
```
0.000, -0.161, 0.036, -0.061, 0.007, -0.095, 0.158, 0.025, 0.052, 0.018, 0.066, 0.013, -0.047, -0.149, 0.064, 0.074,
0.062, -0.061, 0.145, 0.015, -0.063, -0.024, 0.101, -0.006, 0.022, -0.043, 0.037, -0.050, 0.041, -0.126, -0.044, 0.003,
-0.071, 0.024, 0.117, -0.067, -0.100, 0.087, -0.121, -0.046, -0.002, -0.050, -0.081, -0.069, 0.039, 0.107, -0.065, 0.089,
0.025, -0.136, -0.047, 0.154, 0.193, -0.019, 0.052, -0.059, -0.145, 0.034, -0.049, 0.052, 0.102, -0.061

## Related

_No related notes yet._

## Sources

- [[wiki/Sources/Custom LLM README|Custom LLM README]]: `raw/Custom LLM README.md`, sections "How the model learns, with this run's numbers"
