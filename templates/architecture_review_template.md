# Architecture Review Template

**System / Feature Name**: —
**Decision ID**: DEC-[number]
**Status**: Draft / Under Review / Approved
**Author**: LEON
**SOPHIA Clearance**: Pending / CLEARED / ADVISORY / BLOCKED
**Date**: —
**Version**: 1.0

---

## Context
_Brief description of what is being built and why. Link to PRD if applicable._

---

## Quality Attributes (Priority Order)
_The top 3–5 attributes that most constrain the design._
1. —
2. —
3. —

---

## System Diagram
_ASCII or reference to diagram. Describe components and their relationships._

```
[Component A] --> [Component B] --> [Component C]
                       |
                  [Component D]
```

---

## Component Breakdown

| Component | Responsibility | Technology | Owned By |
|-----------|--------------|-----------|---------|
| — | — | — | — |

---

## Data Flow
_How data moves through the system for the primary use case._
1. —
2. —

---

## API Surface

| Endpoint / Interface | Producer | Consumer | Protocol | Auth |
|---------------------|---------|---------|---------|------|
| — | — | — | — | — |

---

## Design Decisions

### Decision 1: [Topic]
**Options considered**:
- Option A: — (pros: —, cons: —)
- Option B: — (pros: —, cons: —)

**Decision**: Option A
**Rationale**: —
**Trade-off accepted**: —

---

## Non-Functional Analysis

| Attribute | How Achieved | Risk | Measurement |
|-----------|-------------|------|------------|
| Availability | — | — | — |
| Scalability | — | — | — |
| Security | — | — | — |
| Observability | — | — | — |
| Recoverability | — | — | — |

---

## Dependencies and Integration Points
| System | Integration Type | Risk | Fallback |
|--------|----------------|------|---------|
| — | API / Event / DB / SDK | — | — |

---

## Scale Analysis

| Dimension | Current Load | 10× Load | 100× Load | Bottleneck? |
|-----------|-------------|---------|---------|------------|
| — | — | — | — | Yes/No |

---

## Migration / Rollout Plan
_How does the existing system transition to this architecture?_

---

## SOPHIA Findings Summary
_Populated after SOPHIA review._

| Finding | Severity | Resolution |
|---------|----------|-----------|
| — | — | — |
