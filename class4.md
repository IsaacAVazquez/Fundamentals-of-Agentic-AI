# Class 4: Deep Learning, Embeddings & Transformers

Source: https://haas-ai-classes-fall-26.vercel.app/class4.html

---

# From Hand-Designed Features to Learned Representations

## Class 3 Recap — In Sixty Seconds

- ML **learns rules from examples** when the rules are too complex to write by hand
- Training = **measure loss, adjust parameters, repeat** — gradient descent walking downhill
- **Generalization is the entire game** — a model that only works on its training data is a lookup table with extra steps
- The classical toolbox (trees, forests, boosting) wins on **tabular data** — but you had to engineer the features yourself
- Evaluation is a **business conversation**: precision vs recall, thresholds, decision rights
- And you shipped a **Deep Q-Network** that learned to play Pac-Man — with a neural network inside it you have not opened yet

Today we do two things: **open up that network**, and remove the biggest limitation of everything we did last class — **the human in charge of deciding what the inputs mean.**

## The Limitation of Classic ML

For text, images, speech, and messy human behavior, deciding the “right” input features **can be most of the work**.

- Last class: *you* translated raw data into signals — rent-to-income ratio, days-since-purchase, amount-vs-average
- Now try that for a photo. What column captures “this is a cat”? Whisker length? Ear angle? Researchers spent **decades** hand-crafting image features (edge detectors, texture histograms) — and hit a ceiling
- Language is worse: what feature of “this contract has an unusual indemnification clause” can you compute from raw characters?

**Important**

This was the wall AI sat behind for fifty years. The breakthrough wasn’t a better algorithm for using human-designed features — it was **getting rid of the human feature designer entirely**.

## Deep Learning Learns Multiple Layers of Representation

```
raw input → simple patterns → combinations → task-specific prediction
```

- Feed the network **raw pixels** or **raw text** — no engineered columns
- Each layer learns to detect patterns in the previous layer’s output
- The features are **discovered, not designed** — and they routinely beat decades of expert hand-crafting

That single idea — **learned representations** — is what “deep” means in deep learning, and it’s the thread connecting everything today: neural nets, embeddings, attention, transformers, LLMs.

## A Neural Network Is Still a Function

It is not a brain and it is not magic. It is a **large collection of weighted calculations organized into layers**.

- Same recipe as last class: inputs → function with adjustable parameters → prediction
- Same training loop: predict, measure loss, gradient descent
- The only news: **many more parameters, arranged in layers** — and that arrangement turns out to matter enormously

**Tip**

Keep this deflationary framing handy for vendor meetings. Every claim about a neural network — “it understands,” “it reasons,” “it hallucinates” — cashes out as statements about a very large parameterized function trained to minimize a loss. Wonder at what that achieves; don’t mystify how.

## Today’s Roadmap

1.  **Neural networks** — from one neuron to deep layers
2.  **Training deep networks** — backpropagation, optimizers, GPUs
3.  **Machines that read** — embeddings, tokens, and meaning as geometry
4.  **Attention** — the mechanism that changed everything
5.  **Transformers** — the architecture behind every modern AI
6.  **From transformers to LLMs** — scaling laws, emergent capabilities, multimodality
7.  **Live demos + exercise** — build attention with your own hands
8.  **Assignment 3** — build a GPT from scratch and train your own language model

# Neural Networks

## The Artificial Neuron

Neural networks are inspired by the brain — networks of simple units (neurons) that can learn complex patterns when connected together.

A single neuron does three things:

1.  Takes **inputs** (numbers)
2.  Multiplies each input by a **weight** (how important that input is)
3.  Adds a **bias**, applies an **activation function**, and produces an **output**

## A Single Neuron in Action

One neuron, one decision: take inputs, multiply by weights, output a score. Score \> 0.5 → Yes. Score \< 0.5 → No. That’s classification. One neuron isn’t smart — but **millions together** can recognize faces, translate languages, and write code.

## The Neuron as a Formula

The whole unit fits in one line:

```
output = activation(weight₁ × input₁ + weight₂ × input₂ + bias)
```

- **Weights express importance.** During training, the model adjusts weights so useful signals matter more and less useful signals matter less
- **Bias gives the function flexibility.** It lets the model shift its decision boundary instead of forcing every pattern through zero — the same job as the intercept in your regression line
- **Activation functions create nonlinearity.** They bend the output — and that bend is where all the power hides

## Why Nonlinearity Matters

- Without activation functions, many layers **collapse into one linear transformation** — stacking ten linear layers gives you… one line. A thousand-layer network would be exactly as smart as linear regression
- Nonlinearity lets models represent **curved, conditional, “it depends” patterns**: “spend predicts loyalty, but only above a usage floor, unless the account is enterprise”
- The most popular activation is embarrassingly simple — **ReLU**: *if the input is negative, output 0; otherwise pass it through.* That one kink, repeated millions of times, builds arbitrarily complex shapes

**Note**

The deep insight: complexity doesn’t come from complicated parts. It comes from **billions of trivially simple parts, composed**. Remember that when someone describes an LLM as if it must contain a reasoning engine somewhere — it’s kinks all the way down.

## Inspired by the Brain

Biological neuron

Dendrites receive signals → cell body processes → axon sends output to the next neuron

Artificial neuron

Inputs × weights → activation function → output to the next layer

This isn’t a coincidence. Neural networks were **designed to mimic the brain**. Your brain learns by adjusting the **strength of connections between neurons** — exactly what training does with weights. Both are pattern recognition machines, one biological, one mathematical.

## One Neuron → A Network

**86 billion neurons**, each connected to thousands of others. You think, remember, and recognize patterns through these connections.

An artificial neural network: layers of nodes, each connected to the next. Every connection has a **weight** — a number the model adjusts during training.

A single neuron is simple. But **billions of them connected together** — that’s where intelligence emerges. Same principle, biological or artificial.

## How a Neural Network Learns

Think of it like a **factory assembly line** — a product passes through stations, and when the result is bad, you trace backward to find the fault:

1.  **Forward pass** — raw materials move through each station in order. Each station does its job. A product comes out at the end.
2.  **Calculate loss** — quality inspection checks the product. How defective is it? (Same loss from last class — a single number for “how wrong.”)
3.  **Backpropagation** — trace **backward** through the stations: which station contributed most to the defect? Station 3’s temperature was off, station 5’s timing was wrong.
4.  **Gradient descent** — adjust each station’s settings proportionally to how much it caused the defect. Big cause → big adjustment.
5.  **Repeat** — run the line again. Inspect. Trace back. Adjust. Thousands of times until the products are good.

## The Training Loop

This is the same cycle every ML model uses — predict, measure loss, adjust. Neural networks just do it with **millions of weights** instead of one line through data.

## What’s Actually Being Adjusted?

Every line connecting two neurons is a **weight** — a knob the model adjusts during training. This tiny network has 20 knobs. GPT-5 has an estimated **5 trillion**.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/gpt)

## Parameters vs Hyperparameters

Not all knobs are the same. There are two kinds:

**Parameters** (the model learns these)

- The **weights** between neurons
- Adjusted automatically by gradient descent
- Millions or billions of them
- You never set these by hand

**Hyperparameters** (you choose these)

- **Learning rate** — how big each step is
- **Number of layers** — how deep the network
- **Number of neurons per layer** — how wide
- **How long to train** — number of epochs

**Note**

Parameters are what the model figures out. Hyperparameters are the decisions **you** make before training starts. Picking good hyperparameters is part art, part science — and one of the key skills in ML.

# Deep Neural Networks

## Why Depth Matters

A single neuron can learn simple patterns. But complex patterns need many **layers** — that’s a **deep** neural network.

Take a network that recognizes **photos of faces**. You feed it raw pixels. It has never been told what a “face” is. But each layer learns something more complex than the last:

- **Layer 1**: Spots edges — light vs dark boundaries in the pixels
- **Layer 2**: Combines edges into textures — skin, hair, fabric
- **Layer 3**: Groups textures into parts — “this looks like an eye”, “that’s a nose”
- **Layer 4**: Assembles parts into a face — “this is a person”

Nobody programmed “look for eyes.” The network figured it out from millions of photos. More layers = more abstraction. This only became practical when **GPUs** gave us the power to train these in parallel.

## The Same Story in Every Domain

The layered-abstraction trick isn’t just for faces:

- **In an image**: one layer detects an edge; deeper layers combine edges into shapes, shapes into objects
- **In text**: one layer detects a local word pattern; deeper layers combine tokens into phrases, phrases into relationships and intent
- **In tabular data**: one layer detects an interaction between features; deeper layers combine interactions into segment-level behavior

**Tip**

This is the promise from the start of class delivered: **the network builds its own feature engineering, layer by layer.** The features your data scientists spent 80% of their time crafting last class? For images and text, the network learns better ones automatically. That’s the entire deep learning revolution in one sentence.

# Training Deep Networks

## Forward Pass: Make a Guess

Data flows through the layers to produce a prediction.

- Pixels in → edges → textures → parts → “92% this is a cat”
- At the start of training, the weights are **random** — so the first guesses are garbage. A network’s first prediction is a coin flip with confidence
- The forward pass is cheap and fast: just multiplications and additions, layer by layer. This is also what happens **every time you use** a trained model — inference is a forward pass and nothing more

## Loss: Score the Guess

The training objective turns “bad prediction” into a **number the optimizer can reduce**.

- Same idea as last class: squared error for numbers, cross-entropy for categories
- The choice of loss **is** the choice of what the network cares about — optimize click-through and you get clickbait; optimize watch time and you get autoplay rabbit holes
- Everything downstream — backprop, gradient descent — blindly minimizes whatever number you picked here

**Warning**

“The model did exactly what we trained it to do, and that was the problem” is the epitaph of many ML products. The loss function is a **management decision** wearing a math costume — it deserves the same scrutiny as a bonus scheme, and it fails the same way: people (and models) optimize what you measure.

## Backpropagation: Assign Responsibility

It calculates how each weight contributed to the error, then sends a correction signal **backward** through the network.

- The factory analogy made literal: the quality inspector walks the line in reverse, leaving each station a note — *“you contributed this much to the defect; adjust this way”*
- Mathematically it’s the **chain rule from calculus**, applied layer by layer — nothing more exotic
- One backward sweep computes the adjustment direction for **every weight at once** — all billions of them, in roughly the cost of one forward pass

## Backpropagation, Visually

The error at the output flows backward, splitting among the connections that produced it. Weights that pushed the answer in the wrong direction get nudged down; weights that pushed toward the right answer get nudged up.

**Note**

Backprop was popularized in **1986** (Rumelhart, Hinton & Williams). The algorithm training GPT-5 today is the same one — it just waited forty years for enough compute and data. Another entry in the “the ideas aren’t new, the resources are” file.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/mini-llm)

## The Nudge, Up Close

Each training example effectively says: *“to have gotten this one right, these weights should be a little higher, those a little lower.”* One example’s opinion is noisy. **Millions of examples, averaged, carve out weights that work for all of them** — that’s the condensation of knowledge from last class, mechanized.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/mini-llm)

## Optimizers Choose the Update

Backprop tells you the **direction**; the optimizer decides **how to step**.

- **SGD** (stochastic gradient descent): take a plain step downhill. Simple, sometimes slow
- **Adam**: the industry default — adapts the step size per weight and builds up “momentum,” like a ball rolling downhill that powers through small bumps
- Related methods are all strategies for the same job: turning gradient information into useful parameter updates without overshooting or stalling

**Note**

You already ran `Adam, lr=1e-4` in last week’s Pac-Man agent. Now you can read that line: “use the adaptive optimizer, with small careful steps.” You’ll set the same two knobs yourself in today’s assignment.

## Batches Make Training Practical

Instead of updating from every example one at a time, train on **small groups**.

- Computing the perfect gradient over 10 million examples before each tiny step would be absurdly slow
- Updating after every single example is fast but erratic — each example yanks the weights toward its own quirks
- The compromise: **mini-batches** of 32–512 examples. This balances speed, memory, and — surprisingly — *useful* noise: the slight randomness helps training escape bad valleys (remember local minima?)

## Epochs Revisit the Dataset

One **epoch** is one full pass through the training data.

- Networks need many passes — early epochs learn coarse patterns, later epochs refine details
- More epochs are **not automatically better**: keep going too long and the network starts memorizing the training set. Overfitting again — same disease as last class, bigger patient
- The standard defense is beautifully simple: watch validation performance every epoch and **stop when it stops improving** (“early stopping”)

**Tip**

Notice how much of Class 3 transferred wholesale: loss, gradient descent, overfitting, validation curves. Deep learning didn’t replace those fundamentals — it **scaled them up**. If you understood last class, you already understand 80% of this one.

## CNNs at a Glance

For images, there’s a specialized architecture worth knowing by name: the **Convolutional Neural Network (CNN)**.

- Key insight: a cat in the top-left corner is the same cat in the bottom-right. So instead of learning separate weights for every pixel position, learn a small **filter** (say 3×3 pixels) and **slide it across the whole image**
- Each filter becomes a reusable pattern-detector — one learns vertical edges, another learns fur texture, another learns eyes
- Massive weight-sharing = far fewer parameters = trainable on realistic data. This is the architecture behind face unlock, medical imaging, self-driving perception — and the Pac-Man agent you trained last week. That stack of `Conv2d` layers Claude Code wrote for you? This slide is what it was doing.

**Note**

The architecture lesson generalizes: **matching the network’s structure to the structure of the data** (images repeat spatially → share weights spatially) is what separates architectures. Hold that thought — transformers are exactly this move, applied to language.

## The GPU Story — Why NVIDIA Is Worth Trillions

Deep learning is, computationally, one thing repeated forever: **multiplying huge grids of numbers** (matrices).

- A **CPU** is a few brilliant workers doing complex tasks one after another
- A **GPU** is **thousands of simple workers** doing identical multiplications simultaneously — originally built to color millions of pixels per frame for video games
- In 2012, **AlexNet** trained on two consumer gaming GPUs and crushed the ImageNet competition — halving the error rate overnight. The field noticed: the hardware for rendering games was the hardware for training minds

**Important**

That accident of history is why a gaming-card company became one of the most valuable corporations on Earth, why “GPU allocation” is a board-level topic, and why nations now treat chips like oil. When you read about **export controls on H100s**, this slide is the context: compute is the strategic input to AI, and GPUs are where compute lives.

# Teaching Machines to Read

## Why Language?

So far, every model we’ve seen works with **numbers** — house prices, pixel values, game screens.

- But the biggest AI breakthroughs came from teaching machines to read **text**
- Why? The internet is mostly text. Trillions of words, freely available
- If you can teach a machine to read, you can train it on the **entire internet**

**Note**

This is exactly what happened. The shift from images to language is what gave us ChatGPT, Claude, and every modern AI assistant.

## The Problem: Words Aren’t Numbers

How do you feed words into a neural network that only understands numbers?

You convert words into **vectors** — lists of numbers that capture meaning.

**Warning**

This is simplified! Real dimensions aren’t neatly labeled “furriness” or “size.” The model discovers its own abstract axes through optimization — each one blends many concepts. But the intuition holds: **similar words end up as nearby points**.

## From Symbol to Vector

A token starts as a meaningless ID. `"bank"` and `"river"` are initially just symbols — the model needs a numerical representation it can **compare and combine**.

An **embedding** is that representation — a learned vector:

```
"contract" → [0.18, -0.42, 0.77, ...]
```

- Hundreds or thousands of dimensions per word, every number **learned during training** — nobody designs them
- Words or documents used in **similar contexts end up near one another** in embedding space
- Once meaning is geometry, the network can do math on it: compare meanings (distance), combine meanings (addition), transform meanings (multiplication by weights)

## Words as Points in Space

**Word2Vec** (2013) learned that words in similar contexts get similar vectors.

“The \_\_\_ sat on the mat” → cat, dog, child all fit → similar vectors.

Words with similar meanings cluster together. Relationships like gender, royalty, and age become **directions** you can navigate with math.

**Important**

**king - man + woman ≈ queen**

The model learned gender as a direction in vector space, without anyone teaching it!

## Explore Word Embeddings in 3D

Metadata:

/

/

.\*

Enable/disable regex mode. \[\[message\]\]

Show All Data

Isolate selection

Clear selection

\[\[item\]\]

neighbors The number of neighbors (in the original space) to show when clicking on a point.

distance

[COSINE](javascript:void(0);) [EUCLIDEAN](javascript:void(0);)

Nearest points in the original space:

neighbors The number of neighbors (in the selected space) to show when clicking on a point.

{{metadataColumn}} labels (click to apply):

Showing only the first 100 results...

\[\[label\]\]

\[\[item.key\]\]

\[\[item.value\]\]

UMAP

uniform manifold approximation and projection

t-SNE

t-distributed stochastic neighbor embedding

PCA

Principal component analysis

Custom

Search for two vectors upon which to project all points.

Dimension

2D 3D

Neighbors The number of nearest neighbors used to compute the fuzzy simplicial set, which is used to approximate the overall shape of the manifold. The default value is 15. \[\[umapNeighbors\]\]

Run

For faster results, the data will be sampled down to \[\[getUmapSampleSizeText()\]\] points.

[Learn more about UMAP.](https://umap-learn.readthedocs.io/en/latest/how_umap_works.html)

Dimension

2D 3D

Perplexity The most appropriate perplexity value depends on the density of the data. Loosely speaking, a larger / denser dataset requires a larger perplexity. Typical values for perplexity range between 5 and 50.

Learning rate The ideal learning rate often depends on the size of the data, with smaller datasets requiring smaller learning rates.

Supervise The label importance used for supervision, from 0 (disabled) to 100 (full importance).

Run Pause Perturb

Iteration: 0

For faster results, the data will be sampled down to \[\[getTsneSampleSizeText()\]\] points.

[How to use t-SNE effectively.](http://distill.pub/2016/misread-tsne/)

\#

Variance (%)

\[\[item.componentNumber\]\]

\[\[item.percVariance\]\]

\#

Variance (%)

\[\[item.componentNumber\]\]

\[\[item.percVariance\]\]

\#

Variance (%)

\[\[item.componentNumber\]\]

\[\[item.percVariance\]\]

PCA is approximate.

Total variance

For fast results, the data was sampled to \[\[getPcaSampleSizeText()\]\] points and randomly projected down to \[\[getPcaSampledDimText()\]\] dimensions.

\[\[item\]\]

## 

Close

Bounding box selection Edit current selection Enable/disable night mode Enable/disable 3D labels mode

Points: Loading...

Dimension: Loading...

Reset zoom to fit all points

![](data:image/svg+xml;base64,PHN2ZyBpZD0ic2VsZWN0b3IiPjwvc3ZnPg==)

Help with interaction controls.

### 3D controls

**Rotate** Mouse left click.\
**Pan** Mouse right click.\
**Zoom** Mouse wheel.\
Holding **ctrl** reverses the mouse clicks.

### 2D controls

**Pan** Mouse left click.\
**Zoom** Mouse wheel.

Click anywhere to dismiss.

Embedding Projector

[Open documentation](https://haas-ai-classes-fall-26.vercel.app/%5B%5BdocumentationLink%5D%5D "Documentation") [Report a bug](https://haas-ai-classes-fall-26.vercel.app/%5B%5BbugReportLink%5D%5D "Report bug")

Embedding projector - visualization of high-dimensional data

**Tip**

Click **Word2Vec 10K** on the left. Search for “king” — then look at what’s nearby. Try toggling between PCA and t-SNE projections.

## Distance Becomes a Retrieval Primitive

Once everything is a vector, **search changes character**:

- Given a question, **embed it** and find stored vectors with similar direction or position
- No keywords needed: “how do I get my money back” retrieves the refunds policy even though it shares zero words with “refund”
- Remember k-NN from last class — “predict by finding similar past examples”? This is that idea, with **learned similarity**: embeddings define “similar,” nearest-neighbor search does the rest

**Warning**

But **similarity is not truth**. Embedding search finds *related* material — it does not prove the material answers the question correctly. A document about “refund fraud” is very close to “refund policy” in embedding space. This distinction becomes a production issue in Class 5, when we build retrieval systems (RAG) on exactly this primitive.

## Context Determines Meaning

One vector per word has a ceiling: “bank” in a finance memo and “bank” in a river report **should not mean the same thing**.

Word2Vec gives both banks the same point in space — a frozen average of every “bank” ever written. Modern models instead create **contextual representations**: the vector for “bank” is adjusted, on the fly, by the words around it. The mechanism that does that adjusting is **attention** — coming right up.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/gpt)

## From Words to Tokens

Modern LLMs don’t use word-level embeddings. They use **subword tokenization** (BPE):

- “unbelievable” → \[“un”, “believ”, “able”\]
- “ChatGPT” → \[“Chat”, “G”, “PT”\]

This handles rare and new words gracefully — even words the model has never seen can be broken into familiar pieces.

**Note**

Embeddings are the bridge between human language and neural networks. The discovery that word relationships are captured as **directions in vector space** was one of the key insights that led to modern NLP and LLMs.

## How BPE Actually Works

**Byte-Pair Encoding** builds its vocabulary bottom-up from the training data:

1.  Start with single characters as the only tokens
2.  Find the **most frequent adjacent pair** in the corpus — say `t`+`h` — and merge it into one token: `th`
3.  Repeat: `th`+`e` → `the`; `ing` forms; common words fuse into single tokens; rare words stay in pieces
4.  Stop at a fixed vocabulary size — typically 50,000–200,000 tokens

The result is a **compression scheme shaped by frequency**: “the” is one token; “electroencephalography” is several; a typo or a new brand name still tokenizes fine as fragments. Nothing is ever “out of vocabulary.”

**Note**

Tokens are also the **billing unit** of the AI economy — every API price is per-token. And because BPE learns from its corpus, English compresses efficiently while many other languages need 2–3× more tokens for the same sentence: the same prompt can literally cost triple in Thai. Tokenization choices are cost, latency, and market-coverage choices.

## BPE — Visually: “unbelievable” Becomes 3 Tokens

## Why Models Miscount the R’s in “Strawberry”

For months, frontier models famously answered that “strawberry” has **two** r’s. Tokenization is the culprit:

- The model never sees `s-t-r-a-w-b-e-r-r-y`. It sees something like `[st][raw][berry]` — three opaque IDs
- Asking it to count letters is like asking you to count the brushstrokes in a photo of a painting — **the information was compressed away before you got it**
- Same root cause for other classic stumbles: reversing strings, arithmetic on long numbers (digits get grouped into unpredictable tokens), rhyming in some languages

**Tip**

Management takeaway: when a model fails at something absurdly simple, the explanation is usually **representation, not intelligence**. Knowing *what the model actually sees* lets you predict entire categories of failure — and route those tasks to plain code, which counts letters perfectly and for free.

# Sequences & Attention

## The Problem with Order

Regular neural networks treat each input independently. But what about data where **order matters**?

- “Dog bites man” vs “man bites dog” — same words, opposite meaning
- “I didn’t say he stole the money” — stressing *different* words changes the meaning entirely
- A stock price today depends on yesterday’s price, which depends on the day before
- The word “bank” means something different after “river” vs after “investment”

Neural networks that look at inputs one at a time, independently, **can’t understand any of this**. Sequence models must understand **arrangement** — they need memory.

## RNNs — Adding Memory

**Recurrent Neural Networks (RNNs)** process sequences one step at a time, passing a “memory” forward to the next step — a running state that summarizes everything read so far.

The memory arrows get thinner — by word 5, the RNN has nearly forgotten word 1. And each step **waits for the previous one**, so it’s slow.

## The Bottleneck Problem

The RNN’s flaw, stated precisely: **compressing an entire paragraph into one fixed-size state**.

- Early details compete with later details for the same limited memory — and later usually wins
- Long-range dependencies die: *“The contract, which was drafted in 2019 after months of negotiation between the Munich and Osaka offices, **is void**”* — by the time the RNN reaches “is void,” the subject “contract” has faded
- And the sequential design has an economic cost: step 500 can’t start until step 499 finishes, so you **can’t parallelize** — GPUs, whose entire superpower is doing everything at once, sit half idle

Two fatal flaws: **forgetting** and **waiting**. The fix required abandoning the whole approach.

## “Attention Is All You Need” (2017)

In 2017, Google researchers published arguably the most important AI paper of the decade. The solution to RNNs forgetting and being slow? **Don’t process words one at a time at all.**

They introduced the **Transformer** — built entirely on a mechanism called **attention**, with no recurrence. Every major AI model today — GPT, Claude, Gemini, LLaMA — is a transformer.

## Attention Changes the Question

The RNN asks: *“what should I remember forever?”* — and inevitably remembers wrong.

Attention asks: *“which earlier information matters **for this prediction, right now**?”* — and goes and gets it.

- No compression bottleneck: every word remains available, at full fidelity, at every step
- No fading: word 1 is as reachable as word 499
- No waiting: all words can look at all words **simultaneously** — which is exactly the shape of work GPUs devour

## Attention: Every Word Looks at Every Other Word

What if, instead of passing a fading memory forward, the model could **look at every word at once** and decide which ones matter?

That’s **attention** — each word asks: *“who in this sentence is relevant to me?”*

“creature” attends to “fluffy” and “blue” — they describe it. “forest” attends to “verdant.” Each word **pulls in context** from the words that matter most to it.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/attention)

## Why This Matters: Same Word, Different Meaning

The word “mole” means completely different things depending on context:

- “American shrew **mole**” → a small animal
- “One **mole** of carbon dioxide” → a chemistry unit (6.02 × 10²³)
- “Take a biopsy of the **mole**” → a skin lesion

The embedding for “mole” starts the same in all three sentences. Attention figures out **which meaning** by looking at surrounding words.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/attention)

## Attention Updates Meaning

After attention, the embedding for “mole” has been **pulled toward the right meaning** by its context:

“American shrew” pulls “mole” toward the animal direction. “Carbon dioxide” pulls it toward the chemistry direction. Same starting point, different ending — that’s what attention does.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/attention)

## Under the Hood: Query, Key, Value

How does a word “ask who’s relevant”? Every token plays three roles at once:

- **Query**: what the current token is **looking for** — “I’m a noun, any adjectives around describing me?”
- **Key**: what each available token **offers** — “I’m an adjective, right in front of a noun”
- **Value**: the **information** each token contributes if selected — the actual meaning to pass along

**Tip**

Think of a **library**: your query is the question you walk in with, each book’s key is its catalog card, and its value is the content inside. You match your question against the cards, then read from the books that match best.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/attention)

## Scoring Relevance

Compare a query to every key. Higher compatibility means more attention.

Mechanically, the comparison is a **dot product** — multiply the two vectors and sum. Aligned vectors score high; unrelated ones score near zero. The grid above is every word scoring every other word, all computed **in parallel** in one matrix multiplication. (Now you see why GPUs love this architecture.)

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/attention)

## Softmax Turns Scores into Weights

Raw scores are arbitrary numbers. **Softmax** turns many raw scores into a probability-like distribution that **sums to one**.

- Exponentiate every score, then divide each by the total — big scores dominate, small ones fade toward zero
- The result is a clean set of mixing proportions: *“pay 72% attention to ‘fluffy’, 21% to ‘blue’, 7% to everything else”*
- You met this shape already: it’s the same normalization that turns a model’s outputs into next-word **probabilities**

## Weighted Sum Creates Context

The final step: the current token receives a **custom blend of information** from relevant tokens — each token’s value, weighted by its attention.

Not a lookup of one word — a **weighted mixture** of all relevant ones. That mixture gets added to the token’s embedding, nudging “mole” toward animal, or chemistry, or dermatology. Query → score → softmax → blend: that’s the entire attention mechanism. You’ll compute all four steps by hand in today’s exercise.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/attention)

## Multi-Head Attention: Several Questions at Once

One attention pass asks one kind of question. Real sentences need many asked **simultaneously**:

- One head might track **syntax** — which adjective modifies which noun
- Another tracks **entity reference** — who does “she” refer to, five sentences back?
- Another tracks **position**, another **topic**, another relationships nobody has a name for
- The model **learns the useful decompositions** during training — nobody assigns the heads their jobs

GPT-3 runs **96 heads per layer, across 96 layers** — thousands of learned relationship-detectors running in parallel on every token.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/attention)

## Attention Cost Matters

The price of “every word looks at every other word”: the work grows with the **square** of the length.

- 1,000 tokens → 1M comparisons. 100,000 tokens → **10 billion**. Doubling your document quadruples the compute
- This is *the* engineering and economic constraint behind **context windows** — the caps on how much text a model can consider at once
- It’s why long-context models cost more per request, why providers charge per token, and why “just paste the whole database into the prompt” is not an architecture

**Note**

When we discuss context windows, token economics, and retrieval in Class 5, this quadratic is the physics underneath every pricing table you’ll see.

# Transformers

## The Transformer Block

All the pieces snap together into one repeating unit:

```
tokens → embeddings + positions → attention → feed-forward layer → repeat
```

- **Attention** moves information *between* tokens — “who matters to whom”
- The **feed-forward layer** processes each token individually — digesting what attention gathered
- Stack this block dozens of times: each pass builds richer representations, exactly like the face-recognition layers (edges → textures → parts → faces), but for meaning

## How a Transformer Processes Text

1.  **Text in** — “The cat sat on the”
2.  **Tokenize** — break into pieces: \[The\] \[cat\] \[sat\] \[on\] \[the\]
3.  **Embed** — each token becomes a vector of numbers (its meaning)
4.  **Attend** — every token looks at every other token to understand context
5.  **Predict** — output a probability for each possible next word

## Positional Information Preserves Order

There’s a hole in the design: attention alone sees a **set**, not a sequence.

- Every token attends to every other token symmetrically — so “dog bites man” and “man bites dog” would look **identical**
- We fired the RNN for being slow, but it did know word order for free. Attention needs order added back explicitly
- The fix: **position information** stamped onto each embedding — telling the model whether a token came first, last, or far away, so attention can weigh *where* as well as *what*

## Residual Connections Keep Learning Stable

A detail that made 96-layer networks possible: each block **adds its output to its input**, rather than replacing it.

- Layers **refine an existing representation** instead of repeatedly rebuilding it from scratch — edit the memo, don’t rewrite it
- It also keeps backpropagation healthy: correction signals flow backward through the “shortcut” without fading across dozens of layers (the *vanishing gradient* problem that plagued early deep networks)
- You’ve already seen this: the mole diagram — context is **added** to the original embedding. That plus sign is a residual connection

## Layer Normalization Keeps Values Well Behaved

The unglamorous plumbing: **layer normalization** rescales values at each layer to a standard range.

- Multiply numbers through 96 layers and they explode toward infinity or vanish to zero — training becomes numerically unstable
- LayerNorm is a thermostat between blocks, keeping every layer’s outputs in a healthy range
- No intelligence here, just stability — but without it, the training runs behind GPT and Claude would simply diverge

**Note**

Why mention plumbing at all? Because modern AI is roughly 20% big ideas (attention, scale) and 80% **engineering that makes the big ideas trainable**. Residuals and normalization are why the theoretical architecture became a shippable product.

## Generating Text: One Word at a Time

The model takes the full conversation, predicts **one word**, appends it, and repeats. Every response from ChatGPT, Claude, or Gemini is generated this way — one token at a time, each time looking at everything that came before.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/mini-llm)

## Encoder vs Decoder

The original transformer had two halves:

- **Encoder**: reads the input, compresses it into a dense embedding that captures the core meaning
- **Decoder**: takes that embedding and expands it into an output — word by word
- The original 2017 paper used both (for translation: English in → embedding → Spanish out)

Both halves live on today, separately. **Decoder-only** transformers generate text: prompt → next token → extended prompt → next token. **Encoder-style** transformers understand representations — they power classification, embeddings, and the retrieval systems you’ll build in Class 5.

## Why GPT Uses Only the Decoder

Modern LLMs like GPT and Claude dropped the encoder. Why?

- The model’s knowledge is already **baked into the weights** from pretraining on trillions of tokens. It doesn’t need to re-encode your input from scratch — it already understands language.
- If you retrained all weights on every new input: **(a)** it would be impossibly slow — updating trillions of parameters per token, and **(b)** it would be chaos — each new sentence would overwrite what the model learned from the previous one.
- Instead, the weights are **frozen after training**. The decoder just generates the next token using what it already knows + your prompt as context.

**Note**

This is why “prompting” matters so much — you’re not teaching the model anything new. You’re steering a frozen model by giving it the right context to generate from.

# From Transformers to LLMs

## The Scaling Hypothesis

A remarkable discovery: as you increase three things together, performance improves **predictably**:

1.  **More parameters** (bigger model)
2.  **More data** (more text to train on)
3.  **More compute** (more GPUs, longer training)

**Important**

Scaling laws mean you can **predict** how good a model will be *before* you finish training it. This turned AI from alchemy (“try things and hope”) into engineering (“invest X compute, get Y performance”).

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/mini-llm)

## Scaling Laws: Kaplan → Chinchilla

The two papers every AI budget decision traces back to:

- **Kaplan et al., OpenAI 2020** ([*Scaling Laws for Neural Language Models*](https://arxiv.org/abs/2001.08361)): loss falls as a smooth, predictable **power law** in parameters, data, and compute — no ceiling in sight. Read at the time as: *bigger model = better model*. The race to hundreds of billions of parameters followed
- **Hoffmann et al., DeepMind 2022** ([*Training Compute-Optimal LLMs*](https://arxiv.org/abs/2203.15556) — the “Chinchilla” paper): the field had it half wrong. Most giant models were **undertrained** — too many parameters, too little data. For a fixed compute budget, scale parameters and training tokens **together** (~20 tokens per parameter)
- The proof: Chinchilla (70B parameters, 1.4T tokens) **beat** Gopher (280B parameters) — a model 4× its size — on the same compute budget

**Tip**

The MBA reading: scaling laws are a **capital allocation formula**. Given \$100M of compute, they tell you what to buy — and Chinchilla showed the entire industry had been allocating it wrong. It’s also why **data** became the scarce strategic asset: parameters are purchasable, trillions of high-quality tokens are not.

## Scaling Laws — Visually: Chinchilla Beats a Model 4× Its Size

## Pretraining Learns Broad Statistical Structure

The recipe behind every foundation model:

- Take **massive text corpora** — a filtered slice of the internet, books, code
- One task, repeated trillions of times: **predict the missing or next token**
- No labels, no annotators — the text itself is the supervision. Every sentence is a tiny exam with the answer key attached
- Result: surprisingly **general** capabilities — grammar, facts, style, reasoning patterns — from a task nobody would call intelligent

**Note**

Remember the labeling bottleneck from Class 3 — “the biggest cost in ML is labeled data”? Pretraining is the industry-scale workaround: the internet is a **free, pre-labeled dataset** if your task is “guess the next word.” That economic unlock, as much as any architecture, is why language became AI’s center of gravity.

## Transfer Learning — Don’t Start From Scratch

Training a model from zero takes **millions of dollars**. Instead, take a **pretrained model** and **fine-tune** it on your specific task.

- GPT was trained on the entire internet → fine-tune it on your company’s support tickets
- A vision model trained on millions of images → fine-tune it on your X-ray dataset
- This is called **transfer learning** — reuse what the model already knows

**Important**

Transfer learning is how most companies actually use AI today. You don’t train a model — you **adapt** one. This is why foundation models (GPT, Claude, LLaMA) are so valuable: they’re the starting point everyone builds on.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/mini-llm)

## Fine-Tuning and Alignment Shape Behavior

A pretrained model is a text predictor, not an assistant. Two further stages shape behavior:

- **Fine-tuning**: continue training on curated examples — your domain’s documents, or demonstrations of helpful question-answering
- **Alignment** (RLHF — reinforcement learning from human feedback): humans rank the model’s answers; RL — the same reward-driven learning from Class 3’s Grid World and Pac-Man — nudges the model toward answers people prefer
- These make a base model more **helpful, safe, or specialized** — but they do not make it omniscient. Tuning shapes *how* it answers, not *what is true*

**Note**

Class 5 opens with exactly this journey — base model → assistant — including what alignment costs, what it fixes, and the strange failure modes it leaves behind.

## GPT — Predict the Next Word, at Scale

**GPT** (Generative Pre-trained Transformer) has one training objective: **predict the next token**.

Given “The cat sat on the,” predict “mat.” That’s it — billions of times, on billions of documents.

From this simple objective, the model learns grammar, facts, reasoning, and coding — all as a side effect of getting better at prediction.

**Note**

GPT-1 (2018) had 117 million parameters. GPT-5 (2025) has an estimated 5 **trillion**. Same idea, 40,000x bigger — and the results went from “interesting toy” to “writes better than most humans.”

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/mini-llm)

## Not Just Words — Real Knowledge

“Michael Jordan plays the sport of \_\_\_” → **basketball** (80%).

This isn’t just word patterns — at scale, the model learns **real facts about the world**. It knows Michael Jordan plays basketball, that Paris is in France, that water boils at 100°C. All from predicting the next word, billions of times.

Image: [3Blue1Brown](https://www.3blue1brown.com/lessons/gpt)

## Beyond Text: The Same Machine, More Senses

Nothing in the transformer is specific to language. Attention operates on **sequences of vectors** — and almost anything can be turned into vectors.

- **Images** → cut into patches, each patch becomes a token (this is a Vision Transformer)
- **Audio** → slice into short frames, each frame becomes a token
- **Video** → patches across time
- **Text** → the tokens you already know

Train one model on several of these at once and the representations land in a **shared space**: a photo of a dog and the words “a dog” end up near each other. That is why you can paste a screenshot and ask a question about it, or describe an image and have one generated.

**Note**

The business consequence: multimodality is not a separate product line built by a different team. It is the same architecture, fed more kinds of tokens. Every capability you learn to reason about for text — context limits, hallucination, cost per token — applies to images and audio too, usually at a **higher** token cost. A single high-resolution image can cost more tokens than a page of text.

## Emergent Capabilities

Something unexpected happens as models scale: they develop abilities **never explicitly trained on**.

- **Few-shot learning** — give it a few examples in the prompt and it infers the task. GPT-3 went from 76% to 86% accuracy on a reading comprehension benchmark just by showing it a handful of examples — no retraining.
  - *“Scaling up language models greatly improves task-agnostic, few-shot performance”* — [Brown et al., NeurIPS 2020](https://arxiv.org/abs/2005.14165)
- **Chain-of-thought reasoning** — say “think step by step” and it solves multi-step problems. On a math benchmark (GSM8K), accuracy jumped from 18% to 58% — just by changing the prompt. This only works above ~100B parameters. Smaller models show no benefit.
  - *“Chain-of-thought prompting elicits reasoning in large language models”* — [Wei et al., 2022](https://arxiv.org/abs/2201.11903)
- **Code generation** — GPT-4 was asked to draw a unicorn in TikZ (LaTeX). It had never seen “draw a unicorn in code” — but it combined knowledge of geometry, LaTeX syntax, and what unicorns look like into working code. Researchers could even ask it to fix the horn placement.
  - *“GPT-4 can solve novel tasks that span mathematics, coding, vision, medicine, law”* — [Bubeck et al., Microsoft Research, 2023](https://arxiv.org/abs/2303.12712)
- **Translation between unseen pairs** — a model trained on English↔︎Portuguese and English↔︎Russian could translate Portuguese↔︎Russian directly — a pair it never saw — by mapping both languages into a shared embedding space.
  - *“Decoupled vocabulary learning enables zero-shot translation from unseen languages”* — [ACL 2024](https://arxiv.org/abs/2408.02290)

None of these were in the training objective. The model was only trained to **predict the next word**.

## Scale Unlocks Capabilities — and Costs

The same dial that buys emergent abilities runs both directions:

- More data, parameters, compute, and inference-time reasoning can improve tasks…
- …while raising **latency** (bigger models answer slower), **price** (per-token costs compound at scale), **energy use** (training runs measured in megawatts), and **governance needs** (more capability = more ways to misuse)
- The frontier model is rarely the right business answer — often a smaller, cheaper, faster model does the job at a tenth the cost

**Tip**

“Which model should we use?” is a **procurement question, not a leaderboard question**: what accuracy do you need, at what latency, at what cost per call, under what compliance constraints? Class 5 gives you the decision framework.

## A Fluent Answer Is Still a Prediction

After everything today, hold onto the deflationary truth:

The model optimizes **likely continuations**, not a direct internal truth database.

- When the likely continuation is true (Michael Jordan → basketball), the model looks brilliant
- When a *false* statement is the most statistically plausible continuation — a fake citation formatted perfectly, a confident wrong date — the model produces it with the **same fluent confidence**
- That’s a **hallucination**, and it isn’t a bug being patched out — it’s the objective doing exactly what it was trained to do

**Important**

This is why grounding and evaluation matter next class: you’ll learn to give models **retrieved facts to lean on** (RAG) and to measure when to trust them. Fluency is not evidence.

## The Current Landscape

| Family | Company | Where it tends to be strong |
|----|----|----|
| GPT | OpenAI | Broad general use, huge ecosystem, multimodal |
| Claude | Anthropic | Coding and agents, long context, safety focus |
| Gemini | Google | Multimodal, very long context, Google integration |
| Llama | Meta | Open-weight, run it yourself |
| Mistral | Mistral AI | Efficient open-weight, EU data residency |
| DeepSeek / Qwen | DeepSeek, Alibaba | Open-weight, strong price-performance |

**Warning**

**Deliberately no version numbers here.** Every one of these families ships a new flagship every few months, and the leaderboard order changes with it. Memorizing “which model is best” is a wasting asset; knowing **how to run the comparison** is the durable skill. Check a live leaderboard — [Artificial Analysis](https://artificialanalysis.ai/), [LMArena](https://lmarena.ai/) — the week you actually need to choose, and evaluate on *your* task (Class 6).

**Note**

Richard Sutton’s “The Bitter Lesson” (2019) argues: the history of AI shows that **general methods that scale with compute ultimately win** over methods that try to encode human knowledge. Transformers + scale are the latest proof.

# See It Work: The Building Blocks of a Language Model

## Try It: Next-Word Probabilities

Step 1 of how a language model works — given previous words, what are the **probabilities** for the next word?

## Try It: Attention Scores

Step 2 — **attention**. Each word builds an embedding from the corpus. To predict the next word, we compute how much each context word “attends to” every other word.

**Note**

Real transformers do exactly this — but with learned embeddings (not co-occurrence), 96 attention heads running in parallel, and billions of parameters. The mechanism is the same: **query the context, score relevance, focus on what matters**.

# Exercise: Make Attention Concrete

## Your Turn — Build Attention By Hand

You just watched attention run on a real corpus. Now build the mechanism yourself, from three vectors up — query, score, softmax, blend. If you can do it with 2 dimensions, you understand what GPT does with 12,288.

## Build a Tiny Similarity Function

The query is what our current token is looking for. Each key is what a context token offers. The dot product scores their compatibility — exactly the grid from the 3Blue1Brown slide, at miniature scale.

## Turn Scores into Attention Weights

That’s softmax — raw scores in, a distribution summing to one out. Notice how the strongest score grabbed most of the weight but didn’t take *all* of it.

## Add Values and Make a Context Vector

Each token contributes its value in proportion to its attention weight. The output is a **blend** — mostly the first token’s information, seasoned with the others.

## Change the Query

Try `query = np.array([0.0, 1.0])`. Which token gets the most attention now, and how does the context vector change?

Same keys, same values, different question → completely different answer. That’s the whole trick: **what gets retrieved depends on what’s being asked** — per token, per layer, billions of times per response.

## Explain It in Plain English

Write three sentences: what the query wanted, which value mattered most, and why the output is a blend rather than a single lookup.

**Tip**

If you can write those three sentences, you can explain the core mechanism of every frontier AI model to a board. Very few people in the room will be able to say the same.

## Definition of Done

- Your code produces scores, weights, and a context vector.
- Changing the query changes the weights.
- You can connect the toy example to a sentence in an LLM.

# Assignment 3: Train Your Own Small Language Model

## Build a GPT From Scratch

**Important**

**Write a transformer from scratch and train it into a working language model** — every component on today’s slides, as code you can point at, on a corpus you choose.

- Implement a **character-level GPT** in PyTorch: embeddings, positional encoding, multi-head causal self-attention, residual connections, LayerNorm
- **Auto-detect your hardware** — Apple Silicon (MPS), NVIDIA GPU (CUDA), or CPU — the same `device.py` pattern as Pac-Man
- Train on **any plain-text corpus you pick**, ~100KB to 2MB
- At fixed steps, **write a text sample to disk** — so `samples/` becomes a timeline of the model learning English
- Plot train vs validation loss and read the gap
- No cloud, no API key — **runs entirely on your laptop**

Last week you trained an agent to *act*. This week you train a model to *speak* — and the whole thing is about 200 lines of code you wrote.

## This Is What Step 0 Looks Like

Before any training, the model samples characters at random from its vocabulary. This is what a transformer with random weights “writes”:

    WtjV'V$
    -iD ;VqC',S:DHIc:SixyeFh3LCCtda-CFugTrsvKKM,nDHDkR M;vXokvHR?mP
    zAVryEPPzqPcJ mzWUNV:HT3g-IJclY.IgfC'Vj;V hCmLE.Nqxo

By step 5000, the same model — same architecture, same code, only the weights changed — writes lines with words, punctuation, and dialogue structure. Your job: make that happen, and keep the receipts.

## Setup

``` bash
mkdir tiny-gpt
cd tiny-gpt

# Pick one:
claude --dangerously-skip-permissions   # Claude Code
codex --yolo                            # OpenAI Codex
```

**Note**

**Requires Python 3.10+.** No dataset download, no API key, no account — just PyTorch and a text file.

**Installing PyTorch for your platform**

- **macOS (Apple Silicon):** `pip install torch` — MPS support is built-in since PyTorch 2.0
- **Linux (NVIDIA GPU):** `pip install torch --index-url https://download.pytorch.org/whl/cu121`
- **Windows / CPU:** `pip install torch`

Same install as Pac-Man. If you already have it, you’re ready.

## Pick Your Corpus

The model learns the statistics of whatever text you give it. Choose something you will recognize in the output:

- **Tiny Shakespeare** (~1.1MB, the default) — every line of dialogue in the plays, and the standard benchmark for this exact build
- **A public-domain book** from Project Gutenberg — pick an author with a voice you know
- **Your own writing** — essays, notes, emails you have exported
- **Transcripts** — earnings calls, podcasts, or interview notes in your industry

Aim for **100KB–2MB of plain text**. Below that it memorizes; far above it and you will not finish training tonight.

**Warning**

Use a corpus you can inspect and are free to use. **No confidential, proprietary, or personal data** — same rule as the Knowledge Hub in Class 5.

## The Prompt

Paste this into Claude Code (click **Copy** then paste):

Copy

/plan Build a small GPT language model from scratch and train it.\
Use Python and PyTorch only — no Hugging Face, no pretrained\
weights, no transformers library. The point is that every part of\
the architecture is written out in our own code. This runs locally\
on the student's laptop.\
\
Stack:\
- PyTorch (detect and use best available device)\
- matplotlib for the loss curves\
- requests (only to download the default corpus)\
\
The project should have these files:\
\
1. device.py — Device detection module:\
   - Detect OS via platform.system() (macOS, Linux, Windows)\
   - Detect best torch device: CUDA (NVIDIA GPU) → MPS (Apple\
     Silicon) → CPU\
   - Print a startup banner: OS, device type, torch version\
   - Export a DEVICE variable used by all other modules\
   - If only CPU is available, print a warning recommending the\
     small config (see config.py)\
\
2. config.py — All hyperparameters in one place, with two presets:\
   - DEFAULT (GPU/MPS): n_layer=6, n_head=6, n_embd=384,\
     block_size=256, batch_size=64, lr=3e-4, dropout=0.2,\
     max_steps=5000   (~10M parameters)\
   - SMALL (CPU): n_layer=4, n_head=4, n_embd=128,\
     block_size=128, batch_size=32, lr=3e-4, dropout=0.1,\
     max_steps=3000\
   - Select via a --config flag, defaulting to DEFAULT when a\
     GPU or MPS device is detected and SMALL otherwise\
   - Print the resulting parameter count at startup\
\
3. data.py — Corpus handling:\
   - Load a plain-text file from data/input.txt\
   - If it is missing, download Tiny Shakespeare into it\
   - Build the character vocabulary (sorted set of characters)\
   - encode(str) -\> list\[int\] and decode(list\[int\]) -\> str\
   - 90/10 train/validation split\
   - get_batch(split) returning random (x, y) tensors of shape\
     (batch_size, block_size) on the detected device\
\
4. model.py — The GPT itself, written out explicitly. Do NOT use\
   nn.Transformer or nn.MultiheadAttention — implement these:\
   - Token embedding table (vocab_size, n_embd)\
   - Learned positional embedding table (block_size, n_embd)\
   - Head: linear key/query/value projections, scaled dot-product\
     attention (scores @ / sqrt(head_size)), a causal mask via\
     tril so a position can never see the future, softmax, dropout,\
     weighted sum of values\
   - MultiHeadAttention: n_head heads in parallel, concatenated,\
     then a projection\
   - FeedForward: Linear(n_embd, 4\*n_embd) -\> ReLU -\>\
     Linear(4\*n_embd, n_embd) -\> dropout\
   - Block: x = x + attention(layernorm(x)); x = x + ffwd(layernorm(x))\
     — keep the residual additions on their own lines with a comment\
     naming them, and use pre-norm LayerNorm\
   - GPT: embeddings -\> n_layer Blocks -\> final LayerNorm -\>\
     Linear to vocab logits; cross-entropy loss when targets given\
   - generate(idx, max_new_tokens, temperature=1.0): crop context\
     to block_size, take the last position's logits, divide by\
     temperature, softmax, multinomial sample, append, repeat\
\
5. train.py — Training loop:\
   - Print the device banner and parameter count at startup\
   - AdamW optimizer\
   - Every eval_interval steps, estimate mean train AND validation\
     loss over several batches (model.eval() / model.train())\
     and append both to a history list\
   - BEFORE the first optimizer step, write a sample from the\
     UNTRAINED model to samples/step_0000.txt so the student sees\
     pure noise first\
   - Write a 500-character sample to samples/step_XXXX.txt at\
     steps 0, 500, 2000, and max_steps\
   - Save checkpoints to checkpoints/ (model state, config, vocab)\
   - Save the loss history to a JSON file for plot.py\
   - On Ctrl+C: save a checkpoint, write a final sample, exit cleanly\
\
6. generate.py — Load a checkpoint and write new text:\
   - --checkpoint, --tokens (default 1000), and --temperature\
     (default 0.8) flags\
   - Print the sample to stdout\
   - Include a --compare flag that prints the same prompt sampled\
     at temperature 0.2, 0.8, and 1.5 side by side\
\
7. plot.py — Save training_curves.png:\
   - Train loss and validation loss on the same axes vs step\
   - Annotate the step where validation loss stops improving,\
     if it does\
\
Include requirements.txt.\
Include README.md with:\
- Platform-specific install instructions\
- How to swap in your own corpus (drop a .txt at data/input.txt)\
- How to train: python train.py\
- How to generate: python generate.py --temperature 0.8\
- How to plot: python plot.py\
- Expected sample quality at each checkpoint\
- Estimated training times by device\
\
IMPORTANT: model.py must be readable line by line — a student\
should be able to point at the attention computation, the\
positional embedding, and a residual connection. Add short\
comments naming each one. The samples/ folder is the key\
deliverable: it is the model learning to write, on disk.\

## What to Expect

**Training times by device**

| Device                  | Config                | Estimated time |
|-------------------------|-----------------------|----------------|
| **NVIDIA GPU (CUDA)**   | default (~10M params) | ~10–15 minutes |
| **Apple Silicon (MPS)** | default (~10M params) | ~20–35 minutes |
| **CPU only**            | small (~1M params)    | ~30–60 minutes |

What lands in `samples/` along the way:

- **Step 0:** Pure noise. Random characters, random spacing.
- **Step 500:** Spacing and line breaks are already right. Common short words appear — *the, and, is* — while longer words are still garbled.
- **Step 2000:** Most words are real and correctly spelled. Speaker names and punctuation land in plausible places.
- **Step 5000:** Lines with structure — sentences that nearly parse, and dialogue that looks like the source.

**Note**

**Why this matters:** Nobody taught it spelling, or that a space follows a period, or that `ROMEO:` starts a line. It learned all of it from **next-character prediction alone** — the scaling hypothesis from earlier today, at a scale you can watch on a laptop. GPT-4 is this file with more layers, more data, and a hundred million dollars of compute.

## Definition of Done

- **Samples from at least three checkpoints**, showing the progression from noise to structure
- **`training_curves.png`**, plus one sentence on whether train and validation loss diverged — and what that told you
- You can **point at the lines in `model.py`** that are the attention computation, the positional embedding, and a residual connection
- You can explain, in plain English, **why long words are still garbled at step 500** when short ones are already correct
- You can say what changed when you moved the **temperature** dial, and why

## Go Further — Optional, Ungraded

Two experiments if you want to keep pulling the thread:

- **Swap the tokenizer.** Replace characters with the BPE vocabulary from earlier today. Same step count, bigger vocabulary, much longer effective context — compare the samples.
- **Sketch the scaling law.** Train the small config and the default config on the same corpus, then plot final validation loss against parameter count. Two points is not a law, but it is the same curve Kaplan and Chinchilla drew.

## Submit Your Assignment

**[→ Submit your homework](https://submissions-portal-eight.vercel.app)** — sign in with GitHub, submit your GitHub repo URL. Include your `samples/` timeline and your `training_curves.png`.

## Thank You & What’s Next

Thank you for being here — giving up your personal time to learn this. It matters, and it will pay off.

You now have the full picture of **how** these models work — neurons, backprop, embeddings, attention, transformers, scale — and by next week you will have **built one**. Next class we stop studying the machinery and start **using** it, at the other end of the scale: why prompts work, why they fail, how context windows behave, and how retrieval gives a model grounded information it can actually cite. That `--temperature` flag in your `generate.py` is where we pick up.

**[Next: Class 5 — LLM Behavior, Prompting & Retrieval →](https://haas-ai-classes-fall-26.vercel.app/class5.html)**
