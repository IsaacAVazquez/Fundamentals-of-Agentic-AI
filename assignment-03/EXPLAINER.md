# What this notebook is doing

This is a plain-language walkthrough of the tiny language model in this folder. The README is the graded document and holds the settings, the results, the eval tables, and the explanation. This file is for anyone who opens `custom_llm.ipynb` and wants to know what each part does, including people who haven't trained a language model before.

The short version is that a small neural network reads thousands of short sentences and, for every word in every sentence, tries to guess the next word. Each time it guesses wrong, its numbers get nudged so that the right word would have been a little more likely. Nobody gives it grammar, definitions, or labels. All it ever sees is which words follow which, and after a few thousand rounds of nudging it can finish sentences that look like the ones it read.

## The idea behind a language model

A language model is a machine that assigns a probability to every possible next word. Give it `the customer` and it produces one number for each of the few hundred words it knows, and those numbers add up to one. Training is the process of making those numbers match the text, so that after `the customer` the verbs that follow a shopper in the training sentences get most of the probability and words like mango get almost none. Generating text is drawing a word from those probabilities, appending it, and asking again.

The network is Andrej Karpathy's nanoGPT, a small transformer, and the course pins the exact source file. It has two blocks, four attention heads, 64-number word vectors, and a 48-token memory, and it comes to about 130,000 numbers once the vocabulary is in place. That is thousands of times smaller than a chat assistant, which is the point, since every piece of it can be printed and inspected.

## What the model reads

The notebook builds most of its training text itself, from eight groups of related words and nine sentence frames, which gives about 4,600 different sentences about customers and stores, loans and banks, fruit and kitchens, and so on. It then adds any text files placed in `corpus/`, and my four files add another 2,208 short passages about grammar, opposites, corrections, and who gave what to whom.

Before anything else happens, the notebook removes every generated sentence that contains one of the 16 test prompts it has reserved for the evals, throws away duplicates, and holds 10% of the passages out as validation text the network never trains on. It then builds the vocabulary from the training passages alone, keeping at most 509 word types, and reports how many words in each split fell outside that list.

## What each piece of the notebook does

| Section | What it does |
| --- | --- |
| 1, the three choices | The corpus mode, the corpus folder, the training steps, and the learning rate, which are the only values a student changes |
| 2, setup | Downloads and hash-checks the eval files and the nanoGPT source if they're missing, fixes the seed, and picks the CPU |
| 3, the corpus | Generates the classroom sentences, imports the files, withholds the reserved test sentences, deduplicates, and splits |
| 4, tokens and IDs | Builds the vocabulary, turns one example passage into numbers, and writes the unknown-word rates |
| 5, the network | Builds the model, prints the embedding table's shape, and shows one word's 64 starting numbers |
| 6, the baseline | Measures the untrained loss on two fixed panels of 20 passages, writes the first samples, and saves the untrained probabilities |
| 6b, evals before | Runs all 48 fixed tests on the untrained model |
| 7, training | The loop described below, with the first gradient and weight update saved |
| 8, inspection | The same word's numbers after training, the same prefix's probabilities, one attention head's weights, and samples at three temperatures |
| 8b, evals after | The same 48 tests on the trained model |
| 9, saving | Writes the config, the model, the viewer checkpoint, the loss table, the plot, and the results ZIP |
| 10, chat | One prompt and reply from the model just trained, appended to a transcript |
| 11, explanation | The questions the student answers in their own words |

## The training loop in detail

Each step draws 32 training passages at random, turns each one into a list of IDs with a start token in front and an end token at the back, and lines them up in a batch. The network reads every position at once and, for each position, produces its probabilities for the next word. The loss is how surprised it was by the words that actually came next, averaged across the batch, and it starts near the log of the vocabulary size because a random network is equally surprised by everything.

PyTorch then works backward from that loss and computes, for every one of the 130,000 numbers, which direction would have made the loss a little smaller. That list of directions is the gradient. The AdamW optimizer moves each number a small distance in its direction, where the distance is set by the learning rate, which ramps up over the first 100 steps and then follows a cosine curve down to a tenth of its starting value. The notebook saves the very first of those moves for one coordinate of one word, so the README can show a real value, gradient, and update. At the halfway point and at the end, it re-measures the loss on the two fixed panels and writes four fresh samples, which is how the sample timeline and the loss table come to exist.

The network's structure is what makes the guessing work. Each token's vector is added to a vector for its position, and then attention lets each position look back at the earlier positions and mix in what it finds there, with a mask that stops it from looking ahead. That is how the model can finish `leo lent a book to maya . maya thanked` with leo, a name from the first sentence. A small feed-forward layer follows, and the two blocks are stacked. Nothing in the loop is specific to English or to sentences, and the same code would learn any sequence of symbols.

## How the before-and-after comparison is kept fair

The same two panels of 20 passages, drawn once with a fixed seed, are used for every loss measurement. The samples use the same starting token, sampling seed, and temperature at every checkpoint, and the temperature comparison changes only the temperature. The 48 tests are the same before and after training and in both experiments, and the runner only ever sends the prompt into the model, never the four choices or the answer, then compares the probabilities of the four choice words afterward. A test whose words the model has never seen is marked unscorable and counts as zero, so there is no guessing on those.

The tests themselves live in `evals/`, and the only training input is `corpus/`. The notebook refuses to import a file that contains a test prompt, and my generator refuses to write one, so no test question reaches training word for word. The teaching files do reuse the tests' sentence frames with other names and objects, and the opposites file teaches the same word pairs the tests ask about, which the README lays out under Keeping the tests out of training.

## The files I added

The notebook and `custom_llm.py`, `nanogpt_model.py`, `run_evals.py`, `chat.py`, `evals/`, and the viewer come from the course. Everything below is mine.

| File | What it does |
| --- | --- |
| `scripts/setup.sh` | Builds `.venv` on Python 3.13 and installs the requirements plus the pieces a scripted run needs |
| `scripts/run_experiment.sh` | Writes the three choices into the notebook and executes it from the top without opening Jupyter |
| `scripts/make_teaching_corpus.py` | Generates the four teaching files from word lists and sentence frames, with its own leakage checks |
| `scripts/publish_run.sh` | Copies a finished run folder and the executed notebook into `results/` |
| `scripts/neighbors.py` | Finds each chosen word's nearest words before and after training by cosine similarity |
| `scripts/probe_model.py` | Scores seventeen extra prompts of mine on a saved model, to check whether a passing test came from the pattern or from a shortcut |
| `scripts/chat_demo.py` | Runs the course's `chat.py` in a pseudo-terminal, types the prompts, and saves what the screen showed |
| `scripts/render_session.py` | Draws a saved chat session log as an image |
| `corpus/` | The four teaching files |
| `results/` | The published evidence from the starter run, the corpus-extension run, the optional 6,000-step run, the setup check, the eval reruns, and the chat sessions |

The generator is deterministic, so running it again produces the same four files, and the notebook run script reproduces the same weights on this machine, which is the only reason to trust a number in the README that isn't linked to a file.

## Where the results are explained

The README covers what actually happened, including the two negation tests the corpus-extension model got wrong, the probes that showed which passes came from shortcuts, and the optional run that fixed them by training twice as long. This file stops at what the code does.
