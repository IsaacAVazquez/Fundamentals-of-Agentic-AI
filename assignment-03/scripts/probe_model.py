"""Score a few extra prompts on a saved model to diagnose eval results.

These probes are mine, written after training and separate from the fixed 48-case
suite. They never train anything. Each probe gives the model only the prompt and
reads the next-token probabilities of four words, the same rule the runner uses,
plus a free continuation at the runner's settings.
Usage: .venv/bin/python scripts/probe_model.py <model.pt> <output.json>
"""
import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_evals import generate_reply, load_model, model_hash, word_tokens  # noqa: E402

PROBES = [
    ("negation, flipped colors", "the cup is not white . it is black . the cup is", ["white", "black", "green", "red"], "black"),
    ("negation, flipped colors", "the cup is not black . it is white . the cup is", ["white", "black", "green", "red"], "white"),
    ("negation, door flipped", "the door is not closed . it is open . the door is", ["closed", "open", "wide", "missing"], "open"),
    ("negation, gate", "the gate is not open . it is closed . the gate is", ["closed", "open", "wide", "missing"], "closed"),
    ("negation, food", "nora did not buy rice . she bought bread . nora bought", ["rice", "bread", "tea", "milk"], "bread"),
    ("negation, food flipped", "nora did not buy bread . she bought rice . nora bought", ["rice", "bread", "tea", "milk"], "rice"),
    ("reference, names swapped", "leo lent a book to maya . maya thanked", ["leo", "maya", "nora", "omar"], "leo"),
    ("reference, giver", "nora gave omar a coin . the person who gave the coin was", ["nora", "omar", "sara", "finn"], "nora"),
    ("reference, receiver", "nora gave omar a coin . the person who received the coin was", ["nora", "omar", "sara", "finn"], "omar"),
    ("grammar, singular", "one cat", ["is", "are", "were", "am"], "is"),
    ("grammar, plural", "the cats", ["is", "am", "was", "are"], "are"),
    ("grammar, past", "yesterday he", ["walking", "walk", "walked", "walks"], "walked"),
    # Added after the first audit pass, to test the sample-based and position-based readings directly.
    ("reference, object copy", "nora gave sara a pencil . the person who received the", ["pencil", "card", "key", "lamp"], "pencil"),
    ("reference, receiver, nora then sara", "nora gave sara a pencil . the person who received the pencil was", ["nora", "sara", "omar", "leo"], "sara"),
    ("reference, receiver, sara then nora", "sara gave nora a pencil . the person who received the pencil was", ["nora", "sara", "omar", "leo"], "nora"),
    ("reference, receiver, omar then nora", "omar gave nora a coin . the person who received the coin was", ["nora", "omar", "sara", "finn"], "nora"),
    ("negation, gate flipped", "the gate is not closed . it is open . the gate is", ["closed", "open", "wide", "missing"], "open"),
]


@torch.inference_mode()
def main():
    model, vocabulary, saved = load_model(Path(sys.argv[1]))
    stoi = {w: i for i, w in enumerate(vocabulary)}
    rows = []
    for index, (label, prompt, choices, expected) in enumerate(PROBES):
        tokens = word_tokens(prompt)
        unknown = [t for t in tokens + choices if t not in stoi]
        row = {"label": label, "prompt": prompt, "choices": choices, "expected": expected, "unknown_words": unknown}
        if not unknown:
            ids = [stoi["<BOS>"]] + [stoi[t] for t in tokens]
            probs = torch.softmax(model(torch.tensor([ids]))[0][0, -1].float(), -1)
            row["choice_probabilities"] = {c: round(probs[stoi[c]].item(), 4) for c in choices}
            row["predicted"] = max(row["choice_probabilities"], key=row["choice_probabilities"].get)
            row["correct"] = row["predicted"] == expected
        row["generated_text"] = generate_reply(model, vocabulary, prompt, seed=3026 + index)["response"]
        rows.append(row)
        print(f"{label:<26} {prompt!r}\n{'':<26} -> {row.get('predicted')} {'ok' if row.get('correct') else 'X'} {row.get('choice_probabilities')} | gen: {row['generated_text']!r}")
    output = {"model": sys.argv[1], "model_sha256": model_hash(model), "completed_steps": saved.get("completed_steps"), "probes": rows}
    Path(sys.argv[2]).write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print("correct:", sum(1 for r in rows if r.get("correct")), "of", sum(1 for r in rows if "correct" in r), "scorable")


if __name__ == "__main__":
    main()
