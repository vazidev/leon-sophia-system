# Workflow — Strategic System Design

## Purpose
Design complex systems or architectures where decisions have long-term, high-stakes consequences. This workflow applies the full rigor of the LEON-SOPHIA framework.

## Input
- A system design problem: "Design a system that does X at Y scale."
- Relevant constraints: performance targets, budget, team size, technology constraints.

## Output
- Approved system architecture document.
- Trade-off analysis with synthesis-approved recommendation.
- Implementation roadmap.

## Steps

### Stage 1: Problem Decomposition (LEON)
1. Restate the design problem as a set of specific requirements.
2. Separate functional requirements (what it does) from non-functional requirements (how well it does it).
3. Identify the top 3 quality attributes that matter most (e.g., availability, consistency, latency).
4. Establish design constraints (must use X, cannot use Y, budget ceiling Z).

### Stage 2: Option Architecture (LEON)
For each major design decision:
1. Identify the decision to be made (e.g., "centralized vs. distributed data store").
2. Present 2–3 options with their trade-offs.
3. Recommend an option with explicit reasoning tied to the quality attributes.
4. Map how options interact and compose at the system level.

### Stage 3: Future State Modeling (LEON)
Apply `agents/LEON/future_state_analysis.md`:
1. Model the system at 1×, 10×, and 100× current scale.
2. Identify at what scale each component becomes a bottleneck.
3. Map evolutionary paths: what would need to change as scale grows?

### Stage 4: SOPHIA Architecture Review
1. Challenge each major design decision with the Steel Man mode.
2. Apply adversarial review: what is the single point most likely to fail under production load?
3. Check for survivorship bias in the reference architectures cited.
4. Evaluate security posture at each system boundary.
5. Assess operational complexity: can the team realistically operate this system?

### Stage 5: Trade-Off Synthesis
1. Debate protocol applied to unresolved architecture decisions.
2. Trade-offs documented explicitly: "We chose X over Y, accepting cost Z."
3. Reversibility of major decisions assessed.

### Stage 6: Implementation Roadmap (LEON)
1. Sequence the system build using recursive planning tiers.
2. Identify the minimum viable architecture that delivers core value.
3. Map the path from MVP to full design.

### Stage 7: Final Architecture Document
Format using `templates/architecture_review_template.md` with synthesis approval.
