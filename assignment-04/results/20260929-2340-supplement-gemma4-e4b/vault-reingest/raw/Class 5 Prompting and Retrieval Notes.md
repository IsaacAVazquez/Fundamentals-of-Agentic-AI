# Class 5: LLM Behavior, Prompting & Retrieval

Source: https://haas-ai-classes-fall-26.vercel.app/class5.html

---

# Why This Class?

## Yesterday’s “Nice to Have” Is Tomorrow’s “Must Have”

Workplace skills follow a lifecycle: **fringe → resume bullet → expected → invisible baseline.**

- **1995** — “Microsoft Excel” was a legitimate resume bullet
- **2010** — nobody listed Excel; it was assumed
- **2015** — “SQL” was the new bullet
- **2020** — Tableau / PowerBI dashboards were the differentiator
- **2023** — “uses Zapier / Airtable / no-code” was the new layer
- **2025** — “uses ChatGPT / Claude daily” was the new bullet
- **2026 (today)** — **building with AI** — prompts, context, RAG, your own agents — is the current bullet
- **~2028** — table-stakes. The way Excel is today.

**Important**

The question isn’t *whether* this becomes the baseline. It’s whether you’re on the curve early enough that it’s still a differentiator **when you graduate**.

## What This Class Gives You

- **Prompting** — how to steer the probability distribution, with or without thinking mode, so you get useful answers the first time
- **Context** — why the model forgets, what compaction does, why this limits every AI feature you’ll ship
- **Fine-tuning, RLHF, alignment** — what labs actually do under the hood, so *“Anthropic values”* and *“OpenAI personality”* become real design choices, not magic
- **RAG** (Retrieval Augmented Generation) — how to bolt your company’s data onto a general model **without** paying \$100M to retrain
- **Embeddings & vector databases** — the retrieval machinery underneath every “chat with your docs” product
- **Capstone v1** — you start building your own Knowledge Hub: a personal, cited, retrieval-grounded knowledge base

Agents, tool use, MCP, and evals — the machinery that turns all of this into a working product — are **next class**.

**Important**

You won’t be an ML engineer. You’ll be the MBA who **ships** working AI workflows instead of the one who waits for IT.

## Agenda

1.  **Recap** — LLMs predict tokens, probabilistically
2.  **Fine-tuning & RLHF** — how a base model becomes an assistant, and what it costs
3.  **Prompting** — probability steering, failure modes, voice prompting
4.  **Prompts are product interfaces** — writing prompts that survive contact with users
5.  **Context windows** — LotR-sized memory, compaction, token economics
6.  **Prompt engineering** — .md files, system prompts, CLAUDE.md, the golden rule
7.  **Thinking models** — when the model plans before it talks
8.  **Hallucination & RAG** — grounding answers in evidence, with a live demo
9.  **Embeddings & vector databases** — from TF-IDF to dense vectors
10. **Capstone: Knowledge Hub v1** — your first retrieval-grounded product

# Class 4 Recap

## Slide 1 of 2: LLMs Predict Tokens

At the core, an LLM does one thing:

**given the context so far, predict the next token**

- not “look up the truth”
- not “run a database query”
- not “execute a plan”
- just predict what text is most likely to come next

## Slide 2 of 2: LLMs Are Probabilistic

The model does not produce one guaranteed answer.

It produces a **probability distribution** over possible next tokens, then samples from it.

- same prompt can produce different answers
- better prompts reshape the distribution
- more context changes what becomes likely
- exact tasks still need deterministic code

## “It Knows” Is a Risky Shorthand

An LLM contains learned statistical structure in its parameters. It does not consult a verified, current, cited database unless you give it one.

That single sentence explains most of what this class covers:

- **why prompting works** — you’re reshaping which continuation is likely
- **why hallucination happens** — plausible ≠ verified
- **why RAG exists** — to bolt a real, cited knowledge source onto the statistical machine

## The Probability Distribution Is the Steering Surface

Prompts, examples, tools, retrieval, fine-tuning, and decoding settings all influence which continuation becomes likely.

Everything in this class — and the next two — is a different **lever on the same distribution**. Some levers are free and instant (prompts). Some cost millions and take months (fine-tuning). Choosing the right lever is the actual skill.

## Practical Implications

If Class 4 explained the machine, Class 5 is about how to use it well.

- **Why prompting matters**: prompts steer the probability distribution
- **Why exact tasks need code**: probabilities are not enough for precise pipelines
- **Why context matters**: the model only sees what you put in the window

## Temperature: The Creativity Dial

Every API call includes a **temperature** setting — a number that controls how “random” the output is.

|              | Low temp                | High temp                     |
|--------------|-------------------------|-------------------------------|
| **Good for** | facts, code, extraction | brainstorming, writing, ideas |
| **Risk**     | repetitive, boring      | hallucinations, nonsense      |

**Note**

Temperature changes **variety, not intelligence**. Lower temperature favors more likely continuations; higher temperature explores more possibilities and raises variance. It doesn’t make the model smarter or dumber — it changes how adventurous the sampling is.

# What Is Fine-Tuning?

## Fine-Tuning Reshapes the Distribution

In Class 4 we saw you can take a pretrained model and **fine-tune** it — train it further on specific data.

But what does that actually mean? It **shifts which tokens the model considers likely**.

Same prompt, completely different predictions — because the weights changed.

**Note**

Fine-tuning is **expensive and permanent** — it changes the model’s weights. Prompting is **cheap and temporary** — it steers the same frozen model. Most of this class is about prompting, because that’s what you’ll use day-to-day.

## RLHF — How Models Learn to Be Helpful

Fine-tuning on examples makes a model follow instructions. But **how does it learn to be helpful, polite, safe?** Not from raw internet. From humans.

**Post-training is three stages** — and each one uses a learning paradigm from Classes 3 and 4:

1.  **Pretraining** (*unsupervised*) — predict next token from raw internet. No labels — just patterns in text. Knows everything, does nothing useful.
2.  **SFT — Supervised Fine-Tuning** (*supervised*) — labeled *instruction → good-response* pairs. This is what most people call “fine-tuning.”
3.  **RLHF — Reinforcement Learning from Human Feedback** (*reinforcement*) — remember Pac-Man from Class 3? Same loop: try an action, get a reward, learn. Only now the “reward” is **human preference** (*A vs. B, which is better?*), encoded in a **reward model** and optimized via **PPO** or **DPO**.

**Tip**

**Callback to Classes 3 and 4.** The same three learning paradigms you met earlier — unsupervised, supervised, reinforcement — are **literally the three stages** of training a modern LLM. In order.

**Important**

**MBA lens.** *A prompt can’t override what RLHF taught.* That’s the difference between **personality** (prompt-level, changeable per-session) and **values** (weight-level, baked in forever). Firms pick an RLHF recipe the same way they pick a hiring rubric — it determines who the model becomes.

*(In Class 7 we’ll see why Anthropic, OpenAI, and Character.AI all hire philosophers for this step.)*

## Alignment Is Product Design

What should the model refuse? When should it ask? How verbose should it be? What values are embedded in the default behavior?

- **Instruction tuning** teaches task-following — examples of useful question-and-answer behavior shape the model into something people can direct
- **Preference training** shapes helpfulness and safety — human or model feedback rewards responses judged better under a chosen rubric
- **Someone chose that rubric.** The refusal style, the hedging, the “As an AI language model…” — all deliberate product decisions, made by people, encoded in weights

**Important**

When Claude and ChatGPT answer the same question differently, you’re not seeing randomness — you’re seeing **two companies’ product philosophies**, baked in at the RLHF stage.

## …But It’s Super Expensive

**Training**: GPT-4 ~**\$100M** · frontier runs cross **\$1B by 2027**

**Inference**: ~**0.3 Wh** per ChatGPT query · billions of queries/day

You spend all that on **one specific model** — and a better one drops 6 months later.

So instead of changing the model… we just **talk to it better**. That’s what prompting is.

## Three Levers, Three Jobs

Before the decision table, get the jobs straight. Each lever changes something different:

- **Prompting changes the instruction for one request.** Use it when the capability exists but the model needs clearer goals, constraints, format, or examples.
- **Retrieval changes the context for one request.** Use it when answers must be grounded in changing, private, or citeable knowledge.
- **Fine-tuning changes the model’s learned behavior.** Use it when a stable, repeated pattern is hard to prompt and you have high-quality examples. It is **not** the default answer to *“the model lacks our latest facts”* — that’s retrieval’s job.

**Tip**

The most common expensive mistake in industry: reaching for fine-tuning when the actual problem is missing context. **Facts go in retrieval. Behavior goes in fine-tuning. Instructions go in prompts.**

## The Three Levers — Visually

## Prompting vs LoRA vs Fine-Tuning — The Decision Table

Each row is roughly an **order of magnitude** more expensive than the one above it. Start at the top; move down only when the row above demonstrably fails.

| Lever | What changes | Typical cost | Time to ship | Reversible? | Reach for it when… |
|----|----|----|----|----|----|
| **Prompting / system prompt** | nothing — steers the frozen model | ~\$0 | minutes | instantly | almost always — the default |
| **Few-shot examples** | nothing — more context per request | pennies per call | hours | instantly | format, style, or label taxonomy must be consistent |
| **RAG** | the context, per request | \$10s–\$100s/mo infra | days | yes | facts are private, changing, or must be cited |
| **LoRA fine-tune** | a small **adapter** (~0.1–1% of weights) | \$100s–\$10Ks | days–weeks | swap the adapter out | tone, domain jargon, or output shape that prompts can’t hold |
| **Full fine-tune** | all the weights | \$10Ks–\$1Ms | weeks | no — new model | you have thousands of gold examples and a stable task |
| **Pretraining** | everything, from scratch | \$100M+ | months | no | you are a frontier lab |

**What’s LoRA?** *Low-Rank Adaptation* — instead of updating billions of weights, you train a tiny add-on matrix (an “adapter”) that nudges the model’s behavior. Same idea as fine-tuning, ~100× cheaper, and you can swap adapters like lenses on a camera. It’s why “fine-tuning” is affordable at all outside the big labs.

**Important**

**MBA lens.** This table is a build-vs-buy decision in disguise. Prompting is renting. LoRA is a lease with an exit clause. Full fine-tuning is buying a depreciating asset — one that a frontier release can make worthless in six months.

# Prompting

## Prompting Is Probability Steering

Prompting is not magic. It is guidance.

When you add detail, examples, constraints, and formatting requirements, you are shrinking the space of acceptable continuations and making the “right” answer more likely.

**Theoretical Reason Specific Prompts Work**

Specific prompts reduce ambiguity. Less ambiguity means lower entropy in the next-token distribution, so the model is less likely to wander into the wrong answer shape.

## Don’t Mistake the Mask for the Model

**Important**

Whatever polite, helpful voice comes out of the API — underneath is a **next-token predictor trained on the internet**, shaped by RLHF into something that sounds human. Prompt it like a tool, not a colleague. You’ll design better.

## Attention Failure — The Model Answers the Wrong Question

Same prompt, two tries. The first misses the intent entirely — only a follow-up aligns it.

**Important**

The model isn’t stupid — it’s **under-specified**. Attention latched onto *“should I drive or walk”* (a distance question) and ignored that the car is the whole point. This is the everyday failure mode prompting exists to fix.

## Why Voice-to-Text Prompts Can Help

Many people get better results when they **talk** to the model instead of typing a short command.

Why?

- speech naturally includes more context
- people say the edge cases they would have omitted
- they explain intent, not just task labels
- longer natural prompts often reduce ambiguity

**How to do it**

- **WhisperFlow** — free app, transcribes anywhere you can type (works system-wide)
- **Mac dictation** — press 🎤 on the keyboard or double-tap Fn
- **Claude / ChatGPT voice** — tap the mic icon in the app to speak your prompt directly

Dictate the messy version first. Then tighten it into bullets, constraints, examples, and output format.

## LLMs Do Not Start Fresh Per Message

One of the most important chat mental models:

the model does **not** think of your second message as “a totally new brain state.”

It starts fresh per **API request**, but the request usually includes the conversation so far.

- chat apps feel continuous
- the model itself is still stateless between requests
- continuity comes from resending context
- that is why earlier messages still affect later answers

## Context Is Everything

Every word the model reads — system prompt, chat history, your latest message — is **context**. Context is what steers the probability distribution toward the right answer.

This is why good prompts work: they add context. Vague prompts fail because they leave the model guessing.

# Prompts Are Product Interfaces

## The Prompt Is the Spec

So far, prompting has been a personal skill — *you*, talking to a chatbot. But the moment a prompt ships inside a product, it stops being a message and becomes an **interface**: thousands of users’ inputs flow through it, and downstream code consumes what comes out.

That changes the standard. A product prompt has to work on the input you didn’t anticipate, written by the user you never met, on the model version that shipped last night.

**Important**

Treat every prompt that ships like an API contract: specified, versioned, and tested. The next eight slides are the contract clauses.

## A Good Prompt Specifies the Job

```
You are reviewing a customer escalation.
Return: risk level, evidence, recommended next action, and unanswered questions.
```

Notice what this does: it names the **role**, the **task**, and the **exact deliverables**. No adjectives, no “please be thorough” — just the shape of the work, the way you’d brief a new analyst.

## Context Is Not Background Reading

Anything included in the context competes for the model’s attention. Put in the material that should influence this response.

Dumping the whole wiki “just in case” isn’t diligence — it’s noise that buries the two paragraphs that actually matter. Remember the car-wash failure: attention goes where the context points it.

**Note**

**Learn the term: context engineering.** The industry has largely stopped saying “prompt engineering” for this work. The job is no longer writing one clever instruction — it is deciding **what occupies the context window on every single call**: system rules, retrieved evidence, tool results, conversation history, and what gets dropped when space runs out. Prompt engineering is one slide in that job. Context engineering is the whole job, and it is what Classes 6 and 7 are really about.

## Separate Instructions From Data

```
SYSTEM: Follow these operating rules.
USER: Here is the customer request.
REFERENCE: Here are the approved policy excerpts.
```

Three channels, three levels of trust. The system rules come from you. The user request comes from someone you mostly trust. The reference material might come from anywhere — keep the roles visibly separate so the model (and your future debugging self) can tell them apart.

## Instruction Hierarchy Is a Trust Boundary

System-level rules, application policy, user requests, and retrieved text should not have equal authority. Untrusted content may inform an answer; it must not rewrite the operating rules.

**Warning**

This is your first taste of **prompt injection** — a retrieved document that says *“ignore your instructions and…”*. We’ll treat it as a full security topic in Class 7. For now: **retrieved text is data, never instructions.**

## Output Format Is a Reliability Tool

Ask for a schema when another system needs to consume the result.

``` json
{"risk": "low|medium|high", "evidence": ["..."], "next_action": "..."}
```

Free-form prose is for humans. The moment a program parses the output, a fixed schema turns “usually works” into “verifiable” — code can check every field before anything downstream trusts it. (Next class this becomes a whole section: structured output.)

## Examples Teach a Pattern

Few-shot examples are especially useful when judgment, style, or a label taxonomy must be consistent.

One good example is worth a paragraph of description. Three examples that cover the edge cases — the sarcastic complaint, the bilingual email, the empty message — are worth a page.

## Constraints Beat Vague Adjectives

“Cite only supplied sources; say ‘insufficient evidence’ if none apply” is more useful than “be accurate.”

**Tip**

Adjectives describe a wish; constraints describe a **test**. If you can’t tell whether an output followed your instruction, the model can’t either.

## Prompting Is Experimental Work

Make a small test set, change one variable, inspect failures, and keep the version that improves the metric you care about.

This is the scientific method applied to prompts — and it’s the seed of the **evals** discipline we’ll build out properly next class. Vibes don’t survive a model upgrade. Test sets do.

# Context Windows and Memory

## How Big Is a Context Window?

State-of-the-art models like **Claude Opus** have a context window of **1 million tokens**.

How much is that?

The entire **Lord of the Rings** trilogy — all three books — is roughly **500,000 tokens**.

A 1M-token context window can hold **two copies** of the full trilogy and still have room left.

More context = you can feed entire codebases, full documents, or long conversation histories — and the model reasons over all of it at once.

## Bigger Context Is Not a Free Solution

It raises cost and latency, can bury important evidence, and still requires selecting what should matter now.

- **Cost** — you pay for every token, every turn (the window gets resent)
- **Latency** — more tokens to read = slower first response
- **Attention** — a needle in a 900K-token haystack is still a needle

The model only sees the active context — it has no durable memory of your previous chat unless a system deliberately sends relevant information again. A bigger window changes *how much* you can send, not *whether you have to choose*.

## Context Rot Is Real

As prompts become cluttered, a model can miss, misweight, or contradict material already present. More text can make an answer worse.

- research calls this **“lost in the middle”** — models recall the start and end of context, and forget the middle
- long-context benchmarks show accuracy dropping well below the advertised window size
- stale instructions from turn 3 can silently fight fresh instructions from turn 40

**Tip**

Practical fix: when a long chat starts acting confused, **start a new chat** and bring only what matters. Pruning context is a feature, not an admission of defeat.

## But Context Fills Up — Enter Compression

Even 1M tokens isn’t infinite. When the window fills, **compaction** summarizes old conversation into a compact block, freeing up space to keep going.

Compaction is **lossy summarization** — it preserves some decisions and discards detail. Design what gets retained rather than hoping the model remembers correctly.

**Note**

In Claude Code, `/compact` triggers this manually — it also happens automatically around 95% usage. Anything that **must** persist should live in `CLAUDE.md` or a plan file: compaction doesn’t touch those.

## Put Stable Rules in Stable Places

System instructions, durable project files, and structured state are better homes for rules than a long casual conversation.

| Where it lives | Survives compaction? | Survives a new chat? |
|----|----|----|
| Chat message from 40 turns ago | ❌ maybe, as a summary | ❌ |
| System prompt | ✅ | ✅ (if the app resends it) |
| `CLAUDE.md` / project file | ✅ | ✅ |
| A file on disk the model can re-read | ✅ | ✅ |

This table is the whole memory strategy: **conversation is volatile, files are durable.** It’s also the design principle behind the Knowledge Hub capstone.

## Why Everyone Talks About Tokens

Each token the model processes is a pass through a neural network with **trillions of parameters**, running on GPUs. That’s expensive compute — and it’s why everything AI is priced per token.

**Important**

**Input is cheap, output is expensive.** Input tokens are read in parallel (one pass). Output tokens are generated one-by-one, each requiring its own pass. That’s why generating a long answer costs more than reading a long document.

Tokens are the unit of work: models see token pieces, not exactly words — and tokens determine context use, latency, and price. When Class 6 turns to **cost engineering**, this slide is the foundation.

# Prompt Engineering

## .md Files — Why They’re Everywhere in AI

A `.md` file is a **markdown** file — a simple way to write formatted text using plain characters. No special software — just a text file.

**You write this:**

``` markdown
# Meeting Notes
## Action Items

Today we discussed **two options**:

- Option A: launch in *June*
- Option B: wait for Q3

> Decision: go with Option A
```

**It renders as this:**

#### Meeting Notes

##### Action Items

Today we discussed **two options**:

- Option A: launch in *June*
- Option B: wait for Q3

> Decision: go with Option A

`#` = title, `##` = subtitle, `**bold**`, `*italic*`, `-` = bullet. That’s most of what you need.

Markdown is everywhere — these slides, Notion, GitHub, and apps like Obsidian all use it. It’s also the most popular format for writing AI instructions and knowledge bases because it’s structured enough for machines to parse but readable enough for humans to write.

## What Is a System Prompt?

Every AI app has **secret instructions** the user never sees — written by the developer before you ever type anything. Think of it like a **job briefing** before an employee’s first day.

\# ROLE\
You are a PM interview coach for MBA students.\
\
\# PERSONALITY\
Supportive but direct. Use frameworks like STAR.\
Never be condescending. Keep answers under 200 words.\
\
\# BOUNDARIES\
- Only help with PM interviews\
- No salary negotiation or offer advice\
- If asked about other roles, say “I specialize in PM interviews”\
\
\# OUTPUT RULES\
- Always use STAR format (Situation, Task, Action, Result)\
- End with one follow-up question to improve the answer\
\
—\
USER: {{user_message}}

← **Role** — who the model is

------------------------------------------------------------------------

← **Personality** — tone and style

------------------------------------------------------------------------

← **Boundaries** — what it refuses

------------------------------------------------------------------------

← **Output rules** — format of every response

------------------------------------------------------------------------

← **Your message gets injected here**

This entire string is sent to the LLM **every time you send a message**. The user only types the yellow part — everything above it is invisible to them.

**Important**

Remember how fine-tuning costs millions and goes obsolete in 6 months? A system prompt does much of the same job — reshaping behavior — but it’s **free, instant, and easy to change**. That’s why most products start here.

## CLAUDE.md & Project Files

**Markdown** is just a simple way to write formatted text — headings, bullet points, bold — using plain characters you already know. No special software needed.

A **CLAUDE.md** file is a small document that lives inside your project folder. It tells the AI things like:

- “Our brand voice is warm and professional — never sarcastic”
- “When writing emails, always include a clear subject line and sign off with the team name”
- “Budgets are in USD. Fiscal year starts in April”

Tools like **Claude Code** read this file automatically and inject it into every conversation — like giving the AI a **cheat sheet about your team** before it starts working.

You write it once. It applies to every conversation in that project. No copy-pasting context every time.

## What Gets Sent Each Turn

- The model reads **all of this** fresh every turn — no memory between calls
- Long chats cost more because the input keeps growing
- Old context can distract — sometimes “start a new chat” is the right fix
- Good early framing (system prompt) helps the **entire** conversation

## The Golden Rule of Prompting

A good prompt has **five parts** — most people only give one.

**Tip**

You don’t need all five every time — but the more you give, the less the model has to guess.

# Thinking Models

## The Biggest Shift Since GPT

Until September 2024, every LLM worked the same way: you ask, it **immediately starts talking**. No pause, no reflection — just next-token prediction as fast as possible.

Then OpenAI released **o1** — a model that **stops and thinks** before answering. It scored in the 89th percentile on competitive programming and placed among the top 500 US math olympiad students.

The trick? “Think step by step” used to be something **you** wrote in the prompt. Now it’s trained into the model itself.

## What Are “Thinking” Models?

Most models answer immediately — you ask, they respond.

**Thinking models** (Claude with extended thinking, OpenAI o-series) **pause and reason** before answering.

What happens during the “thinking” phase?

- The model generates an internal chain of reasoning — you can often see it
- It breaks the problem down into smaller pieces
- It considers different approaches
- It checks its own logic before committing to an answer

Remember: **more relevant context = better answer**. Thinking models create their own extra context before responding.

## Same Puzzle, Thinking On — Intent Catches Itself

**Same prompt. Thinking mode on.**

- The model **previews its own reasoning** (*“Oh, I see the catch here…”*) before committing.
- It catches the intent — *the car has to get to the wash* — with no user correction.

**Tip**

Earlier we needed a second message to fix attention. Here, the second “message” happens **inside the model’s own head**. That’s the whole pitch for thinking models.

## Thinking Is Not a Permission Slip to Skip Evaluation

A more capable model can still use the wrong data, misunderstand the goal, or confidently produce an unverifiable claim.

Thinking mode raises the floor on hard reasoning tasks. It does **not** grant the model access to facts it never saw, and it does not make outputs deterministic. Everything we said about probability distributions still applies — the distribution just got reshaped by better internal context.

## Match the Model to the Task

Use fast, cheap models for extraction and routing. Use stronger reasoning where ambiguity or stakes justify the cost.

| Task                                      | Right-sized model   |
|-------------------------------------------|---------------------|
| Extract dates from 10,000 emails          | small, fast, cheap  |
| Classify support tickets into 5 buckets   | small, fast, cheap  |
| Draft the board memo on a strategic pivot | frontier + thinking |
| Debug a subtle multi-file code issue      | frontier + thinking |

**Tip**

Thinking tokens are output tokens — the expensive kind. Paying frontier prices for a task a small model nails is the AI equivalent of hiring a senior partner to do data entry.

## Delegate a Bounded Subproblem

“Extract each contract’s renewal date into this schema” is a better model task than “figure out our contract process.”

The best delegators to AI are the same people who delegate well to humans: they hand off a **bounded task with clear success criteria**, not a vague anxiety. This becomes doubly true next class, when the model can also *act*.

## Tip: Use Plan Mode

Thinking models reason automatically. But you can also **force** this behavior — that’s what plan mode does.

Tools like Claude Code (`/plan`), Codex, and Gemini CLI let you ask the AI to **plan before executing**.

**You say:**

“Build me an interview prep app”

→

**Plan mode generates:**

**Goal:** Web app for PM interview prep\
**Stack:** Next.js + Claude API\
**Features:**\
  1. Role selector (APM, PM, GPM)\
  2. Question generator by category\
  3. Answer evaluator with rubric\
**UI:** Single page, chat-style\
**Constraints:** No auth, no DB

Try **voice mode** — explain what you want out loud. The AI turns your rambling into a structured plan, which gives it dramatically better context to work from.

Two things make plan mode powerful:

- **It forces longer thinking** — the model spends more time reasoning before writing any code
- **It saves the plan to a file** — so the blueprint lives outside the context window. Even in a long session where early messages get forgotten, the plan file stays. The model can always look back at it.

**Tip**

Prompting is asking for a building. Plan mode is asking for the **blueprint** first — and pinning it to the wall so nobody forgets it.

# Hallucination Is a System Property

## Why Fluent Systems Can Be Wrong

The next-token objective rewards plausible continuation. It does not guarantee source access, truth verification, or current information.

That’s why “hallucination” is a misleading word — nothing malfunctioned. The model did exactly what it was trained to do: produce the most plausible continuation. **Plausibility without evidence is the failure mode; evidence is the fix.**

**Important**

Hallucination is not a bug you patch in the model. It’s a **system property** you manage in the architecture around the model. Which is good news — architecture is something you control.

## Four Defenses

- retrieve authoritative evidence
- require citations tied to evidence
- validate structured outputs in code
- escalate uncertainty or high-impact actions

Notice that only the first one is about the model. The other three are **product and engineering decisions** — the kind you’ll own. The rest of this class is defense \#1 and \#2: retrieval and citations. Next class adds \#3 and \#4: validation and escalation.

# Retrieval Augmented Generation

## There’s Still a Problem

We’ve covered prompts, context, and thinking — but all of it only lasts for **one conversation**. Start a new chat tomorrow, and the model has no idea who you are, what your project is, or what you talked about.

Even the smartest LLM has the memory of **Dory from Finding Nemo** — brilliant in the moment, completely blank the next.

## Retrieval Augmented Generation (RAG)

An LLM only knows what was in its training data. Try asking Claude “who won the Super Bowl last month?” — it can’t answer. Its knowledge is **frozen** at the date it was trained.

Same thing if you ask about your company’s latest earnings, a new HR policy, or what happened in the news yesterday. The model has never seen any of it.

You *could* paste everything into the chat each time — but that doesn’t scale. Imagine copy-pasting 50 pages of company docs every conversation.

**RAG** = **Retrieval Augmented Generation**

## You Already Use RAG

- When **ChatGPT searches the web** before answering — that’s RAG
- When **Claude Code reads your project files** before writing code — that’s RAG
- When a **company chatbot** answers from internal HR docs — that’s RAG
- When a **customer support tool** pulls answers from your help center — that’s RAG

**Note**

86% of enterprises use RAG to connect AI to their own data. — Databricks, 2025

## Why RAG Matters

**1. Grounds answers in evidence → fewer hallucinations**

The model answers from retrieved documents, not from memory. If the document says revenue was \$12.5M, that’s what gets cited — not a guess.

**2. Uses private knowledge without retraining**

Your company’s internal docs, your database, yesterday’s news — just retrieve and inject into the prompt. No fine-tuning, no \$100K training run, no model that goes stale in 6 months.

This is why businesses love RAG: plug in your own data, keep using the same model.

## Building a Tiny RAG Demo

## Retrieval Is a Pipeline, Not a Magic Box

Source quality, chunking, metadata, embedding choice, ranking, and answer policy each affect whether a response is reliable.

The demo you just ran had all six stages, in miniature: documents (sources), one sentence each (chunking), none (metadata — a real system needs it), TF-IDF (embedding choice), cosine similarity (ranking), and “use this context only” (answer policy). Production RAG is the same pipeline with each stage taken seriously.

## Chunk for a Future Question

Chunks should contain enough context to stand alone but not so much unrelated material that retrieval becomes vague.

- too small: *“up 40% year-over-year”* — 40% of **what**? The number retrieved, the meaning lost
- too big: a 30-page chapter matches everything weakly and nothing strongly
- just right: a paragraph or section that answers a question a human might actually ask

**Tip**

Write chunks the way you’d write flashcards: each one should make sense to someone who hasn’t read the others.

## Metadata Prevents Cross-Contamination

Workspace, owner, document type, date, permission level, and source URL are often more important than a fancy embedding model.

Consider the query *“what’s our refund policy?”* — the 2022 draft, the current policy, and the competitor teardown all match semantically. Only **metadata** (date, status, document type) tells the system which one is allowed to answer.

**Warning**

Permission metadata is the difference between a helpful assistant and a data breach. If the CEO’s comp memo is in the index, retrieval **will** find it — for whoever asks.

## Retrieval Should Return Evidence, Not Just Confidence

Show the source excerpt and link. Let a user inspect the factual basis for important claims.

A fluent answer with no citation and a fluent answer with a wrong citation look identical to the reader. The excerpt-plus-link pattern lets users audit the system for free — every click on a citation is a mini-eval.

## “No Answer Found” Is a Successful Result

If the relevant evidence is absent, the system should say so rather than improvise.

This is the single highest-leverage line in a RAG system’s prompt: *“If the notes do not support an answer, say what is missing.”* It converts the model’s most dangerous behavior — confident improvisation — into its most trustworthy one.

## Retrieval Quality Needs Its Own Metric

For each test question, ask whether the correct source appeared in the retrieved set before judging the generated prose. Generation cannot repair absent evidence.

Debug in order: **retrieval first, generation second.** If the right document never reached the context, no prompt tweak will save the answer — you’d be polishing the wrong stage of the pipeline.

## Retrieval Can Fail in Several Ways

It can miss the right source, retrieve irrelevant sources, mix permission scopes, split a key fact from its context, or return stale content. Test each failure deliberately.

| Failure | Symptom the user sees |
|----|----|
| Missed the right source | confident wrong answer, or “no answer” when one exists |
| Irrelevant sources | answer drifts off-topic, cites the wrong doc |
| Mixed permission scopes | someone reads something they shouldn’t |
| Split a key fact | number without unit, quote without speaker |
| Stale content | last year’s policy, presented as current |

## Grounding Is a User-Visible Feature

An answer should make its evidence easy to inspect. Citations, quoted snippets, source dates, and “I could not verify this” increase useful trust.

**Important**

**MBA lens.** Grounding isn’t a technical nicety — it’s the product’s trust story. Users forgive a system that says “I don’t know.” They abandon one that lied to them once, confidently.

## Privacy Shapes the Architecture

Before sending documents to a model provider, decide what data classification is allowed, how long it is retained, who may retrieve it, and what must stay in a private environment.

This question — *can this data leave our infrastructure at all?* — is exactly what drives the API-vs-self-hosted decision we’ll open Class 6 with.

# Embeddings & Vector Databases

## TF-IDF Has a Blind Spot

The demo you ran matches **exact words**. Ask *“How much money did TechCorp earn?”* instead of *“How much revenue did TechCorp make?”* and TF-IDF starts to struggle — *money* and *earn* never appear in the revenue document.

Humans know *revenue ≈ money earned*. Word-counting doesn’t.

- **synonyms fail** — “car” vs “automobile”, “salary” vs “compensation”
- **paraphrases fail** — “who runs the company?” vs “the CEO is…”
- **cross-lingual fails completely** — same meaning, zero shared tokens

What we want is retrieval by **meaning**, not by spelling. And we already met the tool for that in Class 4: **embeddings**.

## From Word Counts to Dense Vectors

Remember Word2Vec from Class 4 — words as points in space, where *king − man + woman ≈ queen*? Modern **embedding models** do the same thing for whole sentences, paragraphs, and documents.

- feed text into a neural network → get back a **dense vector** (typically 384–3,072 numbers)
- texts with **similar meaning** land **close together** in that space — regardless of exact wording
- “How much revenue?” and “What did they earn?” become **neighboring points**
- the vectors are “dense” because every dimension carries a little meaning — unlike TF-IDF’s mostly-zero word-count vectors

**Note**

You don’t train these yourself. OpenAI (`text-embedding-3`), Cohere, Voyage, and open-source models (`all-MiniLM`, `bge`, `nomic-embed`) sell or give away embedding endpoints — pennies per million tokens. Embedding your whole company wiki costs less than lunch.

## Same Math, Better Vectors

Here’s the punchline: **the retrieval code doesn’t change.** It’s still cosine similarity — the angle between two vectors — exactly like the TF-IDF demo. Only the vectors got smarter.

In production, `query_vec` comes from the embedding model, not hand-tuning — but the pipeline is identical: **embed → compare → take the top-K → stuff into the prompt.**

## Where Do a Million Vectors Live? — Vector Databases

Comparing one query against five documents is a `for` loop. Against **ten million chunks**, on every keystroke? You need a database built for nearest-neighbor search — a **vector database**.

| Option | What it is | Best for |
|----|----|----|
| **NumPy / FAISS in memory** | a library, not a database | prototypes, \<100K vectors, this course |
| **pgvector** | an extension for Postgres — vectors next to your existing tables | teams that already run Postgres (most teams) |
| **Chroma** | open-source, embedded, runs in your app process | local apps, personal projects, quick RAG |
| **Pinecone** | managed cloud service, scale-as-you-go | production at scale, no ops team |
| **Weaviate / Qdrant / Milvus** | open-source servers, self-host or cloud | full control + hybrid search features |

**Tip**

**The boring advice is the right advice**: if you have Postgres, start with **pgvector** — your vectors live next to your metadata, and one `WHERE` clause handles permissions. Reach for a dedicated vector DB when scale or latency demands it.

**Important**

**MBA lens.** “We need Pinecone” is often the AI-era version of “we need Hadoop” circa 2014. At personal-wiki scale — like your capstone — even Karpathy skips vectors entirely and greps an index file. Match the infrastructure to the corpus, not the hype cycle.

## Hybrid Search — Because Meaning Isn’t Everything

Dense vectors have their own blind spot — the exact opposite of TF-IDF’s:

- Search for **“invoice \#812”** — embeddings see “some invoice”; keyword search nails the exact ID
- Search for **“Q3 2024 earnings”** — embeddings blur it with Q2 and 2023; keywords don’t
- Product codes, names, acronyms, legal citations — **exact strings matter**

So production systems run **both** and merge the results:

**Hybrid search** = keyword scoring (BM25 — TF-IDF’s polished descendant) **+** dense vectors, combined — often with a **reranker** model ordering the merged top-K by true relevance.

| Stage | What it does | Cost |
|----|----|----|
| Keyword (BM25) | exact matches, IDs, names | ~free |
| Dense retrieval | synonyms, paraphrase, meaning | cheap |
| Reranker | reorders the merged candidates precisely | moderate |
| LLM generation | writes the cited answer | the expensive part |

**Note**

The funnel shape is deliberate: **cheap stages narrow the field so the expensive stage reads only the finalists.** You’ll see this cost-funnel pattern again in Class 6 — it’s how every production AI system is architected.

## Hybrid Search — Visually

# Assignment 4: Knowledge Hub v1

## The Product

Build a personal or team knowledge hub that answers questions from a controlled set of notes and documents.

It is not a general chatbot. It is a system that earns trust by showing its work.

Everything from today ships inside it: prompts as product interfaces, context discipline, retrieval, citations, and “no answer found” as a feature.

## Where This Is Going — Your Personal AI Knowledge Hub

Inspired by [Karpathy’s LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — a personal knowledge base that an LLM maintains for you.

The idea: your notes, highlights, and summaries live as **markdown files** in a folder. A **FastAPI backend** serves them as an MCP server. **Obsidian** renders them locally. Any LLM — Claude on your phone, ChatGPT, a local model — can **read and write** to your hub via MCP.

Deploy to **Vercel** so it’s accessible from anywhere.

**Note**

That full vision is the **v3** you’ll finish in Class 7. This week is **v1**: the vault, the index, retrieval, and grounded answers — the foundation everything else stands on. Class 6 adds the agent and the MCP tools (v2).

## Architecture

Keep this diagram in mind across all three versions: **v1** builds the vault + retrieval (right side), **v2** adds the agent + MCP tools, **v3** deploys the full loop. You’re not doing three projects — you’re doing one project in three passes.

## The Karpathy Pattern: 3 Layers

Read Karpathy’s [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) before you build — it’s the spec. The pattern has three layers:

- **Raw sources** (`vault/raw/`) — immutable input documents you drop in. Articles, papers, meeting notes, web clippings. **Never modified.**
- **Wiki** (`vault/wiki/`) — LLM-maintained interlinked markdown pages: entity pages, concept pages, source summaries. **Compounds over time.**
- **Schema** (`CLAUDE.md` at project root) — conventions telling the LLM how to maintain the wiki. Ingest workflow, query workflow, lint workflow. **Loaded every session.**

**Important**

**Your job**: curate sources, direct analysis, ask good questions. **The LLM’s job**: summarize, cross-reference, file, update, lint. The wiki compounds every time you add a source or ask a question.

## Why Obsidian

[Obsidian](https://obsidian.md) is a free, local-first markdown editor. Point it at a folder of `.md` files and it becomes a navigable knowledge base.

- **Files on disk** — no lock-in, no cloud. The LLM writes files, you read them in Obsidian.
- **`[[wikilinks]]`** render as clickable links between notes
- **Graph view** visualizes the connections — orphan pages, hubs, and clusters become obvious
- **YAML frontmatter** (`tags`, `created`, `sources`) powers filtering and Dataview queries

**Tip**

**The workflow**: LLM is the writer, Obsidian is the reader. Open your vault in Obsidian on one screen, Claude Code on the other — watch the graph grow as you ingest sources.

**Setup**: Open Obsidian → “Open folder as vault” → pick your `vault/` directory. Done.

## Starter Location

`capstone/knowledge-hub` contains a FastAPI/MCP starter, a local Markdown vault, search code, tests, and a credential template.

Notice the vault already follows the Karpathy shape: `raw/` for immutable sources, `wiki/` for derived pages, and an `index.md` catalog. Keep that discipline from day one — v2 and v3 depend on it.

## The v1 Boundary

- In scope: ingest a small set of sources, maintain a clear index, retrieve relevant notes, cite them.
- Out of scope: autonomous edits, multi-agent coordination, public deployment, and broad web search.

**Tip**

The boundary is the point. A retrieval system you fully understand beats an agent you can’t debug. The optional v2 (next class) and v3 (Class 7) builds earn the tools and then the team — while the graded capstone, Assignment 5, applies the same discipline to a 10,000-record insight pipeline.

## Choose a Corpus You Can Inspect

Good examples: a course reading packet, customer discovery notes, company policy excerpts, investment memos, or research summaries.

Never use sensitive data unless you have explicit permission and an approved environment.

## Define Three Answerable Questions

For each question, name the expected source(s) and the answer behavior if the evidence is missing.

This is the “retrieval quality needs its own metric” slide made concrete: you’re writing your eval set **before** you build. Three questions, known sources, known correct behavior — that’s a test suite.

## Keep Raw Sources Immutable

Raw source material is evidence. Derived summaries and wiki pages are a separate layer that can be regenerated or challenged.

This is the Karpathy pattern’s first rule: `raw/` is **never modified**. If a summary is wrong, you fix the summary — the evidence stays untouched, so you can always re-derive.

## Make the Index a Product Surface

The starter’s `vault/index.md` is the catalog. Keep it current so both people and retrieval code can see what knowledge exists.

At personal-wiki scale, the index **is** the retrieval system — Karpathy’s own wiki searches `index.md` first and falls back to TF-IDF only when the index comes up short. No vector database required. (Now you know exactly why that works — and when it stops working.)

## Test Retrieval Before Generation

For each of your three questions, inspect the top retrieved notes. If retrieval is wrong, a better prompt will not fix the system.

## Add a Grounded Answer Policy

```
Answer only from retrieved notes. Cite every material claim.
If the notes do not support an answer, say what is missing.
```

Three sentences that implement three of the four hallucination defenses: evidence, citations, and honest uncertainty.

## Evidence Card

For each answer, record: question, retrieved note paths, answer, citations, and whether the result was supported.

The evidence card is a **trace** — a manual one. Next class we automate exactly this record for every agent run.

## Definition of Done: Knowledge Hub v1

- Three source notes or summaries exist in the vault.
- `vault/index.md` catalogs them.
- Three test questions retrieve relevant evidence.
- Each answer cites a note or explicitly says evidence is insufficient.
- One failure case is documented, not hidden.

## Next Class

Retrieval gives the model evidence. Next we turn the system into a bounded single agent with explicit tools, deterministic guardrails, and evaluation.

**[Next: Class 6 — Production LLMs & Single Agents →](https://haas-ai-classes-fall-26.vercel.app/class6.html)**

## Thank You & What’s Next

Thank you for being here. You now understand how to steer an LLM — prompting, context, fine-tuning economics, and retrieval — and you’ve started building a product on top of it.

**[Next: Class 6 — Production LLMs & Single Agents →](https://haas-ai-classes-fall-26.vercel.app/class6.html)**
