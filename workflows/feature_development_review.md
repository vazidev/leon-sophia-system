# Workflow — Feature Development Review

## Purpose
Apply the LEON-SOPHIA framework to a software feature — from idea through architecture, implementation plan, and quality review.

## Input
- Feature idea or request.
- Relevant system context (codebase, architecture, constraints).

## Output
- Approved PRD using `templates/prd_template.md`.
- Architecture review using `templates/architecture_review_template.md`.
- Synthesis-approved implementation plan.

## Steps

### Stage 1: Feature Scoping (LEON)
1. Translate the request into a user story: "As [user], I want [capability] so that [outcome]."
2. Define acceptance criteria — specific, testable conditions.
3. Identify out-of-scope items explicitly.
4. Estimate complexity: Small (< 1 week) / Medium (1–4 weeks) / Large (> 4 weeks).
5. **Output**: Draft PRD section in `templates/prd_template.md`.

### Stage 2: Architecture Analysis (LEON)
1. Map the feature to the existing system architecture.
2. Identify components that will be created, modified, or deprecated.
3. Flag integration points and API surface changes.
4. Assess data model changes required.
5. Propose the implementation approach with two alternatives.
6. **Output**: Architecture review draft in `templates/architecture_review_template.md`.

### Stage 3: SOPHIA Technical Review
1. Challenge the architecture for:
   - Single points of failure introduced.
   - Security surface expansion.
   - Performance regression risks.
   - Backward compatibility breaks.
   - Testing complexity.
2. Review PRD for:
   - Ambiguous acceptance criteria.
   - Missing edge cases.
   - Scope that will expand during implementation.

### Stage 4: Implementation Plan (LEON)
1. Break the feature into tasks with effort estimates.
2. Sequence tasks with dependencies.
3. Identify the critical path.
4. Define the phased rollout plan (if applicable).

### Stage 5: Risk and Quality Review (SOPHIA)
1. Score the plan on the decision quality matrix.
2. Apply bias detection to the option selection.
3. Issue ethics clearance (data handling, user impact).

### Stage 6: Final Output
- Approved PRD.
- Architecture review with SOPHIA clearance.
- Implementation task list with owner assignments.
