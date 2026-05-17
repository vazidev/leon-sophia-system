# Tests — Bias Test Cases

## Purpose
Validate that SOPHIA's bias detection is functioning correctly by presenting known-biased inputs and verifying detection.

## Test Format
Each test provides a biased input, the expected bias type detected, minimum expected severity, and the expected correction.

---

## TC-BIAS-001: Confirmation Bias
**Input**: A plan recommending Technology A that cites three sources supporting A, none acknowledging known drawbacks of A, and no comparison to alternatives.
**Expected Detection**: Confirmation Bias
**Expected Severity**: WARNING or higher
**Expected Correction**: SOPHIA should request evidence of A's drawbacks and alternative comparison.
**Pass Criteria**: SOPHIA flags confirmation bias and specifies which claims lack counter-evidence.

---

## TC-BIAS-002: Anchoring Bias
**Input**: A timeline estimate of "30 days" where the first message in context mentioned "let's finish in a month" without justification.
**Expected Detection**: Anchoring Bias
**Expected Severity**: WARNING
**Expected Correction**: SOPHIA should request an independent estimate ignoring the initial anchor.
**Pass Criteria**: SOPHIA identifies the anchor value and challenges the estimate's independence.

---

## TC-BIAS-003: Planning Fallacy
**Input**: A project plan with estimates totaling 6 weeks, no buffer, no pessimistic scenario, and no comparable historical completion times cited.
**Expected Detection**: Planning Fallacy (Optimism Bias)
**Expected Severity**: BLOCKING (plan viability depends on tight estimates)
**Expected Correction**: Apply 1.5× multiplier; require pessimistic scenario.
**Pass Criteria**: SOPHIA applies the multiplier test and requires downside modeling.

---

## TC-BIAS-004: Survivorship Bias
**Input**: A recommendation to use a startup-style development process citing 3 successful companies that used it, with no mention of failure rates.
**Expected Detection**: Survivorship Bias
**Expected Severity**: WARNING
**Expected Correction**: SOPHIA requests base rate of success/failure for this approach.
**Pass Criteria**: SOPHIA asks for failure-rate data alongside success examples.

---

## TC-BIAS-005: In-Group Bias
**Input**: A vendor recommendation that selects a tool built by the same company as the proposing team's primary platform, with superficial analysis of alternatives.
**Expected Detection**: In-Group Bias
**Expected Severity**: WARNING
**Expected Correction**: External benchmarking or independent evaluation required.
**Pass Criteria**: SOPHIA flags the potential conflict and requires external comparison.

---

## TC-BIAS-006: Clean Input (Control)
**Input**: A plan that presents two options with equal evidence quality, cites primary sources, models both optimistic and pessimistic cases, and acknowledges known limitations.
**Expected Detection**: No blocking biases
**Expected Result**: SOPHIA may note advisories but should not issue blocking flags.
**Pass Criteria**: SOPHIA issues bias clearance without blocking flags.
