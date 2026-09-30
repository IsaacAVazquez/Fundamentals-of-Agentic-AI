---
title: Model Performance and Results
aliases:
  - model-performance-and-results
topic: Projects
summary: Compares results from different training runs and evaluates model performance.
sources:
  - raw/Custom LLM README.md
source_id: custom-llm-readme
source_sha256: 0293ff499fdd970bee6aeb0310c48a81919cb8028af1272b13bf71c8ae71110e
sections_used:
  - What happened
  - The starter run
  - The teaching material I added
  - The corpus-extension run
  - The optional 6,000-step run
  - The 48 evals across all four result sets
  - Coverage and what changed for which reason
  - Actual continuations
  - What the scores do and do not show
  - Rerunning the evals on the saved models
  - Keeping the tests out of training
created: 2026-09-30
updated: 2026-09-30
reviewed: true
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: custom-llm-readme/model-performance-and-results
plan_origin: model-retry
---
# Model Performance and Results

## Summary

This note details the model's performance across several training stages, including a starter run and a corpus-extension run. The main point is that by systematically adding targeted teaching material—such as grammar, opposites, negation, and reference—the model's performance on specific skills improved, as demonstrated by changes in generated samples and loss curves.

## Details

### The starter run
The notebook generated 6,360 classroom sentences, withheld the 160 that contain one of the 16 reserved test prefixes, removed 1,608 duplicates, and kept 4,592 unique passages, which it split into 4,132 for training and 460 held out. The vocabulary built from the training passages has 133 word and punctuation types plus the three special tokens, 136 in all, so nothing hit the 509-type cap and both unknown-token rates were 0%. The network has 111,872 parameters. The manifest and vocabulary report are `results/starter/corpus_manifest.json` and `results/starter/vocabulary_report.json`.

| Step | Training panel loss | Validation panel loss |
| --- | --- | --- |
| 0 | 4.9263 | 4.9275 |
| 1,500 | 0.6821 | 0.7182 |
| 3,000 | 0.6783 | 0.7061 |

These are the fixed panels the notebook draws once, 20 training documents and 20 validation documents, and the loss is the mean over every non-padding next-token target in the panel, so they are estimates from 40 passages and the loss over the whole corpus could differ. The table is `results/starter/history.json` and the plot is `results/starter/training_curves.svg`.

The samples below are the four sentences the notebook draws at each checkpoint with the same starting token, sampling seed, and temperature of 0.8, from `results/starter/samples/`. Before training they are word salad, and by the halfway point every sample is a well-formed classroom frame. Two of the four halfway lines survived unchanged to the end and the other two turned into different frames, so the halfway and final models are different, but both had already learned the templates, which is what I expected.

On the 48 tests the untrained model got 9 of 48 and the trained model got 20 of 48, all 16 starter patterns and 4 of the 8 new phrasings, with all 24 extension cases unscorable in both stages because their words were missing. The trained model's weights hash to `bf49f05b14d5...`, the same value the course's published reference run reports for its final model, and the untrained model's hash matches the reference's untrained model too, so this run reproduced the course's measured run weight for weight.

### The teaching material I added
I chose four skills to teach: grammar, opposites, negation, and reference, because they are teachable with short sentences and because they sit at different distances from what the starter corpus already does. Grammar is agreement, a local pattern between neighboring words, which is the kind of thing a next-word model picks up first. Opposites is a word association like the starter's own domain associations. Negation and reference need the model to reach back across a sentence boundary and copy a specific earlier word, which is the thing attention is for, and reference also needs it to tell the two people in a story apart.

Adding the files took the corpus to 6,807 unique passages, 4,592 from the classroom and 2,215 from the files, split 6,126 to 681, and the vocabulary to 424 types plus the three special tokens, 427 in all, still under the cap with 0% unknown tokens in both splits. The network grew to 130,496 parameters because the tied embedding table has more rows. The manifest and vocabulary report are `results/expanded/corpus_manifest.json` and `results/expanded/vocabulary_report.json`.

### The corpus-extension run
| Step | Training panel loss | Validation panel loss |
| --- | --- | --- |
| 0 | 6.0635 | 6.0459 |
| 1,500 | 0.8536 | 1.0449 |
| 3,000 | 0.8140 | 0.9557 |

Same fixed panels of 20 documents each, drawn from this run's split, so these numbers are not comparable to the starter run's, and the brief says as much about different corpora. The starting loss is again about the log of the vocabulary size, which is 6.06 for 427 words. The validation panel ended about 0.14 above the training panel, 0.9557 against 0.8140. The table is `results/expanded/history.json` and the plot is `results/expanded/training_curves.svg`.

- Assignment Model Training Overview: This note compares results from different training runs and evaluates model performance.
- Model Learning Mechanics Explained: This section details the specific skills taught (grammar, opposites, negation, and reference) and how they were implemented in the corpus.

## Related

- [[Assignment Model Training Overview]]: These sections detail the results of the training described here

## Sources

- [[wiki/Sources/Custom LLM README|Custom LLM README]]: `raw/Custom LLM README.md`, sections "What happened", "The starter run", "The teaching material I added", "The corpus-extension run", "The optional 6,000-step run", "The 48 evals across all four result sets" and more
