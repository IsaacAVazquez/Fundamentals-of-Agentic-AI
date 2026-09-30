---
title: Model Customization Techniques Comparison
aliases:
  - model-customization-techniques-comparison
topic: Concepts
summary: Comparing fine-tuning, LoRA, and prompting for model adaptation.
sources:
  - raw/Class 5 Prompting and Retrieval Notes.md
source_id: class-5-prompting-and-retrieval-notes
source_sha256: 535af3de2b0afdda285bcf17d3bfbb3850936db0c8ef4fed9584cff5f7c34a1c
sections_used:
  - Fine-Tuning Reshapes the Distribution
  - RLHF — How Models Learn to Be Helpful
  - Alignment Is Product Design
  - …But It’s Super Expensive
  - Three Levers, Three Jobs
  - The Three Levers — Visually
  - Prompting vs LoRA vs Fine-Tuning — The Decision Table
  - Prompting
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: class-5-prompting-and-retrieval-notes/model-customization-techniques-comparison
plan_origin: model-retry
---
# Model Customization Techniques Comparison

## Summary

This note compares three model adaptation techniques—prompting, LoRA, and full fine-tuning—to help determine the best approach for customizing an LLM. Prompting is the cheapest and most temporary method, ideal for day-to-day use, while full fine-tuning is the most expensive and permanent. The decision should be guided by whether the need is for better instructions, external facts, or deep behavioral changes.

## Details

**Fine-Tuning Reshapes the Distribution**
*   Fine-tuning trains a pretrained model further on specific data, which shifts which tokens the model considers likely.
*   Fine-tuning is **expensive and permanent** because it changes the model’s weights.
*   Prompting is **cheap and temporary** because it steers the same frozen model.

**RLHF — How Models Learn to Be Helpful**
*   Post-training has three stages:
    1.  **Pretraining** (*unsupervised*): predict next token from raw internet.
    2.  **SFT — Supervised Fine-Tuning** (*supervised*): labeled *instruction → good-response* pairs.
    3.  **RLHF — Reinforcement Learning from Human Feedback** (*reinforcement*): uses human preference (*A vs. B, which is better?*), encoded in a **reward model** and optimized via **PPO** or **DPO**.
*   **Important:** *A prompt can’t override what RLHF taught.* This is the difference between **personality** (prompt-level, changeable per-session) and **values** (weight-level, baked in forever).

**Three Levers, Three Jobs**
*   **Prompting** changes the instruction for one request. Use it when the capability exists but the model needs clearer goals, constraints, format, or examples.
*   **Retrieval** changes the context for one request. Use it when answers must be grounded in changing, private, or citeable knowledge.
*   **Fine-tuning** changes the model’s learned behavior. Use it when a stable, repeated pattern is hard to prompt and you have high-quality examples.

**Prompting vs LoRA vs Fine-Tuning — The Decision Table**
*   **Prompting / system prompt**: steers the frozen model; cost ~\$0; time minutes; reversible instantly; reach for it when almost always — the default.
*   **Few-shot examples**: more context per request; cost pennies per call; time hours; reversible instantly; reach for it when format, style, or label taxonomy must be consistent.
*   **RAG**: changes the context, per request; cost \$10s–\$100s/mo infra; time days; reversible yes; reach for it when facts are private, changing, or must be cited.
*   **LoRA fine-tune**: trains a small **adapter** (~0.1–1% of weights); cost \$100s–\$10Ks; time days–weeks; reversible swap the adapter out; reach for it when tone, domain jargon, or output shape that prompts can’t hold.
*   **Full fine-tune**: changes all the weights; cost \$10Ks–\$1Ms; time weeks; reversible no — new model; reach for it when you have thousands of gold examples and a stable task.

## Related

- [[Prompting as Probability Steering]]: Prompting is cheap and temporary — it steers the same frozen model
- [[Structuring Prompts as Product Interfaces]]: Prompting changes the instruction for one request
- [[Advanced Retrieval and Knowledge Hub]]: Retrieval changes the context for one request

## Sources

- [[wiki/Sources/Class 5 Prompting and Retrieval Notes|Class 5 Prompting and Retrieval Notes]]: `raw/Class 5 Prompting and Retrieval Notes.md`, sections "Fine-Tuning Reshapes the Distribution", "RLHF — How Models Learn to Be Helpful", "Alignment Is Product Design", "…But It’s Super Expensive", "Three Levers, Three Jobs", "The Three Levers — Visually" and more
