# Workflow — Post-Mortem Reverse Path

## Purpose
Analyze a failure or unexpected outcome by working backward from the result to the root causes, then forward to preventive measures.

## Input
- A description of what happened (incident, failed project, missed goal).
- Timeline of events if available.

## Output
- Root cause analysis with confidence levels.
- Updated failure mode documentation.
- Prevention recommendations approved by synthesis.

## Steps

### Stage 1: Failure Description (LEON)
1. State what happened in precise, factual terms.
2. Identify what was expected vs. what occurred.
3. Establish the timeline of events.
4. Identify who and what was affected.
5. **Gate**: Factual description is complete before analysis begins.

### Stage 2: Reverse Path Analysis (LEON)
Work backward from the failure:
1. **Immediate cause**: What directly caused the failure?
2. **Contributing causes**: What conditions made the failure possible?
3. **Root causes**: What systemic factors created those conditions?
4. **Early warning signals**: What signals, if noticed, would have indicated the problem earlier?
5. Apply the 5-Whys technique at each cause level.

### Stage 3: SOPHIA Adversarial Review
1. SOPHIA applies the pre-mortem mode in reverse: challenge the root cause analysis.
2. Test for alternative causal explanations.
3. Check for attribution bias (blaming individuals rather than systems).
4. Check for recency bias in timeline interpretation.
5. **Output**: Challenges to LEON's causal analysis.

### Stage 4: Synthesis of Root Causes
1. Agreed-upon root causes documented with confidence levels.
2. Disputed causes labeled `[DISPUTED]` with both positions logged.

### Stage 5: Prevention Design (LEON)
For each root cause:
1. Propose a systemic change that addresses the root cause.
2. Identify how this change would have affected the failure timeline.
3. Specify how the change will be implemented and by whom.

### Stage 6: Prevention Review (SOPHIA)
1. Challenge each prevention proposal for feasibility.
2. Identify second-order effects of prevention measures.
3. Confirm prevention addresses root cause, not just symptom.

### Stage 7: Final Output
- Approved root cause analysis.
- Prevention roadmap with owners and timelines.
- Updated `agents/[LEON or SOPHIA]/failure_modes.md` if new failure mode discovered.
