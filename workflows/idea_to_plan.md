# Workflow — Idea to Plan

## Purpose
Transform a raw idea or request into a fully reviewed, synthesis-approved plan ready for execution.

## Input
- A goal, idea, or request in any form (can be vague).

## Output
- A `[SYNTHESIS-APPROVED]` plan using `synthesis/final_output_template.md`.

## Steps

### Stage 1: Goal Crystallization (LEON)
1. Receive the raw idea.
2. Restate as a goal with measurable success criteria.
3. Identify constraints and stakeholders.
4. Confirm scope boundaries.
5. **Gate**: Goal statement agreed upon before proceeding.

### Stage 2: Recursive Planning (LEON)
1. Map Tier 1, 2, and 3 horizons per `agents/LEON/recursive_planning.md`.
2. Generate 2–3 approach options.
3. Select and justify a recommended approach.
4. Construct phase plan with milestones and risk register.
5. Prepare challenge surface for SOPHIA.
6. **Output**: `[LEON-DRAFT]` using `templates/leon_response_template.md`.

### Stage 3: Adversarial Review (SOPHIA)
1. Run full review per `agents/SOPHIA/operating_protocol.md`.
2. Apply bias detection, adversarial review, epistemic confidence, and ethics review.
3. Score on decision quality matrix.
4. **Output**: `[SOPHIA-REVIEW]` using `templates/sophia_review_template.md`.

### Stage 4: Revision Cycle (LEON)
1. LEON responds to each SOPHIA flag.
2. Revise plan for BLOCKING flags; document response for all others.
3. Re-submit as `[LEON-REVISED]`.
4. SOPHIA re-reviews revised sections only.
5. **Gate**: No open BLOCKING flags.

### Stage 5: Synthesis
1. Apply decision protocol from `synthesis/decision_protocol.md`.
2. Run arbitration if needed.
3. Produce final output using `synthesis/final_output_template.md`.
4. Log decision in `templates/decision_log_template.md`.

## Estimated Cycle Time
- Simple ideas: 1 revision cycle.
- Complex plans: 2–3 revision cycles.
- Escalated decisions: variable.
