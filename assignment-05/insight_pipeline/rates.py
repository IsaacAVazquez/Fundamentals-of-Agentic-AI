"""Editable price table and the one cost formula: billed units x price per unit.

Input, cached-input, cache-write, and output tokens are mutually exclusive categories.
Reasoning tokens are billed as output by both providers and are never counted twice.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .config import DEFAULT_RATES

UNITS = ("input", "cached_input", "cache_write", "output")


def write_default_rates(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["provider", "model", "unit", "usd_per_million_tokens", "currency", "source_and_date"])
        for provider, model, unit, price, source in DEFAULT_RATES:
            w.writerow([provider, model, unit, price, "USD", source])


def load_rates(path: Path | None) -> dict[tuple[str, str, str], float]:
    rates: dict[tuple[str, str, str], float] = {}
    if path and Path(path).exists():
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                rates[(row["provider"], row["model"], row["unit"])] = float(row["usd_per_million_tokens"])
    else:
        for provider, model, unit, price, _ in DEFAULT_RATES:
            rates[(provider, model, unit)] = price
    return rates


def call_cost(rates: dict, provider: str, model: str, usage: dict) -> tuple[float, bool]:
    """Return (usd, priced). priced is False when a unit has no rate, so the caller can label it unknown."""
    total = 0.0
    priced = True
    for unit in UNITS:
        tokens = int(usage.get(f"{unit}_tokens", 0) or 0)
        if tokens == 0:
            continue
        price = rates.get((provider, model, unit))
        if price is None:
            priced = False
            continue
        total += tokens * price / 1_000_000
    return round(total, 8), priced
