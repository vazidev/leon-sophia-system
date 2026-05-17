# SOPHIA — Bias Detection Framework

## Purpose
Systematically identify cognitive and structural biases that may have shaped the plan or analysis under review.

## Bias Checklist

### Confirmation Bias
**Signal**: Plan only cites evidence that supports the recommended option; contradicting evidence is absent.
**Test**: Can you find one credible source that argues against the recommendation? If yes and it's not addressed, flag it.
**Severity**: BLOCKING if central to a major claim.

### Anchoring Bias
**Signal**: Estimates cluster suspiciously close to an initial number mentioned early in the discussion.
**Test**: Would the estimates change significantly if the anchor number had been different?
**Severity**: WARNING.

### Planning Fallacy
**Signal**: Timelines and costs are consistently optimistic with no downside modeling.
**Test**: Apply a 1.5× multiplier to all time and cost estimates. Does the plan still make sense?
**Severity**: BLOCKING if plan viability depends on tight estimates.

### Survivorship Bias
**Signal**: Plan cites successful examples without acknowledging comparable failures.
**Test**: Are there known failures in similar contexts that are unaddressed?
**Severity**: WARNING to BLOCKING depending on stakes.

### Authority Bias
**Signal**: A claim is justified primarily because an authority figure said it, without independent evidence.
**Test**: If the authority hadn't endorsed it, would the claim still hold?
**Severity**: ADVISORY.

### In-Group Bias
**Signal**: Solutions consistently favor the proposing team's tools, methods, or vendors.
**Test**: Would an external evaluator recommend the same solution?
**Severity**: WARNING.

### Status Quo Bias
**Signal**: The "do nothing" option is not seriously evaluated; change is assumed to be better.
**Test**: What are the costs and risks of maintaining the current state?
**Severity**: ADVISORY to WARNING.

### Recency Bias
**Signal**: Plan heavily weights recent data points while ignoring longer historical trends.
**Test**: How does the recommendation hold under a 3-year vs. 3-month data window?
**Severity**: WARNING.

## Bias Report Format
For each detected bias:
```
Bias: [name]
Location: [section or claim in LEON output]
Evidence of bias: [what triggered detection]
Effect on plan: [how this bias distorts the recommendation]
Correction: [what would need to change to remove the bias]
Severity: [INFO / ADVISORY / WARNING / BLOCKING]
```
