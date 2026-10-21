# 100-review cost and runtime report

Replayed offline at 2026-10-20T23:26:18Z from saved usage and `rates.csv`. API calls made by this replay: 0.

## cold run

Input `cost_100.csv`, 100 rows, statuses {'pending': 0, 'completed': 100, 'quarantined': 0}, measured at 2026-10-20T23:25:56Z.

Wall clock 56.545 s (summed call durations 55.905 s). New enrichment calls in this run: 4.

API spend $0.008234 (enrichment $0.005919); cost per 1,000 inputs $0.05919; cost per completed record $8.234e-05; throughput 106.11 records/min; local compute estimate $0.0; unknown costs: False.

| stage | provider | model | effort | requests | ok | failed | records | input | cached | cache write | output | USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| classify | anthropic | claude-haiku-5-5 | low | 4 | 4 | 0 | 100 | 6921 | 6628 | 0 | 10321 | 0.005919 |
| verify | anthropic | claude-haiku-5-5 | low | 1 | 1 | 0 | 10 | 800 | 1677 | 0 | 998 | 0.000596 |
| group | anthropic | claude-haiku-5-5 | low | 7 | 7 | 0 | 37 | 4447 | 0 | 0 | 534 | 0.000712 |
| memo | anthropic | claude-haiku-5-5 | low | 1 | 1 | 0 | 0 | 4124 | 817 | 0 | 1172 | 0.001007 |

## warm run

Input `cost_100.csv`, 100 rows, statuses {'pending': 0, 'completed': 100, 'quarantined': 0}, measured at 2026-10-20T23:26:18Z.

Wall clock 22.169 s (summed call durations 77.524 s). New enrichment calls in this run: 0.

API spend $0.010588 (enrichment $0.005919); cost per 1,000 inputs $0.05919; cost per completed record $0.00010588; throughput 270.65 records/min; local compute estimate $0.0; unknown costs: False.

| stage | provider | model | effort | requests | ok | failed | records | input | cached | cache write | output | USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| classify | anthropic | claude-haiku-5-5 | low | 4 | 4 | 0 | 100 | 6921 | 6628 | 0 | 10321 | 0.005919 |
| verify | anthropic | claude-haiku-5-5 | low | 2 | 2 | 0 | 20 | 1600 | 3354 | 0 | 2015 | 0.001201 |
| group | anthropic | claude-haiku-5-5 | low | 14 | 14 | 0 | 74 | 8894 | 0 | 0 | 1061 | 0.00142 |
| memo | anthropic | claude-haiku-5-5 | low | 2 | 2 | 0 | 0 | 8248 | 1634 | 0 | 2413 | 0.002048 |

## Full-run projection

Basis: anthropic:claude-haiku-5-5 at effort low, {'input': 69.21, 'cached_input': 66.28, 'cache_write': 0.0, 'output': 103.21} tokens per record, $5.919e-05 per record, 0.3589 s per record on one worker. Volume {'rows': 660622, 'nonempty': 660609, 'empty': 13, 'distinct_nonempty_texts': 484189}. Controls {'spending_limit_usd': 100.0, 'output_token_cap_per_request': 8000, 'workers': 4, 'fallback_fraction': 0.0}.

| scenario | reuse | first-pass records | enrichment | verification | fallback | total API USD | over limit | hours (1 worker) | hours (workers) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base_with_reuse | True | 484,189 | 29.23 | 0.08 | 0.0 | 29.34 | False | 49.41 | 12.35 |
| base_no_reuse | False | 660,609 | 39.88 | 0.08 | 0.0 | 39.99 | False | 67.35 | 16.84 |
| conservative_with_reuse | True | 484,189 | 45.14 | 0.12 | 0.0 | 45.28 | False | 76.2 | 19.05 |
| conservative_no_reuse | False | 660,609 | 61.58 | 0.12 | 0.0 | 61.73 | False | 103.91 | 25.98 |

One memo and eight grouping calls are counted once; the memo cost is never multiplied by the review count.

Worker speedup is modeled, not measured. Refresh this projection after the 500 and 10,000 checkpoints.
