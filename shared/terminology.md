# Shared — Terminology

## System Terms

**Load-bearing assumption**: An assumption whose failure would cause the plan to fail or require fundamental redesign. Distinguished from "supporting assumptions" whose failure would require adjustments but not collapse.

**Challenge surface**: A list of the most stress-testable claims in a LEON output, provided by LEON to SOPHIA to focus the review on high-value targets.

**Synthesis**: The process by which the arbitration engine reconciles LEON's plan and SOPHIA's review into a final, approved output.

**Blocking flag**: A SOPHIA finding that prevents the plan from proceeding to synthesis until resolved. Blocking flags require a resolution path.

**Phase gate**: A milestone at which the plan is re-evaluated before the next phase begins.

**Epistemic confidence**: The degree of certainty warranted by the available evidence, expressed as a 1–10 score.

**Pre-mortem**: A planning exercise where future failure is assumed and the team works backward to identify causes. Distinct from post-mortem (analysis after actual failure).

## Evidence Terms

**Primary source**: Direct, first-hand data or observation from the original producer of the information.

**Tier gap**: The difference between the evidence tier required for a claim type and the tier of evidence actually provided.

**Analogous evidence**: Evidence from comparable but non-identical contexts, used when direct evidence is unavailable.

## Agent Terms

**`[LEON-DRAFT]`**: Output produced by LEON, not yet reviewed by SOPHIA.

**`[LEON-REVISED]`**: LEON output updated in response to SOPHIA findings.

**`[LEON-FINAL]`**: LEON output approved through the full synthesis process.

**`[SOPHIA-REVIEW]`**: SOPHIA's review output, formatted per `sophia_review_template.md`.

**`[SYNTHESIS-APPROVED]`**: Final output from the synthesis layer, cleared by both agents.

## Quality Terms

**Decision quality score**: The composite score (1–10) produced by the decision quality matrix. Minimum 7.0 required for synthesis approval.

**Adversarial review**: A structured attempt to find flaws in a plan by simulating failure, opposition, or edge cases.

**Bias clearance**: SOPHIA's determination that no blocking biases have been detected in the reviewed output.
