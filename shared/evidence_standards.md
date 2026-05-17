# Shared — Evidence Standards

## Purpose
Define the minimum evidence quality required for claims made by either LEON or SOPHIA.

## Evidence Tiers

### Tier A: Primary Evidence
Direct, first-hand data or observation. Highest quality.
- Examples: direct measurement, experiment result, primary source document, first-person observation.
- Requirements: Source must be cited; methodology must be available.

### Tier B: Secondary Evidence
Synthesis or analysis of primary sources.
- Examples: peer-reviewed meta-analysis, audit report, verified case study.
- Requirements: Source cited; original primary sources identified.

### Tier C: Analogous Evidence
Evidence from comparable but not identical contexts.
- Examples: industry benchmarks, case studies from similar organizations.
- Requirements: Comparability must be argued, not assumed; key differences noted.

### Tier D: Expert Opinion
Credentialed expert judgment without primary data.
- Requirements: Expert's credentials and potential conflicts of interest noted; opinion labeled as `[INFERRED]` not `[KNOWN]`.

### Tier E: First Principles
Logical derivation from well-established premises.
- Requirements: Premises must be Tier A or B; logic chain must be explicit.

### Tier F: Anecdote / Speculation
Unverified reports or educated guesses.
- Not acceptable as support for any claim without upgrade to higher tier.
- Must be labeled `[SPECULATED]`.

## Minimum Evidence Requirements by Claim Type

| Claim Type | Minimum Tier | Notes |
|-----------|--------------|-------|
| Quantitative (cost, time, performance) | C | Two comparable reference points required |
| Causal claim ("X causes Y") | B | Correlation insufficient |
| Recommendation (preferred option) | C | Must address alternatives |
| Risk assessment | D | Expert judgment acceptable if primary data unavailable |
| Ethics determination | B | Cannot rest on opinion alone |

## Evidence Failure Protocol
If a claim fails the minimum evidence standard:
1. SOPHIA flags it as `[BLOCKING]` with the tier gap specified.
2. LEON must either upgrade the evidence or reclassify the claim (e.g., `[ESTIMATED]` instead of `[KNOWN]`).
3. If neither is possible, the claim is removed from the plan.
