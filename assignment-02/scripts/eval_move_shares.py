"""Count which moves an agent chose in the five evaluation games, and when it scored.

Run it with the notebook's Python on a finished run folder:
    .venv/bin/python scripts/eval_move_shares.py pacman_runs/20260913_215514_100404 results/450-games/move_shares.json

It reuses the notebook's own game, network, and move-choice code, so it scores the five games
exactly the way the notebook does. The scores have to match the run's comparison.json, and the
script stops if they do not. Alongside the move counts it records, for each game, the score the
agent had reached by the end of the GIF window and the decisions at which it lost a life, which
is what the README's gameplay paragraph describes.
"""

import json
import random
import statistics
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
CODE_TAGS = {"imports", "settings", "preview-settings", "environment", "network", "actions"}


def main():
    run, out = Path(sys.argv[1]), Path(sys.argv[2])
    nb = {}
    for cell in nbformat.read(ROOT / "pacman_dqn.ipynb", as_version=4).cells:
        if cell.cell_type == "code" and CODE_TAGS & set(cell.metadata.get("tags", [])):
            exec(cell.source, nb)
    torch = nb["torch"]
    probe = nb["make_env"]()
    moves, n_actions = probe.unwrapped.get_action_meanings(), int(probe.action_space.n)
    probe.close()
    device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
    comparison = json.loads((run / "comparison.json").read_text())

    def load(name):
        checkpoint = torch.load(run / name, map_location="cpu", weights_only=True)
        model = nb["DQN"](checkpoint["n_actions"]).to(device)
        model.load_state_dict(checkpoint["model"])
        return model

    def shares(counts):
        total = sum(counts)
        return {move: round(count / total, 3) for move, count in zip(moves, counts)}

    def play(model, seeds):
        counts, scores, games = [0] * n_actions, [], []
        for seed in seeds:
            game = nb["make_env"]()
            try:
                rng = random.Random(seed + 10000)
                obs, info = game.reset(seed=seed)
                lives, score, preview_score = info.get("lives"), 0.0, 0.0
                per_game, life_losses = [0] * n_actions, []
                for step in range(nb["MAX_STEPS"]):
                    action = nb["choose_action"](model, obs, nb["EVAL_EXPLORATION"], rng, n_actions)
                    counts[action] += 1
                    per_game[action] += 1
                    obs, reward, ended, truncated, info = game.step(action)
                    score += reward
                    if step < nb["PREVIEW_DECISIONS"]:
                        preview_score = score
                    if info.get("lives") is not None and info["lives"] < lives:
                        life_losses.append(step + 1)
                        lives = info["lives"]
                    if ended or truncated:
                        break
            finally:
                game.close()
            scores.append(score)
            games.append({"seed": seed, "score": score, "decisions": step + 1,
                          "score_by_end_of_gif_window": preview_score,
                          "life_loss_decisions": life_losses, "move_shares": shares(per_game)})
        return {"scores": scores, "mean": statistics.mean(scores), "move_shares": shares(counts), "games": games}

    report = {"device": str(device), "run": run.name, "eval_seeds": nb["EVAL_SEEDS"],
              "eval_exploration": nb["EVAL_EXPLORATION"], "max_decisions_per_game": nb["MAX_STEPS"],
              "gif_window_decisions": nb["PREVIEW_DECISIONS"], "models": {}}
    for name, key in (("untrained.pt", "before"), ("trained.pt", "after")):
        result = play(load(name), nb["EVAL_SEEDS"])
        assert result["scores"] == comparison[key]["scores"], f"{name} did not reproduce comparison.json"
        result["matches_comparison_json"] = True
        report["models"][name] = result
        top = max(result["move_shares"].items(), key=lambda pair: pair[1])
        print(f"{name}: scores {result['scores']}, most common move {top[0]} at {top[1]:.0%}", flush=True)

    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
