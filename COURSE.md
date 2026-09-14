# MBA 290T-LEC-001, Fundamentals of Agentic AI (Fall 2026)

Pulled from bCourses course 1555592 on 2026-09-13. bCourses lists Alexandre Mas as the teacher, and the syllabus names Alexandre Mas and Pepe Alonso as co-instructors. Class meets Tuesdays from 4:00 to 6:00 PM in N570.

Most of the course lives outside bCourses. The bCourses syllabus tab is only a link to the course site at https://haas-ai-classes-fall-26.vercel.app, and the assignment prompts are Google Docs linked from each assignment. Everything below maps what bCourses has to the files in this repo.

## Course site pages in this repo

| File | Source |
| --- | --- |
| [syllabus.md](syllabus.md), [SYLLABUS.pdf](SYLLABUS.pdf) | https://haas-ai-classes-fall-26.vercel.app/syllabus.html |
| [orientation.md](orientation.md) | https://haas-ai-classes-fall-26.vercel.app/orientation.html |
| [class1.md](class1.md) through [class7.md](class7.md) | https://haas-ai-classes-fall-26.vercel.app/class1.html through class7.html |

The slide decks are Quarto reveal.js pages converted to markdown, with images left pointing at the course site. Interactive embeds, like the 3D agent-pattern diagrams in Class 7, don't survive the conversion, so the source page is the place to see those.

## Weekly schedule

The objectives below are copied from each week's bCourses page. Weeks 4 through 7 on bCourses still point at the older https://haas-ai-classes.vercel.app/ link with a "will be updated before class" note, but the Fall 2026 site already had the Class 4 through 7 decks up when I pulled them.

| Week | Date | Topic | Slides | Due that week |
| --- | --- | --- | --- | --- |
| 1 | Tue 8/25 | Code & Programming Foundations | [class1.md](class1.md) | |
| 2 | Tue 9/1 | Software Systems | [class2.md](class2.md) | Assignment 1, 9/8 |
| 3 | Tue 9/8 | Machine Learning Foundations | [class3.md](class3.md) | Assignment 2, 9/15 |
| 4 | Tue 9/15 | Deep Learning & Transformers | [class4.md](class4.md) | Assignment 3, 9/22 |
| 5 | Tue 9/22 | LLM Behavior, Prompting & Retrieval | [class5.md](class5.md) | Assignment 4, 9/29 |
| 6 | Tue 9/29 | Production LLMs & Single Agents | [class6.md](class6.md) | Assignment 5, 10/13 |
| 7 | Tue 10/6 | Multi-Agent Systems, Ops & Safety | [class7.md](class7.md) | Assignment 5 (cont.) |
| 8 | | | | |

The Week 8 page is still the blank Canvas template with no topic, date, or materials.

### Week 1 objectives

What code actually is and how it runs. Variables, types, conditionals, loops, and functions. Lists vs. dictionaries, and why data shape is a management decision. Errors, tracebacks, and debugging as hypothesis testing. Tests as executable promises. Programming languages and why Python. The terminal. Git, GitHub, branches, diffs, and pull requests. AI coding agents: plan mode, YOLO mode, and when not to reach for the agent.

Setup the page asks for before Class 1 is free GitHub, Vercel, and Supabase accounts, one AI coding agent (Claude Code, OpenAI Codex CLI, or Google Antigravity), and Python 3.10+, Git, a code editor, and Obsidian on the laptop. The page budgets $25 to $45 for the course, meaning about $20 a month for an agent subscription plus roughly $5 to $20 of LLM API credit across Exercises 4 and 5. It also warns that Exercise 3 (Pac-Man) trains a neural network locally and takes several hours on a CPU-only machine.

### Week 2 objectives

Frontend: HTML, CSS, JavaScript, the DOM, components, and state. Backend: servers, APIs, HTTP methods, status codes, and JSON. Databases: tables, relationships, SQL, transactions, migrations, indexes, and caching. Environment variables and secrets, and why a frontend cannot keep one. Authentication vs. authorization, and OAuth. Cloud platforms and latency. Testing and the test pyramid. CI, deployment, environments, rollback, logs, and alerts. Tech stacks and the tradeoffs behind them.

### Week 3 objectives

When to write rules and when to learn them from examples. Classification, regression, and ranking. Data as the product before the model: labels, leakage, splits, and missingness. Loss and gradient descent. Generalization, overfitting, underfitting, bias–variance, regularization, and cross-validation. The classical toolbox: linear models, decision trees, random forests, gradient boosting, kNN, and SVMs. Feature engineering. Unsupervised learning: clustering, dimensionality reduction, anomaly detection. Evaluation as a business conversation: confusion matrices, precision, recall, thresholds, and calibration. Fairness, causality, and decision rights.

### Week 4 objectives

Neurons, activations, and why depth matters. Forward pass, loss, backpropagation, optimizers, batches, and epochs. CNNs and the GPU story. Reinforcement learning: states, actions, rewards, and the Bellman equation. Teaching machines to read: embeddings, tokenization, and BPE. Sequences and attention — query, key, value, softmax, and multi-head. The transformer block, positional encoding, and residual connections. Scaling laws, pretraining, transfer learning, fine-tuning, and alignment. How we got from transformers to LLMs.

### Week 5 objectives

LLMs as probability distributions, and temperature as the steering dial. Fine-tuning, LoRA, and prompting — three levers, three jobs. Prompts as product interfaces: specifying the job, separating instructions from data, instruction hierarchy as a trust boundary, and output format as a reliability tool. Context windows, context rot, and compression. System prompts and CLAUDE.md. Thinking models. Hallucination as a system property, and four defenses. Retrieval-augmented generation: chunking, metadata, grounding, and "no answer found" as success. Embeddings, vector databases, and hybrid search.

### Week 6 objectives

Where an LLM lives: hosted, self-hosted, or local. Budgets, timeouts, and retries. Structured output as an interface, and validating before acting. What an agent actually is: the loop, state, tools, and a stopping rule. Tool allowlists, permission policies, and why the model must never enforce its own guardrails. Stochastic agents vs. deterministic workflows — the skeleton-and-spark pattern. Designing tools like public APIs. MCP and skills. Orchestration patterns: prompt chaining, routing, and evaluator-optimizer. Evaluations, traces, and diagnosability. Cost engineering: token budgeting, prompt caching, model routing, and batch APIs.

### Week 7 objectives

Where single agents hit walls. The three axes of "more than one": specialization, coordination, and communication. Swarm intuitions and the credit assignment problem. Canonical patterns: orchestrator-workers, fan-out, subagents, and the advisor strategy. Managed agents, pets vs. cattle. Knowledge architecture as coordination architecture. Production ops: cron and webhook triggers, observability, run records, and the honest cost curve. Safety: alignment failures, context rot, prompt injection and the confused deputy, and the OWASP LLM Top 10. Accountability, procurement, and regulation. When not to go multi-agent.

## Assignments

Times are Pacific. Status is as of 2026-09-13.

| Assignment | Due | Points | Status | Prompt |
| --- | --- | --- | --- | --- |
| [Assignment 1](https://bcourses.berkeley.edu/courses/1555592/assignments/9130917) | 9/8, 11:59 PM | 10 | Submitted 9/8, 11:24 PM, not graded yet | [assignment-01/ASSIGNMENT.md](assignment-01/ASSIGNMENT.md) |
| [Assignment 2](https://bcourses.berkeley.edu/courses/1555592/assignments/9130935) | 9/15, 11:59 PM | 10 | Unsubmitted | [assignment-02/ASSIGNMENT.md](assignment-02/ASSIGNMENT.md) |
| [Assignment 3](https://bcourses.berkeley.edu/courses/1555592/assignments/9130938) | 9/22, 11:59 PM | 10 | Unsubmitted | No description posted yet |
| [Assignment 4](https://bcourses.berkeley.edu/courses/1555592/assignments/9130939) | 9/29, 11:59 PM | 10 | Unsubmitted | No description posted yet |
| [Assignment 5](https://bcourses.berkeley.edu/courses/1555592/assignments/9130940) | 10/13, 11:59 PM | 20 | Unsubmitted | No description posted yet |
| [Academic Integrity Assignment](https://bcourses.berkeley.edu/courses/1555592/assignments/9145855) | 9/26, 12:59 AM | 1 (not counted) | Unsubmitted | Completed through the Academic Integrity tool in the bCourses course nav |

All five numbered assignments are submitted as a URL.

## What bCourses has that isn't here

The only discussion is "Introduce Yourself," which had no replies when I pulled it, and there were no announcements. The Files and Pages list endpoints are turned off for students (403 and 404), so anything uploaded only as a course file couldn't be reached. The Media Library (Panopto), Study.Net Materials, and Academic Integrity tabs are external tools that the API doesn't expose, so I didn't check what's inside them.
