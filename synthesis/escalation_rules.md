# Synthesis — Escalation Rules

## Purpose
Define clear escalation paths when the LEON-SOPHIA synthesis process cannot resolve a dispute or meet the decision gate criteria.

## Escalation Triggers
Escalation is required when:
1. An arbitration produces no resolution after one full cycle.
2. A BLOCKING ethics flag cannot be resolved by any plan modification.
3. A decision quality score remains below 7.0 after two full revision cycles.
4. A fundamental scope disagreement cannot be resolved by returning to the goal statement.
5. External conditions change materially mid-review, invalidating the current analysis.

## Escalation Levels

### Level 1: Extended Review
**When**: One revision cycle is insufficient; more information is needed.
**Action**: Pause the decision. Assign research tasks to gather missing evidence. Resume after a defined deadline.
**Max Duration**: 48 hours for time-sensitive decisions; 1 week otherwise.

### Level 2: Human Judgment Input
**When**: The dispute involves a values trade-off that neither agent is authorized to resolve unilaterally.
**Action**: Present the structured disagreement to the human decision-maker using `final_output_template.md` with `[ESCALATED - PENDING HUMAN INPUT]` status.
**Required Content**: Both positions, supporting evidence, quality scores, and a clear articulation of the values trade-off.

### Level 3: Scope Reframe
**When**: The original goal statement is ambiguous enough that LEON and SOPHIA are legitimately answering different questions.
**Action**: Suspend the current process. Return to goal clarification. LEON restates the goal with the human decision-maker before re-engaging.

### Level 4: No-Decision Record
**When**: No viable path to synthesis exists and the decision cannot be escalated further.
**Action**: Document the unresolved state in the decision log with full context. Log the conditions under which the decision should be revisited.

## Escalation Record Format
```
Escalation ID: ESC-[number]
Trigger: [which trigger condition was met]
Level: [1 / 2 / 3 / 4]
Date Triggered: —
Status: [Open / Resolved / Closed-Unresolved]
Resolution: [description or "none"]
Decision ID (if resolved): DEC-[number]
```
