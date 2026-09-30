---
title: Prompting as Probability Steering
aliases:
  - prompting-as-probability-steering
topic: Concepts
summary: Understanding prompting as steering the model's probability distribution.
sources:
  - raw/Class 5 Prompting and Retrieval Notes.md
source_id: class-5-prompting-and-retrieval-notes
source_sha256: 535af3de2b0afdda285bcf17d3bfbb3850936db0c8ef4fed9584cff5f7c34a1c
sections_used:
  - Prompting Is Probability Steering
  - Don’t Mistake the Mask for the Model
  - Attention Failure — The Model Answers the Wrong Question
  - Why Voice-to-Text Prompts Can Help
  - LLMs Do Not Start Fresh Per Message
  - Context Is Everything
  - Prompts Are Product Interfaces
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: class-5-prompting-and-retrieval-notes/prompting-as-probability-steering
plan_origin: model-retry
---
# Prompting as Probability Steering

## Summary

Prompting functions as guidance, effectively steering the model's probability distribution by reducing ambiguity. When you add detail, examples, constraints, and formatting requirements, you make the desired answer more probable. The core concept is that context, which is provided through prompts, is what directs the model's output.

## Details

*   **Prompting Is Probability Steering**
    *   When you add detail, examples, constraints, and formatting requirements, you are shrinking the space of acceptable continuations and making the “right” answer more likely.
    *   Specific prompts reduce ambiguity. Less ambiguity means lower entropy in the next-token distribution, so the model is less likely to wander into the wrong answer shape.
*   **Don’t Mistake the Mask for the Model**
    *   Underneath is a **next-token predictor trained on the internet**, shaped by RLHF into something that sounds human. Prompt it like a tool, not a colleague.
*   **Attention Failure — The Model Answers the Wrong Question**
    *   The model isn’t stupid — it’s **under-specified**.
*   **Why Voice-to-Text Prompts Can Help**
    *   People get better results when they **talk** to the model instead of typing a short command because speech naturally includes more context, people say the edge cases they would have omitted, they explain intent, not just task labels, and longer natural prompts often reduce ambiguity.
    *   To do it: Use **WhisperFlow** (free app, transcribes anywhere you can type), **Mac dictation** (press 🎤 on the keyboard or double-tap Fn), or **Claude / ChatGPT voice** (tap the mic icon in the app).
    *   Dictate the messy version first. Then tighten it into bullets, constraints, examples, and output format.
*   **LLMs Do Not Start Fresh Per Message**
    *   The model does **not** think of your second message as “a totally new brain state.”
    *   It starts fresh per **API request**, but the request usually includes the conversation so far.
    *   Continuity comes from resending context.
*   **Context Is Everything**
    *   Every word the model reads — system prompt, chat history, your latest message — is **context**. Context is what steers the probability distribution toward the right answer.
*   **Prompts Are Product Interfaces**

## Related

- [[LLM Behavior and Probabilistic Nature]]: Prompting Is Probability Steering
- [[Structuring Prompts as Product Interfaces]]: Prompts Are Product Interfaces

## Sources

- [[wiki/Sources/Class 5 Prompting and Retrieval Notes|Class 5 Prompting and Retrieval Notes]]: `raw/Class 5 Prompting and Retrieval Notes.md`, sections "Prompting Is Probability Steering", "Don’t Mistake the Mask for the Model", "Attention Failure — The Model Answers the Wrong Question", "Why Voice-to-Text Prompts Can Help", "LLMs Do Not Start Fresh Per Message", "Context Is Everything" and more
