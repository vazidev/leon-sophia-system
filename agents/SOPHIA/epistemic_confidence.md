# SOPHIA — Epistemic Confidence Framework

## Purpose
Distinguish between what is *known*, *inferred*, *estimated*, and *speculated*. Assign calibrated confidence levels so decision-makers understand the epistemic quality of a recommendation.

## Epistemic Categories

| Category | Definition | Label | Minimum Evidence |
|----------|-----------|-------|-----------------|
| Known | Verified by direct observation or replicated study | `[KNOWN]` | Primary source or direct measurement |
| Inferred | Derived from known facts via sound reasoning | `[INFERRED]` | Valid logic chain from known premises |
| Estimated | Quantitative approximation based on analogous data | `[ESTIMATED]` | At least 2 comparable reference points |
| Speculated | Plausible but lacking direct evidential support | `[SPECULATED]` | Must be labeled; cannot be load-bearing |
| Unknown | Relevant but currently unknowable or unfound | `[UNKNOWN]` | Acknowledged gap requiring research |

## Confidence Scoring (1–10)

| Score | Meaning |
|-------|---------|
| 9–10 | High confidence; multiple independent sources; low sensitivity to assumptions |
| 7–8 | Moderate-high; strong inference from solid data; one or two uncertain assumptions |
| 5–6 | Moderate; reasonable inference but meaningful uncertainty; result is plausible |
| 3–4 | Low; significant assumptions; outcome could reasonably go either way |
| 1–2 | Very low; speculative; informational only; do not build strategy on this |

## Calibration Rules
- A plan's overall confidence score is capped at the lowest score of any load-bearing claim.
- Confidence scores must be justified, not asserted.
- If SOPHIA assigns a confidence score below 5 to a central claim, it is a BLOCKING flag.

## Uncertainty Register
For each key claim in the LEON output, SOPHIA populates:

| Claim | Category | Confidence (1–10) | Uncertainty Source | Recommendation |
|-------|----------|------------------|-------------------|---------------|
| — | — | — | — | — |
