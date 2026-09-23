# Next Ms. Pac-Man run

Written 2026-09-22, after grading. This is everything I'd need to try for a stronger agent later, from why it's worth trying, to what I'd change and the exact edits, to how to run it on this Mac and pick the checkpoint without touching the leaderboard games. None of it has been run for real yet, and the only runs so far are the 5-game tests of the edits described under "Checked so far."

## Why try again

Assignment 2 got 9.81 of 10, graded on 2026-09-20, with the comment "Complete 450-episode submission with both runs preserved and thoughtful checkpoint validation. Continue separating checkpoint-selection evidence from the five-game class benchmark."

The rubric on bCourses has four lines. Explanation (4 points) and evidence (3) are full or no marks, and executed run (2) gives partial credit only if the notebook's outputs are missing, which mine weren't. Gameplay (1) pays by where the mean of the five trained evaluation games ranks among eligible submissions, with the best rank earning 1 and the lowest earning 0. The grader typed the score in by hand, so no line-by-line breakdown is recorded, but the 0.19 I lost almost certainly came off the gameplay line, and if that line scales evenly from best to worst rank, 0.81 put me about a fifth of the way down the class. The write-up had nothing left to earn, and the only way up is a stronger agent.

A classmate reportedly scored 7,700, and nothing on bCourses says whether that's a five-game mean, one game, or five games added up. As a mean it would be about 8 times my 946 and more than double the best single game any of my agents ever played, which was 2,910 in evaluation and 3,020 in training. A luckier checkpoint pick couldn't close that gap, so it would mean either a much stronger training setup or a different way of scoring. As one game it says little about their mean, and as a five-game total it's a mean of 1,540, which is a lot closer.

## What I think is holding the agent back

The notebook's replay memory holds 5,000 decisions, where one decision is four game frames. My 450 training games averaged 611 decisions each, so at any point the agent was learning from only about its last 8 games and overwriting everything older. I think that's the main reason the first run's saved agents swung so much. Loaded at different 25-game checkpoints, they averaged anywhere from 418 to 1,182 on the same 30 validation games, and the final 500-game agent landed at 439, next to the untrained network's 449. On 50 test games it beat the untrained network by only 45 points, inside the 95% margin of plus or minus 124. I haven't proven that the memory is the cause. Run A below will show whether the swings calm down, but since it changes three things at once, it can't say which one did it.

The training budget was also small. The 450 games were 274,814 decisions and 68,454 learning updates in 12.7 minutes. The original DQN paper (Mnih et al. 2015, "Human-level control through deep reinforcement learning," which the notebook cites) trained each game for "a total of 50 million frames (that is, around 38 days of game experience in total)." At the Atari's 60 frames a second, 38 days only works out if each counted frame is one decision of four game frames, so that's about 50 million decisions, roughly 180 times what I trained.

Losing a life costs the agent almost nothing it can see. The game keeps going across lives, the maze carries over, and the reward has no penalty for dying, so the only sign that dying is bad is the points the agent misses afterward. The paper handled this directly, since "for games where there is a life counter, the Atari 2600 emulator also sends the number of lives left in the game, which is then used to mark the end of an episode during training."

Rewards are clipped to between -1 and 1 before the agent learns from them. On 2026-09-22 I played three games (seeds 20001 to 20003) with the 450-game agent and logged the raw rewards, and they were 10 for a dot, 50 for a power pellet, and 200 or 400 for a ghost. Clipping turns every one of those into 1. The paper names this cost of its own clipping, that "it could affect the performance of our agent since it cannot differentiate between rewards of different magnitude."

## The plan

I'd do two runs, in order. Run A changes the replay memory, the number of games, and how a lost life is treated, since all three are standard DQN practice and the paper did all three. Run B is run A plus reward scaling. It runs separately so any difference between the two comes only from the reward change, though one pair of runs can't show that the difference would repeat. It also doubles as the one controlled next experiment that the rubric's explanation line asks for.

| Setting | 450-game run | Run A | Run B |
| --- | --- | --- | --- |
| Exploration | 0.10 | 0.10 | 0.10 |
| Learning rate | 0.0001 | 0.0001 | 0.0001 |
| Episodes | 450 | 3000 | 3000 |
| Replay memory, in decisions | 5,000 | 100,000 | 100,000 |
| A lost life in training | ignored | ends the learning target | ends the learning target |
| Training reward | clipped to ±1 | clipped to ±1 | sign(r) × log(1 + abs(r)) |

Everything else stays as the course ships it, including the five evaluation seeds (101, 202, 303, 404, 505), the 5% random moves during evaluation, and the cap of 3,000 decisions per game. The brief allows changing the fixed settings as long as the README explains the change, in its words "You can tune the other hyperparameters, but explain what you did and why." That covers the replay memory. The life-loss and reward edits change training code instead of a setting, and the brief only says "Use the supplied DQN," so I'd ask whether a run with them still counts for the leaderboard.

At the old 611 decisions a game, 3,000 games is about 1.8 million decisions. That's about 6.7 times the 450-game run and still fits in an evening. Keep the value as plain digits, `3000` and not `3_000`, because the 5-game check in `tests/verify_notebook.py`, which `scripts/verify.sh` runs, finds that line with a pattern that only matches digits, and a comment at the end of the line would break it too. It also has to stay under 9,959, because training game n uses seed 42 + n and `scripts/check_checkpoints.py` stops if a training seed reaches its held-out seeds, which start at 10001.

## The edits

Every edit goes in `pacman_dqn.ipynb` itself, located by each code cell's tag, because `scripts/check_checkpoints.py`, `scripts/eval_move_shares.py`, and `tests/verify_notebook.py` all read the notebook by that name. Do the work on a branch. The graded submission is https://github.com/IsaacAVazquez/Fundamentals-of-Agentic-AI/tree/main/assignment-02, so anything merged into main changes what a grader sees.

```bash
git switch -c a2-next-run
```

In the cell tagged `choices`, change only the episodes.

```diff
-EPISODES = 450
+EPISODES = 3000
```

In `settings`, make the replay memory bigger.

```diff
-REPLAY_CAPACITY = 5000   # About 168 MiB of pixel data, allocated gradually.
+REPLAY_CAPACITY = 100_000  # About 3.3 GiB of pixel data, allocated gradually.
```

In `train-episode`, a lost life goes into replay as terminal while the game itself keeps going to game over.

```diff
-    obs, _ = train_env.reset(seed=SEED + episode)
+    obs, info = train_env.reset(seed=SEED + episode)
+    lives = info["lives"]
     score, losses = 0.0, []
     for step in range(MAX_STEPS):
         epsilon = 1.0 if total_steps < WARMUP_STEPS else EXPLORATION
         action = choose_action(model, obs, epsilon, train_rng, N_ACTIONS)
-        next_obs, reward, ended, truncated, _ = train_env.step(action)
-        replay.add(obs, action, reward, next_obs, ended, truncated)
+        next_obs, reward, ended, truncated, info = train_env.step(action)
+        # A lost life ends the learning target; the game itself keeps going.
+        life_lost = info["lives"] < lives
+        lives = info["lives"]
+        replay.add(obs, action, reward, next_obs, ended or life_lost, truncated)
```

In `run-config`, record the change so `config.json` tells the truth. The wrapper's own `terminal_on_life_loss` flag stays False, because the game still runs to game over.

```diff
-          "stack_size": 4, "terminal_on_life_loss": False, "max_decisions_per_game": MAX_STEPS,
+          "stack_size": 4, "terminal_on_life_loss": False,
+          "training_life_loss_as_terminal": True, "max_decisions_per_game": MAX_STEPS,
```

Run B adds two more edits on top of those. In `replay`, scale the reward instead of clipping it.

```diff
-                           float(np.clip(reward, -1, 1)),
+                           float(np.sign(reward) * np.log1p(abs(reward))),
```

In `run-config`, record the transform in place of the clipping range.

```diff
-          "training_reward_clipping": [-1, 1], "eval_exploration": EVAL_EXPLORATION,
+          "training_reward_transform": "sign(r) * log(1 + |r|)", "eval_exploration": EVAL_EXPLORATION,
```

Log scaling turns a dot into 2.4, a power pellet into 3.9, and 200- and 400-point ghosts into 5.3 and 6.0, so a ghost ends up worth two to two and a half dots instead of one. That's a gentle push toward ghosts. Dividing rewards by 10 would push harder, since a dot would stay at 1 while a 200- or 400-point ghost became 20 or 40. Single rewards that big are what the paper's clipping was there to prevent, because clipping "limits the scale of the error derivatives," so that's where training is most likely to go unstable, and the notebook stops with "Loss became non-finite" if it does.

The notebook's own text still describes the starter settings in a few places. The note above `settings` says the agent remembers 5,000 past decisions, and section 3c says each memory stores whether the game ended. Section 3's intro calls the replay memory small, and it, the 3e note, and the comment in `learning` say only game over removes future reward. The same intro says rewards are clipped, which only goes out of date in run B. The closing implementation notes say replay is deliberately small for laptops. I'd update those sentences in the same edit, or say in the README that they describe the starter notebook.

## Checked so far

On 2026-09-22 I applied both sets of edits to scratch copies of the notebook and ran the course's own check (`tests/verify_notebook.py`, which runs a 5-game copy) on each one, and both passed in about 20 seconds. With the life-loss edit, replay held 15 terminal flags after 5 games of 3 lives each, where the unedited notebook would hold 5. Under run B the largest stored reward was 3.93, which is a 50-point power pellet after scaling. A second run A check matched the first one on every `training.csv` column except wall-clock time, and on the final weights, so training still repeats exactly on this Mac with the edits, at least over 5 games. The game reports lives through all of the notebook's wrappers, starting at 3, and the last lost life lands on the same step the game ends.

## How to run it

1. Check the environment. The venv is uv on Homebrew Python 3.13, and `scripts/setup.sh` rebuilds it if it's gone. On 2026-09-22 this printed `3.13.15 2.14.0 1.3.0 0.11.2 True`.

   ```bash
   cd ~/Fundamentals-of-Agentic-AI/assignment-02
   .venv/bin/python -c "import sys, torch, gymnasium, ale_py; print(sys.version.split()[0], torch.__version__, gymnasium.__version__, ale_py.__version__, torch.backends.mps.is_available())"
   ```

2. Make the edits above, then run the 5-game check, which takes about 20 seconds. It edits an in-memory copy, not the notebook file, and writes its run to `pacman_runs/`. Leave `DEMO_EVERY` at 25, because the check swaps in 2 by matching `DEMO_EVERY = 25` and then expects samples at games 2 and 4.

   ```bash
   scripts/verify.sh
   ```

3. Before starting, write down a prediction for the five-game mean and for which checkpoint will win validation, since the README has to show that the expectation came before the result.

4. Run the whole notebook headless with the Mac plugged in, since caffeinate's `-s` only keeps the Mac awake on AC power. The kernel is `python3` because the notebook's metadata names a `py313` kernel that doesn't exist on this machine. The venv has no Tk, so every gameplay sample prints "Popup unavailable in this kernel," which is harmless. The run lands in a new `pacman_runs/<timestamp>/` folder with a ZIP next to it, and `pacman_runs/` is gitignored.

   ```bash
   caffeinate -is .venv/bin/jupyter-nbconvert --to notebook --execute --inplace --allow-errors \
     --ExecutePreprocessor.kernel_name=python3 --ExecutePreprocessor.timeout=-1 pacman_dqn.ipynb
   ```

5. Pick the checkpoint using the rule in the next section.

6. If the winner isn't the final checkpoint, set `EPISODES` to the winner's game number, run step 4 again, and confirm that the rerun's final agent is the same network. This is how the 450-game submission was made. That rerun's `trained.pt` matched the first run's `episode_0450.pt`, and this command printed True for that pair on 2026-09-22.

   ```bash
   .venv/bin/python -c "import sys, torch; a, b = (torch.load(p, weights_only=True)['model'] for p in sys.argv[1:]); print(all(torch.equal(a[k], b[k]) for k in a))" \
     pacman_runs/<rerun>/trained.pt pacman_runs/<first run>/episode_NNNN.pt
   ```

## Picking the checkpoint without the leaderboard games

Write this rule down before training, and follow it even if the final agent's leaderboard score looks better.

The notebook saves a checkpoint every 25 games, which is 120 of them over 3,000 games. After the notebook finishes, run the checkpoint check on the run folder.

```bash
.venv/bin/python scripts/check_checkpoints.py pacman_runs/<run>
```

It plays every checkpoint on validation seeds 10001 to 10030 and picks the one with the highest mean. It then measures that pick and the final agent on test seeds 10031 to 10080 against the untrained network, and writes `checkpoint_check.json` with `best_on_validation`. The validation winner is the one I submit, and the test games only measure it. The five leaderboard games get played by the notebook itself and replayed by the script only to confirm it scores the same way, and they never feed a choice. In the README I'd say plainly which evidence chose the checkpoint (validation) and which only measured it (test and leaderboard), since that's the grader's standing request.

There's one more thing to word carefully in the README. Training game n uses seed 42 + n, so any run of 463 games or more has also started a training game from each leaderboard seed, at games 59, 160, 261, 362, and 463, and the 450-game run did the same for the first four. That's how the course notebook is built, and it's the same for everyone who trains that long. It does mean the README can say the leaderboard seeds never chose anything, but it shouldn't claim they never appeared in training.

## What it costs

The 450-game run went at 361 decisions a second on the M4 Pro, counting its periodic samples. A replay memory of 100,000 decisions takes about 3.3 GiB of this Mac's 24 GiB. In timings on 2026-09-22 with the notebook's own replay code, filled the way training fills it, drawing a batch took about 0.5 to 0.9 milliseconds at 100,000 against 0.1 at 5,000, which works out to roughly 4 to 7% slower per decision. At the old 611 decisions a game, 3,000 games is about 1.8 million decisions and roughly an hour and a half. A better agent survives longer, though, and at 900 decisions a game it would be 2.7 million decisions and a little over two hours.

The checkpoint check plays 30 validation games for each of 121 saved agents (the 120 checkpoints plus the untrained network) and 160 more games besides, about 3,800 games in all. Last time it played 790 games in 567 seconds, so at that pace it's about 45 minutes, and longer games stretch it. If the winner is an earlier checkpoint, the rerun costs the training time up to that game again. All told I'd budget between about two and five hours, mostly unattended.

Each checkpoint is 6.8 MB, so 120 of them come to about 810 MB, and the run's ZIP holds another copy (the 450-game run's folder was 136 MB and its ZIP 125 MB). So plan on about 1.6 GB per run, and double that with a rerun. The disk had between 32 and 34 GiB free on 2026-09-22 and was 93% full.

## If I resubmit

The grade is already posted. On 2026-09-22 Canvas showed unlimited attempts and no lock date for the assignment, but I don't know whether the instructor would re-rank a resubmission, or whether one with the life-loss and reward edits would still be among the "eligible submissions" the rubric ranks, so I'd ask about both before doing the work for that reason.

A resubmission means merging the branch into main, since the submitted URL points at main, and the README would need to hold up to the same rubric. It needs the reason for every changed setting, the new prediction and what happened, and all five before-and-after scores with both means. It needs the run statistics, the dashboard, and the untrained, best, and every intermediate GIF, one for every 25 games at about 30 KB each. The submitted run is whichever one the notebook ends on, so if step 6 reran to an earlier checkpoint at game N, it's an N-game run with N/25 intermediate GIFs, and its evidence goes in `results/<N>-games/` the way the last one went in `results/450-games/`. That folder should hold `config.json`, `training.csv`, `training_summary.json`, and `comparison.json`, all linked from the README. And it needs one controlled next experiment, which run B is if it hasn't been run yet.

I'd keep the 450-game and 500-game evidence where it is, since the grader singled out that both runs were preserved, and rewrite the notebook's explanation cell for the new run. If the README describes gameplay the way the last one did, `.venv/bin/python scripts/eval_move_shares.py pacman_runs/<run> results/<N>-games/move_shares.json` records the move counts behind it. Checkpoints go in a GitHub release like the existing `assignment-02-checkpoints`, since `.gitignore` keeps `*.pt` files out of the repository.
