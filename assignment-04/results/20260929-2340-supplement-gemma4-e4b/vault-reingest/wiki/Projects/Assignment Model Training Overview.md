---
title: Assignment Model Training Overview
aliases:
  - assignment-model-training-overview
topic: Projects
summary: Details the setup and initial training runs for the custom LLM assignment.
sources:
  - raw/Custom LLM README.md
source_id: custom-llm-readme
source_sha256: 0293ff499fdd970bee6aeb0310c48a81919cb8028af1272b13bf71c8ae71110e
sections_used:
  - Custom LLM with nanoGPT
  - Where to find each requirement
  - Open and run the notebook
  - My three choices
  - What I expected before each run
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: custom-llm-readme/assignment-model-training-overview
plan_origin: model-retry
---
# Assignment Model Training Overview

## Summary

This note details the setup and results of training a custom LLM using nanoGPT for Assignment 3 of Fundamentals of Agentic AI. I conducted three training runs—a starter run, a corpus-extension run, and an optional third run—by adjusting training steps while keeping the learning rate constant. The main result shows that adding my own teaching passages significantly improved performance, moving the model from 20/48 correct tests to 35/48, with the optional run achieving 35/48 while losing one specific pattern.

## Details

I trained this model for Assignment 3 of Fundamentals of Agentic AI. It's the course's word-token nanoGPT notebook, a two-block, four-head transformer with 64-number embeddings and a 48-token context, run on my laptop's CPU.

In the first run, I trained on the course's classroom corpus for 3,000 steps at a learning rate of 0.001, and the trained model got 20 of the 48 tests right, with 24 of the 48 unscorable because their words were not in the vocabulary. Its weights came out identical to the course's published reference model, which I checked by hash.

In the second run, I added 2,215 teaching passages of my own for four of the eight extension skills, grammar, opposites, negation, and reference, and trained a fresh model with the same two settings. That made 12 more tests scorable and the trained model got 35 of 48, with the one miss in reference.

For an optional third experiment, I doubled the steps to 6,000 and changed nothing else I set. It got all 12 of the extension tests in the four skills I taught but lost 1 of the 8 new phrasings of the starter patterns, for 35 of 48 again.

I kept the corpus as the classroom sentences for the first run because the assignment requires a starter run before any extension, and it's the run the course's own reference results were measured on. For the second run I kept the classroom sentences and added my files on top. I kept 3,000 steps for both required runs because it's the course's starting budget. The optional third run changed only this setting, to 6,000. I kept the learning rate at 0.001 because it's the recommended starting point.

## Related

- [[Model Performance and Results]]: This note details the setup and initial training runs for the custom LLM assignment
- [[Training Budget and Hardware Details]]: I kept 3,000 steps for both required runs because it's the course's starting budget
- [[Model Customization Techniques Comparison]]: For the second run I kept the classroom sentences and added my files on top

## Sources

- [[wiki/Sources/Custom LLM README|Custom LLM README]]: `raw/Custom LLM README.md`, sections "Custom LLM with nanoGPT", "Where to find each requirement", "Open and run the notebook", "My three choices", "What I expected before each run"
