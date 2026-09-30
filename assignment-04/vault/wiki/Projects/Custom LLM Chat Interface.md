---
title: Custom LLM Chat Interface
aliases:
  - Interacting with Trained Model
  - interacting-with-trained-model
topic: Projects
summary: Describes the interface for chatting with the final trained model.
sources:
  - raw/Custom LLM README.md
source_id: custom-llm-readme
source_sha256: 0293ff499fdd970bee6aeb0310c48a81919cb8028af1272b13bf71c8ae71110e
sections_used:
  - Chat with the trained model
  - One limitation and the next experiment
  - Files and models
  - Where the code comes from
created: 2026-09-30
updated: 2026-09-30
reviewed: true
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: custom-llm-readme/interacting-with-trained-model
plan_origin: model-retry
---
# Custom LLM Chat Interface

## Summary

This note details the interface for interacting with the final trained model using the `chat.py` script. The process involves loading a saved `model.pt` and running a terminal loop that accepts prompts and prints the model's continuation. The note also discusses a limitation observed—that passing scores might come from shortcuts—and outlines the next planned experiment to test remaining extension skills.

## Details

The interface is the course's `chat.py`, a terminal loop that loads a saved `model.pt` with its vocabulary, takes a prompt, prints the model's continuation, and asks for another, with each prompt starting from a fresh context. It labels itself as a tiny language model, reports any prompt words outside the vocabulary, and says when a prompt longer than the 48-token context was truncated to its last 48 tokens. It never trains and never writes anything into `corpus/`. The transcript filename has to be new each time, since the script refuses to overwrite one.

I first ran it through `scripts/chat_demo.py`, which starts `chat.py` in a pseudo-terminal and types each prompt as a person would, so the transcript, `results/chat/chat_transcript.json`, was written by `chat.py` itself, and the screen text is in `results/chat/chat_session.log`. I then ran `chat.py` myself in Terminal on the same model and typed the same five prompts, the fourth without the space before one period, which the tokenizer reads the same way, and got the same replies, since `chat.py` seeds each turn from 2026 plus the turn's number.

The limitation I'd point to is that a passing score on these tests can come from a shortcut. The next experiment I'd run is the remaining four extension skills with the same method, at both 3,000 and 6,000 steps.

## Related

- [[Custom LLM Results]]: The chat transcripts and session logs, the Terminal screenshot, and the drawing of the 6,000-step session
- [[How the Custom LLM Learns]]: The corpus-extension experiment, executed with every output saved

## Sources

- [[wiki/Sources/Custom LLM README|Custom LLM README]]: `raw/Custom LLM README.md`, sections "Chat with the trained model", "One limitation and the next experiment", "Files and models", "Where the code comes from"
