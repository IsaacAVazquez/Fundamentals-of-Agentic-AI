# What this notebook is doing

This is a plain-language walkthrough of the Ms. Pac-Man agent in this folder. The README is the graded document and holds the settings, the scores, the gameplay, and the explanation. This file is for anyone who opens `pacman_dqn.ipynb` and wants to know what each part does, including people who haven't trained a reinforcement learning agent before.

The short version is that a small neural network plays Ms. Pac-Man over and over, and after each handful of moves it nudges its own numbers so that moves which led to points look slightly better next time. Nobody tells it the rules of the game, and all it ever sees is the screen and the score.

## The idea behind a DQN

DQN is short for Deep Q-Network. The Q part is an old idea from reinforcement learning, which is that for any situation you can ask how many points will follow from each move you could make, and then take the highest one. That number is the move's value. The deep part is that a neural network does the estimating, since there are far too many possible Ms. Pac-Man screens to write the answers down in a table.

The agent starts with random numbers, so its first estimates are meaningless. Two things fix that over time. It plays, and it remembers. Each decision is stored with what the screen looked like, what it did, what it scored, and what the screen looked like afterward. Then it repeatedly pulls small random batches out of that memory and adjusts the network so its estimate for the move it took moves closer to the reward it actually got plus the value of wherever it ended up.

## What the agent sees, does, and gets

The observation is four game screens, each shrunk to 84 by 84 pixels and turned to grayscale, stacked together. One still frame would show where everything is but not which way anything is moving, and four frames in a row show direction and speed. `make_env()` builds that, and three of its settings shape everything below. One decision covers four emulator frames, so the agent acts about 15 times a second rather than 60. Controls are sticky, with a one in four chance that the previous move repeats on a frame, which stops an agent from memorizing a fixed rhythm. And a game is capped at 3,000 decisions, or roughly 200 seconds.

The action is one of nine joystick positions, meaning no move, the four straight directions, and the four diagonals.

The reward is the game's own points. For learning, each decision's reward is clipped to between -1 and +1, so eating a ghost teaches the network no more than eating a pellet does. That keeps the updates from being dominated by a few huge numbers. Every score reported in the README is the raw game score, not the clipped one.

## What each piece of the notebook does

| Cell or function | What it does |
| --- | --- |
| The three settings at the top | Exploration, episodes, and learning rate, which are the only values a student changes |
| The fixed settings below them | Seed, replay size, batch size, warm-up length, target sync interval, discount, and the five evaluation seeds |
| `make_env()` | Builds the game with the preprocessing described above |
| `DQN` | The network, three convolution layers that read the picture, then two dense layers that output one number per move |
| `ReplayMemory` | Holds the last 5,000 decisions and hands back random batches of 32 |
| `choose_action()` | Picks the highest-valued move, or a random one with probability equal to the exploration setting |
| `learn()` | One learning step, described below |
| `evaluate()` | Plays the five fixed evaluation games and optionally records a GIF |
| `train_one_episode()` | Plays one training game and learns while it plays |
| The training loop | Runs that for every episode, writing the log, the GIFs, the checkpoints, and the plot as it goes |
| The comparison cell | Re-evaluates the trained agent and writes `comparison.json` |
| The download cell | Zips the run folder |

## The learning step in detail

`learn()` is four lines of real work. It asks the network what value it predicted for the move that was actually taken. It then builds a target, which is the reward that came back plus 0.99 times the best value available from the next screen, and that second part comes from a frozen copy of the network called the target network, refreshed every 1,000 decisions. Using a frozen copy matters because otherwise the thing being learned would move every time the network changed, which tends to spiral. If the game truly ended there is no next screen to add, though a game that only hit the time limit still counts the next screen, since the game was not really over.

The gap between prediction and target is turned into a loss with a Huber function, which is less sensitive to a few extreme values than a plain squared error, and the network is adjusted to shrink it. Gradients are clipped at 10 so no single batch can throw the weights, and there's a guard that stops the run if the loss stops being a finite number, with a message suggesting a smaller learning rate.

## The training loop

Each game resets with a seed tied to its episode number, so game 7 is the same maze and ghost behavior every time you run the notebook. For the first 1,000 decisions of the whole run, the agent moves completely at random to fill the memory with something to learn from. After that it uses the exploration setting, which in my run means one move in ten is random.

Once past warm-up, the network updates once every four decisions from a random batch of 32 remembered ones. That's why the update count in the README is roughly a quarter of the decision count. Every 25 games the notebook plays one extra demonstration game, saves it as a GIF, saves a checkpoint of the weights, and redraws the training dashboard. The per-game log is written to `training.csv` after every game, so an interrupted run still leaves a complete record of what happened.

## How the before-and-after comparison is kept fair

The same five games, seeds 101 through 505, are played before training and after, both with 5% random moves and the same time limit. The baseline is the untrained network, not an agent that moves at random, which matters because an untrained network isn't random. Mine held up and to the left on 96% of its moves, which is enough to score about 492 by itself.

The untrained GIF captures the first of those five games. The final GIF is the best of the five. Both show only the first 20 seconds at four times speed, while the score beside them counts the whole game.

## The files I added

The notebook and `pacman_player.py`, `requirements.txt`, and `tests/verify_notebook.py` come from the course. Everything below is mine.

| File | What it does |
| --- | --- |
| `scripts/setup.sh` | Builds `.venv` on Python 3.13 and installs the requirements plus the pieces a scripted run needs |
| `scripts/verify.sh` | Runs the course's five-game check, which executes the whole notebook and inspects its artifacts |
| `scripts/lab.sh` | Opens the notebook in JupyterLab |
| `scripts/check_checkpoints.py` | Replays every saved checkpoint on 30 validation games and 50 test games that were never used for training or grading, which is how I chose 450 episodes |
| `scripts/eval_move_shares.py` | Replays a run's untrained and final agents on the five evaluation games and counts which moves they chose |
| `results/450-games/` and `results/500-games/` | The published evidence from both runs |

Both of my replay scripts import the notebook's own tagged cells and run its code rather than reimplementing it, and both check themselves by reproducing the scores in `comparison.json` before they report anything. That's the only reason to trust a number they produce.

## Where the results are explained

The README covers what actually happened, including the run that didn't improve, why I retrained with 450 episodes, and what the agent's instability looks like across checkpoints. This file stops at what the code does.
