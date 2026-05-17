# LEON — Recursive Planning Protocol

## Purpose
Complex goals cannot be fully specified upfront. Recursive planning breaks them into tiers, solving the top tier concretely while holding lower tiers as provisional.

## Tiered Planning Model

### Tier 1: Immediate Horizon (0–2 weeks)
- Fully specified steps with owners, tools, and acceptance criteria.
- No ambiguity permitted at this tier.

### Tier 2: Near Horizon (2–8 weeks)
- Milestones and phase gates defined.
- Steps are directional but not fully decomposed.
- Dependencies identified but not scheduled.

### Tier 3: Strategic Horizon (8+ weeks)
- Outcomes and north stars only.
- No step-by-step planning — conditions are too uncertain.
- Revisited at each Tier 1 completion cycle.

## Recursion Trigger
After completing any Tier 1 phase:
1. Promote the first Tier 2 milestone to Tier 1 and fully specify it.
2. Revise Tier 2 based on learnings from completed Tier 1.
3. Update Tier 3 if strategic conditions have changed.

## Plan Versioning
Each recursion cycle produces a new plan version. Log version, date, and what changed.

| Version | Date | Changes | Trigger |
|---------|------|---------|---------|
| 1.0 | — | Initial plan | Goal received |
| 1.1 | — | — | Tier 1 complete |

## Anti-Patterns to Avoid
- **False precision**: Over-specifying Tier 3 creates the illusion of control.
- **Plan rigidity**: Refusing to update Tier 2/3 when Tier 1 reveals new information.
- **Scope creep disguised as recursion**: Tier promotions should clarify, not expand.
