# Workflow — Tool Gap Analysis

## Purpose
Systematically identify missing capabilities or tooling that are blocking progress, and produce a prioritized tool creation roadmap.

## Input
- A process or workflow being analyzed.
- Description of pain points, manual steps, or recurring blockers.

## Output
- Prioritized tool gap registry.
- Top-priority tool specifications approved for development.

## Steps

### Stage 1: Process Mapping (LEON)
1. Document the current process step-by-step.
2. For each step, note: who does it, how long it takes, how often it recurs, and the error rate.
3. Identify manual steps that could plausibly be automated.
4. Identify steps where output is inconsistent or quality varies.

### Stage 2: Gap Identification (LEON)
For each candidate gap:
1. Name the gap: "There is no tool that [does X]."
2. Quantify the cost: time lost per occurrence × recurrence rate.
3. Assess the risk of the gap: what goes wrong when the gap is unaddressed?
4. Check if an existing tool could be configured or extended to fill the gap.

### Stage 3: SOPHIA Gap Review
1. Challenge the cost estimates for optimism bias.
2. Check for tool gaps that are really process gaps (the tool won't help if the process is broken).
3. Identify second-order risks: new tools introduce maintenance burden, onboarding cost, and failure modes.
4. Flag any proposed tools that solve the symptom rather than the root cause.

### Stage 4: Prioritization (Synthesis)
Score each gap on:
| Criterion | Weight |
|-----------|--------|
| Time saved per year | 30% |
| Risk reduction | 25% |
| Implementation complexity (inverse) | 20% |
| Recurrence frequency | 15% |
| Strategic alignment | 10% |

Rank gaps by weighted score. Top 3 proceed to specification.

### Stage 5: Tool Specification (LEON)
For each top-priority gap, produce a specification using `agents/LEON/tool_creation_protocol.md`.

### Stage 6: Specification Review (SOPHIA)
1. Validate that the spec addresses the root gap.
2. Challenge the success criteria for measurability.
3. Assess failure mode completeness.

### Stage 7: Final Output
- Approved gap registry with priority rankings.
- Approved specifications for top-priority tools.
- Deferred gaps logged for quarterly review.
