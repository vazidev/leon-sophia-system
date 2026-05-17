# Tests — Output Quality Checklist

## Purpose
A quick-reference checklist for evaluating the quality of any output produced by the LEON-SOPHIA system.

## Pre-Synthesis Checklist (applies to `[LEON-DRAFT]`)

### Structure
- [ ] Goal is stated with measurable success criteria
- [ ] Constraints are documented
- [ ] Stakeholders are identified
- [ ] Scope boundaries are explicit
- [ ] At least two approaches are documented
- [ ] Recommended approach is justified
- [ ] Assumptions section is present and complete
- [ ] Load-bearing assumptions are labeled
- [ ] Risk register is populated
- [ ] Dependencies are mapped
- [ ] Challenge surface is provided for SOPHIA

### Content Quality
- [ ] No unsourced quantitative claims
- [ ] No absolute claims without evidence
- [ ] No scope beyond the stated goal
- [ ] Timeline includes confidence range or buffer
- [ ] Pessimistic scenario is documented

## SOPHIA Review Checklist (applies to `[SOPHIA-REVIEW]`)

- [ ] All LEON claims categorized by evidence tier
- [ ] All blocking flags have a resolution path
- [ ] Bias detection checklist completed
- [ ] Adversarial review completed (pre-mortem minimum)
- [ ] Epistemic confidence scores assigned to key claims
- [ ] Ethics review completed and clearance issued or blocked
- [ ] Decision quality matrix fully populated
- [ ] Overall score ≥ 7.0 or escalation triggered

## Final Output Checklist (applies to `[SYNTHESIS-APPROVED]`)

- [ ] No open BLOCKING flags
- [ ] Ethics clearance status documented
- [ ] Decision type recorded (Clean / Conditional / Revised / Arbitrated / Escalated)
- [ ] All arbitration records referenced by ID
- [ ] Open advisories documented with resolution timeline
- [ ] Implementation next steps include owner and timeline
- [ ] Decision logged with correct Decision ID
- [ ] Dissenting positions logged (if any)

## Output Quality Score
Score 1 point for each checked item. Divide by total applicable items.
- 90–100%: High quality output
- 75–89%: Acceptable, with noted gaps
- Below 75%: Requires revision before use
