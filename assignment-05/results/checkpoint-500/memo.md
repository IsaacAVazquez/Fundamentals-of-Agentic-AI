## Recommendation
Prioritize the free-user restriction on choosing and replaying songs [ISS-usability], which has the highest priority score (157) [C11] and the most complaints (68) [C7] among the 500 completed records [C2]. Scope the next quarter's effort to this issue, with playback stability [ISS-playback] as the closely watched second item.

## Why this issue
[ISS-usability] ranks first on priority score (157) [C11] and complaint count (68) [C7], with a mean severity of 2.308824 [C10]. Its evidence quotes describe users unable to pick or repeat songs and a navigation problem that sends them to unexpected tracks, for example review cc39673b-e332-4f1d-a6c6-ce378a715dcb and 08d3a5a9-1ec1-4b10-a5c8-393da33843e1. Playback [ISS-playback] has a higher mean severity (3.405405) [C16] and a priority score of 126 [C17], and its quotes describe stops and crashes, for example 179d79f7-d052-490f-a9d6-f97525b32642. Mean severity alone would favor playback, so the choice rests on the combined score and complaint volume.

## Alternatives considered
- [ISS-playback]: priority score 126 [C17], 37 complaints [C13], 5 cancellation-intent records [C14]. Strong severity signal; a credible alternative if the team weights severity over volume.
- [ISS-other]: priority score 107 [C23], 58 complaints [C19], reflecting broad update-related dissatisfaction. Its mean severity is the lowest (1.844828) [C22], and its theme is diffuse, so it is harder to act on.
- [ISS-billing]: priority score 80 [C29], 31 complaints [C25], with quotes about premium purchase failures such as 1d1480fb-0142-46da-8570-45bf3983bf6d. Its concrete purchase-blocking failures make it a candidate for a targeted fix.

## Limitations
- Reviews are self-selected public app store posts, not a representative customer population.
- The data contains no account, plan, or cancellation records, so cancellation intent is expressed in reviews and not observed. Counts such as 5 cancellation-intent records for [ISS-usability] [C8] describe stated intent only.
- Labels come from a model checked against a 50-review golden set and a verifier sample; see evals/.
- Quarantined records [C3] and pending records [C4] are zero in this run. Partial months 2022-05 and 2023-11 are flagged in the scope and may affect trend reading.
- The ranking reflects the sampled reviews only and does not establish how much any issue affects users overall.
