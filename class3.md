# Class 3: Machine Learning Foundations

Source: https://haas-ai-classes-fall-26.vercel.app/class3.html

### A quick recap

LAST CLASS

#### Building software with AI

We used AI to turn an idea into working software.

THIS CLASS

#### Understanding how AI works

We’ll learn how models learn from data and make predictions.

![Vibe coding meme showing a person expecting to direct AI, then becoming overwhelmed while the AI systems take charge](https://haas-ai-classes-fall-26.vercel.app/diagrams/class3-vibe-coding-recap.png)

---

## Why This Class?

### Industry Expectations for MBAs Have Changed

Business roles increasingly connect **product, strategy, data, and technical execution**.

- Evaluating an AI proposal means understanding what the model learns, what data it needs, and how its performance is measured.
- Building an in-house model involves choices about labels, costs, errors, and deployment. Those are management decisions too.
- When someone says “the model is overfitting,” you should be able to ask the next useful question.

**The goal is technical fluency:** enough understanding to make decisions about AI, including when to use something simpler.

### Big Tech Now *Requires* AI/ML

![Original course examples of AI and ML expectations in big-tech MBA internship postings](https://haas-ai-classes-fall-26.vercel.app/diagrams/internship-frontline.png)

Examples collected for the course from 2025–26 internship postings.

### Not Just Tech: Finance, Consulting, Healthcare Too

![Original course examples of AI expectations in finance, consulting, and healthcare internship postings](https://haas-ai-classes-fall-26.vercel.app/diagrams/internship-frontline-2.png)

The same vocabulary appears beyond technology companies.

---

## Why AI Instead of Code?

### Last Class We Wrote the Rules

#### Software

```python
if invoice_is_overdue:
    block_discount()
```

We specify the rule. The app applies it to each customer.

#### Machine learning

```text
past usage + renewal outcomes
            ↓ train
       learned model
            ↓ predict
renewal estimate for a new account
```

We choose the inputs and objective. Training fits the model’s settings.

> **Speaker notes**
>
> Connect to the Class 1 discount calculator and Class 2 database. ML becomes another function the backend can call. Rules can also change and contain bugs; ML is not inherently preferable. Ask students which approach they would use for a sales-tax calculation and for predicting next month’s demand.

### Why Can’t We Just Code All the Rules?

![image](https://haas-ai-classes-fall-26.vercel.app/diagrams/chessboard.jpg)

Chess has simple rules. A finite board. A finite set of pieces. Couldn’t we just program every possible move?

|   | Number | Scale |
| --- | --- | --- |
| **Possible chess games** | 10^120 | a 1 followed by **120** zeros |

| **Atoms in the universe** | 10^80 | a 1 followed by 80 zeros |
| --- | --- | --- |

Chess has **a trillion trillion trillion times** more possible games than there are atoms in the universe.

You cannot brute-force chess. This is why we need AI.

![image](https://haas-ai-classes-fall-26.vercel.app/diagrams/kasparov.gif)

> **Speaker notes**
>
> Preserve the original chess example and Kasparov GIF. Chess is also a useful distinction between AI and ML: search-based systems can play chess without learning a policy from examples. Do not imply that all chess AI is machine learning or that every possible continuation can be exhaustively searched.

### AI Feels Like an Alien Oracle…

![Original SpongeBob AI oracle meme about treating AI as a mysterious source of answers](https://haas-ai-classes-fall-26.vercel.app/diagrams/ai-magic-meme.png)

Underneath: **statistics, linear algebra, and optimization**, running at a scale we could not work through by hand.

### Condensation of Knowledge

A chess grandmaster does not memorize every possible game. They develop **intuition from patterns across many games.**

- A learned model captures useful patterns from its training examples in its **parameters**.
- Those parameters let it make predictions about **new examples**.
- That only helps if the learned patterns still apply when the situation changes.
- **Predicting an outcome does not tell us how to change it:** knowing who might leave does not tell us how to make them stay.

**This is the intuition behind learning:** turn experience into a reusable mathematical model.

![Hand-drawn visual showing many chess games becoming learned patterns that guide a move in a new game](https://haas-ai-classes-fall-26.vercel.app/diagrams/condensation-of-knowledge-handdrawn-v2.png)

> **Speaker notes**
>
> The chess analogy makes the distinction between memorization and learning concrete. A model stores parameter values rather than copies of every training example, although some models can still memorize parts of their training data.

---

## AI Is Older Than You Think

### AI: A 70-Year Journey

![AI history: Dartmouth in 1956 established a research field; AI winters brought funding setbacks; Deep Blue won at chess in 1997; AlexNet advanced image recognition in 2012; the transformer introduced a new attention architecture in 2017; ChatGPT brought conversational AI to a broad public audience in 2022.](https://haas-ai-classes-fall-26.vercel.app/diagrams/ai-history-horizontal.png)

**AI grew through rules, search, and learning, long before chatbots.**

> **Speaker notes**
>
> The AI winters were distinct periods of reduced funding and enthusiasm, particularly in the 1970s and from the late 1980s into the early 1990s, not a continuous decline. Deep Blue beat Garry Kasparov through specialized search and evaluation. AlexNet marked a major image-recognition breakthrough for deep learning. The transformer introduced an attention-based architecture that became central to modern language models. ChatGPT made these capabilities accessible through a conversational interface.

### Scale Became a Driver of AI Progress

- **Earlier AI:** experts often designed rules and features for each task.
- **Modern AI:** designs like transformers can improve with **more data, more compute, and larger models**, without a new algorithm each time.

![More data and more computing power let researchers scale a small neural network into a larger one and improve predictions.](https://haas-ai-classes-fall-26.vercel.app/diagrams/scaling-laws-mba-neural.png)

**Scaling laws help predict how much improvement that extra scale can buy.**

> **Speaker notes**
>
> The point is the change in how progress can be achieved, not a lesson in logarithmic axes. Earlier AI included hand-written rules, search, and statistical learning with manually designed features. Modern neural networks learn features, and transformer-based language models have shown predictable improvements in prediction loss as parameters, data, and training compute scale within studied ranges. Algorithms and architecture breakthroughs still matter; transformers are themselves an important example. The additional source of progress is scaling an existing design, without needing another algorithmic breakthrough at each step. These empirical relationships help researchers estimate the benefit of larger training runs and allocate compute. More scale does not guarantee correctness or business value. Source: Kaplan et al. (2020), https://arxiv.org/abs/2001.08361.

### The AI Landscape

![Five nested colored boxes showing AI, machine learning, deep learning, generative AI, and large language models as a simplified map of modern generative systems.](https://haas-ai-classes-fall-26.vercel.app/diagrams/ai-landscape-nested-icons.png)

Today: **machine learning**. Next class: **deep learning** and transformers.

> **Speaker notes**
>
> This is a simplified map of the modern generative systems discussed in the course, not a universal taxonomy. Machine learning is part of AI, and deep learning is part of machine learning. Modern generative systems predominantly use deep learning; generative models also exist outside it. The innermost box represents the generative LLMs discussed in this course. Language-model-based systems can also be multimodal. Rules, search, and planning belong to AI; NLP spans multiple methods. Source: IBM, https://www.ibm.com/think/topics/ai-vs-machine-learning-vs-deep-learning-vs-neural-networks.

### Today’s Route

| First half | Second half |
| --- | --- |
| AI history, the landscape, and why learning helps | Check whether learning generalizes |
| Define the prediction and prepare data | Compare models and evaluate errors |
| Fit a model by reducing loss | Find clusters without labels |
| **Train a digit classifier in Colab** | Choose actions through reinforcement learning |
|   | **Train a Grid World policy, then start Pac-Man** |

**The question throughout:** what did the model learn, and how would we know?

> **Speaker notes**
>
> Suggested two-hour pacing, adaptable to the room: 15 minutes motivation, AI history and the landscape; 10 data; 10 training; 15 MNIST hands-on; 10 break; 15 generalization and model families; 10 evaluation and threshold exercise; 10 unsupervised learning; 15 RL and Grid World; 10 Pac-Man and Class 4 bridge. Protect the hands-on time. Use local minima as a brief debrief after fitting the line, extrapolation to connect shifted MNIST to generalization, and the test-set and bias/variance visuals to introduce the adjacent validation and complexity slides. Self-study after the close holds extra depth.

### You Already Know the Math Behind AI

Machine learning builds on **statistics, probability, linear algebra, and optimization**.

Your background in **econ, stats, or finance** gives you a foundation for understanding how these models work.

Remember **Data and Decisions**? You have already worked with the core ideas:

| You already know | In machine learning, that’s |
| --- | --- |
| **Probability and distributions** | Describing uncertainty and noise |
| **Linear regression** | A machine learning algorithm you already know |
| **Optimization / minimizing error** | How training finds better model parameters |
| **Sampling and validation** | Checking whether results hold for new data |

**Machine learning is applied math at scale. Your MBA has already introduced the fundamentals.**

> **Speaker notes**
>
> Connect this to the students’ MBA experience rather than presenting AI as a separate technical discipline. Regression in economics, uncertainty in finance, and optimization in business decisions all provide useful intuition. Linear algebra organizes the inputs and model parameters; code lets us run the calculations at scale. Avoid suggesting that programming is irrelevant or that one degree makes someone better equipped than another. The point is that students have an existing mathematical foundation to build on. Adapted from the original course slide: https://haas-ai-classes.vercel.app/class2.html#/its-math-not-computer-science.

### Three Ways a Machine Can Learn

| Learning | What we give it | What it learns | Today’s example |
| --- | --- | --- | --- |
| **Supervised** | Inputs + known answers | Predict an answer | Read a handwritten digit |
| **Unsupervised** | Inputs without answers | Find structure | Group similar customers |
| **Reinforcement** | An environment + rewards | Choose actions over time | Navigate a grid, then Pac-Man |

**Neural networks are a type of model.** They can be used in all three forms of learning. We open them up in Class 4.

> **Speaker notes**
>
> AI is the broader field; ML learns from data or experience; deep learning uses neural networks with multiple layers. Avoid teaching these learning paradigms as nested circles. Reinforcement learning and deep learning are not successive rungs of the same taxonomy.

### Classification, Regression, and Ranking

#### Classification: which category?

![Example of an image classified as hot dog or not hot dog](https://haas-ai-classes-fall-26.vercel.app/diagrams/not-hot-dog.webp)

Spam or not spam. Digit 0 through 9. Churn or stay.

#### Regression: what number?

![A fitted line predicts a numerical outcome from an input](https://haas-ai-classes-fall-26.vercel.app/diagrams/regression-line.png)

Sales next week. Delivery time. House price.

**Ranking** puts candidates in order, such as which leads sales should contact first.

### Labels Are the Answers We Learn From

**Supervised learning** starts with examples paired with known answers.

**Features (\(x\))**

What the model can see: words, links, and sender information.

**Label (\(y\))**

The answer attached to that example: **spam** or **legitimate**.

Labeling can come from **human review** or **recorded outcomes**.

![Hand-drawn emails receive known labels: a free-prize email is labeled spam, while a meeting email is labeled legitimate. A person annotates each example.](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-labeling-emails-handdrawn.png)

**Classification:** learn a category. **Regression:** learn a number, such as a house’s recorded sale price.

For a new example, the answer is unknown. The model makes a **prediction**.

> **Speaker notes**
>
> Each email is one training example. Features are the inputs; the target is the variable we want to predict; the label is its observed value for an example. A human can label an email, while a sale price or renewal outcome can come from business records. Classification labels may be encoded as 0 and 1 without becoming a regression problem. Binary classification has two possible classes; predicting a digit from 0 through 9 is multiclass classification. Agree on labeling rules, review ambiguous cases, distinguish missing values from zero, and check who is missing from the sample. Labels can be noisy. Use only features available at prediction time: for an August 31 renewal prediction, August usage is valid, but a September payment leaks the future. Split before fitting preprocessing, then fit transforms only on training data. Sources: SVM-Introduction-Tanya.pptx, slides 2 and 4–11. Illustration generated for the course.

---

## Training a Model

### A Model Has Adjustable Parameters

\[\text{predicted revenue} = w \times \text{ad spend} + b\]

**The input:** ad spend.

**The parameters:** slope \(w\) and intercept \(b\).

Training chooses parameter values that fit historical examples.

```python
def predict(ad_spend, w, b):
    return w * ad_spend + b
```

Using the fitted model on new inputs is **inference**.

You already know this as **fitting a regression**. ML uses the same idea for many kinds of prediction.

### Loss Measures Prediction Error

Toy revenue data, in **thousands of dollars**:

| Actual revenue | Prediction | Error | Squared error |
| --- | --- | --- | --- |
| 10 | 8 | −2 | 4 |
| 20 | 23 | +3 | 9 |
| 30 | 25 | −5 | 25 |

\[\text{mean squared error} = \frac{4 + 9 + 25}{3} \approx 12.7\]

**Training tries to reduce this average.** Squaring makes large misses count more.

> **Speaker notes**
>
> The loss here is in squared thousands of dollars, not dollars and not percent. A model’s training loss is the objective it fits; a business metric can be different. For classification we will penalize incorrect probabilities instead of numerical distances between class names.

### Training Starts With a Poor Guess

![Original illustrative regression plot: initial line with large residual errors](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-regression-step1.png)

**Start:** the predictions miss most of the observations.

The dashed lines show the gap between predictions and observations. Loss values in this sequence are illustrative.

### Adjusting the Line

![Original illustrative regression plot: updated line with smaller residual errors](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-regression-step2.png)

**Update:** change the slope and intercept to reduce loss.

Loss drops from **847 → 312**. The fit improves, but the predictions still miss the observations.

### Repeated Updates Improve the Fit

![Original illustrative regression plot: a line approaching the data trend](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-regression-step3.png)

**Keep adjusting:** the errors get smaller.

Loss drops from **312 → 58**. The line is getting closer to the data trend.

### The Fit Converges

![Original illustrative regression plot: a converged line fitting the data trend](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-regression-step4.png)

**Converge:** further updates make little difference.

Loss reaches **12**. **That is training:** measure error, adjust parameters, repeat. Next, we will make the updates ourselves.

### Gradient Descent Updates the Parameters

![A parameter moves downhill on a loss curve, with the learning rate controlling step size](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-gradient-descent.png)

**Predict → measure loss → compute the gradient → take a small downhill step → repeat.**

The **gradient** tells us how loss changes with each parameter. The **learning rate** controls the step size.

> **Speaker notes**
>
> For differentiable models, update parameters by subtracting learning rate times gradient. Trees fit splits differently; not every ML algorithm trains by gradient descent. The bowl is a one-parameter sketch. Our linear regression loss is convex, while neural-network loss surfaces can be more complicated.

### Try It: Fit the Line

Change the learning rate, then step through training. Watch the **line, residuals, and loss** change together.

**Try:** reset, select **Too large**, and take a few steps. Explain why more training does not help that run.

### Local Minima

![Original loss landscape comparing a local minimum with a lower global minimum](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-local-minima.png)

**The line we just fitted has a convex loss:** one bowl, with no competing local valleys.

More complicated models can have several valleys. Gradient descent may settle in a **local minimum**; different starting points can lead to different fits.

### Classification Learns Probabilities

For an account that **did renew**, compare three predictions:

| Predicted renewal probability | Cross-entropy loss, \(-\log(p)\) |
| --- | --- |
| 90% | 0.11 |
| 50% | 0.69 |
| 1% | 4.61 |

**A confident wrong answer gets a much larger penalty.** For an account that did not renew, the loss uses \(-\log(1-p)\).

**Logistic regression** turns a weighted sum of features into a probability with a sigmoid. Despite its name, it is used for classification.

> **Speaker notes**
>
> Values rounded using natural logarithms. Minimizing cross-entropy does not guarantee calibrated probabilities on new data. For MNIST, softmax extends the idea to ten class probabilities that sum to one. The actual image classes do not have a meaningful numerical distance from each other.

### Classification Learns a Decision Boundary

Each point is a labeled email. The boundary separates **where the model predicts each class**.

![A straight decision boundary separates blue circles representing legitimate emails from amber triangles representing spam. The inputs are suspicious words and links.](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-classification-boundary-handdrawn.png)

**Binary:** spam or legitimate. **Multiclass:** one of ten handwritten digits, 0 through 9.

**Logistic regression** estimates a class probability. A **threshold** turns it into a label:

70% estimated spam probability + a 50% threshold → **predict spam**.

> **Speaker notes**
>
> The example is illustrative, with deliberately separable points. Boundaries can be straight or curved, depending on the model and features. Numeric features encode an email so it becomes a point in an input space. The coloring represents known labels; the regions represent the model’s predictions, which can disagree with labels on new examples. Binary means two classes; multiclass means one of more than two classes. Multilabel, such as tagging an article both sports and finance, is a separate concept. Class imbalance describes the proportions of the classes, not the number of classes. Despite its name, logistic regression is used for classification: it estimates probabilities, not an unrestricted numeric target like sale price. The 70% and 50% values are a toy example. A threshold of 50% is a choice, not a universal optimum. Sources: SVM-Introduction-Tanya.pptx, slides 5–12; Logistic Regression-Introduction-Tanya-v2.pptx, slides 2, 6, and 12–16; https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression. Illustration generated for the course.

### Training and Inference Use Different Information

|   | During training | During inference |
| --- | --- | --- |
| Inputs | Historical features | Features for a new case |
| Known answers | Labels used to compute loss | Usually unavailable yet |
| Parameters | Updated to reduce loss | Held fixed for prediction |
| Result | A fitted model | A score, category, or number |

An app making a prediction is **not automatically learning from that interaction**. Updating the model requires a training process.

---

## Mid-Class Project: Read Handwritten Digits

### MNIST Turns Pictures Into Training Examples

![Handwritten digit images from MNIST with labels from zero through nine](https://haas-ai-classes-fall-26.vercel.app/diagrams/mnist-samples.png)

**28 × 28 pixels = 784 input features.** Each image has one label: its digit.

The notebook fits ten weighted scores: **784 × 10 weights + 10 biases = 7,850 parameters**.

### Run the Classifier in Colab

**[Open the MNIST notebook →](https://colab.research.google.com/github/pepealonso95/mnist-from-scratch/blob/main/mnist_from_scratch.ipynb)**

Choose **Runtime → Run all**. It runs in your browser; nothing to install.

1. Find the **weights**, **loss**, and **update step** in the code.
2. Record the test accuracy from your run.
3. Inspect three mistakes. What makes those images difficult?
4. Run the shifted-image experiment. Record what changed.

[![Scan to open the MNIST notebook in Google Colab](https://haas-ai-classes-fall-26.vercel.app/diagrams/class3-mnist-colab-qr.png)](https://colab.research.google.com/github/pepealonso95/mnist-from-scratch/blob/main/mnist_from_scratch.ipynb)

**Scan to open the notebook**

**Done:** show one correct prediction, one mistake, and one limitation of the model. This is the in-class learning exercise.

> **Speaker notes**
>
> Allow about 15 minutes across this slide and the debrief. Keep students on the existing notebook. It implements multinomial logistic regression in NumPy, with no hidden layers. The fixed split gives a first evaluation; repeatedly tuning against that test score would compromise it.

### A Small Image Shift Changes the Task

The notebook moves test digits sideways while keeping their labels the same.

| Test input | What changes? | What to record |
| --- | --- | --- |
| Original digit | Same placement as training | Your starting accuracy |
| Shifted 2 pixels | Ink lands on different inputs | New accuracy |
| Shifted 5 pixels | A larger change in position | New accuracy and an example |

The model learned **which pixels predict each digit in the training distribution**. It was not designed to recognize a shape equally well wherever it appears.

**Keep this failure in mind. Class 4 introduces networks that learn useful image features.**

> **Speaker notes**
>
> Use students’ observed results, rather than a universal accuracy or time promise. Shift implementation may also crop strokes near the edge. Distinguish failure under distribution shift from simply memorizing training examples.

### Extrapolation Uses the Model Beyond Its Data

![Regression extrapolates a trend outside the observed training range](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-extrapolation.png)

The shifted digits showed a change in input conditions. **Extrapolation** is a related risk: predicting beyond the observed training range.

A trend for small purchases may not hold for very large ones. Flag inputs outside that range and check performance under new conditions.

---

## Generalization and Model Choice

### Keep a Test Set Outside Development

![Original illustration separating training data from an untouched test set](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-train-test-split.png)

**If we keep changing the model after seeing its test score, that score starts guiding development.** Keep the final test set untouched until our choices are fixed.

Use **validation data** to choose settings. The illustrated 80/20 split is only an example; the split should reflect future deployment.

### Separate Fitting, Choosing, and Testing

| Training data | Validation data | Test data |
| --- | --- | --- |
| Fit weights or tree splits | Choose model, settings, threshold | Estimate final performance |
| Can be revisited during fitting | Can guide development | Keep untouched until choices are fixed |

**For future predictions:** train on older cases, validate on later ones, test on the newest held-out period.

Keep related records together when necessary. The same person’s near-duplicate images in both sets can make the score misleading.

> **Speaker notes**
>
> No universal 80/20/other split ratio. The right split reflects the deployment question: unseen people, unseen places, or future time. Fit preprocessing on training data only. Source: https://scikit-learn.org/stable/modules/cross_validation.html

### Overfitting Fits Noise Along With Signal

![Illustrative comparison of an overfit wiggly curve and a simpler fit, with stronger test performance for the simpler model](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-overfitting.png)

**Underfitting:** the model is too limited to capture the pattern. **Overfitting:** it fits training details that do not carry over.

Compare **training and validation performance**, not just training loss. Numbers in the diagram are illustrative.

### Bias and Variance

![Target diagrams distinguish systematic error from variation across fitted models](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-bias-variance.excalidraw.png)

**Bias:** systematic error from simplifying assumptions. **Variance:** how much the fitted model changes with the training sample.

**Too rigid:** miss the pattern. **Too flexible:** chase the sample. Choose complexity using validation; noise also limits prediction quality.

### Control Complexity, Then Validate

| What you observe | What to investigate |
| --- | --- |
| Poor training and validation results | Weak features, too little capacity, incomplete training |
| Good training, poor validation | Overfitting, leakage, or a mismatched split |
| Good validation, poor live results | Distribution shift or a production data problem |

**Regularization** discourages overly complex fits. Examples: penalize large weights, limit tree depth, or stop training when validation stops improving.

**Parameters** are fitted during training. **Hyperparameters**, such as learning rate and tree depth, are settings we choose using validation.

> **Speaker notes**
>
> These are diagnostic starting points, not proofs. More representative data can help overfitting; more of the same biased data may not. A low training loss alone cannot identify the cause of poor deployment performance.

### K-Nearest Neighbors Takes a Vote

Find the **\(k\) most similar labeled examples**. For classification, let them vote.

![With k equal to five, a new email has three spam triangles and two legitimate circles as its nearest neighbors. The majority vote predicts spam.](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-knn-vote-handdrawn.png)

**\(k = 5\):** three neighbors are spam, two are legitimate → **predict spam**.

“Near” depends on the features and their scale. For **regression**, average the neighbors’ numbers instead.

> **Speaker notes**
>
> KNN stands for k-nearest neighbors. The drawing shows a toy example with uniform voting: each of the five neighbors gets one vote, and all points outside the dashed circle are farther away. Distance-weighted variants give nearer examples more influence. The model keeps training examples available at prediction time; it does not have to fit a single line. Here, similar means close in a chosen feature representation, not geographically nearby. Scale numeric features so large units do not dominate distance, fitting that scaling on training data only. Choose k using validation: small k can follow noise, while large k can blur local distinctions. For a numeric target such as price, a basic KNN regressor averages the neighboring targets. Sources: SVM-Introduction-Tanya.pptx, slides 9–10; https://scikit-learn.org/stable/modules/neighbors.html. Illustration generated for the course.

### Decision Trees Learn a Flowchart

![Decision tree classifies fruit through questions about weight and shape](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-decision-tree.png)

Each **split** asks a question about a feature.

Training chooses questions that separate the observed outcomes.

A **leaf** gives the prediction. For regression, it can give a mean value.

**Deeper trees** fit more detail and can overfit.

### Random Forests Combine Different Trees

![Five trees vote on a fruit classification, with apple winning four votes](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-random-forest.png)

Train trees on resampled data with random feature choices. **Combine their predictions** by voting or averaging.

Different trees make different errors. Combining them can reduce variance, at the cost of a more complicated explanation.

### Features Translate Raw Records Into Signals

| Raw record | Possible feature | Why it might help |
| --- | --- | --- |
| Login timestamps | Days since last activity | Separates active from lapsed use |
| Purchases | Amount ÷ customer’s usual amount | Measures an unusual purchase |
| Income and rent | Rent-to-income ratio | Makes the relationship explicit |

**Compute features using only information available at prediction time.**

For images, what would the equivalent columns be? Edge direction? Loops? Curves? **Learning those representations is the next class.**

### Compare Against a Simple Baseline

| Problem | First comparison | What else to try |
| --- | --- | --- |
| Predict a number | Historical mean or linear regression | Trees and ensembles |
| Predict a category | Majority class or logistic regression | Trees and ensembles |
| Group unlabeled rows | Inspect a scatterplot | Clustering |
| Choose actions over time | Random or hand-written policy | Reinforcement learning |

A more complex model earns its place through **better held-out results at an acceptable cost**.

> **Speaker notes**
>
> No universal model winner. Feature quality, dataset size, latency, interpretability and maintenance all matter. Nearest neighbors and SVMs are in self-study. Images and text motivate neural networks in Class 4.

---

## Evaluating Predictions

### True Positives and False Alarms

First define **positive = spam**. A **confusion matrix** compares predictions with known labels.

| Known label ↓ Prediction → | Predicted spam (+) | Predicted legitimate (−) |
| --- | --- | --- |
| Actually spam (+) | **True positive (TP)**Spam caught. | **False negative (FN)**Spam reaches your inbox. |
| Actually legitimate (−) | **False positive (FP)**Your job offer goes to spam. | **True negative (TN)**Your job offer reaches your inbox. |

**Positive / negative:** what the model predicted. **True / false:** whether it was right.

**Which costs more: a missed spam email or a lost job offer?**

> **Speaker notes**
>
> Read each cell by crossing the known-label row with the prediction column. Positive means the class we chose to detect, not something desirable. A false positive is a false alarm; a false negative is a missed positive. The job offer is an illustrative legitimate email, and the table has no measured counts. For a spam filter, a false positive can hide an important message; for fraud detection, missed positives can carry a different cost. Later, the fraud example will put counts into this same table and derive precision and recall. Source: SVM-Introduction-Tanya.pptx, slides 13–15.

### Accuracy Can Hide the Error You Care About

Toy dataset: **100 transactions, including 5 frauds**.

| Model | Correct predictions | Accuracy | Frauds caught |
| --- | --- | --- | --- |
| Always predict legitimate | 95 | **95%** | **0 of 5** |
| Flag 10, including 4 frauds | 93 | **93%** | **4 of 5** |

The second model catches fraud, but also flags **6 legitimate payments**.

**Which is better depends on the cost of missed fraud and false alarms.**

### Precision and Recall Count Different Mistakes

The same 100 transactions:

|   | Flagged as fraud | Not flagged |
| --- | --- | --- |
| **Actually fraud** | **4** true positives | **1** false negative |
| **Actually legitimate** | **6** false positives | **89** true negatives |

**Precision = 4 / 10 = 40%**

Of the flagged payments, how many really were fraud?

**Recall = 4 / 5 = 80%**

Of the actual frauds, how many did we catch?

> **Speaker notes**
>
> Both denominators refer to the same confusion matrix. Define the positive class before using the terms. Source: https://scikit-learn.org/stable/modules/model_evaluation.html

### Try It: Choose a Renewal Threshold

Predict **renewal** when usage is at or above the threshold. Here, **positive means renewed**.

**Try 4, 6, and 8 days.** Then add the messy account. Explain which mistake your chosen threshold accepts. This exercise is ungraded.

> **Speaker notes**
>
> Allow five minutes. A false positive is an account predicted to renew that actually leaves, possibly missing a chance to intervene. A false negative is an account predicted to leave that would renew anyway, potentially wasting retention effort. Six rows illustrate the calculation; they are not evidence for a production policy. The optional appendix adds cross-validation.

### A Prediction Still Needs a Decision Policy

| Model output | Decision we still have to make |
| --- | --- |
| High estimated churn risk | Call, discount, investigate, or do nothing? |
| High fraud score | Block automatically or route to review? |
| An uncertain case | What context does a reviewer need? |

**Predicting who leaves does not tell us whether a discount will make them stay.** Test the intervention separately.

Check error rates across relevant groups, give reviewers authority to override, and monitor outcomes after launch.

> **Speaker notes**
>
> Correlation is not an intervention effect. A feature can proxy historical exclusion; subgroup evaluation and the source of labels matter. Human review requires enough time and context to change an outcome. Calibration, drift, and decision rights have further examples in self-study.

---

## Unsupervised Learning

### Clustering Finds Groups Without Outcome Labels

**k-means** groups similar points around \(k\) centers, called **centroids**.

1. Start with \(k\) centers.
2. Assign each point to its nearest center.
3. Move each center to the mean of its assigned points. Repeat.

You choose the features, their scales, and \(k\). The algorithm finds a grouping; **you decide whether it is useful**.

### Try It: Watch the Clusters Form

Each point is a synthetic customer. The axes are standardized so both features contribute to distance.

**Try:** compare \(k=2\) with \(k=3\). Does choosing more groups prove more customer segments exist?

### Compression and Anomaly Detection

#### Compression

**PCA** combines correlated columns into fewer dimensions that preserve as much variance as possible.

Useful for plotting and reducing inputs. Preserving variance does not guarantee preserving the signal your task needs.

#### Anomaly detection

Learn typical patterns, then flag unusual cases.

A sudden spending spike might be fraud, or a customer furnishing a house. **Unusual does not mean harmful.**

Without outcome labels, inspecting a neat chart is not enough. Validate the usefulness of the grouping, compression, or alerts.

---

## Reinforcement Learning

### Actions Change What Happens Next

![Agent receives state and reward from an environment and chooses the next action](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-rl-loop.png)

**State:** where the agent is now.

**Action:** a move it chooses.

**Reward:** feedback after acting.

**Policy:** the rule it uses to choose actions.

In supervised learning, we have example answers. In RL, the agent learns a policy from **experience and rewards**.

> **Speaker notes**
>
> The environment provides transitions and reward; the agent does not need to be told the best action in each state. A state is sufficient information for the modeled decision process; in practice an agent may only observe part of it. A neural network is not required for RL, and neural networks are not limited to supervised learning.

### Reward Now Versus Reward Later

**A self-driving taxi can earn more later by driving empty now.**

![Self-driving taxi dispatch example: a nearby pickup earns one reward point now; driving empty toward a busy station earns nothing yet, then ten points later.](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-reward-robotaxi.png)

#### Take a nearby pickup

Earn **+1 now** in this toy example.

#### Head to the busy station

Earn **0 while repositioning**, then **+10 on the next step**.

With a discount factor of **0.9**, that later reward counts as **9 today**. It still beats 1.

**The objective is expected cumulative reward**, not the biggest reward on the next move.

**Credit assignment:** the empty drive helped make the later pickup possible.

Simplified dispatch example with invented reward points.

> **Speaker notes**
>
> This is a hypothetical autonomous-taxi dispatch exercise, not a description of Waymo’s actual training or reward system. Compare two short episodes: the nearby pickup earns +1 and ends the episode; repositioning earns 0, then a station pickup earns +10 and ends the episode. The totals are 1 versus 0 + 0.9 × 10 = 9. The values are invented reward points, not fares. State includes location, demand, time, and other relevant information. Assume both options are feasible and safe; this example isolates timing and omits operating costs. More waiting passengers do not automatically mean a higher-valued fare. In a realistic objective, account for costs, service outcomes, and uncertainty. Discounting weights later rewards less; it is not a 90% probability of success. Ask which earlier action helped produce the delayed outcome to introduce credit assignment.

### Q-Learning Stores a Value for Each Action

**The taxi learns a forecast for each dispatch choice.**

![A self-driving taxi at its current location has two dispatch options on a city map: a nearby pickup with Q equal to 1, or heading toward the station with Q equal to 9.](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-q-learning-robotaxi.png)

#### State: the situation now

Where the taxi is, the time, and nearby demand.

#### Action: what to do next

Take the nearby pickup or head to the station.

#### Q-value: how worthwhile it looks

\(Q(s,a)\) estimates **total discounted reward** from that choice, then following the best-known choices.

**After a move:** adjust its value toward **reward received** + discounted best value at the next state. At the end, there is no future value.

Policy: choose the highest value, except when exploring. Here, head to the station. A Q-table needs no neural network.

Same simplified example. These values are learned estimates.

> **Speaker notes**
>
> This is a hypothetical autonomous-taxi dispatch exercise, not a description of Waymo’s implementation. The image shows forecasts learned by the agent, not physical road signs or guaranteed outcomes. Q-values estimate cumulative discounted return, not immediate rewards or success probabilities. Reuse the preceding toy episode: nearby pickup has return 1; repositioning has return 0 + 0.9 × 10 = 9. These are illustrative estimates after learning the stipulated outcomes. Each modeled state has a value for every available action; another location, time, or demand level can change which action is best. Q(s,a) estimates return for action a in state s followed by the learned greedy policy. Q-learning is an off-policy temporal-difference method targeting the optimal action-value function under its assumptions. The explicit update and a numerical example are in self-study. Do not claim that the Bellman equation is the basis of all ML.

### Exploration Collects New Experience

**If the car always takes the highway, it may never discover a faster route.**

![A self-driving car chooses two routes to the same destination: a solid teal highway route with the best-known travel time, or a dashed amber route through city streets and traffic lights whose travel time is less certain.](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-exploration-navigation.png)

#### Exploit: use the best estimate

Take the highway. Past trips suggest it is **usually fastest in these conditions**.

#### Explore: collect experience

Sometimes try the side roads. Traffic and lights may make the trip **faster or slower**.

The actual travel time helps **update the car’s route estimates** for future trips.

Epsilon-greedy: with probability \(\epsilon\), choose a random action; otherwise choose the best known action.

With \(\epsilon=0.2\), about 20% of decisions use a random choice. Too little exploration can miss better options; too much can reduce current reward.

Simplified navigation example: both routes reach the same destination.

> **Speaker notes**
>
> This is a hypothetical autonomous-car navigation example, not a description of Waymo’s actual learning system. Both routes lead to the same destination. The highway currently has the best estimated travel time in the relevant conditions; the alternative route is less well tested. An exploratory trip can be faster or slower, and either outcome provides learning data. For a simple RL formulation, give a negative reward for each unit of travel time until arrival; less time then gives a higher return. State includes location, destination, time of day, and observed traffic, so one fast trip does not prove a route is always fastest. The illustration treats route selection as a high-level action. Epsilon-greedy chooses randomly among available actions on the epsilon branch; it does not deliberately seek the least-known route. The random branch can choose the highway too, so 20% random decisions does not mean exactly 20% of trips take the side roads. Exploration concerns feasible route choices in a simplified learning environment, not unsafe driving behavior.

### The Grid World Challenge

![Original hand-drawn Grid World: agent at the top left, goal at the bottom right, with movement actions and rewards](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-grid-world.png)

We program the environment and its rewards. **The agent must learn which actions lead to the goal.**

### Try It: Train a Grid World Policy

Start at the top left. Goal: bottom right. **+10 at the goal, −0.1 per other step.**

**Train, then watch the policy.** Reset and compare exploration at 0% and 20%. Inspect a cell’s four Q-values.

> **Speaker notes**
>
> The simulator computes real tabular Q-learning updates in the browser; the path is not prewritten. Zero explicit exploration can also succeed here: a negative step reward lowers a tried action below untried actions initialized to zero. Compare what each run learns rather than promising failure at epsilon=0. The environment rules and reward are programmed; the agent learns action values, not the source code of the world.

### The Reward Defines What the Agent Optimizes

| What we want | A weak reward | What can go wrong |
| --- | --- | --- |
| Finish a maze | +1 for every move | Keep moving without finishing |
| Resolve support issues | Reward closing tickets | Close tickets before solving them |
| Drive safely | Reward speed alone | Take dangerous shortcuts |

**Evaluate the behavior, not just the reward curve.** Design a safe environment for exploration.

A software agent using tools is not necessarily trained with RL. RL is a **learning method**, not a synonym for an autonomous workflow.

### A Q-Table Cannot List Every Game Screen

| Small Grid World | Pac-Man from pixels |
| --- | --- |
| 9 states × 4 actions = **36 values** | Vast numbers of possible screen configurations |
| Store each value in a table | Learn a function that estimates values |
| Look up \(Q(s,a)\) | Input frames → **neural network** → one Q-value per action |

**Deep Q-Network (DQN)** uses a neural network in place of the Q-table.

The RL objective stays the same. The way we represent action values changes.

> **Speaker notes**
>
> Pac-Man is observed through images, which do not directly contain all state information. Stacking frames helps reveal movement. DQN uses replayed transitions and a target network to stabilize training. Source: https://storage.googleapis.com/deepmind-media/dqn/DQNNaturePaper.pdf

---

## End Project: Pac-Man DQN

### Train an Agent to Play Ms. Pac-Man

![Untrained Ms. Pac-Man agent demonstrating random gameplay](https://haas-ai-classes-fall-26.vercel.app/diagrams/pacman-untrained.gif)

**[Open the Pac-Man project on GitHub →](https://github.com/pepealonso95/pacman-dqn)**

**[Open the notebook in Google Colab →](https://colab.research.google.com/github/pepealonso95/pacman-dqn/blob/main/pacman_dqn.ipynb)**

Run it in **Google Colab**, or clone the project for **Jupyter or VS Code**.

1. Choose **exploration**, **episodes**, and **learning rate**.
2. Select **Run All** to train the ready-made agent.
3. Watch gameplay and compare the before/after scores.

Using **Claude Code or Codex**? The notebook tells it to ask for your three choices before training.

> **Speaker notes**
>
> The notebook is self-contained and installs its dependencies. Exploration is a fixed random-action probability after a short warm-up. Start with five episodes to check setup; longer training does not guarantee good play. The public GitHub repository is the canonical project source, and the Colab link opens its main-branch notebook directly.

### Show What the Agent Actually Learned

**[Pac-Man project on GitHub →](https://github.com/pepealonso95/pacman-dqn)** · **[Open in Google Colab →](https://colab.research.google.com/github/pepealonso95/pacman-dqn/blob/main/pacman_dqn.ipynb)** · **[Assignment instructions (Google Doc) →](https://docs.google.com/document/d/1lnn9etY1Utpf-FMMyoatUjxzli02-FHXIFWo_KDW3n4/edit)**

Your repository should include:

- Your notebook and the **three hyperparameters** you chose.
- An untrained GIF, later checkpoints, and your best gameplay GIF.
- A training plot and a comparison of **five evaluation games** with the untrained baseline, using the same evaluation settings.
- A short explanation of the state, actions, reward, and one observed limitation.

**Lower DQN loss does not guarantee better play.** Learning speed varies; report what happened, including failed runs.

**[Submit your GitHub repository →](https://submissions-portal-eight.vercel.app/)**

> **Speaker notes**
>
> Retain the existing submission destination and core screenshot/GIF deliverables. Evaluation is needed to support any claim of improvement; the best GIF alone is selective evidence. Several games give a small comparison, not a robust research estimate. Do not promise competent play after 300 episodes or a particular laptop runtime. Source for DQN mechanism: https://storage.googleapis.com/deepmind-media/dqn/DQNNaturePaper.pdf

### Class 4: Learn the Features Too

![Illustrative neural network learns successive image representations: edges, textures, parts, and objects](https://haas-ai-classes-fall-26.vercel.app/diagrams/c2-deep-layers.png)

Today: choose features, fit parameters, evaluate on unseen cases, learn actions from rewards.

**Next: how layers learn representations, how backpropagation trains them, and how the same ideas lead to embeddings and transformers.**

**[Class 4: Deep Learning, Embeddings & Transformers →](https://haas-ai-classes-fall-26.vercel.app/class4.html)**

> **Speaker notes**
>
> The image is a conceptual sketch, not a claim that every network has these literal intermediate categories. Return to the shifted MNIST experiment and Pac-Man’s screen inputs. Students already know parameters, loss, gradient descent, held-out evaluation, and value estimation. Class 4 opens the network rather than introducing an unrelated machine.

---

## Optional Self-Study

### Cross-Validation Rotates the Held-Out Fold

![Five rounds each hold out a different fold, then summarize validation scores](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-kfold-cv.excalidraw.png)

Train on four folds; validate on the fifth. Rotate and compare the **average and spread**.

Use these scores to choose settings. Keep a separate **final test set**. Use time-aware or group-aware folds when rows are related.

> **Speaker notes**
>
> Diagram scores are illustrative. Cross-validation estimates how choices behave across these splits; a small spread does not establish future reliability. Source: https://scikit-learn.org/stable/modules/cross_validation.html

### Boosting Adds Trees That Reduce Remaining Error

![Sequential trees add corrections to the current ensemble prediction](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-gradient-boosting.excalidraw.png)

**Forest:** fit many trees independently, then combine. **Boosting:** add a tree that improves the current prediction, then repeat.

The number of trees, their depth, and the learning rate still need validation. Diagram error values are illustrative.

> **Speaker notes**
>
> For squared error, each added tree fits residuals. More generally, gradient boosting fits negative loss gradients. Avoid promising that each tree makes validation performance better. XGBoost and LightGBM are implementations, not a separate learning paradigm.

### Nearest Neighbors and SVMs

**Nearest neighbors:** predict from similar examples. The choice of distance and feature scaling matters.

**Support vector machine:** fit a boundary with a wide margin. Kernels can represent nonlinear boundaries.

![An SVM boundary maximizes the margin to nearby support vectors](https://haas-ai-classes-fall-26.vercel.app/diagrams/c3-svm-margin.excalidraw.png)

Both need validation. Neither is automatically the best choice because of its mathematical form.

### Calibration Checks Probability Estimates

Among cases assigned roughly **70% renewal probability**, about 70% should renew if the model is calibrated for that population.

| Good ranking | Good calibration |
| --- | --- |
| Higher scores tend to belong to positive cases | Stated probabilities match observed frequencies |
| Useful for ordering a queue | Useful when probabilities enter a cost calculation |

A model can rank well but be overconfident. Check calibration on held-out data and again as conditions change.

### Monitor the Model After Launch

| Monitor | Why |
| --- | --- |
| Input distributions and missingness | Tracking or the customer population may have changed |
| Outcomes once labels arrive | Useful predictions may have become inaccurate |
| Errors by relevant group | Overall improvement can hide who loses out |
| Human overrides and review volume | The policy may be overwhelming the team |

Assign an owner and a response: investigate, change a threshold, retrain, or roll back. Retraining itself still requires evaluation.

### Validation Error in Python

Fit increasingly flexible curves. Compare training and validation error on this synthetic dataset.

Which degree would you investigate further? These validation rows guide the choice; they are not an untouched final test set.

### Cross-Validate the Renewal Rule

Choose a threshold on four accounts, then evaluate on the held-out pair. Rotate the pair.

Add a low-usage account that renewed and repeat. Six rows demonstrate the procedure; a real evaluation needs representative data and appropriate splits.

### The Q-Learning Update

\[Q(s,a) \leftarrow Q(s,a) + \alpha\left[r + \gamma\max_{a'} Q(s',a') - Q(s,a)\right]\]

Suppose current \(Q=2\), reward \(r=0\), best next Q-value \(=5\), \(\gamma=0.9\), and learning rate \(\alpha=0.1\).

**Target = 0 + 0.9 × 5 = 4.5.** New Q = 2 + 0.1 × (4.5 − 2) = **2.25**.

For a terminal transition, target = reward only. There is no next-state value to add.

> **Speaker notes**
>
> This is a sample-based Q-learning update. In a stochastic environment, repeated experience estimates expected outcomes. Gamma discounts future reward; alpha controls how far to move the current estimate. They are different parameters.

### Why DQN Uses Replay and a Target Network

| Component | Purpose |
| --- | --- |
| **Frame stack** | Gives the network information about motion |
| **Experience replay** | Samples past transitions to reduce correlation and reuse experience |
| **Target network** | Provides a slower-changing target for value updates |
| **Exploration schedule** | Balances trying new actions with using current estimates |

The loss measures error against a **value target**, not whether the game was played well. Track evaluation reward and watch behavior too.

> **Speaker notes**
>
> Source: https://storage.googleapis.com/deepmind-media/dqn/DQNNaturePaper.pdf

### Pac-Man Notebook Setup

**[Download the notebook →](https://haas-ai-classes-fall-26.vercel.app/class3-labs/pacman-dqn/pacman_dqn.ipynb)** · [Setup and publishing guide](https://haas-ai-classes-fall-26.vercel.app/class3-labs/pacman-dqn/README.md)

- **Colab:** File → Upload notebook. Select a GPU under Runtime → Change runtime type if available.
- **Local:** open the notebook in Jupyter or VS Code and select a Python kernel.
- Choose your **exploration**, **episodes**, and **learning rate**, then **Run All**.
- Start with **five episodes** to check setup. Download the results ZIP when finished.

The notebook handles setup, training, GIFs, plots, checkpoints, and evaluation. Read the code to connect each step to the RL concepts.

**Optional:** [Build an agent from scratch with AI](https://haas-ai-classes-fall-26.vercel.app/class3-labs/pacman-prompt.txt).

> **Speaker notes**
>
> ALE setup reference checked during revision: https://ale.farama.org/getting-started/ Current ale-py packages include ROMs; avoid mixing obsolete AutoROM instructions with a modern install. Hardware availability is not a guarantee that the selected operations are supported or that training will be fast.
