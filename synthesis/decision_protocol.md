# Synthesis — Decision Protocol

## Purpose
Define exactly how a final decision is made once LEON and SOPHIA have completed their exchange.

## Decision Gate Checklist
A decision can only enter the final output stage when ALL of the following are true:
- [ ] No BLOCKING flags from SOPHIA are open
- [ ] Ethics clearance issued (`ETHICS-CLEARED` or `ETHICS-ADVISORY`)
- [ ] Decision quality score ≥ 7.0
- [ ] All disputed claims are resolved (via debate or arbitration)
- [ ] All load-bearing assumptions are documented
- [ ] Risk register is populated for material risks

## Decision Types

### Type 1: Clean Approval
All gate criteria met. LEON's recommendation proceeds with SOPHIA's clearance.

### Type 2: Conditional Approval
Non-blocking flags remain. Plan proceeds with documented conditions and a timeline to resolve advisories.

### Type 3: Revised Approval
LEON revised the plan in response to SOPHIA's feedback. The revised plan meets all gate criteria.

### Type 4: Arbitrated Approval
One or more points resolved via the arbitration engine. Dissenting positions logged.

### Type 5: Escalated Decision
Gate criteria cannot be met. Decision escalated per `escalation_rules.md`.

## Final Decision Record
```
Decision ID: DEC-[number]
Date: —
Goal: —
Recommendation: —
Decision Type: [1 / 2 / 3 / 4 / 5]
Quality Score: —
Ethics Status: —
SOPHIA Clearance: [CLEARED / ADVISORY / conditions listed]
Open Advisories: [list or "none"]
Arbitration IDs: [list or "none"]
Rationale Summary: —
```

## Decision Log
All decisions are appended to `templates/decision_log_template.md`.
