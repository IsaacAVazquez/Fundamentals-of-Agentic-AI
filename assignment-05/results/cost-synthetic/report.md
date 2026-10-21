# 100-review cost and runtime report

Replayed offline at 2026-10-21T08:55:18Z from saved usage and `rates.csv`. API calls made by this replay: 0.

## cold run

Input `syn100.csv`, 100 rows, statuses {'pending': 0, 'completed': 99, 'quarantined': 1}, measured at 2026-10-20T23:02:40Z. SYNTHETIC INPUT.

Wall clock 0.035 s (summed call durations 0.0 s). New enrichment calls in this run: 2.

API spend $0.0 (enrichment $0.0); cost per 1,000 inputs $0.0; cost per completed record $0.0; throughput 169714.29 records/min; local compute estimate $0.0; unknown costs: False.

| stage | provider | model | effort | requests | ok | failed | records | input | cached | cache write | output | USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| classify | fake | fake-deterministic-v1 | low | 2 | 2 | 0 | 48 | 2959 | 0 | 0 | 2987 | 0.0 |
| verify | fake | fake-deterministic-v1 | low | 1 | 1 | 0 | 10 | 1107 | 0 | 0 | 627 | 0.0 |
| group | fake | fake-deterministic-v1 | low | 7 | 7 | 0 | 54 | 2166 | 0 | 0 | 133 | 0.0 |
| memo | fake | fake-deterministic-v1 | low | 1 | 1 | 0 | 0 | 2670 | 0 | 0 | 249 | 0.0 |

## warm run

Input `syn100.csv`, 100 rows, statuses {'pending': 0, 'completed': 99, 'quarantined': 1}, measured at 2026-10-20T23:02:40Z. SYNTHETIC INPUT.

Wall clock 0.015 s (summed call durations 0.0 s). New enrichment calls in this run: 0.

API spend $0.0 (enrichment $0); cost per 1,000 inputs $0.0; cost per completed record $0.0; throughput 396000.0 records/min; local compute estimate $0.0; unknown costs: False.

| stage | provider | model | effort | requests | ok | failed | records | input | cached | cache write | output | USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| verify | fake | fake-deterministic-v1 | low | 1 | 1 | 0 | 10 | 1107 | 0 | 0 | 627 | 0.0 |
| group | fake | fake-deterministic-v1 | low | 7 | 7 | 0 | 54 | 2166 | 0 | 0 | 133 | 0.0 |
| memo | fake | fake-deterministic-v1 | low | 1 | 1 | 0 | 0 | 2670 | 0 | 0 | 249 | 0.0 |

## Full-run projection

Basis: fake:fake-deterministic-v1 at effort low, {'input': 29.89, 'cached_input': 0.0, 'cache_write': 0.0, 'output': 30.17} tokens per record, $0.0 per record, 0.0001 s per record on one worker. Volume {'rows': 660622, 'nonempty': 660609, 'empty': 13, 'distinct_nonempty_texts': 484189}. Controls {'spending_limit_usd': 100.0, 'output_token_cap_per_request': 4000, 'workers': 4, 'fallback_fraction': 0.02}.

| scenario | reuse | first-pass records | enrichment | verification | fallback | total API USD | over limit | hours (1 worker) | hours (workers) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base_with_reuse | True | 484,189 | 0.0 | 0.0 | 0.0 | 0.0 | False | 0.18 | 0.04 |
| base_no_reuse | False | 660,609 | 0.0 | 0.0 | 0.0 | 0.0 | False | 0.18 | 0.05 |
| conservative_with_reuse | True | 484,189 | 0.0 | 0.0 | 0.0 | 0.0 | False | 0.19 | 0.05 |
| conservative_no_reuse | False | 660,609 | 0.0 | 0.0 | 0.0 | 0.0 | False | 0.19 | 0.05 |

One memo and eight grouping calls are counted once; the memo cost is never multiplied by the review count.

Worker speedup is modeled, not measured. Refresh this projection after the 500 and 10,000 checkpoints.
