# Shared — Context Rules

## Purpose
Define what context must be loaded, preserved, and passed between agents to ensure coherent reasoning.

## Required Context at Task Start
Every task session must establish:
1. **Goal statement**: Exact wording of what is being asked.
2. **Constraints**: Known constraints (time, budget, technical, political).
3. **Stakeholders**: Who is affected by or has authority over this decision.
4. **Prior decisions**: Any relevant prior decisions from the decision log.
5. **Scope boundaries**: What is explicitly out of scope.

## Context Handoff Rules (LEON → SOPHIA)
When LEON passes output to SOPHIA, the handoff package must include:
- The original goal statement (unchanged)
- LEON's interpretation of the goal
- All assumptions made during planning
- The "challenge surface" (list of claims most worth testing)

## Context Preservation Rules
- The original goal statement must not be paraphrased or summarized once set.
- Constraints established at task start remain in force unless explicitly updated.
- Scope boundaries set at task start are binding on both agents.

## Context Contamination Rules
The following must NOT bleed into the current task context:
- Preferences or conclusions from a prior unrelated task
- External opinions not cited as evidence
- Emotional framing or urgency not grounded in the actual constraints

## Scope Creep Prevention
If either agent believes the scope needs to change, they must:
1. Explicitly flag the scope change request.
2. State why the original scope is insufficient.
3. Get acknowledgment from the synthesis layer before expanding scope.
