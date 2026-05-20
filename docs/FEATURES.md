# LEON · SOPHIA — Features

LEON·SOPHIA is an AI-powered debate engine that turns any question into a structured, self-improving analysis — delivered in real time, ending only when the answer is genuinely good.

---

## Core Features

### Dual-Agent Adversarial Reasoning

Two specialized AI agents work in opposition by design:

**LEON** — the strategist — builds structured recommendations, gathers evidence, and proposes implementation plans. He is constructive and forward-thinking.

**SOPHIA** — the critic — systematically challenges every claim. She flags unsupported assertions, detects cognitive bias, raises ethical concerns, and identifies scope blind spots. She is rigorous and uncompromising.

Neither agent can override the other. The only path forward is for the analysis to improve.

---

### Infinite Deepening — No Deadlock

Most AI tools stop when they run out of tokens or hit a round limit. LEON·SOPHIA never deadlocks.

When SOPHIA finds an issue, LEON deepens his analysis — expanding evidence, broadening scope, resolving each flag. The loop continues until the quality threshold is genuinely met. There is no cap on rounds, no "close enough," and no escape hatch.

This produces answers that have survived real adversarial pressure, not just surface-level review.

---

### Live Streaming Debate

Watch the debate happen token by token. Every word from every agent streams directly to your browser via Server-Sent Events. You don't wait for a round to finish — you see the thinking as it develops.

- Live text cursor shows the active agent
- Flags appear inline as SOPHIA raises them
- Quality scores update the moment SOPHIA finishes a review
- New rounds begin automatically without any user interaction

---

### Structured Quality Scoring

SOPHIA scores LEON's analysis on a 0–10 scale after every round. The score reflects:

- Claim support (evidence quality and quantity)
- Logical consistency
- Scope completeness
- Ethical clearance
- Analytical depth

**Convergence requires a score of 7.0 or above with zero blocking flags.** The score is displayed live and tracked across all rounds.

---

### Blocking Flag System

SOPHIA raises two types of flags:

**Blocking flags** — Must be resolved before convergence. These represent genuine gaps: an unsupported claim, a logical contradiction, an ethical concern, or a critical stakeholder not considered. LEON receives every blocking flag and must address them in his next response.

**Advisory flags** — Informational notes about risks or trade-offs. They do not prevent convergence but appear in the final report so decision-makers have the full picture.

The flag system creates an explicit, trackable record of every issue raised and resolved across the debate.

---

### Evolution Analytics

As LEON's analysis develops across rounds, LEON·SOPHIA tracks and visualizes the growth:

**Score Timeline** — Line chart of SOPHIA's quality score per round. See how quickly LEON improves.

**Evidence Growth** — Horizontal bar chart of cumulative evidence items. Watch the evidence base expand.

**Scope Map** — Knowledge graph of topics LEON explored. Shows how broadly the analysis was considered.

**Position Diff** — Round-by-round comparison of LEON's recommendation text. See exactly what changed, what was added, and what was revised.

**Radar Chart** — Six-axis comparison of Round 1 vs. the final round across analytical dimensions. The gap between shapes shows how much the analysis matured.

---

### Convergence Report

When convergence is reached, LEON·SOPHIA delivers a structured final output:

**Final Decision** — The approved recommendation in full, with the explicit trade-off SOPHIA accepted and any remaining advisory notes.

**Achievement Guide** — A step-by-step implementation roadmap with timeline estimates and suggested owners. Not aspirational — this is the path that survived SOPHIA's scrutiny.

**Predicted Outcome** — Three measurable metrics, a plain-English outcome narrative, and a confidence percentage. SOPHIA generates these — not LEON — so they reflect realistic expectations, not optimistic projections.

---

### One-Click Decision Export

Export the complete convergence report as a Markdown file. Includes the recommendation, trade-off, open advisories, the full achievement guide, and predicted outcomes.

Compatible with Notion, Obsidian, GitHub, Confluence, or any Markdown-capable tool.

---

### Progressive Web App (PWA)

Install LEON·SOPHIA directly to your desktop or mobile device. Works like a native app with:

- No browser chrome
- Home screen icon
- Offline support for previously loaded sessions
- Fast, cached load times

Install from Chrome, Edge, or Safari — no app store required.

---

### Multi-Session Support

Every debate creates an isolated session with a unique ID. All session data — rounds, flags, evolution snapshots, and the convergence report — is persisted in the database.

Open multiple debates in separate browser tabs simultaneously. Each tab runs its own independent session.

---

## Technical Capabilities

### Server-Sent Events (SSE) Streaming

The debate streams over a persistent HTTP connection. No polling, no WebSockets required. Token-by-token delivery with round-trip latency under 100ms on a local connection.

Designed for long-lived connections: idle timeout set to 3600 seconds in production to prevent mid-debate disconnection.

### Structured Agent Output

Both agents produce structured typed output alongside their streaming text:

- LEON emits `LeonChunk` — recommendation, evidence list, new claims, resolved flags, scope keywords, confidence score
- SOPHIA emits `SophiaReviewChunk` — quality score, flags, summary
- SOPHIA emits `SophiaConvergenceChunk` — final recommendation, key trade-off, achievement steps, predicted metrics

This structured output powers the Evolution Panel analytics and the Convergence Report.

### Full Debate History

Every round is stored. The full conversation — every LEON proposal and every SOPHIA review — is retrievable via the `/api/debate/{id}/state` endpoint.

LEON's evolution is separately tracked at `/api/debate/{id}/evolution` — one snapshot per round, never overwritten, full growth history always recoverable.

### Production-Grade Deployment

Designed for AWS EKS from the ground up:

- Docker multi-stage builds (non-root containers, production image excludes dev dependencies)
- Kubernetes manifests with health probes, resource limits, and horizontal pod autoscaling (2–10 pods)
- ALB Ingress with sticky sessions ensuring SSE connections stay on the same pod
- GitHub Actions CI/CD with OIDC authentication — no stored AWS credentials
- PostgreSQL 16 on AWS RDS for persistence
- ECR for container image storage

---

## Use Cases

**Strategic decisions** — Evaluate a major product, technology, or organizational decision with adversarial pressure before committing.

**Architecture reviews** — Have LEON propose a system design and SOPHIA tear it apart before a single line is written.

**Risk analysis** — Surface the gaps and assumptions in a plan that internal reviewers miss because they're too close to it.

**Policy evaluation** — Test the robustness of a proposed policy or process change against rigorous critique.

**Research synthesis** — Synthesize competing perspectives on a complex topic into a convergence-qualified answer.

**Pre-mortem analysis** — Input a plan that already exists; let SOPHIA find everything that could go wrong before it does.
