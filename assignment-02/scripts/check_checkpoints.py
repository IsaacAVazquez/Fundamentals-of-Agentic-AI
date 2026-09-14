"""Check whether training helped, using games the notebook never plays.

Run it with the notebook's Python on a finished run folder:
    .venv/bin/python scripts/check_checkpoints.py pacman_runs/20260913_205300_537031

It reuses the notebook's own game, network, and move-choice code. Every saved checkpoint is
compared on 30 validation games, and the best one is then measured on 50 separate test games.
None of those games is a training game or one of the five leaderboard games. The leaderboard
games are only replayed to confirm this script scores exactly like the notebook and to count moves.
"""

import json
import random
import statistics
import sys
import time
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
VALIDATION_SEEDS = list(range(10001, 10031))
TEST_SEEDS = list(range(10031, 10081))
CODE_TAGS = {"imports", "settings", "environment", "network", "actions"}


def main():
    run = Path(sys.argv[1])
    nb = {}
    for cell in nbformat.read(ROOT / "pacman_dqn.ipynb", as_version=4).cells:
        if cell.cell_type == "code" and CODE_TAGS & set(cell.metadata.get("tags", [])):
            exec(cell.source, nb)
    torch = nb["torch"]
    probe = nb["make_env"]()
    moves, n_actions = probe.unwrapped.get_action_meanings(), int(probe.action_space.n)
    probe.close()
    device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")

    config = json.loads((run / "config.json").read_text())
    comparison = json.loads((run / "comparison.json").read_text())
    training_seeds = set(range(nb["SEED"] + 1, nb["SEED"] + config["episodes_requested"] + 1))
    held_out = set(VALIDATION_SEEDS) | set(TEST_SEEDS)
    assert not held_out & (training_seeds | set(nb["EVAL_SEEDS"])) and not set(VALIDATION_SEEDS) & set(TEST_SEEDS)

    def load(name):
        checkpoint = torch.load(run / name, map_location="cpu", weights_only=True)
        model = nb["DQN"](checkpoint["n_actions"]).to(device)
        model.load_state_dict(checkpoint["model"])
        return model

    def play(model, seeds):
        """Score games exactly like the notebook's evaluate(), and count which moves were chosen."""
        scores, counts = [], [0] * n_actions
        for seed in seeds:
            game = nb["make_env"]()
            try:
                rng = random.Random(seed + 10000)
                obs, _ = game.reset(seed=seed)
                score = 0.0
                for _ in range(nb["MAX_STEPS"]):
                    action = nb["choose_action"](model, obs, nb["EVAL_EXPLORATION"], rng, n_actions)
                    counts[action] += 1
                    obs, reward, ended, truncated, _ = game.step(action)
                    score += reward
                    if ended or truncated:
                        break
            finally:
                game.close()
            scores.append(score)
        total = sum(counts)
        return {"scores": scores, "mean": statistics.mean(scores),
                "move_shares": {move: round(count / total, 3) for move, count in zip(moves, counts)}}

    started = time.monotonic()
    report = {"device": str(device), "validation_seeds": VALIDATION_SEEDS, "test_seeds": TEST_SEEDS,
              "leaderboard_games": {}, "validation": {}, "test": {}}
    for name, key in (("untrained.pt", "before"), ("trained.pt", "after")):
        result = play(load(name), nb["EVAL_SEEDS"])
        result["matches_comparison_json"] = result["scores"] == comparison[key]["scores"]
        report["leaderboard_games"][name] = result
        print(f"leaderboard games, {name}: {result['scores']} matches comparison.json: {result['matches_comparison_json']}", flush=True)

    checkpoints = ["untrained.pt"] + sorted(path.name for path in run.glob("episode_*.pt"))
    for name in checkpoints:
        report["validation"][name] = play(load(name), VALIDATION_SEEDS)
        print(f"validation, {name}: mean {report['validation'][name]['mean']:.1f}", flush=True)
    best = max(checkpoints[1:], key=lambda name: report["validation"][name]["mean"])
    report["best_on_validation"] = best

    untrained = report["test"]["untrained.pt"] = play(load("untrained.pt"), TEST_SEEDS)
    for name in dict.fromkeys(["trained.pt", best]):
        result = play(load(name), TEST_SEEDS)
        gaps = [after - before for before, after in zip(untrained["scores"], result["scores"])]
        result["difference_vs_untrained"] = statistics.mean(gaps)
        result["margin_95"] = 1.96 * statistics.stdev(gaps) / len(gaps) ** 0.5
        result["higher_than_untrained"] = sum(gap > 0 for gap in gaps)
        report["test"][name] = result

    report["seconds"] = time.monotonic() - started
    (run / "checkpoint_check.json").write_text(json.dumps(report, indent=2))
    print(f"best on validation: {best}")
    for name, result in report["test"].items():
        extra = "" if name == "untrained.pt" else (
            f", {result['difference_vs_untrained']:+.1f} vs untrained (95% margin ±{result['margin_95']:.0f}),"
            f" higher in {result['higher_than_untrained']} of {len(TEST_SEEDS)}")
        print(f"test, {name}: mean {result['mean']:.1f}{extra}")
    print(f"wrote {run / 'checkpoint_check.json'} in {report['seconds']:.0f} s")


if __name__ == "__main__":
    main()
