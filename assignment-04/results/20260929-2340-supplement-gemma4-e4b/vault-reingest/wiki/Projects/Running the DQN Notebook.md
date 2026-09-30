---
title: Running the DQN Notebook
aliases:
  - running-the-dqn-notebook
topic: Projects
summary: Details on executing the final 450-game run notebook and its outputs.
sources:
  - raw/Pac-Man DQN README.md
source_id: pac-man-dqn-readme
source_sha256: cd469243a82e4f8b831e84de0e0e23277841ebb23499bde0585bb31c84a7fd69
sections_used:
  - Open and run the notebook
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: pac-man-dqn-readme/running-the-dqn-notebook
plan_origin: model-retry
---
# Running the DQN Notebook

## Summary

This note details how to run the final 450-game run notebook, `pacman_dqn.ipynb`, and provides instructions for local execution and verification. The executed notebook retains all outputs, including the baseline, 450 training lines, progress GIFs, dashboard, and final comparison, meaning no rerunning is necessary for inspection. I also detail the commands for running verification scripts like `scripts/check_checkpoints.py` and `scripts/eval_move_shares.py`.

## Details

The executed notebook is `pacman_dqn.ipynb`, from the final 450-game run. It keeps every output from that run, including the baseline, all 450 training lines, the progress GIFs, the dashboard, and the final comparison, so none of it needs rerunning to inspect. One catch is that GitHub's notebook viewer can't display the notebook's GIF outputs and shows the text `<IPython.core.display.Image object>` in each of those 20 spots instead, so every one of those GIFs is also embedded in this README and saved in `results/450-games/demos/`. The first run's executed notebook is `results/500-games/pacman_dqn_500_games.ipynb`, and I left its explanation cell at the end as the course's blank template, since this README covers both runs.

To run it again locally, clone the repository and set up Python 3.13 in this folder. I used `scripts/setup.sh`, which builds `.venv` with uv on whichever Python 3.13 uv finds or downloads, or the one named in `PYTHON=`, installs `requirements.txt` plus the Jupyter pieces a scripted run needs, and registers the `py313` kernel the notebook's metadata names. On my Mac that Python is Homebrew's. The course's own instructions use a plain virtual environment and pip instead, and either way the notebook's setup cell installs anything that's missing.

```
git clone https://github.com/IsaacAVazquez/Fundamentals-of-Agentic-AI.git
cd Fundamentals-of-Agentic-AI/assignment-02
scripts/setup.sh
scripts/lab.sh
```

`scripts/lab.sh` opens the notebook in JupyterLab, where Run All repeats the experiment. I ran mine without opening Jupyter's interface, using the command below, which executes every cell in order and writes the outputs back into the notebook. `caffeinate` only keeps the Mac awake until it finishes.

```
caffeinate -is .venv/bin/jupyter-nbconvert --to notebook --execute --inplace --allow-errors \
  --ExecutePreprocessor.kernel_name=python3 --ExecutePreprocessor.timeout=-1 pacman_dqn.ipynb
```

In Colab, the route from the Class 3 setup slide is File, then Upload notebook, then Run all. Any rerun starts a fresh experiment in a new `pacman_runs/` folder and replaces the outputs saved in the notebook, and the notebook itself notes that GPU results can vary even with fixed seeds, so a rerun on different hardware may not reproduce my scores exactly.

`scripts/verify.sh` runs the course's five-game check without touching the notebook, and I ran it on 2026-09-13 before the real runs, when it passed in about 20 seconds. `scripts/check_checkpoints.py` replays a finished run's saved agents on games the notebook never plays, which is how I chose 450 games. It took about nine and a half minutes on this laptop. `scripts/eval_move_shares.py` replays a run's untrained and final agents on the five evaluation games instead, counting which moves each one chose, and it stops if the scores don't match that run's `comparison.json`.

```
.venv/bin/python scripts/check_checkpoints.py pacman_runs/<run folder>
.venv/bin/python scripts/eval_move_shares.py pacman_runs/<run folder> results/<N>-games/move_shares.json
```

## Related

- [[Assignment Overview and Requirements Pac-Man]]: This note covers the execution of the final 450-game run notebook and its outputs
- [[Model Performance and Results]]: This note details how to run the final 450-game run notebook, `pacman_dqn.ipynb`, and provides instructions for local execution and verification

## Sources

- [[wiki/Sources/Pac-Man DQN README|Pac-Man DQN README]]: `raw/Pac-Man DQN README.md`, sections "Open and run the notebook"
