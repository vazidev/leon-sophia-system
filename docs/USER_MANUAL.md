# LEON · SOPHIA User Manual

This guide covers everything you need to use the LEON-SOPHIA debate app — from entering your first topic to reading a convergence report.

---

## Table of Contents

1. [What Is LEON·SOPHIA?](#what-is-leonsophia)
2. [Starting the App](#starting-the-app)
3. [Running a Debate](#running-a-debate)
4. [Reading the Interface](#reading-the-interface)
5. [Understanding Quality Scores](#understanding-quality-scores)
6. [Understanding Flags](#understanding-flags)
7. [The Evolution Panel](#the-evolution-panel)
8. [The Convergence Report](#the-convergence-report)
9. [Exporting Your Decision](#exporting-your-decision)
10. [Installing as a PWA](#installing-as-a-pwa)
11. [Frequently Asked Questions](#frequently-asked-questions)

---

## What Is LEON·SOPHIA?

LEON·SOPHIA is a live AI debate tool. You give it a question or decision, and two AI agents argue it out until they reach a high-confidence answer.

**LEON** (blue) is the strategist. He builds structured recommendations supported by evidence and proposes implementation plans.

**SOPHIA** (red) is the critic. She challenges every claim LEON makes — flagging gaps, unsupported assertions, ethical concerns, and scope blindness. Her job is to break the argument.

After each of SOPHIA's reviews, LEON deepens his analysis: he expands his evidence, broadens his scope, and resolves SOPHIA's flags. This loop continues until SOPHIA scores LEON's analysis ≥ 7.0/10 with no remaining blocking flags — that's **convergence**.

There is no round limit. The system only stops when the answer is good enough.

---

## Starting the App

### Local development

If you're running the app locally, start both services and open your browser:

```
http://localhost:5175
```

The backend must be running on port 8000. See [README.md](../README.md) for setup instructions.

### Hosted / deployed

Open the URL provided by your administrator. The app works in any modern browser (Chrome, Firefox, Safari, Edge).

---

## Running a Debate

### Step 1 — Enter a topic

Type your question or topic into the input bar at the bottom of the screen. The topic can be:

- A decision: *"Should we migrate our monolith to microservices this quarter?"*
- A question: *"What is the best database architecture for a multi-tenant SaaS product?"*
- A scenario: *"We are losing market share to a lower-cost competitor — what should we do?"*
- A plan: *"Evaluate our proposed marketing strategy for Q3."*

Be specific. LEON produces better analysis when the topic is concrete.

### Step 2 — Start the debate

Click **Start Debate**. The button disables while the debate runs — you cannot start a second debate until the current one finishes or you click **New Debate**.

### Step 3 — Watch it unfold

The debate streams live. You will see:

- New round entries appearing in the left sidebar
- Live text streaming in the main panel as the active agent speaks
- Flags appearing inline as SOPHIA raises them
- Quality scores updating after each SOPHIA review

The debate continues automatically until convergence.

---

## Reading the Interface

The interface has four main areas:

```
┌─────────────────────────────────────────┐
│  TopBar — topic + live status           │
├────────────────┬────────────────────────┤
│  Sidebar       │  Detail Panel          │
│  (Timeline /   │  (selected round       │
│   Evolution)   │   content)             │
├────────────────┴────────────────────────┤
│  InputBar — topic input + buttons       │
└─────────────────────────────────────────┘
```

### TopBar

Shows the current topic and a status indicator:
- **Ready** — Waiting for input
- **Debating…** — Debate in progress
- **Converged** — Final answer reached

### Sidebar — Timeline tab

Lists every round in order. Each entry shows:
- The agent (LEON in blue, SOPHIA in red)
- The round number
- A quality score (SOPHIA rounds only)
- A streaming indicator (blinking dot) while the agent is speaking
- A blocking flag count badge (if any flags remain)

Click any round to read its content in the Detail Panel.

### Sidebar — Evolution tab

Switches the sidebar to the Evolution Panel (see [The Evolution Panel](#the-evolution-panel)).

### Detail Panel

Shows the full content of the selected round:
- Agent badge and round number
- The agent's full streaming text (with live blinking cursor while streaming)
- Any flags raised, with severity badges
- A quality score progress bar (SOPHIA rounds only)

### InputBar

- **Topic input** — Disabled while a debate is running
- **Start Debate** — Begins a new debate with the entered topic
- **New Debate** — Resets everything and allows you to enter a new topic (can be clicked at any time)

---

## Understanding Quality Scores

SOPHIA scores LEON's analysis after every round on a scale of **0 to 10**.

| Score | Meaning |
|-------|---------|
| 0 – 3 | Poor — major gaps, unsupported claims, no evidence |
| 4 – 5 | Developing — some valid points, significant issues remain |
| 6 – 6.9 | Approaching — solid foundation but blocking issues exist |
| **7.0+** | **Convergence threshold** — analysis is high-quality, blocking flags resolved |
| 8 – 9 | Strong — well-evidenced, well-scoped, minimal advisories |
| 10 | Exceptional — rare; all criteria met perfectly |

**The debate only ends at 7.0 or above with zero blocking flags.** A score of 6.9 with no flags is not enough — SOPHIA will push for another round.

The quality score appears:
- As a badge on each SOPHIA round in the sidebar
- As a progress bar in the Detail Panel
- On the final Convergence Report

---

## Understanding Flags

Flags are issues SOPHIA raises during her review. There are two types:

### Blocking flags (red)

A blocking flag means LEON must address this issue before convergence is possible — no matter what the quality score is. Blocking flags indicate:

- A claim made without supporting evidence
- A logical contradiction in the argument
- An ethical concern that cannot be bypassed
- A critical gap in scope (e.g., a stakeholder group not considered)

LEON will receive all blocking flags and must resolve them in his next round.

### Advisory flags (yellow)

An advisory flag is informational — it notes a potential weakness or risk worth acknowledging, but it does not prevent convergence. Advisories that remain at convergence are listed in the final report under **Open Advisories**.

---

## The Evolution Panel

Switch to the **Evolution** tab in the sidebar to see how LEON's analysis changed across rounds.

The Evolution Panel contains five charts:

### Score Timeline
A line chart tracking SOPHIA's quality score for each round. Upward trend means LEON is improving his analysis. Flat or downward movement means SOPHIA found new issues.

### Evidence Growth
A horizontal bar chart showing cumulative evidence items per round. Watch LEON's evidence base expand as he deepens the analysis.

### Scope Map
A knowledge graph (SVG) showing the topics LEON expanded into across rounds. Each node is a scope keyword; edges connect rounds. A denser, more interconnected graph means LEON broadened his analysis significantly.

### Position Diff
A round-by-round comparison of LEON's recommendation text. Shows exactly how his position changed — what he added, revised, or retracted from round to round.

### Radar Chart
A six-axis radar comparing LEON's Round 1 analysis against his latest round across dimensions like evidence depth, scope breadth, and confidence. The gap between the two shapes shows how much the analysis grew.

---

## The Convergence Report

When SOPHIA approves the analysis (score ≥ 7.0, zero blocking flags), the debate ends and the Convergence Report appears.

The report has three sections:

### Final Decision

- **Final Recommendation** — LEON's approved recommendation in full
- **Quality Score** — SOPHIA's final score
- **Key Trade-off** — The one explicit trade-off SOPHIA accepted as the cost of this recommendation
- **Open Advisories** — Any advisory flags that remain (acknowledged, not blocking)

### Achievement Guide

A step-by-step implementation roadmap with:
- Step title and description
- Estimated timeline
- Suggested owner / responsible team

### Predicted Outcome

- **Predicted metrics** — Three measurable outcomes with confidence levels
- **Outcome narrative** — A plain-English explanation of the predicted future state
- **Overall confidence** — SOPHIA's confidence in the prediction (0–100%)

---

## Exporting Your Decision

On the Convergence Report screen, click **Export Decision** to download the full decision as a Markdown file.

The exported file includes:
- The topic
- The final recommendation
- The key trade-off
- Open advisories
- The achievement guide (all steps)
- Predicted metrics and narrative

The file is named `leon-sophia-decision-[topic].md` and can be dropped into any Markdown-capable tool (Notion, Obsidian, GitHub, etc.).

Click **View Full Debate** to scroll back to Round 1 and read the full debate history. Click **New Debate** to start over.

---

## Installing as a PWA

LEON·SOPHIA is a Progressive Web App. You can install it to your device for offline access and a native app feel.

### Chrome / Edge (desktop or Android)
- Look for the install icon in the browser address bar (a plus sign or computer icon)
- Click it and select **Install**

### Safari (iOS / macOS)
- Tap the Share button
- Select **Add to Home Screen**

Once installed, the app opens in its own window without browser chrome and works offline for previously loaded content.

---

## Frequently Asked Questions

**How many rounds will the debate take?**
It depends on how quickly LEON satisfies SOPHIA's criteria. Simple, well-scoped topics often converge in 3–5 rounds. Complex or ambiguous topics may take 7–10 rounds or more. There is no upper limit.

**Can I stop a debate mid-way?**
Click **New Debate** at any time to reset. The in-progress debate session is preserved in the database — but the UI resets to idle and you can start a new topic.

**What topics work best?**
Topics that have a real decision to make, meaningful trade-offs, and enough scope for evidence produce the most valuable output. Vague topics (e.g., "what is the meaning of life?") will produce philosophically interesting debates but less actionable convergence reports.

**Is the conversation private?**
Debate content is sent to the Anthropic API for processing. Refer to the Anthropic privacy policy. Sessions are stored in the application database as configured by your administrator.

**Can I run multiple debates at once?**
Each browser tab runs independently. You can have separate debates in separate tabs — each gets its own session ID. The same tab cannot run two debates simultaneously.

**What does it mean if the quality score drops between rounds?**
SOPHIA re-evaluates from scratch each round. If LEON introduces a new claim that is poorly supported, or expands into a scope area with weak evidence, the score may decrease. LEON needs to address all issues, not just the most recent ones.

**Why is a score of 6.9 not enough for convergence?**
The convergence threshold is strict by design: **7.0 and zero blocking flags**. A 6.9 means SOPHIA still has substantive concerns. The system is designed to prioritize quality over speed.
