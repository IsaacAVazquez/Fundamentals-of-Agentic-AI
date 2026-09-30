---
title: LLM Behavior and Probabilistic Nature
aliases:
  - llm-behavior-and-probabilistic-nature
topic: Course
summary: Recapping LLMs as probabilistic token predictors and the role of temperature.
sources:
  - raw/Class 5 Prompting and Retrieval Notes.md
source_id: class-5-prompting-and-retrieval-notes
source_sha256: 535af3de2b0afdda285bcf17d3bfbb3850936db0c8ef4fed9584cff5f7c34a1c
sections_used:
  - "Class 5: LLM Behavior, Prompting & Retrieval"
  - Why This Class?
  - Yesterday’s “Nice to Have” Is Tomorrow’s “Must Have”
  - What This Class Gives You
  - Agenda
  - Class 4 Recap
  - "Slide 1 of 2: LLMs Predict Tokens"
  - "Slide 2 of 2: LLMs Are Probabilistic"
  - “It Knows” Is a Risky Shorthand
  - The Probability Distribution Is the Steering Surface
  - Practical Implications
  - "Temperature: The Creativity Dial"
  - What Is Fine-Tuning?
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: class-5-prompting-and-retrieval-notes/llm-behavior-and-probabilistic-nature
plan_origin: model-retry
---
# LLM Behavior and Probabilistic Nature

## Summary

This note recaps that Large Language Models (LLMs) fundamentally operate by predicting the next token based on a probability distribution, rather than looking up verified facts. The key takeaway is that this probability distribution is the "steering surface," which can be influenced by various methods like prompting or setting the temperature. Understanding this probabilistic nature is crucial for knowing how to guide the model's output effectively.

## Details

At the core, an LLM does one thing:
given the context so far, predict the next token

The model does not produce one guaranteed answer; it produces a **probability distribution** over possible next tokens, then samples from it.

*   **Temperature: The Creativity Dial**
    *   Every API call includes a **temperature** setting — a number that controls how “random” the output is.
    *   Low temp is good for facts, code, extraction, but risks being repetitive, boring.
    *   High temp is good for brainstorming, writing, ideas, but risks hallucinations, nonsense.
    *   Temperature changes **variety, not intelligence**. Lower temperature favors more likely continuations; higher temperature explores more possibilities and raises variance.

## Related

- [[Prompting as Probability Steering]]: prompts steer the probability distribution
- [[Structuring Prompts as Product Interfaces]]: Prompts are product interfaces
- [[Advanced Retrieval and Knowledge Hub]]: Capstone: Knowledge Hub v1

## Sources

- [[wiki/Sources/Class 5 Prompting and Retrieval Notes|Class 5 Prompting and Retrieval Notes]]: `raw/Class 5 Prompting and Retrieval Notes.md`, sections "Class 5: LLM Behavior, Prompting & Retrieval", "Why This Class?", "Yesterday’s “Nice to Have” Is Tomorrow’s “Must Have”", "What This Class Gives You", "Agenda", "Class 4 Recap" and more
