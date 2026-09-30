---
title: Advanced Retrieval and Knowledge Hub
aliases:
  - advanced-retrieval-and-knowledge-hub
topic: Projects
summary: Covering RAG, vector databases, and the architecture for a knowledge hub.
sources:
  - raw/Class 5 Prompting and Retrieval Notes.md
source_id: class-5-prompting-and-retrieval-notes
source_sha256: 535af3de2b0afdda285bcf17d3bfbb3850936db0c8ef4fed9584cff5f7c34a1c
sections_used:
  - Context Windows and Memory
  - How Big Is a Context Window?
  - Bigger Context Is Not a Free Solution
  - Context Rot Is Real
  - But Context Fills Up — Enter Compression
  - Put Stable Rules in Stable Places
  - Why Everyone Talks About Tokens
  - Prompt Engineering
  - .md Files — Why They’re Everywhere in AI
  - What Is a System Prompt?
  - CLAUDE.md & Project Files
  - What Gets Sent Each Turn
  - The Golden Rule of Prompting
  - Thinking Models
  - The Biggest Shift Since GPT
  - What Are “Thinking” Models?
  - Same Puzzle, Thinking On — Intent Catches Itself
  - Thinking Is Not a Permission Slip to Skip Evaluation
  - Match the Model to the Task
  - Delegate a Bounded Subproblem
  - "Tip: Use Plan Mode"
  - Hallucination Is a System Property
  - Why Fluent Systems Can Be Wrong
  - Four Defenses
  - Retrieval Augmented Generation
  - There’s Still a Problem
  - Retrieval Augmented Generation (RAG)
  - You Already Use RAG
  - Why RAG Matters
  - Building a Tiny RAG Demo
  - Retrieval Is a Pipeline, Not a Magic Box
  - Chunk for a Future Question
  - Metadata Prevents Cross-Contamination
  - Retrieval Should Return Evidence, Not Just Confidence
  - “No Answer Found” Is a Successful Result
  - Retrieval Quality Needs Its Own Metric
  - Retrieval Can Fail in Several Ways
  - Grounding Is a User-Visible Feature
  - Privacy Shapes the Architecture
  - Embeddings & Vector Databases
  - TF-IDF Has a Blind Spot
  - From Word Counts to Dense Vectors
  - Same Math, Better Vectors
  - Where Do a Million Vectors Live? — Vector Databases
  - Hybrid Search — Because Meaning Isn’t Everything
  - Hybrid Search — Visually
  - "Assignment 4: Knowledge Hub v1"
  - The Product
  - Where This Is Going — Your Personal AI Knowledge Hub
  - Architecture
  - "The Karpathy Pattern: 3 Layers"
  - Why Obsidian
  - Starter Location
  - The v1 Boundary
  - Choose a Corpus You Can Inspect
  - Define Three Answerable Questions
  - Keep Raw Sources Immutable
  - Make the Index a Product Surface
  - Test Retrieval Before Generation
  - Add a Grounded Answer Policy
  - Evidence Card
  - "Definition of Done: Knowledge Hub v1"
  - Next Class
  - Thank You & What’s Next
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: class-5-prompting-and-retrieval-notes/advanced-retrieval-and-knowledge-hub
plan_origin: model-retry
---
# Advanced Retrieval and Knowledge Hub

## Summary

This note covers advanced concepts in AI interaction, focusing on context management, retrieval augmentation, and advanced prompting techniques. It details how context windows are limited and how to use structured methods like RAG and "thinking models" to improve reliability. The main takeaway is that durable knowledge requires external, structured storage rather than relying solely on the model's immediate context.

## Details

*   **Context Windows and Memory**: State-of-the-art models like **Claude Opus** have a context window of **1 million tokens**. This can hold **two copies** of the full **Lord of the Rings** trilogy. However, bigger context raises cost and latency, and the model only sees the active context.
*   **Context Rot Is Real**: As prompts get cluttered, a model can miss, misweight, or contradict material. Research calls this **“lost in the middle”**. A practical fix is to **start a new chat** and bring only what matters.
*   **But Context Fills Up — Enter Compression**: When the window fills, **compaction** summarizes old conversation into a compact block, which is **lossy summarization**. Anything that **must** persist should live in `CLAUDE.md` or a plan file.
*   **Put Stable Rules in Stable Places**: Conversation is volatile, files are durable. System prompts, durable project files, and structured state are better homes for rules than a long casual conversation.
*   **Tokens**: Each token processed is a pass through a neural network. **Input is cheap, output is expensive.**
*   **.md Files — Why They’re Everywhere in AI**: A `.md` file is a **markdown** file, which is a simple way to write formatted text using plain characters. It is popular for writing AI instructions and knowledge bases because it’s structured enough for machines to parse but readable enough for humans to write.
*   **What Is a System Prompt?**: This is the **secret instructions** written by the developer before you type anything, acting like a **job briefing**. It is **free, instant, and easy to change**.
*   **Retrieval Augmented Generation (RAG)**: This process involves using external knowledge sources. **Retrieval Is a Pipeline, Not a Magic Box**. Metadata Prevents Cross-Contamination, and Retrieval Should Return Evidence, Not Just Confidence.
*   **Embeddings & Vector Databases**: **TF-IDF Has a Blind Spot**. We move from word counts to dense vectors, which are stored in **Vector Databases**. **Hybrid Search** is used because meaning isn’t everything.
*   **Architecture**: The recommended pattern is **The Karpathy Pattern: 3 Layers**.
*   **Knowledge Hub v1**: To build this, I must **Choose a Corpus You Can Inspect**, **Define Three Answerable Questions**, **Keep Raw Sources Immutable**, and **Make the Index a Product Surface**. I must **Test Retrieval Before Generation** and **Add a Grounded Answer Policy**.
*   **Thinking Models**: These models **pause and reason** before answering, generating an internal chain of reasoning. **Thinking Is Not a Permission Slip to Skip Evaluation**.
*   **Plan Mode**: This forces the model to **plan before executing**. Plan mode saves the blueprint to a file, which is powerful because the plan file stays outside the context window.

## Related

- [[Model Customization Techniques Comparison]]: System Prompt
- [[Prompting as Probability Steering]]: Thinking Models
- [[Structuring Prompts as Product Interfaces]]: .md Files — Why They’re Everywhere in AI

## Sources

- [[wiki/Sources/Class 5 Prompting and Retrieval Notes|Class 5 Prompting and Retrieval Notes]]: `raw/Class 5 Prompting and Retrieval Notes.md`, sections "Context Windows and Memory", "How Big Is a Context Window?", "Bigger Context Is Not a Free Solution", "Context Rot Is Real", "But Context Fills Up — Enter Compression", "Put Stable Rules in Stable Places" and more
