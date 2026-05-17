# LEON–SOPHIA Live Debate UI — Design Spec

**Date**: 2026-05-14
**Status**: Approved
**Target platform**: PWA (Progressive Web App) — installable on Android via Chrome

---

## 1. Overview

A live AI debate application where two specialized Claude agents — LEON (strategic planner) and SOPHIA (adversarial critic) — exchange analysis rounds until they converge on a single highest-confidence answer. The user types a question and watches the debate unfold in real time.

### Core Principle: Infinite Deepening, Not Deadlock
There is no permanent disagreement between LEON and SOPHIA. When they conflict, the analysis deepens and broadens — LEON expands his evidence base, explores new angles, and revises his position. The loop has no deadlock exit. It has only two states: **deepening** and **converged**. Convergence is earned when SOPHIA's quality score reaches ≥ 7.0 and zero blocking flags remain.

---

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React (Vite) + CSS |
| PWA | `manifest.json` + service worker (Workbox) |
| Backend | Python 3.12 + FastAPI |
| AI | Claude API (claude-sonnet-4-6) via `anthropic` SDK |
| Streaming | Server-Sent Events (SSE) |
| Data analysis | pandas, numpy (callable as tool_use by agents) |
| Persistence | SQLite (dev) / PostgreSQL (prod) via SQLModel |
| State | React hooks + EventSource API |

---

## 3. Layout

**Timeline + Detail** — two-panel layout:

```
┌─────────────┬──────────────────────────────────────────────┐
│  TOP BAR    │  Topic input · Live status                   │
├─────────────┼──────────────────────────────────────────────┤
│  SIDEBAR    │  DETAIL PANEL                                │
│  Timeline   │  Selected round content (streams live)       │
│  ─────────  │  ─────────────────────────────────────────── │
│  R1 · LEON  │  Inline flags · Evidence badges              │
│  R1 · SOPHIA│  SOPHIA flags panel                          │
│  R2 · LEON  │  Quality score bar                           │
│  ...        │                                              │
│  SYNTHESIS  │  [on convergence: Decision + Guide + Pred.]  │
├─────────────┴──────────────────────────────────────────────┤
│  INPUT BAR  │  New Debate · Export Decision                │
└─────────────────────────────────────────────────────────────┘
```

**Evolution tab**: accessible from the sidebar header — shows LEON's evolution panel (score timeline, position diff, scope map, radar, evidence growth, flag lifecycle).

---

## 4. Backend Architecture

### File Structure
```
backend/
├── main.py                  # FastAPI app, routes
├── orchestrator.py          # Infinite deepening loop
├── agents/
│   ├── leon.py              # LEON persona + Claude API calls
│   └── sophia.py            # SOPHIA persona + Claude API calls
├── analysis.py              # Data analysis tools (pandas)
├── models/
│   ├── debate.py            # DebateSession, DebateRound, LeonEvolution
│   └── flags.py             # Flag, Severity enum
└── db.py                    # SQLite/PostgreSQL connection
```

### API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/debate/start` | Create session, return `session_id` |
| `GET` | `/api/debate/{id}/stream` | SSE stream of all debate events |
| `GET` | `/api/debate/{id}/state` | Full session snapshot |
| `GET` | `/api/debate/{id}/evolution` | LEON evolution history |

### SSE Event Types
| Event | Payload | UI Effect |
|-------|---------|-----------|
| `round_start` | `{round, agent}` | New sidebar entry |
| `token` | `{text}` | Detail panel streams text |
| `flag` | `{severity, claim, description}` | Inline badge appears |
| `quality_score` | `{score}` | Score bar updates |
| `convergence` | `{final_output}` | Convergence banner + 3 sections |

---

## 5. Orchestration Loop

```python
async def run_debate(topic: str, session_id: str):
    history = []
    round_num = 0
    last_flags = []   # populated after each SOPHIA review; passed to LEON next round

    while True:
        round_num += 1

        leon_output = await leon.respond(
            topic=topic,
            history=history,           # full prior context — LEON evolves
            sophia_flags=last_flags,
            stream_to=session_id
        )
        history.append(leon_output)
        save_leon_evolution_snapshot(session_id, round_num, leon_output)

        sophia_output = await sophia.review(
            topic=topic,
            history=history,
            stream_to=session_id
        )
        history.append(sophia_output)

        # Only exit: convergence
        if sophia_output.quality_score >= 7.0 and not sophia_output.blocking_flags:
            yield ConvergenceEvent(final=sophia_output)
            break
        # Otherwise: loop continues, LEON deepens with full history
```

**No round limit. No deadlock. No escalation path. Deepening is the only response to conflict.**

---

## 6. LEON Evolution Tracking

Each round, after LEON responds, the orchestrator saves a `LeonEvolution` snapshot:

```python
class LeonEvolution(SQLModel, table=True):
    id: int
    session_id: str
    round: int
    recommendation_snapshot: str   # LEON's position this round
    evidence_count: int            # cumulative evidence pieces cited
    claims_added: list[str]        # new claims introduced
    claims_resolved: list[str]     # SOPHIA flags LEON addressed
    scope_keywords: list[str]      # new topics LEON expanded into
    confidence_score: float        # LEON's self-assessed certainty
    quality_score: float           # SOPHIA's score this round (set after review)
```

Never overwritten — every round appends a new row. Full growth history is always recoverable.

---

## 7. Evolution Panel (Graphical View)

Accessed via the "Evolution" tab in the UI. Four visualizations:

### 7a. Score Timeline Chart
Line chart: quality score per round, convergence threshold (7.0) shown as dashed green line. Dots colored blue until convergence round (green).

### 7b. Position Diff View
Per-round diff of LEON's recommendation text. Green highlights = new claims added. Red strikethrough = replaced claims. Each row shows the round tag and SOPHIA flag status.

### 7c. Scope Growth Map
SVG knowledge graph. Center node = original topic. Each round sprouts new child nodes for topics LEON expanded into (driven by `scope_keywords`). Node size reflects depth of evidence at that node. Nodes still open (SOPHIA-flagged) show a warning indicator.

### 7d. Right Column (3 panels)
- **Evidence Growth**: horizontal bar chart, one bar per round, cumulative evidence count
- **Dimensions Radar**: hexagonal radar comparing Round 1 vs final round across 6 axes (Evidence, Scope, Confidence, Risk, Depth, Specificity)
- **Flag Lifecycle**: list of all SOPHIA flags, status (resolved ✓ / open ⚠), and the round they were resolved in

---

## 8. Convergence Screen

When SOPHIA's quality score ≥ 7.0 and zero blocking flags, the synthesis entry appears in the timeline sidebar. The detail panel shows three sections:

### 8a. ⚖️ Final Decision
- Synthesis-approved recommendation in plain language
- Clearance badges: Ethics ✓, Bias ✓, Evidence Tier
- Key trade-off accepted (explicit statement)
- Open advisories with resolution deadlines
- Decision logged to `templates/decision_log_template.md`

### 8b. 🗺️ How to Achieve This
- LEON's step-by-step implementation roadmap (SOPHIA-reviewed)
- Each step: title, description, timeline chip, owner chip
- Steps with open SOPHIA advisories show a warning badge

### 8c. 🔭 Best Predicted Outcome
- 3 headline metrics (e.g., latency reduction, timeline, scale headroom) with confidence levels
- Plain-English narrative of the most likely outcome
- Milestone timeline bar (horizontal dot-and-line)
- SOPHIA's confidence note: what's capping the score and how to raise it
- Overall prediction confidence score (capped by any open advisory)

### Action bar
- **Export Decision** → writes to `templates/decision_log_template.md`
- **View Full Debate** → scrolls timeline to Round 1
- **New Debate** → clears session, returns to input

---

## 9. PWA Configuration

```json
// public/manifest.json
{
  "name": "LEON · SOPHIA",
  "short_name": "LEON·SOPHIA",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#f6f8fa",
  "theme_color": "#0969da",
  "icons": [{ "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }]
}
```

Service worker (Workbox): caches the app shell for offline launch. Debate stream requires network — graceful offline message shown if disconnected mid-debate.

**Install flow on Android**: Open in Chrome → tap ⋮ menu → "Add to Home Screen" → full-screen app icon on home screen.

---

## 10. Visual Style

**Clean Research** — light academic theme:
- Background: `#f6f8fa`
- Surface: `#ffffff` with `1px solid #d0d7de` borders
- LEON accent: `#0969da` (blue)
- SOPHIA accent: `#cf222e` (red)
- Convergence/resolved: `#1a7f37` (green)
- Advisory: `#d29922` (yellow)
- Body text: `#1f2328`, secondary: `#57606a`
- Border radius: 8px cards, 20px chips
- Font: `'Segoe UI', -apple-system, sans-serif`

---

## 11. CLAUDE.md Update

The system `CLAUDE.md` must be updated to reflect the infinite deepening principle:
- Remove all references to escalation-to-deadlock
- Replace with: "When LEON and SOPHIA conflict, the analysis deepens — never deadlocks. The loop continues until convergence."
- Remove the "escalation rules" as a blocking mechanism; reframe as a "depth trigger" (SOPHIA flags → LEON broadens scope, not gives up)

---

## 12. Project File Structure

```
leon-sophia-system/
├── frontend/
│   ├── public/
│   │   ├── manifest.json
│   │   └── icon-512.png
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── TopBar.tsx
│   │   │   ├── TimelineSidebar.tsx
│   │   │   ├── DetailPanel.tsx
│   │   │   ├── EvolutionPanel.tsx
│   │   │   │   ├── ScoreTimeline.tsx
│   │   │   │   ├── PositionDiff.tsx
│   │   │   │   ├── ScopeMap.tsx
│   │   │   │   └── RadarChart.tsx
│   │   │   ├── ConvergenceScreen.tsx
│   │   │   │   ├── FinalDecision.tsx
│   │   │   │   ├── AchievementGuide.tsx
│   │   │   │   └── PredictedOutcome.tsx
│   │   │   └── InputBar.tsx
│   │   ├── hooks/
│   │   │   ├── useDebate.ts
│   │   │   └── useEvolution.ts
│   │   └── types/
│   │       └── debate.ts
│   ├── vite.config.ts
│   └── package.json
│
└── backend/
    ├── main.py
    ├── orchestrator.py
    ├── agents/
    │   ├── leon.py
    │   └── sophia.py
    ├── analysis.py
    ├── models/
    │   ├── debate.py
    │   └── flags.py
    ├── db.py
    └── requirements.txt
```
