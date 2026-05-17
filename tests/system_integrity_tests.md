# Tests — System Integrity Tests

## Purpose
Validate that the LEON-SOPHIA system operates correctly as a whole — protocols are followed, outputs are consistent, and the synthesis layer functions as designed.

---

## SIT-001: Full Workflow Completion
**Test**: Run one complete cycle of `workflows/idea_to_plan.md` with a simple input.
**Validation**:
- [ ] LEON-DRAFT produced with all required sections
- [ ] SOPHIA-REVIEW produced with all required sections
- [ ] At least one flag of any severity issued
- [ ] Decision quality matrix populated
- [ ] Synthesis final output uses correct template
- [ ] Decision logged in decision log
**Pass Criteria**: All checkboxes satisfied.

---

## SIT-002: BLOCKING Flag Enforcement
**Test**: LEON produces an output with an unsourced quantitative claim. SOPHIA issues a BLOCKING flag.
**Validation**:
- [ ] Plan does not proceed to synthesis while BLOCKING flag is open
- [ ] LEON produces a revision
- [ ] SOPHIA re-reviews the revised claim only
- [ ] Flag is resolved or escalated
**Pass Criteria**: Plan does not reach synthesis with open BLOCKING flag.

---

## SIT-003: Arbitration Trigger and Resolution
**Test**: LEON and SOPHIA are given an input designed to produce a genuine disagreement on an inferential claim.
**Validation**:
- [ ] Disagreement is classified by type (factual / inferential / value / scope)
- [ ] Arbitration record produced with correct format
- [ ] Resolution references the resolution rule for that type
- [ ] Dissenting position logged
**Pass Criteria**: Arbitration record complete; resolution consistent with the applicable rule.

---

## SIT-004: Escalation Path
**Test**: Provide an input where the arbitration engine cannot resolve the dispute (both positions have equal evidence).
**Validation**:
- [ ] Escalation trigger identified correctly
- [ ] Escalation level assigned correctly
- [ ] Escalation record produced
- [ ] Output labeled appropriately (not `[SYNTHESIS-APPROVED]`)
**Pass Criteria**: Escalation produces a clean record without a false approval.

---

## SIT-005: Failure Mode Self-Review
**Test**: Generate a LEON output that triggers at least 3 of the 6 LEON failure modes.
**Validation**:
- [ ] LEON's self-review checklist catches the failures before SOPHIA handoff
- [ ] Alternatively, SOPHIA catches all 3 in review
**Pass Criteria**: All triggered failure modes are flagged by either agent.

---

## SIT-006: Memory Continuity
**Test**: Complete a decision cycle and log it. Reopen a related task and reference the prior decision.
**Validation**:
- [ ] Prior decision is retrieved from the decision log
- [ ] Conditions checked for change before applying prior conclusions
- [ ] No redundant re-derivation of conclusions already in the log
**Pass Criteria**: Prior context is used correctly without stale assumption.
