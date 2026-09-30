---
title: Structuring Prompts as Product Interfaces
aliases:
  - structuring-prompts-as-product-interfaces
topic: Concepts
summary: Best practices for designing prompts to specify jobs and maintain structure.
sources:
  - raw/Class 5 Prompting and Retrieval Notes.md
source_id: class-5-prompting-and-retrieval-notes
source_sha256: 535af3de2b0afdda285bcf17d3bfbb3850936db0c8ef4fed9584cff5f7c34a1c
sections_used:
  - The Prompt Is the Spec
  - A Good Prompt Specifies the Job
  - Context Is Not Background Reading
  - Separate Instructions From Data
  - Instruction Hierarchy Is a Trust Boundary
  - Output Format Is a Reliability Tool
  - Examples Teach a Pattern
  - Constraints Beat Vague Adjectives
  - Prompting Is Experimental Work
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: class-5-prompting-and-retrieval-notes/structuring-prompts-as-product-interfaces
plan_origin: model-retry
---
# Structuring Prompts as Product Interfaces

## Summary

Designing prompts for product use requires treating them as versioned API contracts rather than simple messages. The core principle is to specify the job clearly by defining the role, task, and exact deliverables, while rigorously separating instructions from data. The main result is that structured, testable prompts lead to reliable, predictable outputs that can be consumed by downstream systems.

## Details

*   **The Prompt Is the Spec**: A product prompt must work on unanticipated user inputs and on the model version that shipped last night. I must treat every prompt that ships like an API contract: specified, versioned, and tested.
*   **A Good Prompt Specifies the Job**: I should name the **role**, the **task**, and the **exact deliverables**, avoiding adjectives like “please be thorough.”
*   **Context Is Not Background Reading**: I must put in the material that should influence the response, as dumping the whole wiki is noise. I learned the term: **context engineering**. The job is deciding **what occupies the context window on every single call**: system rules, retrieved evidence, tool results, conversation history, and what gets dropped when space runs out.
*   **Separate Instructions From Data**: I should use visible separation, such as `SYSTEM:`, `USER:`, and `REFERENCE:`, to keep roles distinct.
*   **Instruction Hierarchy Is a Trust Boundary**: I must remember that **retrieved text is data, never instructions**, to prevent prompt injection.
*   **Output Format Is a Reliability Tool**: When another system needs to consume the result, I should ask for a schema, like `{"risk": "low|medium|high", "evidence": ["..."], "next_action": "..."}`.
*   **Examples Teach a Pattern**: Few-shot examples are useful for consistency, and three examples covering edge cases are better than a page of description.
*   **Constraints Beat Vague Adjectives**: I should use constraints like “Cite only supplied sources; say ‘insufficient evidence’ if none apply” instead of vague adjectives.
*   **Prompting Is Experimental Work**: I must make a small test set, change one variable, inspect failures, and keep the version that improves the metric I care about.

## Related

- [[Prompting as Probability Steering]]: The concept of treating prompts as specifications and testing variables relates to steering model behavior
- [[Model Customization Techniques Comparison]]: The discussion of different input channels (SYSTEM, USER, REFERENCE) relates to structuring inputs

## Sources

- [[wiki/Sources/Class 5 Prompting and Retrieval Notes|Class 5 Prompting and Retrieval Notes]]: `raw/Class 5 Prompting and Retrieval Notes.md`, sections "The Prompt Is the Spec", "A Good Prompt Specifies the Job", "Context Is Not Background Reading", "Separate Instructions From Data", "Instruction Hierarchy Is a Trust Boundary", "Output Format Is a Reliability Tool" and more
