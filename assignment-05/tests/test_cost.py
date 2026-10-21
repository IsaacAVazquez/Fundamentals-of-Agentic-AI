import csv
import json

from insight_pipeline.classify import Controls
from insight_pipeline.cost import rebuild_usage, replay, run_pilot
from insight_pipeline.rates import call_cost, load_rates


def test_cost_formula_and_rate_doubling(synthetic_csv, tmp_path):
    cost_dir = tmp_path / "cost"
    run_pilot(synthetic_csv, cost_dir, Controls(backend="fake", batch_size=25), synthetic=True)
    cold = json.loads((cost_dir / "measured_cold.json").read_text())
    assert cold["rows"] == 300 and cold["new_enrichment_calls_this_run"] > 0
    run_pilot(synthetic_csv, cost_dir, Controls(backend="fake", batch_size=25), warm=True, synthetic=True)
    warm = json.loads((cost_dir / "measured_warm.json").read_text())
    assert warm["new_enrichment_calls_this_run"] == 0
    # The warm run's usage counts only its own calls, not the cold run's calls in the shared state file.
    warm_usage = list(csv.DictReader(open(cost_dir / "usage_warm.csv", newline="")))
    warm_calls = [json.loads(line) for line in open(cost_dir / "pilot_calls_warm.jsonl")]
    assert "classify" not in {u["stage"] for u in warm_usage}
    assert sum(int(u["requests"]) for u in warm_usage) == len(warm_calls) > 0
    # And the usage files can be rebuilt offline from the call logs, byte for byte.
    saved = {name: (cost_dir / name).read_bytes() for name in ("usage_cold.csv", "usage_warm.csv", "usage.csv")}
    rebuild_usage(cost_dir)
    assert {name: (cost_dir / name).read_bytes() for name in saved} == saved
    # Give the fake model real prices and check spend doubles when prices double, with time untouched.
    rates = cost_dir / "rates.csv"
    rows = list(csv.DictReader(open(rates, newline="")))
    for r in rows:
        if r["provider"] == "fake":
            r["usd_per_million_tokens"] = "1.0"
    with open(rates, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    one = replay(cost_dir)
    for r in rows:
        if r["provider"] == "fake":
            r["usd_per_million_tokens"] = "2.0"
    doubled = tmp_path / "rates2.csv"
    with open(doubled, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    two = replay(cost_dir, rates_override=doubled)
    assert one["runs"]["cold"]["api_cost_usd"] > 0
    assert abs(two["runs"]["cold"]["api_cost_usd"] - 2 * one["runs"]["cold"]["api_cost_usd"]) < 1e-6
    assert two["runs"]["cold"]["wall_clock_seconds"] == one["runs"]["cold"]["wall_clock_seconds"]
    # Changing projected volume changes the projection, never the measured pilot.
    proj = json.loads((cost_dir / "projection.json").read_text())
    proj["nonempty"] = 10
    proj["distinct_nonempty_texts"] = 5
    p2 = tmp_path / "proj.json"
    p2.write_text(json.dumps(proj))
    three = replay(cost_dir, projection_override=p2)
    assert three["runs"]["cold"]["api_cost_usd"] == one["runs"]["cold"]["api_cost_usd"]
    assert three["projection"]["scenarios"][0]["first_pass_records"] == 5
    assert (cost_dir / "report.md").exists() and (cost_dir / "pilot_calls.jsonl").exists()


def test_call_cost_units_are_exclusive():
    rates = load_rates(None)
    usd, priced = call_cost(rates, "anthropic", "claude-haiku-5-5", {"input_tokens": 1_000_000, "cached_input_tokens": 1_000_000, "output_tokens": 1_000_000})
    assert priced and abs(usd - (0.10 + 0.01 + 0.50)) < 1e-9
