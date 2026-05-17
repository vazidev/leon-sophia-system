# Shared — Memory Protocol

## Purpose
Define how LEON and SOPHIA retain and retrieve context across sessions to maintain continuity without redundant recalculation.

## Memory Tiers

### Tier 1: Session Memory
Exists for the duration of a single session. Automatically available to both agents. Not persisted.

### Tier 2: Decision Log Memory
Persisted in `templates/decision_log_template.md`. Retrievable by decision ID. Reviewed at the start of any related follow-up task.

### Tier 3: System Memory
Stored in the agent identity and protocol files. Updated when a lasting behavioral change is warranted (e.g., a new failure mode is discovered).

## Memory Update Rules
1. **Session memory** requires no explicit save action.
2. **Decision log** must be updated at the end of every completed synthesis cycle.
3. **System memory** (protocol files) updated only when a pattern recurs 3+ times or a new permanent constraint is identified.

## Retrieval Protocol
Before beginning any task:
1. Check if a related decision log entry exists.
2. If yes: load the prior context, note what has changed since that decision.
3. Do not re-derive conclusions that are already in the decision log unless conditions have changed.

## Memory Anti-Patterns
- **Stale memory**: Using a prior decision without checking if conditions have changed.
- **Over-reliance**: Treating memory as a substitute for current analysis.
- **Under-use**: Starting from zero when prior decisions are directly relevant.
