# Class 6: Production LLMs & Single-Agent Systems

Source: https://haas-ai-classes-fall-26.vercel.app/class6.html

---

# Why This Class?

## What This Class Gives You

Class 5 taught you to steer the model. This class puts it **in production** — and inside a loop.

- **Where the LLM lives** — API vs self-hosted, and the budgets, timeouts, and retries around every call
- **Structured output** — turning language into an interface other code can trust
- **Agentic AI** — tool use, the self-feeding loop, why the terminal changed everything
- **Anatomy of an agent** — the four parts every framework wraps, error handling, memory, guardrails
- **Skeleton and spark** — the production design question: which steps are code, which are LLM?
- **OpenClaw as a case study** — how the most popular agent on GitHub is actually wired. *Not* magic.
- **MCP & skills** — reusable tools and reusable workflows
- **Orchestration patterns** — chaining, routing, evaluator — all inside one agent
- **Evals & cost engineering** — how to know it works, and how to afford it
- **Capstone: Assignment 5, part 1** — a bounded enrichment agent, the single-agent stage of your graded multi-agent insight pipeline
- **Knowledge Hub v2** — optional, ungraded: your Assignment 4 hub becomes a bounded single agent

**Important**

By the end of tonight you can look at any “AI agent” product and see the loop, the tools, the harness, and the two or three places where actual judgment happens. That X-ray vision is the skill.

## Agenda

1.  **From prompt to product** — what a production model call actually needs
2.  **Where does an LLM live?** — API provider vs self-hosted
3.  **Structured output** — schemas, validation, side effects
4.  **Agentic AI** — tool use, the loop, the harness
5.  **What an agent actually is** — anatomy, failure modes, guardrails
6.  **Stochastic agents vs deterministic code** — skeleton and spark
7.  **Case study: OpenClaw** — 250K stars of the same loop
8.  **Tools, MCP & skills** — design tools like public APIs
9.  **Orchestration patterns** — inside one agent
10. **Evaluations & cost engineering** — ship it, measure it, afford it
11. **Capstone: Assignment 5, part 1 — the Insight Pipeline**
12. **Optional build: Knowledge Hub v2**

**Note**

**A note on pacing.** Slides badged **SELF-STUDY** are real material, not filler — they’re the operational depth you’ll want when you actually build this. We may skip them live to protect time for the hands-on parts. They stay in the published deck; read them when the question comes up at work.

# From a Useful Prompt to a Reliable Product

## A Model Call Is One Dependency

Production LLM applications need a provider, credentials, request limits, retries, cost controls, logs, evaluation, permissions, and a safe way to touch real systems.

In Class 5 the model call was the whole show. In production it’s **one box in a system diagram** — and most of tonight is about all the other boxes. The pattern to watch for, over and over: **deterministic code wrapped around a stochastic core.**

# Where Does an LLM Live?

## Option A: Call an API Provider

An LLM is **not** in the browser. It runs on powerful servers with GPUs. Most companies access it by calling a provider’s API — your backend sends the prompt and gets text back.

- **No GPUs needed** on your side — the provider handles the hardware
- **Pay per token** (~\$0.01–\$0.10 per 1K tokens) — scales with usage
- **No model management** — they update, scale, and monitor it
- Best for: **startups, MVPs, and most products**

## Option B: Self-Hosted (LLM on Your Server)

Alternatively, you can run an open-source model **on your own server** — right next to your backend code. The LLM lives inside your infrastructure.

- **Full control** — data never leaves your servers
- **No per-token cost** — but you need GPUs (\$\$\$)
- **Customizable** — fine-tune on your own data
- Best for: **privacy requirements, high volume, or heavy customization**

**Tip**

Start with an API provider. Switch to self-hosted only when you have a specific reason — privacy regulations, cost at massive scale, or fine-tuning needs.

## Hosted, Self-Hosted, and Local Models

| Choice | Strength | Tradeoff |
|----|----|----|
| Hosted API | fastest path, frontier capability | data, cost, and vendor dependency |
| Self-hosted | control over data and deployment | operations and model-quality burden |
| Local model | privacy and offline experiments | limited capability and device constraints |

The third row is new: models small enough to run on **your laptop** (Ollama, LM Studio). Great for experiments and sensitive scratch work — but don’t confuse a 8B local model with a frontier model. They’re different tools.

## Choose by the Workload, Not the Brand

Consider quality, latency, token cost, context size, data residency, tool support, uptime, and the cost of an incorrect answer.

**Important**

**MBA lens.** “Which model is best?” is the wrong question — it’s “best **for this workload, at this price, with this failure cost**.” The extraction pipeline and the board-memo drafter should probably not be the same model. (Cost engineering, later tonight, turns this into a discipline.)

## Every Model Call Needs a Budget

Set maximum input, output, retries, tool calls, wall-clock time, and dollar cost. “Let it keep trying” is not a strategy.

An unbounded loop with a credit card attached is how you wake up to a four-figure API bill. Every budget on this list is a **number in code** — not a hope in a prompt.

## Timeouts Are a Product Decision

Decide when to wait, when to show progress, and when to return a partial or deferred result. A slow correct answer can still be a failed user experience.

Remember from Class 5: output tokens are generated one at a time. Long answers are *inherently* slow — so streaming, progress indicators, and “I’ll email you when it’s done” are product features, not engineering afterthoughts.

## Retries Need a Reason

Retry transient network errors. Do not blindly retry invalid input, permission failure, or a completed side effect. Classify the failure first.

| Failure                        | Retry?                                    |
|--------------------------------|-------------------------------------------|
| Rate limit / timeout / 500     | ✅ with backoff                           |
| Invalid input schema           | ❌ fix the input, don’t repeat it         |
| Permission denied              | ❌ escalate — retrying won’t grant access |
| “Send email” already succeeded | ❌ retrying **sends it twice**            |

That last row matters most once the model can act — hold that thought for idempotency, two sections from now.

# Structured Output Turns Language Into an Interface

## Natural Language Is a Bad Database Schema

It is flexible for people and fragile for downstream code.

*“The risk seems moderate, though arguably…”* — a human nods; `if risk == "high"` crashes. The moment another system consumes the model’s output, prose stops being a feature and becomes a parsing bug factory.

## Define the Shape First

``` json
{
  "answer": "string",
  "citations": ["wiki/path.md"],
  "confidence": "supported|insufficient_evidence",
  "next_action": "none|ask_clarifying_question"
}
```

This is the Class 5 “output format is a reliability tool” slide, promoted to a contract: enums instead of adjectives, paths instead of vague references, and a `confidence` field that makes “I don’t know” machine-readable.

## Worked Example — A Tool Definition Is Just a JSON Schema

The same schema idea powers **tool use**. When you give a model a tool, you literally hand it a JSON schema. Here’s a real one — the `search_notes` tool from your capstone:

``` json
{
  "name": "search_notes",
  "description": "Search the knowledge vault for notes matching a query. Returns the top matches with paths and snippets. Use this BEFORE answering any factual question about the vault.",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Keywords or a natural-language question, e.g. 'Q3 revenue TechCorp'"
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 5,
        "default": 5,
        "description": "How many results to return"
      }
    },
    "required": ["query"]
  }
}
```

Read it like the model does:

- **`description` is a prompt.** *“Use this BEFORE answering any factual question”* steers when the model reaches for the tool. Vague descriptions → wrong tool choices.
- **`minimum`/`maximum` are guardrails** — but only if your code *enforces* them. The schema tells the model the rules; the harness makes them true.
- **`required` prevents half-formed calls** — the model can’t request a search with no query.
- The model never runs anything. It emits `{"name": "search_notes", "input": {"query": "...", "limit": 3}}` — **your code** does the rest.

**Tip**

Writing a good tool schema is the same skill as writing a good job description: precise verb, clear inputs, explicit constraints, and enough context that the candidate (the model) knows **when** the job applies.

## Validate Before Acting

If the response is malformed, outside the allowed enum, or includes an unapproved citation, reject it and retry or escalate.

The validation code is boring — ten lines of schema checking. It’s also the single cheapest reliability upgrade in AI engineering: it converts *“the model usually formats this right”* into *“nothing malformed gets through.”*

## Separate Generation From Side Effects

A model can propose an email, database update, or deletion. Deterministic code should validate and execute the approved action.

**Propose → validate → execute** — three stages, and the model only owns the first. This split is the seed of everything in the agent sections coming up: the model suggests, the harness decides.

## Idempotency Matters for Agents Too

A tool action must be safe to retry. “Create a note” and “send an email” need unique operation IDs or confirmation state.

Stochastic systems retry **a lot** — failed validations, timeouts, wobbly loops. If retrying a step can double-charge a customer, the bug isn’t the retry; it’s the missing idempotency key. (You met this exact idea with payment APIs in Class 2 — same principle, new caller.)

## Prompt Versions Belong in Source Control

Treat prompts as behavior-changing product code: name them, review them, test them, and record which version produced each important run.

*“Who changed the prompt last Tuesday?”* should have an answer — a commit, an author, a diff. If the prompt lives in a Notion doc or someone’s clipboard, your product’s behavior has no audit trail.

## Model Changes Need Compatibility Checks

A new model version can change tone, tool choice, structured-output reliability, and cost. Run the evaluation suite before treating it as a drop-in replacement.

Model upgrades are silent API migrations. Same endpoint, same request — different behavior. The eval suite (later tonight) is your regression test for a dependency you don’t control.

# Agentic AI

## From Text to Action

Until recently, an LLM could only **generate text**. It couldn’t send an email, edit a file, or deploy your app — it could only *talk about* doing those things.

**Tool use** is what made agentic AI possible. The model can now request real actions:

- send a Slack message
- edit and save files
- run code and tests
- create a pull request
- deploy an application

**Note**

The model doesn’t execute the tool itself — it says “call this tool with these arguments.” Your code runs it, and the **result goes back into the context**.

## How Tool Use Works

1.  You define the tools available
2.  The model chooses which tool to call
3.  Your application executes it
4.  The result comes back into the context
5.  The model continues with the new information

**Important**

The model does not run the tool itself. It emits a structured request saying which tool to call and with what arguments. Your code executes the tool.

## What Is Agentic AI?

**Agentic AI** = AI systems that can **plan, act, and adapt** to achieve a goal — without a human directing every step.

Traditional AI waits for a prompt and gives you an answer. Agentic AI receives an **objective**, figures out the steps, executes them, evaluates the results, and keeps going until the job is done.

**Note**

Gartner predicts 40% of enterprise apps will include AI agents by end of 2026, up from less than 5% in 2025.

## The Self-Feeding Loop

This is the key insight: when tool results feed back into the context, the model can **react to what happened** and decide what to do next.

1.  **Think** — what should I do?
2.  **Act** — call a tool
3.  **Observe** — read the result
4.  **Repeat** — until the task is done

This is what people mean by “agentic AI.” The model isn’t just answering — it’s **working**.

## The Terminal Changes Everything

When an AI can access the **terminal**, it can do anything your computer can do:

- read and write any file
- run any command or script
- install packages
- interact with git
- call APIs
- deploy applications

This is why **Claude Code**, **Codex**, and **Gemini CLI** are all terminal-first. The terminal is the universal tool.

## Claude Code: Built on This Loop

Claude Code is Anthropic’s agentic tool. It lives in your terminal and runs the exact loop we just described.

- It reads your **entire project** before acting
- It writes code across **multiple files**
- It runs **terminal commands** and reacts to the output
- It manages **git** — branches, commits, PRs
- It’s not limited to code — anything you can do in a terminal, it can do

**Tip**

These slides were built with Claude Code. It created the diagrams, edited the markdown, ran the preview server, and deployed to Vercel — all from natural language instructions.

## How Claude Code Sees Your Project

## What Is a Harness?

The model is the brain. The **harness** is everything around it that makes the loop work.

- **Tools** — what actions the model can take
- **Context management** — what info gets sent each turn
- **Memory** — what persists between sessions (plan files, CLAUDE.md)
- **Safety & permissions** — what the model is and isn’t allowed to do
- **The loop itself** — the orchestration that runs think → act → observe

**Tip**

“Start simple. Add agentic systems only when simpler solutions fall short.” — Anthropic

# What an Agent Actually Is

## Anatomy of an Agent — The Loop

**An agent is a loop: a model observes state, picks a tool, the harness runs it, the result feeds back — until the task is done.**

Every real agent framework — Claude Code, LangGraph, OpenAI Agents SDK, a hand-rolled Python `while` loop — wraps the **same four parts** into that loop. The only thing that changes is **how much of the harness you write yourself.**

In plainer words: an agent is **an LLM inside a control loop** — *observe state → choose an action → call a tool → inspect result → continue or stop.* It is not simply “a chatbot with a longer prompt.”

## Anatomy of an Agent — The Four Parts

| Component | What it does | Analogy |
|----|----|----|
| **Memory** | Context window + external store | Notebook of recipes |
| **Planning** | Decides next action given state | Reasoning through the steps to plate the dish |
| **Tools** | Executes actions in the world | Knife, pot, stove |
| **Loop** | The harness that runs it all | The shift — order in, plate out, repeat |

## The State Is the Agent’s Working Memory

It includes the user goal, conversation, retrieved evidence, intermediate results, tool history, budget, and allowed next actions.

“State” is broader than “context window”: the budget counter, the list of allowed tools, the approval flags — those live in the **harness**, in plain variables, and they shape what happens next just as much as the conversation does.

## Tools Create Real Leverage — and Real Risk

**The leverage**

Reading a note, searching a vault, writing a draft, querying a database, and calling an API let an LLM affect systems beyond its training data.

Tools are why an agent is worth more than a chatbot: it stops describing work and starts **doing** it.

**The risk**

Every tool expands the blast radius. A correct-looking description can hide broad permissions, ambiguous inputs, or an irreversible side effect.

`delete_note(path)` is one hallucinated argument away from being a data-loss incident. The tool list is your risk register.

**Warning**

**Tool output is untrusted input too.** External APIs, retrieved documents, and tool error messages can carry malicious or misleading text. Validate and bound the output before placing it back into the agent’s context. (Prompt injection gets the full treatment in Class 7.)

## Who Decides Which Tool? — Code vs LLM

Inside the loop, **something has to pick the next tool**. There are two ways to decide — and the choice is a governance decision, not just a technical one.

### 💻 Code-based planner

**Plain Python: `if / elif` on the input.**

- ✅ **Deterministic** — same input, same tool, every time
- ✅ **Cheap** — no model call to decide
- ✅ **Auditable** — the routing logic is literally the source code
- ❌ **Brittle** — *“multiply 5 × 21”* routes correctly; *“five times twenty-one please”* doesn’t

### 🧠 LLM-based planner

**Let the model choose the tool itself.**

- ✅ **Flexible** — handles any phrasing, any language
- ✅ **Generalizes** — you add a tool, it figures out when to use it
- ❌ **Costs tokens** on every decision
- ❌ **Non-deterministic** — can pick the wrong tool, or **hallucinate a tool name that doesn’t exist**

**Important**

**Rule of thumb:** code-based when routing is stable and you need an audit trail (finance, healthcare, anything regulated). LLM-based when the input surface is open-ended (assistants, agents-as-products).

The **Routing pattern** coming up later tonight is exactly this tradeoff — applied to whole workflows instead of individual tool calls.

## When Tools Break — Error Handling in the Loop

Tools fail. **A lot.** Every production agent needs a story for each class of failure:

- **Network** — timeout, rate limit, 500 from the API
- **Permission** — the token’s scope doesn’t cover this tool
- **Bad arguments** — model called `read_file(path="../../etc/passwd")`
- **Tool crashed** — uncaught exception in your own code
- **Hallucinated tool** — model calls `slack_search` or `geocode(...)` with perfect JSON — tools you never registered. It was trained on millions of APIs; it remembers ones you didn’t give it.

**What the harness must do:**

- Catch the error, format it as a tool result
- Feed it *back into the model* — let it retry, pick a different tool, or give up
- Enforce a **retry budget** so the loop doesn’t burn through your wallet
- **Strict tool registry** — unknown tool → `"tool_not_found: <name>. Available: [list]"`. Never silently execute a “close match.”
- Log every failure for the trace

**Warning**

Silent failures are the worst kind. If a tool crashes and you return empty string, the model happily invents an answer on the non-result. **Always return a structured error — never nothing.**

## An Agent Needs a Stopping Rule

Successful answer, exhausted budget, repeated failure, no permitted tool action, or human escalation are all legitimate stopping states.

“The model decides it’s done” is one stopping condition — the **optimistic** one. Production agents need the pessimistic ones too, enforced in code: max steps, max dollars, max wall-clock. A loop without a stopping rule isn’t an agent; it’s a leak.

## State Machines Make Loops Inspectable

Represent states such as `retrieve`, `answer`, `validate`, `await_approval`, and `stop` explicitly. It becomes much easier to test which transitions are allowed.

```
retrieve → answer → validate ─→ stop
                        │
                        └→ await_approval → stop
```

An explicit state machine means you can assert things like *“no path reaches `write` without passing `await_approval`”* — as a **test**, before the agent ever runs. This is exactly how you’ll structure the capstone’s permission policy.

## State & Memory — Beyond the Context Window

**Three places to put information:**

- **Context window** — what the model sees this turn. Expensive, volatile, forgets the middle.
- **Session log** — the full conversation, durable on disk. Outlives the context window and even the process.
- **External store** — filesystem, wiki, vector DB. Survives everything. The “filing cabinet.”

**Three decisions to make:**

- **Checkpoint** — what must survive a restart? (plan, key findings, open questions)
- **Discard** — what was just scratch work? (intermediate tool outputs, stale search results)
- **Retrieve** — when do we pull something back in? (only when the current step needs it)

**Memory is a harness decision, not a model decision.** The model doesn’t remember between calls — *you* decide what to carry forward. Every token you re-send costs money and crowds the window.

## Prompt Isolation & Tool Allowlists

The system prompt defines **what an agent is allowed to think about.** The tool list defines **what it’s allowed to do.** Both are doors you can lock.

**Prompt isolation**

- Each agent has *its own* system prompt — no bleed from the parent’s instructions
- Subagents **do not see** the main conversation history; only the narrow task the parent handed them
- Stops injection attacks from propagating across agents

**Tool allowlist**

- Declarative: `.claude/agents/researcher.md` lists exactly `[WebSearch, WebFetch, ingest_source]`
- **Nothing else** is callable — even if the model hallucinates the name
- Least-privilege at the agent level, not just the human level

These two mechanisms — prompt isolation and tool allowlists — are **why subagents are safe** to spin up in the multi-agent patterns of Class 7. Without them, every agent is a liability. With them, each is a contained box.

## Why Agents Need Guardrails

Everything above — error handling, hallucination, retries, allowlists — traces back to one truth:

**Same input, different output.** The same prompt twice does **not** produce the same tool calls. Sometimes trivial (phrasing). Sometimes catastrophic (skips a step, picks the wrong tool, exfiltrates data).

**Evals don’t make it deterministic.** An eval says *“passes 94% of the time on our test set”* — a **probability threshold**, not a guarantee. The 6% still ships. Guardrails (schemas, allowlists, retries, humans) live *around* the LLM, not inside it.

Which drives the rest of this class: **which steps should be stochastic agents, which should be deterministic code?**

## Never Ask the Model to Enforce Its Own Guardrails

“Do not exceed \$10” in a prompt is a preference. A \$10 budget enforced in code is a control.

**Important**

This one sentence separates hobby agents from production agents. Prompts shape behavior **probabilistically**; code enforces it **absolutely**. Every rule that matters — spend caps, permission checks, path restrictions — must exist in the harness, where the model can’t argue with it.

# Stochastic Agents vs Deterministic Code Workflows

## The Production Design Question

Every agent system you’ll design is a mix of two kinds of steps. Naming them is the most important decision you’ll make.

**In production, the scaffolding is always code. The LLM is inserted only at the *spark points* where judgment is actually needed.** Get this wrong and you’re either brittle (all code, no flexibility) or broke (all LLM, no predictability).

## The Decision Rubric

**Prefer code.** It’s cheaper, deterministic, testable. Only reach for an LLM when code genuinely can’t do the job.

### 💻 Default — use code

- Logic is expressible as **rules, schemas, or SQL**
- Output must be **exactly reproducible** (reports, invoices, migrations)
- It’s a **system boundary** — auth, payments, persistence, external API
- **Latency or cost** matters (every millisecond, every penny)
- You need a **test** that catches regressions forever

### 🧠 Exception — when code can’t

- Input is **unstructured natural language** or ambiguous
- The space of valid outputs is **open-ended**
- **Judgment, synthesis, or summarization** is required
- No rule-based spec is feasible (too many edge cases)
- A human would do it with soft skills, not a spec

**If the answer is “both” — split the step.** One code step (the deterministic part) calling one LLM step (the judgment part), then code again to validate and persist.

## The Split, In One Slide

**Put deterministic work in code**

- validate schemas and permissions
- sort, filter, deduplicate, calculate, and schedule
- enforce budgets and retries
- execute writes and irreversible actions

**Put ambiguous work in the LLM**

- interpret intent and messy language
- summarize and synthesize evidence
- choose among bounded strategies
- produce a user-facing explanation

Print this slide. It settles 80% of the design arguments you’ll have about AI systems.

## Skeleton and Spark — The Production Pattern

Every real agent system has the same shape. The **skeleton** is code: retries, ordering, routing table, persistence, state machine, auth, error handling, validation. The **spark** is the LLM step, dropped in only where judgment is actually needed.

**Pink = LLM. Blue = code.** Seven steps, two LLM calls. That ratio — mostly code, sparingly LLM — is what a production pipeline actually looks like.

Code provides the reliable skeleton: state machine, tool contracts, limits, validation, and logs. The LLM provides the flexible spark: language understanding and judgment inside those boundaries.

## Worked Example — Code Skeleton, LLM Sparks

Task: *a customer email lands in support — classify it, draft a reply, send it.* The production design wraps **deterministic code** around **two narrow LLM calls** — each one guarded by code before it’s trusted.

**Two LLM calls, five code steps, every LLM output checked before it hits the customer.** The LLM is where the judgment is; the code is everything else — and the code is what keeps you out of the headlines.

## Failure Modes Tell You the Difference

Code and LLM steps fail in completely different ways. This is why the split matters.

| Dimension | 💻 Code step | 🧠 LLM step |
|----|----|----|
| **Failure** | Reproducible (same input → same crash) | Probabilistic (fails 1 in 20 runs, nobody knows why) |
| **Fix** | Add a test, patch the bug, done forever | Prompt eng, evals, retries, fallback model |
| **Observability** | `print`, logs, debugger | Traces + evals + sampled human review |
| **Cost** | CPU cycles, ~free | Tokens, measurable per-call |
| **Latency** | ms | seconds |
| **Auditability** | Source code is the spec | The prompt is *a* spec; outputs still vary |

**Warning**

**The lens for the rest of this class**: on every pattern diagram that follows, ask *which boxes are code and which are LLM?* That’s the real architecture.

# Meet OpenClaw

## Meet OpenClaw — The Agent That Broke GitHub

**Note**

**~60 days → 250,000+ ⭐** — fastest-growing agent project in OSS history, built by **one developer** (Peter Steinberger). Twice renamed after an Anthropic trademark complaint (*Clawd* ≈ *Claude*).

- **What it is.** Self-hosted personal AI — runs on WhatsApp, Telegram, Slack, Discord, iMessage, Signal, and 20+ other channels. Voice on macOS / iOS / Android.
- **Why it exploded.** *Config-first.* Write one `SOUL.md` file describing the agent’s personality, tools, memory, channels. Run one command. **No Python. No chains. No graphs.**
- **What it proves.** The agent loop is now a **commodity**. One dev + one config file + a weekend → the fastest-growing repo on GitHub. Two years ago that was unthinkable.

**Important**

The loop we just drew — **observe → plan → act → update** — *is* OpenClaw. It’s also Claude Code, Cursor, Cline, OpenDevin. The **anatomy is shared**; what’s now commoditizing is the harness around it.

## OpenClaw Architecture — It’s Not That Different

Zoom in on what’s actually inside. The **four components** you just learned are right in the middle. Everything else is plumbing.

**Tip**

**SOUL.md** configures the agent. **Messaging channels** are the new “user interface.” **Tools + Memory** are still the same two boxes. The **Runtime** is just the generic loop running in a container somewhere.

## OpenClaw Through the Code-vs-LLM Lens

Apply the lens from the last section. Which parts of OpenClaw are **deterministic code**, and which are the **stochastic LLM step**?

### 💻 Code (the skeleton)

- The **runtime loop** — while not done, call model, dispatch tool, loop
- **Channel adapters** — WhatsApp, Slack, Signal webhooks, parsing
- **Tool dispatch** — match tool name, route to handler, enforce timeouts
- **Permission checks** — is this user allowed to invoke this tool?
- **Memory store** — append to session log, retrieve past messages
- **SOUL.md loader** — parse config, build tool registry

### 🧠 LLM (the spark)

- **The reasoning inside the loop** — what to say, which tool to call
- **Synthesizing a reply** from tool outputs
- **Deciding when the task is done**

OpenClaw is **\>95% code** and a sliver of LLM at the center. That’s the commoditization story — the harness is the same everywhere; the only thing left to vary is the prompt and the tools.

**This is true of every agent framework** — Claude Agent SDK, LangGraph, OpenAI Agents SDK. The code skeleton is nearly identical. The LLM is the spark.

## The Shape Is Familiar

A useful agent framework is mostly this: **code around the ReAct loop**, plus prompts, tools, memory, and guardrails.

# Design Tools Like Public APIs

## Your Tools Deserve API Discipline

You saw the tool-definition schema earlier tonight. Now the design principles — because from the model’s side, your tool **is** a public API: called by an intelligent stranger who only knows what the docs say.

Everything you learned about API design in Class 2 applies. Four rules follow.

## A Good Tool Has a Narrow Verb

`search_notes(query, limit)` is clearer and safer than `run_any_search(instructions)`.

A narrow verb bounds the blast radius **and** improves the model’s tool choice — a model picks correctly between five specific tools far more reliably than it composes one omnipotent one. `do_anything(text)` is not a tool; it’s an incident report waiting for a timestamp.

## Make Inputs Typed and Constrained

``` json
{"query": "string", "limit": "integer 1–5"}
```

Every constraint in the schema is one less way a hallucinated argument hurts you — but remember: the schema **informs** the model, the harness **enforces** it. Validate server-side, always. (`limit: 999999` should die in validation, not in your database.)

## Return Useful Observations

Tool results should include enough evidence for the model and user to reason about what happened, without dumping irrelevant secrets or huge payloads.

The tool result is a **prompt you’re writing to the model**. Return `{"matches": 3, "top": [...paths + snippets...]}` and the model reasons well. Return a raw 80KB JSON dump and you’ve paid tokens to bury the signal.

## Design Failures Intentionally

Return a safe, actionable error: not authorized, no result, invalid path, rate limited, or dependency unavailable.

Remember the harness rule — **never return nothing**. A structured `"no_results: try broader keywords"` teaches the model its next move. An empty string invites it to make one up.

## When There Is No API: Computer Use

Every tool so far assumed a clean interface existed. Often it doesn’t — the legacy vendor portal, the internal system nobody will re-platform, the supplier who emails PDFs.

**Computer use / browser agents** take a screenshot, decide where to click, and click. The “tool” is the screen: `screenshot`, `click(x,y)`, `type(text)`, `scroll`.

- **What it unlocks** — automation of systems that will never get an API, without an integration project
- **What it costs** — slow (seconds per step), expensive (every screenshot is thousands of image tokens), and brittle (a redesigned page breaks the flow silently)
- **What it risks** — the agent reads whatever is on that screen, so anything on the page becomes potential instruction

**Important**

**The design rule stays the same.** Prefer an API when one exists; reach for pixels when one doesn’t. And treat computer use as the **highest-privilege tool you can hand an agent** — it can do anything the logged-in human could do, which means the guardrails belong outside the model: scoped accounts, read-only sessions where possible, and human confirmation before anything irreversible. We’ll name this failure mode properly in Class 7 as the *confused deputy*.

# MCP

## MCP: One Standard for All Tools

MCP = **Model Context Protocol** — an open standard that makes tool integrations reusable across AI apps.

- **Tools**: actions the model can request (search, calculate, deploy)
- **Resources**: data the model can read (files, databases, docs)
- **Prompts**: reusable prompt templates

**Tip**

Think of MCP as “USB for AI” — build the connector once, plug it into any app. A Slack MCP server works in Claude Code, Cursor, Windsurf, or any MCP-compatible tool.

Your capstone hub **is** an MCP server — the six tools you’ll ship tonight can be called from Claude Desktop, Claude mobile, or any compatible client. Build the connector once; every AI app you use gets your knowledge base.

# Skills

## Tools vs Skills

**Tool** = one atomic action (read a file, run a command)

**Skill** = a reusable workflow that combines prompts, tools, and judgment

**Important**

Tools give capabilities. Skills package **good ways of using them**. A skill is like a playbook — it tells the model what steps to follow, what to look for, and how to present results.

## Skills in Practice

In Claude Code, a skill is just a markdown file with instructions:

``` markdown
---
name: review-pr
description: Review a pull request for bugs and style
---
# PR Review Skill
1. Read the diff with `git diff`
2. Check for security issues, bugs, and style
3. Write a summary with findings
```

When you type `/review-pr`, Claude loads these instructions and follows them. Skills are how teams standardize AI workflows — same model, same tools, consistent results.

A skill gives an agent instructions, workflows, templates, and constraints for a recurring job — far more durable than pasting a giant prompt into every chat. It’s the `CLAUDE.md` idea from Class 5, scoped to one repeatable task.

# Orchestration Patterns — Inside One Agent

## Three Patterns That Don’t Need a Team

Before anyone sells you a “multi-agent platform,” notice this: **three of the classic workflow patterns work with a single agent.** Chaining, routing, evaluator — all run in one process, with one model (or a couple), one context window per call. **The agent you just built can already do these.**

**The lens from two sections ago:** on each diagram, ask *which boxes are code, which are LLM?* The answer is often surprising — most of the “orchestration” is code. The LLM is inserted at the judgment points.

## Pattern 1 — Prompt Chaining

**The assembly line.** Output of step N is the input of step N+1.

- Each step is a **separate LLM call** with a narrow job
- No routing decisions — the **pipeline is hardcoded**
- Cheapest, most predictable pattern

**Example:** *Draft → Translate → Format for brand voice → Publish* — or in your capstone’s terms: *extract → classify → draft → verify*

**Best for:** fixed, ordered steps where accuracy per step matters more than flexibility — when stages are stable and each output improves the next stage.

**Trade-off:** errors cascade. If step 2 garbles, steps 3 and 4 polish the garbage.

**Note**

**Reading every pattern diagram in this class: arrows = code, boxes = LLM.** The code is the scaffolding; the LLM sits only where judgment is needed.

Schema-check between each step so a bad output doesn’t cascade.

## Pattern 2 — Routing

**The triage desk.** Classify first, dispatch to the right specialist.

- A **classifier** reads the input and picks a route
- Each route has its **own prompt, tools, often its own model**
- Add new routes without touching the others

**Example:** support — billing → cheap + SQL; legal → strong + policy docs; chit-chat → fast, no tools.

**Best for:** inputs with **distinct categories** where a generic prompt would be mediocre on every one — when one task type needs a different prompt, model, toolset, or approval policy than another.

Why the same product feels smart on some questions, dumb on others — it’s silently routing underneath.

The classifier itself can be code or LLM — default to the cheapest that works.

## Pattern 3 — Evaluator-Optimizer

**Editor + writer.** One role generates. Another critiques. Loop.

- **Generator** produces an attempt
- **Evaluator** scores it against a rubric, explains what’s wrong
- Generator revises — repeat until approved

**Example:** code writer + code reviewer; translator + fluency judge; draft writer + editor.

**Best for:** tasks with a **clear quality rubric** — one-shot isn’t good enough but iteration is cheap.

**Trade-off:** needs a **stop condition** — a rubric the evaluator can grade, plus a max-iteration cap. Uncapped self-critique becomes expensive theater.

Prefer a code rubric (tests, schema) over an LLM judge whenever you can write one.

## Pattern 4 — Deterministic Workflow With LLM Steps

The code decides the sequence. The model fills only the ambiguous steps. This is often the best production default.

You already saw it run: the **worked email example** was exactly this — a hardcoded pipeline with two LLM sparks and guards between them. Pattern 4 is skeleton-and-spark, named. When someone says “we built an agent,” a solid fraction of the time they built **this** — and that’s a compliment.

## Do Not Use an Agent When a Function Is Enough

If inputs and outputs are structured and the logic is known, code is cheaper, faster, easier to test, and more reliable.

**Important**

The decision ladder, cheapest first: **a function → one LLM call → a workflow with LLM steps → an agent loop → (Class 7) a team of agents.** Move down a rung only when the current one demonstrably fails. Anthropic’s own guidance: *“Start simple. Add agentic systems only when simpler solutions fall short.”*

## Three Inside-One-Agent Patterns, Then More

These three patterns **do not require a team**. You can run all of them with tonight’s single agent — they’re just different ways to structure one workflow.

| Pattern       | What it adds                            | Still one agent? |
|---------------|-----------------------------------------|------------------|
| **Chaining**  | Sequence with a schema between steps    | ✅ yes           |
| **Routing**   | A classifier picks which branch to take | ✅ yes           |
| **Evaluator** | A critic loop that tightens the output  | ✅ yes           |

**So what’s next?** The patterns that **do** need a team — parallel fan-out, orchestrator-workers, advisor, managed agents. Those are where coordination cost starts to pay for itself — and they’re the whole first half of **Class 7**. First: prove the single agent works, with evals.

# Evaluations

## LLMs Are Stochastic — and Prompts Are Brittle

**Stochastic**

Run the same prompt twice → two different answers. Same model, same input, different output.

That’s not a bug — that’s the architecture.

**Brittle**

Tiny prompt changes cause dramatic shifts. *“List 3 bullets”* vs *“Give me 3 bullet points”* → different tone, format, even correctness.

And every new model release (Claude 4.6 → Mythos, GPT-5 → GPT-5.4) moves the floor. Your prompts might silently break.

**Important**

You can’t eyeball this. You can’t manually re-test every scenario every time you tweak a prompt, swap a model, or add a tool. You need **systematic, repeatable checks** — or you’re flying blind.

## Evals = Replicable + Human-Verifiable

An eval is a test case with **two properties that must both hold**:

1.  **Machine-automated** — a script runs it and produces a pass/fail, so you can run hundreds of cases on every change
2.  **Human-verifiable** — open any failure, read input + output, and see why it’s wrong in seconds

Miss either half → evals rot, or you can’t tell signal from noise. **Benchmarks are scored. Evals are *understood*.**

## Start With a Task Contract

What should the system do, what must it never do, and what evidence proves success?

Write the contract **before** the prompt. For your capstone agent it fits on an index card:

- **Should:** answer vault questions with citations
- **Must never:** write without approval, invent citations, answer without searching
- **Evidence:** the three v2 evals, passing

No contract → no evals → no way to know whether Tuesday’s prompt tweak made things better or just *different*.

## Build a Small Adversarial Test Set

Include easy cases, ambiguous cases, missing-evidence cases, permission boundaries, malformed inputs, and temptation to take unauthorized actions.

That last category is the agent-era novelty: a test where the *easiest* path to a good-looking answer is the forbidden one — *“just update the note yourself”* — and passing means the agent **didn’t take it**. You’re not only testing competence anymore; you’re testing restraint.

## Running Evals in Practice

- **Start with 5–10 test cases**, not 500. Evals compound.
- **Every real-world failure becomes a new test case.** Your eval set grows with your product.
- **Run on every change**: prompt edit, model upgrade, new tool, new context.

Three common check types:

- **Exact / format checks** — cheap, deterministic (JSON keys match, regex matches, contains string)
- **LLM-as-judge** — flexible, ~80% agreement with human reviewers. Use for subjective qualities (tone, helpfulness)
- **Human review** — gold standard, reserved for the cases machines can’t score

**Important**

Teams that ship reliable AI invest in evals early. It’s what separates *“works on my laptop”* from *“works in production.”*

## The Eval Tooling Landscape

You don’t need a platform to start — but know what’s out there:

| Approach | What it looks like | Best for |
|----|----|----|
| **pytest-style evals** | plain test functions calling your system, asserting on outputs | starting out — it’s what your capstone uses |
| **promptfoo** | YAML config: prompts × models × test cases → pass/fail matrix in your terminal or CI | comparing prompt variants and models side-by-side |
| **Braintrust / LangSmith / Langfuse** | hosted platforms: datasets, scoring, dashboards, trace links | teams, once eval volume outgrows the terminal |
| **LLM-as-judge** | a second model scores the first against a rubric | subjective qualities at scale — with caveats ↓ |

**Warning**

**LLM-as-judge caveats** — the judge is stochastic too:

- **Position bias** — prefers whichever answer it read first; swap the order, the verdict can flip
- **Verbosity bias** — longer answers score higher, correct or not
- **Self-preference** — models rate their own outputs above other models’
- **~80% human agreement** means 1 in 5 judgments differs from yours — fine for trends, shaky for a single release gate

**Calibrate the judge**: score 20 cases yourself, compare, and tighten the rubric until you agree. And keep the *hard* gates deterministic — schema checks and permission tests don’t have opinions.

## Evaluate the Whole System

Model quality is only one layer. Measure retrieval, tool selection, schema validity, latency, cost, permission compliance, and user outcome.

Class 5’s rule — *test retrieval before generation* — generalizes: when an agent gives a bad answer, the model is only one of seven suspects. Your evals should indict the right one.

## Trace Every Run

Capture prompt version, model, retrieved sources, tool calls, outputs, validation errors, time, and cost with sensitive values redacted.

A chatbot’s output is one string. An agent’s output is **a sequence of decisions** — and the trace is its bank statement. If you can’t produce one, you can’t let the agent near anything that matters. (Class 7 goes deep on observability tooling.)

## A Bad Answer Should Be Diagnosable

Was the source missing? Retrieval wrong? Prompt ambiguous? Tool unavailable? Schema rejected? The trace should make the answer visible.

This is the payoff of the whole architecture: because your system is **mostly code with narrow LLM sparks**, a failure localizes to a specific step in the trace — not to a shrug and “the AI messed up.”

## Evaluation Needs a Decision Threshold

Define what score or failure rate blocks release, what requires a warning, and what is accepted for a low-risk experiment. Measurement without a release rule is just reporting.

*“94% pass”* means nothing on its own. 94% on tone? Ship it. 94% on “doesn’t write without approval”? That’s 6 unauthorized writes per hundred runs — **blocked**. Thresholds are per-eval, set by consequence, and written down before the number comes in.

## Human Approval Should Be Concrete

Specify who sees the proposed action, the evidence they receive, what they can edit, and what happens if they do nothing. “Human in the loop” is not an implementation.

An approval no one reads is worse than none — it launders the agent’s decision with a human signature. Design it like any workflow: queue, evidence shown, default-on-timeout (**deny**, for anything irreversible), and an audit record.

## Reliability Comes From the System, Not a Heroic Prompt

The durable application combines model capability with source control, retrieval, schemas, tools, permissions, budgets, traces, and tests that each catch a different class of failure.

**Important**

Notice what that list is: **everything from tonight, stacked.** No single layer is impressive. Together they’re the difference between a demo and a product. This is defense in depth — and it returns as a security principle in Class 7.

# Cost Engineering

## Tokens Are the New Cloud Bill

From Class 5: every token is a pass through a trillion-parameter network on a GPU. In production, that physics becomes a line item — and like cloud spend circa 2015, it’s easy to ignore until it’s terrifying.

The good news: LLM costs respond to engineering. Four levers, in order of effort:

1.  **Token budgeting** — send less, cap more
2.  **Prompt caching** — stop re-paying for the same prefix
3.  **Model routing** — stop using a frontier model for intern work
4.  **Batch APIs** — trade latency for a discount

**Important**

**MBA lens.** Per-token pricing means **unit economics apply to intelligence** now. Know your cost per task, per user, per month — before your CFO asks.

## Lever 1 — Token Budgeting

You can’t manage what you don’t meter. Budget tokens like money, because they are.

- **Input vs output** — recall the asymmetry: output tokens cost ~5× more. A prompt that says *“answer in 3 bullets”* isn’t style advice; it’s a cost control.
- **The conversation tax** — chat history is resent every turn, so turn 30 costs many times turn 1. Compaction and “start a new chat” are cost features.
- **Trim the context** — don’t send the whole document when retrieval can send the right paragraph. RAG is also a cost strategy.
- **Cap everything** — `max_tokens` per call, tool-call limits per run, dollar ceiling per session. Every cap is code, not prompt.

Back-of-envelope: an agent averaging 20K input + 2K output tokens per run, 1,000 runs/day, on a frontier model — that’s a **five-figure monthly bill**. On a small model with caching: often **under a hundred dollars**. Same loop. The difference is engineering.

## Lever 2 — Prompt Caching

Every call to your agent resends the same prefix: system prompt, tool schemas, CLAUDE.md, maybe a big document. **Prompt caching** lets the provider keep that prefix warm and charge a fraction for re-reading it.

- Cached input tokens typically cost **~10% of normal price** — a 90% discount on the repeated part
- Agents are the perfect customer: the loop hits the API dozens of times per task, **same prefix every time**
- The rule: **stable content first** (system prompt, tools, docs), volatile content last (the user’s message) — a cache matches from the top
- One byte changed at position zero = cache miss for everything after it. Prompt structure is now a billing decision.

**Tip**

For a typical tool-using agent, caching alone routinely cuts the bill **50–90%**. It’s the closest thing to free money in AI engineering — usually a one-line change.

## Prompt Caching — Visually

## Lever 3 — Model Routing

Frontier and small models differ in price by **1–2 orders of magnitude**. Most workloads are a mix of easy and hard — so route.

- **Static routing** — the Routing pattern from earlier tonight: classify the request, send extraction to the cheap model, synthesis to the strong one
- **Escalation routing** — try cheap first; if validation fails or confidence is low, retry on the frontier model. Most requests never escalate.
- **Match the model to the task** (Class 5) — this is that slide, wired into the architecture instead of left as advice

**Note**

**Preview:** Class 7’s *advisor pattern* is escalation routing formalized — a cheap model does the work and calls an expensive model only for hard judgment calls, with real published numbers on the savings. The cost logic starts here.

## Lever 4 — Batch APIs

If nobody is waiting on the answer, don’t pay real-time prices.

- Providers offer **batch endpoints**: submit thousands of requests, results within ~24 hours, **~50% off**
- Perfect fits: nightly eval runs, backfilling summaries over an archive, classifying last quarter’s tickets, re-embedding a corpus
- Wrong fits: anything with a user watching a spinner

**The complete cost picture** for a mature AI product:

| Traffic           | Path                   | Price                   |
|-------------------|------------------------|-------------------------|
| Interactive, easy | small model + cache    | ~pennies                |
| Interactive, hard | frontier model + cache | the premium you planned |
| Offline, bulk     | batch API              | half price              |

Same funnel logic as hybrid search in Class 5: **cheap paths absorb the volume so the expensive path only sees what deserves it.**

## Do the Math Once: A Support Bot

Every AI feature has a unit cost. Here is the arithmetic your CFO will ask for, on a support deflection bot handling **10,000 tickets/month**.

**Per ticket, one answer:**

| Component                 | Tokens   | Note                                 |
|---------------------------|----------|--------------------------------------|
| System prompt + policy    | 2,000 in | identical every call → **cacheable** |
| Retrieved docs (5 chunks) | 4,000 in | varies per ticket                    |
| Conversation so far       | 1,000 in | short threads                        |
| The answer                | 500 out  | output costs ~5× input               |

At **\$3 per million input / \$15 per million output** *(illustrative mid-tier pricing — check current rates)*:

- Input: 7,000 × \$3/1M = **\$0.021**
- Output: 500 × \$15/1M = **\$0.0075**
- **≈ \$0.029 per ticket → ~\$290/month**

## The Number That Actually Matters

\$290/month is not the interesting number. **Cost per deflected ticket** is.

- A human-handled ticket costs on the order of **\$5–\$8** fully loaded
- The bot resolves **60%** of tickets without a human → 6,000 deflected
- Spend: \$290. Avoided: 6,000 × ~\$6 ≈ **\$36,000/month**

**Tip**

**Now the levers earn their keep.** Cache the 2,000-token system prompt and input cost drops sharply. Route the easy 70% to a small model and the blended price falls again. Together they can cut that \$290 by more than half — but notice: **the levers were never the point.** The deflection rate was.

**Important**

**The trap.** A 5-point drop in deflection rate costs ~\$3,000/month. Halving your token bill saves ~\$150. Optimize the model spend *after* you have measured quality — which is exactly why evals came before cost engineering in this deck. **Cheap and wrong is the most expensive outcome available.**

# Capstone: Assignment 5 — The Insight Pipeline

## One Deliverable, Two Classes

**How the capstone is graded**

**Assignment 5 is a single multi-agent deliverable**, worth 30% of your grade — the largest single component of the course. It spans Classes 6 and 7:

- **Tonight — part 1:** build the **single-agent enrichment stage** — one bounded agent that turns a raw feedback record into validated, structured data.
- **Class 7 — part 2:** scale it into the **full multi-agent pipeline** — orchestrated fan-out, a verifier agent, issue grouping, a deterministic impact ranking, and a cited decision memo.
- **One submission, due Tuesday 10/13 at 11:59 pm PT** — one week after Class 7. Nothing is submitted this week.

Treat tonight’s stage as a hard checkpoint anyway: Class 7’s pipeline fans out **your enricher**. Arrive with it working on a 500-record slice, or you will be building both stages in one week.

## The Business Problem

A subscription software company’s churn is climbing. Leadership has one quarter and one fix-it budget — and four camps arguing for it: onboarding, billing, performance, support quality.

The evidence to settle the argument exists. It is just unreadable at scale:

- **~10,000 records over 12 months** — support emails, app-store reviews, NPS survey verbatims
- each tied to **account metadata** — plan tier, tenure, monthly revenue, date
- qualitative text plus quantitative context: exactly the shape of most real corporate data

No human reads 10,000 messages. No dashboard reads intent. **This is a job for an LLM pipeline with code wrapped around it** — the skeleton-and-spark pattern from tonight, industrialized. The dataset ships with the assignment brief.

## The Pipeline Shape

| Stage | Who | What |
|----|----|----|
| 1\. Ingest & normalize | code | load, dedupe, one record schema |
| 2\. Enrich each record | LLM agent | label, score sentiment, classify intent, rate severity, extract entities |
| 3\. Validate & verify | code + agent | schema-check 100%, re-label a sample |
| 4\. Group into issues | code + LLM | cluster duplicates, name each issue |
| 5\. Score & rank issues | **code only** | deterministic impact arithmetic |
| 6\. Write the memo | LLM | every claim cites issue IDs and numbers |

Stages 1 and 5 are pure code — auditable arithmetic. The LLM sparks live in 2, 4, and 6, each wrapped in validation. **The final ranking can be re-run and checked by anyone with a spreadsheet — after all the labeling is done.** That is the design goal, and it is why this capstone is gradeable at all.

## Part 1, Tonight: the Enrichment Agent

One bounded agent: raw record in, validated JSON out.

``` json
{
  "topic": "billing",
  "intent": "churn_threat",
  "sentiment": -0.8,
  "severity": 4,
  "entities": ["invoice", "annual plan"],
  "evidence_quote": "third month in a row the invoice is wrong"
}
```

- **Design the taxonomy first** — 6–10 topic labels and a written 1–5 severity rubric. These are product decisions, not code, and you will defend them.
- **Structured output + validation in code** — a record that fails schema is retried once, then quarantined with a reason. Never silently dropped.
- **Golden set** — hand-label 50 records yourself. Agreement between your agent and your own labels is your accuracy eval.
- **Cost budget** — estimate tokens × 10,000 records; choose a model and batching strategy that keeps the full run affordable. Show the math.

## Part 1 Checkpoint — Not a Submission

- The enricher runs end-to-end on a ~500-record slice.
- Every output validates against the schema; failures are quarantined and counted.
- A 50-record hand-labeled golden set exists, with an accuracy number against it.
- A written cost estimate for the full 10,000-record run.

This is tonight’s class in miniature: structured output, validating before acting, evals, and cost engineering. Class 7 adds the team around it. **One submission, due Tuesday 10/13 at 11:59 pm PT.**

# Optional Build: Knowledge Hub v2

## Upgrade the v1 System Into a Bounded Single Agent

The agent’s job: answer a knowledge question by searching the hub, reading selected notes, synthesizing a cited answer, and stopping safely.

Everything from tonight ships in it: the loop, tool schemas, a permission policy in code, a stopping rule, evals, and a trace. v1 gave the model evidence; v2 gives it **hands** — carefully.

## Use the Included MCP Tools

The starter exposes `search_notes`, `get_note`, `create_note`, `update_note`, `ingest_source`, and `lint_wiki` in `api/index.py`.

Six narrow verbs — exactly the tool-design discipline from earlier tonight. Read their schemas before you write the agent prompt: the descriptions are half of the agent’s behavior.

## What the Hub Should Do

**Important**

- **Three-layer vault**: `raw/` (sources), `wiki/` (LLM-maintained), `CLAUDE.md` (schema)
- **Six MCP tools**: `search_notes`, `get_note`, `create_note`, `update_note`, `ingest_source`, `lint_wiki`
- **Supabase Auth** (email/password) — your hub is private
- **Supabase Storage** as the backing store (Vercel is stateless, no disk)
- **FastAPI** JSON-RPC endpoint with JWT-protected `/mcp`
- **Deploy to Vercel** → remote MCP URL works from Claude mobile/desktop
- **Obsidian** opens the same folder of `.md` files for graph-view browsing
- **`sync.py`** pulls remote vault to local for Obsidian, pushes local edits back

That’s the full build — and it is **optional and ungraded**: the natural continuation of Assignment 4 for anyone who wants their hub to grow hands. Build it on your own schedule; Class 7 sketches an optional agent-team layer (v3) on top. The graded capstone is the insight pipeline above.

## Define a Minimum Permission Policy

| Tool                  | Default policy                     |
|-----------------------|------------------------------------|
| Search and read       | allowed                            |
| Create draft note     | allowed with audit log             |
| Update existing note  | require explicit user approval     |
| Ingest source         | allowed only from supplied content |
| External side effects | out of scope                       |

This table is a **tool allowlist plus approval gates** — the two locks from the anatomy section. Implement it in the harness, in code. The prompt may *mention* it; the code must *enforce* it.

## Write the Agent’s Operating Instructions

Include its goal, allowed tools, evidence requirement, citation format, stop conditions, and what to do when evidence conflicts or is missing.

This is a system prompt with the structure from Class 5 — role, boundaries, output rules — plus the agent-era additions: tool guidance and stopping rules. Keep it short; every rule that *can* live in code should.

## Add One Deterministic Guardrail

Examples: reject paths outside `vault/`, cap search at five results, enforce JSON output, block writes without approval, or stop after three tool calls.

One is the minimum, not the goal. Each of these is five lines of code — and each closes a failure class *permanently*, which no prompt edit can claim.

## Add Three v2 Evaluations

- an answer correctly grounded in known notes
- an unsupported question that produces `insufficient_evidence`
- a write request that is proposed but not executed without approval

Note the shape: one competence test, one honesty test, one **restraint** test. That’s a balanced agent eval set in miniature.

## Run the Starter Checks

``` bash
cd capstone/knowledge-hub
pytest evals
```

Add or adapt tests for your own three evaluation cases.

## Suggested Build Prompt

**First, read** [Karpathy’s LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — this prompt is a concrete instantiation of that pattern. Then paste into Claude Code:

Copy

/plan Build a personal AI knowledge hub following Karpathy's LLM Wiki pattern:\
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f\
\
=== STACK ===\
- FastAPI (Python) for the MCP server backend\
- Supabase Auth (email/password) for login\
- Supabase Storage bucket as the backing store\
  (Vercel serverless has no persistent disk — files cannot live on disk)\
- MCP protocol for tool definitions over a JSON-RPC endpoint\
- Obsidian for local viewing of the vault folder\
- Vercel for deployment\
- pytest for evals\
\
=== 3-LAYER VAULT ===\
vault/\
  raw/                  # immutable source documents (never modify)\
  wiki/                 # LLM-maintained interlinked markdown pages\
  index.md              # content catalog, updated on every wiki change\
  log.md                # chronological activity log, append-only\
  schema.md             # human-readable wiki conventions\
  templates/            # page templates the LLM follows\
    entity.md           # entity pages (people, tools, companies)\
    concept.md          # concept pages (ideas, techniques)\
    source-summary.md   # digests of raw sources\
\
CLAUDE.md at project root is the 3rd layer — the schema file.\
It tells the LLM how to maintain the wiki (ingest / query / lint).\
\
=== PAGE CONVENTIONS ===\
Every wiki page MUST have YAML frontmatter:\
  title, tags, created, updated, sources\
Tag taxonomy: entity, concept, source-summary, comparison, analysis\
Use \[\[wikilinks\]\] between pages — NEVER markdown \[links\](url)\
Cite raw sources by linking to the source-summary page\
\
=== 6 MCP TOOLS ===\
search_notes(query, limit=5)   # index.md keyword match, TF-IDF fallback\
get_note(path)                 # return full markdown of a page\
create_note(path, title,       # create page with frontmatter,\
            content, tags)     # update index.md, append to log.md\
update_note(path, content)     # update body, bump \`updated\` date, log\
ingest_source(title, content,  # create source-summary page in wiki/,\
              source_type)     # update index + log\
lint_wiki()                    # report broken \[\[wikilinks\]\], orphan pages,\
                               # pages missing from index.md\
\
=== SEARCH STRATEGY (NO VECTOR DB) ===\
At personal-wiki scale (hundreds of pages), Karpathy's index.md approach works:\
1. Read index.md, match query tokens against titles + tags + summaries\
   (title weighted 3x, tags 2x, summary 1x)\
2. If sparse results, fall back to TF-IDF + cosine similarity over\
   the full text of all wiki/\*.md files\
Return top-K: {path, title, snippet, score}\
\
=== AUTH (IMPORTANT) ===\
Supabase now issues ES256 JWTs, not HS256.\
Verify tokens via the JWKS endpoint:\
  https://.supabase.co/auth/v1/.well-known/jwks.json\
Use PyJWKClient from the \`pyjwt\` library.\
Routes:\
  POST /auth/signup  — proxy to Supabase auth\
  POST /auth/login   — returns access_token\
  GET  /health       — public, no auth\
  POST /mcp          — JWT-protected, JSON-RPC\
\
=== MCP ENDPOINT (SERVERLESS-COMPATIBLE) ===\
The streamable HTTP transport with SSE does NOT work on Vercel serverless —\
it needs persistent task groups that don't exist between invocations.\
Implement a plain JSON-RPC POST /mcp that handles:\
  method: "initialize"        → return server info + tool capabilities\
  method: "tools/list"        → return the 6 tool schemas\
  method: "tools/call"        → dispatch to the tool and return result\
Same MCP protocol, stateless — works perfectly from Claude desktop/mobile.\
\
=== SYNC SCRIPT ===\
sync.py:\
  python sync.py pull   # download all files from Supabase Storage → local vault/\
  python sync.py push   # upload local vault/ edits → Supabase Storage\
This lets Obsidian view/edit the vault locally, then push back to the\
deployed server so Claude on your phone sees the changes.\
\
=== EVALS (pytest) ===\
- test_auth.py       — unauthenticated, invalid token, expired token all 401\
- test_search.py     — index search + TF-IDF fallback return relevant pages\
- test_crud.py       — create persists, update bumps date, index/log updated\
- test_mcp.py        — tools/list returns 6 tools, tools/call for each works\
\
=== DELIVERABLES ===\
Working local (uvicorn) + deployed (Vercel) server\
README with: env var setup, Supabase bucket creation, platform install notes\
CLAUDE.md with ingest / query / lint workflows\
Seed vault/ with schema.md, starter index.md, log.md, and all 3 templates\
All 24+ evals passing\
Obsidian-viewable vault after running \`python sync.py pull\`\
\
IMPORTANT: The goal is the Karpathy pattern — a compounding wiki,\
not a chatbot. The LLM is the writer, Obsidian is the reader,\
CLAUDE.md is the discipline.\

## Tips & Gotchas From Building This

**Things that will bite you (and how to fix them)**

**Vercel has no persistent filesystem.** Serverless functions get a fresh, read-only container per request. You **cannot** store markdown files on disk. Use **Supabase Storage** as the backing store and a `sync.py` script to pull/push between remote and local Obsidian vault.

**MCP’s streamable HTTP transport doesn’t work on serverless.** It needs persistent connections and background task groups. Instead, implement a **simple JSON-RPC endpoint** (`POST /mcp`) that handles `initialize`, `tools/list`, and `tools/call` directly — same protocol, stateless.

**Supabase now issues ES256 JWTs, not HS256.** Your auth code needs to verify tokens via Supabase’s **JWKS endpoint** (`/auth/v1/.well-known/jwks.json`), not a shared secret. Use `PyJWKClient` from the `pyjwt` library.

**Vercel env vars set via CLI can get trailing newlines.** Always `.strip()` environment variables in your code, or use `printf` instead of `<<<` when setting them.

**Obsidian won’t open a folder via URI until it’s been opened once manually.** The first time, open Obsidian → “Open folder as vault” → select the vault directory. After that, the `obsidian://` URI scheme works.

**FastAPI and the MCP SDK can have version conflicts.** The `mcp` package installs `starlette 1.0`, which requires `fastapi >= 0.135`. Pin your versions in `requirements.txt`.

## CLI Tips: Vercel & Supabase

**Vercel CLI — deploy and manage from the terminal**

``` bash
npm i -g vercel            # install
vercel                     # deploy (interactive, creates project)
vercel --yes --prod        # deploy to production, no prompts
vercel env add KEY production   # set an env var (pipe value in)
vercel env ls              # list all env vars
vercel env rm KEY production --yes  # remove an env var
vercel logs <url>          # stream runtime logs
```

**Tip:** set env vars with `printf 'value' | vercel env add KEY production` to avoid trailing newlines from `<<<`.

**Supabase CLI — manage your project without the dashboard**

``` bash
brew install supabase/tap/supabase   # install on Mac
supabase login                       # authenticate (stores token in keychain)
supabase projects list               # list your projects
supabase link --project-ref <ref>    # link current directory to a project
supabase projects api-keys --project-ref <ref>  # get anon + service_role keys
```

**Get the JWT secret** (not exposed directly by CLI — use the management API):

``` bash
# 1. Get your access token from the macOS keychain
TOKEN=$(security find-generic-password -s "Supabase CLI" -w \
  | sed 's/go-keyring-base64://' | base64 -d)

# 2. Fetch the JWT secret via the API
curl -s "https://api.supabase.com/v1/projects/<ref>/postgrest" \
  -H "Authorization: Bearer $TOKEN" | python3 -c \
  "import sys,json; print(json.loads(sys.stdin.read())['jwt_secret'])"
```

**Create a storage bucket** via the Supabase Storage API:

``` bash
curl -X POST "https://<ref>.supabase.co/storage/v1/bucket" \
  -H "Authorization: Bearer <service_role_key>" \
  -H "Content-Type: application/json" \
  -d '{"id":"wiki","name":"wiki","public":false}'
```

**Disable email confirmation** (useful for personal projects):

``` bash
curl -X PATCH "https://api.supabase.com/v1/projects/<ref>/config/auth" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mailer_autoconfirm": true}'
```

## What This Project Teaches

| Concept | Where it appears |
|----|----|
| markdown & .md files | entire vault is plain markdown — portable forever |
| system prompts as files | `CLAUDE.md` defines conventions the LLM reads every session |
| authentication | Supabase Auth with ES256 JWTs verified via JWKS |
| evals | 24+ pytest tests across auth, search, CRUD, MCP |
| RAG (done Karpathy-style) | index.md as search catalog + TF-IDF fallback, no vector DB |
| tool use / MCP | 6 tools via JSON-RPC, protected by JWT, works on serverless |
| agentic loops | LLM ingests sources → updates entities → lints → synthesizes |
| deployment patterns | Supabase Storage as stateless backing store for Vercel |
| the Karpathy pattern | 3 layers: raw sources + LLM wiki + CLAUDE.md schema |
| human/LLM workflow | you curate and ask; LLM summarizes, cross-references, files |

## Definition of Done: Knowledge Hub v2 (Optional)

- A compatible client can discover the MCP tools.
- The agent uses search/read tools before answering factual questions.
- Output includes valid citations or an explicit evidence gap.
- Tool calls and stopping reasons are recorded.
- Your three evaluations pass.

If you take this build on, this is the bar. Nothing here is submitted or graded — **Assignment 5, the graded capstone, is the insight pipeline** in the previous section.

## Next Class

One well-bounded agent is usually enough. When it is not, the answer is not “add more agents” — it is to choose an architecture that earns its coordination cost.

Bring your running enricher: Class 7 fans it out into the multi-agent pipeline that completes Assignment 5.

**[Next: Class 7 — Multi-Agent Systems, Ops & Safety →](https://haas-ai-classes-fall-26.vercel.app/class7.html)**

## Thank You & What’s Next

Thank you for being here. You now understand how production AI systems actually work — where the model lives, structured output, the agent loop, skeleton-and-spark, MCP, evals, and cost engineering.

**[Next: Class 7 — Multi-Agent Systems, Ops & Safety →](https://haas-ai-classes-fall-26.vercel.app/class7.html)**
