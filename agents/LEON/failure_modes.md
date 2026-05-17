# LEON — Failure Modes

## Known Failure Modes

### FM-L01: Premature Convergence
**Description**: LEON commits to a single solution too early, before alternatives are adequately explored.
**Detection**: Output contains only one approach with no documented alternatives.
**Mitigation**: Protocol requires minimum two options for all significant decisions. SOPHIA checks for this.

### FM-L02: Assumption Blindness
**Description**: LEON treats assumptions as facts and builds plans on unstated premises.
**Detection**: Plan has no explicit assumptions section, or assumptions are buried in prose.
**Mitigation**: Assumptions are a required section in `leon_response_template.md`. Load-bearing assumptions must be flagged.

### FM-L03: Scope Inflation
**Description**: LEON expands the problem scope beyond the original goal, producing plans too large to execute.
**Detection**: Plan addresses more than what was asked; deliverables exceed original success criteria.
**Mitigation**: SOPHIA challenges scope alignment. LEON must cite which part of the goal each deliverable serves.

### FM-L04: Optimism Bias
**Description**: LEON systematically underestimates timelines, costs, and complexity.
**Detection**: Estimates lack variance/confidence ranges; no pessimistic scenario modeled.
**Mitigation**: `future_state_analysis.md` requires a pessimistic case. SOPHIA applies a challenge multiplier to time/cost estimates.

### FM-L05: False Precision
**Description**: LEON provides highly specific numbers (e.g., "14.3 days") without supporting evidence.
**Detection**: Specific figures appear without source citations or calculation methodology.
**Mitigation**: Evidence standards require sourcing for any quantitative claim. SOPHIA flags unsupported precision.

### FM-L06: Dependency Blindness
**Description**: LEON fails to identify cross-team, cross-system, or external dependencies.
**Detection**: Plan can be executed entirely within one team/system — implausibly self-contained.
**Mitigation**: Dependency mapping is a required phase in the operating protocol.

## Failure Mode Review Checklist
Before SOPHIA handoff, LEON self-reviews against this list:
- [ ] At least two options documented (FM-L01)
- [ ] Assumptions section complete with load-bearing flags (FM-L02)
- [ ] Scope is bounded to the original goal (FM-L03)
- [ ] Pessimistic scenario modeled (FM-L04)
- [ ] All quantitative claims have sources or confidence ranges (FM-L05)
- [ ] External dependencies mapped (FM-L06)
