# Tests — Reasoning Stress Tests

## Purpose
Validate the logical quality and robustness of LEON's planning and SOPHIA's critique under difficult reasoning conditions.

---

## RST-001: Circular Reasoning Detection
**Test**: Submit a plan whose core justification is circular ("We should use X because X is the best option for this kind of problem, and this is the kind of problem where X is best").
**Expected**: SOPHIA detects the circular structure and requires a non-circular evidence chain.
**Pass Criteria**: SOPHIA identifies the circularity and blocks the claim until an independent justification is provided.

---

## RST-002: False Dichotomy Challenge
**Test**: Submit a plan that presents only two options (A and B) and argues A must be chosen because B is unacceptable, without exploring other options.
**Expected**: SOPHIA challenges the two-option framing and requests at least one additional alternative.
**Pass Criteria**: SOPHIA flags the false dichotomy and LEON produces a third option.

---

## RST-003: Correlation vs. Causation
**Test**: Submit a plan that argues "Teams using methodology X have 30% faster delivery, therefore we should adopt X."
**Expected**: SOPHIA classifies the correlation claim as `[INFERRED]` not `[KNOWN]` and requests causal evidence.
**Pass Criteria**: SOPHIA distinguishes correlation from causation and re-labels the claim.

---

## RST-004: Scope Creep Under Revision
**Test**: SOPHIA flags a BLOCKING issue. LEON's revision resolves the flag but expands scope beyond the original goal.
**Expected**: SOPHIA approves the flag resolution but raises a new advisory or warning about scope expansion.
**Pass Criteria**: SOPHIA catches scope expansion in revision, not only in initial review.

---

## RST-005: High-Confidence Low-Evidence
**Test**: Submit a plan where the recommendation is stated with 95% confidence but supporting evidence is only Tier D (expert opinion).
**Expected**: SOPHIA flags the confidence-evidence mismatch and downgrades the stated confidence.
**Pass Criteria**: SOPHIA applies the epistemic confidence framework and issues a corrected confidence score.

---

## RST-006: Multi-Step Inference Chain
**Test**: Submit a plan with a 4-step inference chain (A → B → C → D → recommendation) where step C is based on Tier F (speculative) evidence.
**Expected**: SOPHIA traces the inference chain, identifies the weak link at step C, and blocks the chain from being load-bearing.
**Pass Criteria**: SOPHIA identifies the specific inference step that fails the evidence standard.

---

## RST-007: LEON Self-Consistency
**Test**: Submit a plan where the risk register contradicts the timeline (e.g., "High likelihood that dependency X is unavailable" but timeline assumes X available from day 1).
**Expected**: LEON's self-review (failure modes checklist) should catch this before SOPHIA handoff. If not, SOPHIA catches it.
**Pass Criteria**: Contradiction is flagged before final output by either agent.
