"""Cosine neighbors of chosen words before and after training, from a run's checkpoint.json.

The embedding viewer shows the same thing interactively. This writes neighbors.json
into the run folder so the numbers can be quoted and checked.
Usage: .venv/bin/python scripts/neighbors.py <run folder> word [word ...]
"""
import json
import sys
from pathlib import Path

import torch


def neighbors(table, vocabulary, word, count=5):
    index = vocabulary.index(word)
    unit = torch.nn.functional.normalize(table, dim=1)
    similarity = unit @ unit[index]
    similarity[index] = -2  # skip the word itself
    order = similarity.argsort(descending=True)[:count]
    return [(vocabulary[i], round(similarity[i].item(), 3)) for i in order]


def main():
    run = Path(sys.argv[1])
    words = sys.argv[2:]
    checkpoint = json.loads((run / "checkpoint.json").read_text())
    vocabulary = checkpoint["vocabulary"]
    before = torch.tensor(checkpoint["initial_embeddings"])
    after = torch.tensor(checkpoint["weights"]["wte"])
    report = {}
    for word in words:
        index = vocabulary.index(word)
        moved = torch.nn.functional.cosine_similarity(before[index], after[index], dim=0).item()
        report[word] = {"token_id": index, "cosine_before_vs_after": round(moved, 3),
                        "neighbors_before": neighbors(before, vocabulary, word),
                        "neighbors_after": neighbors(after, vocabulary, word)}
        print(f"{word} (id {index}): before {report[word]['neighbors_before']}")
        print(f"{' ' * len(word)}          after  {report[word]['neighbors_after']} | cosine(before, after) = {moved:.3f}")
    (run / "neighbors.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
