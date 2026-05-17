# SOPHIA — Adversarial Review Protocol

## Purpose
Actively attempt to break, falsify, or find unacceptable failure modes in a plan before it is executed. The goal is not to destroy the plan — it is to find the breaks before reality does.

## Adversarial Review Modes

### Mode 1: Pre-Mortem
Assume the plan has already failed. Work backward to identify the most likely causes.
1. State: "It is 6 months from now. The plan failed catastrophically. Why?"
2. Generate 5 plausible failure narratives.
3. For each: trace back to the earliest detectable warning sign.
4. Flag any narratives where the warning sign is unmonitored in the current plan.

### Mode 2: Red Team
Simulate an adversarial actor who wants the plan to fail.
1. What is the single weakest point in the plan?
2. If someone wanted to sabotage this plan without being detected, what would they do?
3. What external event (competitor move, market shift, regulation change) would invalidate the core assumption?

### Mode 3: Steel Man
Present the strongest possible case *against* the recommended option.
1. Articulate the best argument for each rejected alternative.
2. Why is the rejected option actually appealing?
3. Under what conditions would the rejected option be correct and the recommended option wrong?

### Mode 4: Edge Case Stress Test
Push the plan to its limits.
1. What happens if demand/load/usage is 10× higher than projected?
2. What happens if a key dependency is unavailable?
3. What happens if the primary owner leaves the project?

## Adversarial Findings Format
```
Mode: [Pre-Mortem / Red Team / Steel Man / Edge Case]
Finding: [description of the discovered weakness]
Severity: [INFO / ADVISORY / WARNING / BLOCKING]
Probability: [Low / Medium / High]
Impact if realized: [Low / Medium / High / Catastrophic]
Recommended response: [what LEON should add or change]
```
