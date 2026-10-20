# 100-review cost and runtime report

Replayed offline at 2026-10-20T06:22:39Z from saved usage and `rates.csv`. API calls made by this replay: 0.

## cold run

Input `syn100.csv`, 100 rows, statuses {'pending': 0, 'completed': 99, 'quarantined': 1}, measured at 2026-10-20T06:21:16Z. SYNTHETIC INPUT.

Wall clock 0.049 s (summed call durations 0.001 s). New enrichment calls in this run: 2.

API spend $0.0 (enrichment $0.0); cost per 1,000 inputs $0.0; cost per completed record $0.0; throughput 121224.49 records/min; local compute estimate $0.0; unknown costs: False.

| stage | provider | model | effort | requests | ok | failed | records | input | cached | cache write | output | USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| classify | fake | fake-deterministic-v1 | low | 2 | 2 | 0 | 42 | 2773 | 0 | 0 | 2655 | 0.0 |
| verify | fake | fake-deterministic-v1 | low | 1 | 1 | 0 | 10 | 1143 | 0 | 0 | 655 | 0.0 |
| group | fake | fake-deterministic-v1 | low | 7 | 7 | 0 | 53 | 2161 | 0 | 0 | 133 | 0.0 |
| memo | fake | fake-deterministic-v1 | low | 1 | 1 | 0 | 0 | 2630 | 0 | 0 | 247 | 0.0 |

## warm run

Input `syn100.csv`, 100 rows, statuses {'pending': 0, 'completed': 99, 'quarantined': 1}, measured at 2026-10-20T06:21:16Z. SYNTHETIC INPUT.

Wall clock 0.031 s (summed call durations 0.001 s). New enrichment calls in this run: 0.

API spend $0.0 (enrichment $0.0); cost per 1,000 inputs $0.0; cost per completed record $0.0; throughput 191612.9 records/min; local compute estimate $0.0; unknown costs: False.

| stage | provider | model | effort | requests | ok | failed | records | input | cached | cache write | output | USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| classify | fake | fake-deterministic-v1 | low | 2 | 2 | 0 | 42 | 2773 | 0 | 0 | 2655 | 0.0 |
| verify | fake | fake-deterministic-v1 | low | 2 | 2 | 0 | 20 | 2286 | 0 | 0 | 1310 | 0.0 |
| group | fake | fake-deterministic-v1 | low | 14 | 14 | 0 | 106 | 4322 | 0 | 0 | 266 | 0.0 |
| memo | fake | fake-deterministic-v1 | low | 2 | 2 | 0 | 0 | 5260 | 0 | 0 | 494 | 0.0 |

## Full-run projection

Basis: fake:fake-deterministic-v1 at effort low, {'input': 28.01, 'cached_input': 0.0, 'cache_write': 0.0, 'output': 26.82} tokens per record, $0.0 per record, 0.0002 s per record on one worker. Volume {'rows': 660622, 'nonempty': 660609, 'empty': 13, 'distinct_nonempty_texts': 484189}. Controls {'spending_limit_usd': 100.0, 'output_token_cap_per_request': 4000, 'workers': 4, 'fallback_fraction': 0.02}.

| scenario | reuse | first-pass records | enrichment | verification | fallback | total API USD | over limit | hours (1 worker) | hours (workers) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base_with_reuse | True | 484,189 | 0.0 | 0.0 | 0.0 | 0.0 | False | 0.19 | 0.05 |
| base_no_reuse | False | 660,609 | 0.0 | 0.0 | 0.0 | 0.0 | False | 0.2 | 0.05 |
| conservative_with_reuse | True | 484,189 | 0.0 | 0.0 | 0.0 | 0.0 | False | 0.2 | 0.05 |
| conservative_no_reuse | False | 660,609 | 0.0 | 0.0 | 0.0 | 0.0 | False | 0.21 | 0.05 |

One memo and eight grouping calls are counted once; the memo cost is never multiplied by the review count.

Worker speedup is modeled, not measured. Refresh this projection after the 500 and 10,000 checkpoints.
