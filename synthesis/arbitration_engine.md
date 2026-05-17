# Synthesis — Arbitration Engine

## Purpose
Resolve disagreements between LEON and SOPHIA that cannot be resolved through direct revision. The arbitration engine produces a binding resolution.

## When Arbitration Is Triggered
1. SOPHIA issues a BLOCKING flag that LEON disputes.
2. LEON's revision fails to satisfy SOPHIA's flag after two revision cycles.
3. SOPHIA and LEON reach opposite conclusions on a key claim.
4. A decision quality score falls below 7.0 and neither agent can resolve it.

## Arbitration Process

### Step 1: State the Disagreement
Precisely characterize the point of contention:
- What is the specific claim or decision being disputed?
- What is LEON's position and its supporting evidence?
- What is SOPHIA's position and its supporting evidence?

### Step 2: Classify the Disagreement Type
| Type | Description | Resolution Approach |
|------|-------------|-------------------|
| Factual | Dispute about what is true | Seek additional evidence; apply evidence standards |
| Inferential | Dispute about what the evidence means | Trace logic chains; identify where they diverge |
| Value | Dispute about what matters most | Apply decision quality matrix weightings |
| Scope | Dispute about what is in/out of scope | Return to original goal statement |
| Ethics | Dispute about ethical classification | Ethics framework is authoritative; no arbitration |

### Step 3: Apply Resolution Rules

**Factual disputes**: The higher-evidence-tier position wins. If tied, label the claim `[DISPUTED]` and proceed with documented uncertainty.

**Inferential disputes**: Map the logic chain for both positions. The position with fewer unverified inferential steps wins.

**Value disputes**: Apply the decision quality matrix weightings. The position that maximizes the overall score wins.

**Scope disputes**: The original goal statement is authoritative. Neither agent can expand scope through arbitration.

**Ethics disputes**: Ethics framework governs. Arbitration cannot override ethics blocks.

### Step 4: Arbitration Output
Document the resolution:
```
Arbitration ID: ARB-[number]
Dispute: [description]
Type: [Factual / Inferential / Value / Scope / Ethics]
LEON position: [summary]
SOPHIA position: [summary]
Resolution: [winning position and rationale]
Dissent noted: [yes/no — if yes, the losing position is logged]
```

## Escalation
If arbitration cannot produce a resolution, the issue escalates per `escalation_rules.md`.
