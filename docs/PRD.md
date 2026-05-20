# Product Requirements Document — LEON · SOPHIA

**Version:** 1.0
**Status:** Shipped
**Last updated:** 2026-05-20

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Goals and Success Metrics](#2-goals-and-success-metrics)
3. [User Stories](#3-user-stories)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Agent Specifications](#6-agent-specifications)
7. [Data Model](#7-data-model)
8. [API Specification](#8-api-specification)
9. [Frontend Requirements](#9-frontend-requirements)
10. [Deployment Requirements](#10-deployment-requirements)
11. [Out of Scope](#11-out-of-scope)

---

## 1. Product Overview

### Problem Statement

AI assistants are good at generating answers but bad at stress-testing them. A single model asked to evaluate its own proposal will rationalize weaknesses away. Human review is slow, expensive, and subject to bias. Organizations making consequential decisions need adversarial scrutiny — fast, systematic, and uncompromising.

### Solution

LEON·SOPHIA is a real-time AI debate system in which two specialized agents argue a topic from opposing stances — LEON as the strategic builder, SOPHIA as the adversarial critic — until the analysis meets a defined quality threshold. The debate loops automatically, deepening on each pass, and terminates only at convergence: SOPHIA's quality score ≥ 7.0 with zero blocking flags.

### Product Type

Web application (React PWA) + REST/SSE API (FastAPI). Deployable locally via Docker Compose or to production on AWS EKS.

---

## 2. Goals and Success Metrics

### Goals

1. Produce high-quality, adversarially-tested analysis on any question or decision
2. Make the reasoning process transparent and observable in real time
3. Deliver structured, actionable output at convergence
4. Support production deployment with no manual intervention per debate

### Success Metrics

| Metric | Target |
|--------|--------|
| Convergence rate (% of debates that reach a score ≥ 7.0) | > 95% |
| Average rounds to convergence | ≤ 7 |
| Token stream latency (first token to browser) | < 2 seconds |
| Backend test coverage | > 80% |
| Frontend unit tests passing | 100% |
| Uptime (production) | ≥ 99.5% |
| Deployment time (GitHub push to live) | < 10 minutes |

---

## 3. User Stories

### Core Debate Flow

**US-01** — As a user, I want to enter a topic and start a live debate so that I can get an adversarially-tested answer.

**US-02** — As a user, I want to watch the debate stream in real time so that I can see the reasoning develop as it happens.

**US-03** — As a user, I want to see which flags SOPHIA raised so that I understand what weaknesses were found.

**US-04** — As a user, I want to see SOPHIA's quality score after each of her reviews so that I can track whether the analysis is improving.

**US-05** — As a user, I want the debate to continue automatically until convergence so that I don't have to manage the loop myself.

**US-06** — As a user, I want to read any round in the debate by clicking it so that I can review the full reasoning.

### Convergence Report

**US-07** — As a user, I want to see a structured convergence report when the debate ends so that I have a clear, actionable final answer.

**US-08** — As a user, I want to see an implementation roadmap in the convergence report so that I know the next steps.

**US-09** — As a user, I want to see predicted outcomes with confidence scores so that I can calibrate my expectations.

**US-10** — As a user, I want to export the convergence report as Markdown so that I can share or archive the decision.

### Evolution Analytics

**US-11** — As a user, I want to see how LEON's analysis evolved across rounds so that I can understand the depth of the debate.

**US-12** — As a user, I want to see which topics LEON expanded into across rounds so that I can assess scope coverage.

### Session Management

**US-13** — As a user, I want to start a new debate at any time so that I can explore a different topic.

**US-14** — As a user, I want multiple browser tabs to run independent debates so that I can compare analyses.

### Deployment

**US-15** — As an operator, I want to run the system locally with one command so that I can develop and test it quickly.

**US-16** — As an operator, I want pushes to `main` to automatically deploy to production so that I don't manually manage releases.

---

## 4. Functional Requirements

### 4.1 Debate Session

**FR-01** — The system shall create a new debate session on `POST /api/debate/start` with a topic string and return a unique `session_id`.

**FR-02** — Each session shall maintain an ordered list of rounds, each attributed to either `leon` or `sophia`.

**FR-03** — The orchestrator shall run the LEON → SOPHIA loop automatically with no user interaction between rounds.

**FR-04** — The system shall pass all unresolved blocking flags from SOPHIA's last review to LEON at the start of each new LEON round.

**FR-05** — The system shall terminate the loop only when SOPHIA's `quality_score` ≥ 7.0 **and** there are zero unresolved blocking flags.

**FR-06** — There shall be no round limit. The loop shall run until convergence.

### 4.2 Streaming

**FR-07** — The system shall stream debate events to the browser via Server-Sent Events on `GET /api/debate/{id}/stream`.

**FR-08** — The stream shall emit the following event types:

| Event | Payload | Trigger |
|-------|---------|---------|
| `round_start` | `{round, agent}` | New round begins |
| `token` | `{text}` | Agent generates a token |
| `flag` | `{severity, claim, description}` | SOPHIA raises a flag |
| `quality_score` | `{score}` | SOPHIA submits her review score |
| `convergence` | Full ConvergenceData object | Debate ends |

**FR-09** — Token events shall stream in real time as the AI generates them, not buffered.

**FR-10** — The SSE connection shall remain open for the full duration of the debate.

### 4.3 Evolution Tracking

**FR-11** — After each LEON round, the system shall store a `LeonEvolution` snapshot containing: recommendation text, evidence count, new claims, resolved flags, scope keywords, confidence score.

**FR-12** — Evolution snapshots shall be append-only — never overwritten.

**FR-13** — The evolution history shall be retrievable via `GET /api/debate/{id}/evolution`.

### 4.4 Convergence Report

**FR-14** — On convergence, SOPHIA shall emit a `SophiaConvergenceChunk` containing:
- `quality_score` (≥ 7.0)
- `final_recommendation` (full approved recommendation)
- `key_tradeoff` (explicit trade-off accepted)
- `open_advisories` (list of remaining advisory-level flags)
- `achievement_steps` (array of `{title, description, timeline, owner}`)
- `predicted_metrics` (array of `{label, value, confidence}`)
- `predicted_narrative` (plain-English outcome description)
- `overall_confidence` (float 0.0–1.0)

**FR-15** — The convergence data shall be sent to the frontend as the `convergence` SSE event and persisted in the session state.

### 4.5 Session State

**FR-16** — The full session state (all rounds, flags, evolution history, convergence data) shall be retrievable via `GET /api/debate/{id}/state` at any time during or after the debate.

### 4.6 Export

**FR-17** — The frontend shall provide an "Export Decision" button on the Convergence Screen that downloads the convergence report as a `.md` file.

---

## 5. Non-Functional Requirements

### Performance

**NFR-01** — The first token shall appear in the browser within 2 seconds of a round starting.

**NFR-02** — SSE idle timeout shall be configured to 3600 seconds to prevent mid-debate disconnection on production infrastructure.

### Reliability

**NFR-03** — If database initialization fails at startup, the backend process shall exit with a logged critical error rather than start in a degraded state.

**NFR-04** — The backend shall return a 200 response on `GET /health` only when the service is operational.

### Security

**NFR-05** — The `ANTHROPIC_API_KEY` shall never be committed to the repository. It shall be injected via environment variable at runtime.

**NFR-06** — The production Kubernetes Secret shall be a template with `${PLACEHOLDER}` values. CI/CD shall substitute real values via `envsubst` — never committing them.

**NFR-07** — The production Docker image shall run as a non-root system user (`appuser`).

**NFR-08** — The production backend Docker image shall not include development dependencies (pytest, httpx).

**NFR-09** — The GitHub Actions deploy workflow shall authenticate to AWS via OIDC — no long-lived AWS access keys stored as secrets.

### Scalability

**NFR-10** — The backend shall support horizontal scaling. Session state shall be persisted in PostgreSQL (not in-process memory).

**NFR-11** — The ALB Ingress shall use sticky sessions to ensure SSE connections are routed to the same pod throughout a debate.

**NFR-12** — The Horizontal Pod Autoscaler shall scale backend pods between 2 and 10 based on 70% CPU utilization.

### Maintainability

**NFR-13** — Backend tests shall cover core routes, models, agents, and the orchestrator loop.

**NFR-14** — The CI pipeline shall run all backend and frontend tests on every pull request before merge.

### Accessibility and Compatibility

**NFR-15** — The frontend shall be installable as a PWA on desktop and mobile.

**NFR-16** — The frontend shall run correctly on Chrome, Firefox, Safari, and Edge (latest versions).

---

## 6. Agent Specifications

### 6.1 LEON

**Model:** `claude-sonnet-4-6`

**Role:** Forward-planning strategic analyst

**Inputs per round:**
- The debate topic
- Full conversation history (all prior rounds)
- List of blocking flags from SOPHIA's last review (empty on Round 1)

**Output — `LeonChunk` (structured, via tool call):**

| Field | Type | Description |
|-------|------|-------------|
| `recommendation` | string | Current top recommendation |
| `evidence` | string[] | Supporting evidence items |
| `new_claims` | string[] | Claims introduced this round |
| `resolved_flags` | string[] | SOPHIA flags explicitly addressed |
| `scope_keywords` | string[] | New topics or dimensions explored |
| `confidence_score` | float | Self-assessed confidence (0.0–1.0) |

**Behavioral constraints:**
- Must address every blocking flag passed to it
- Must expand scope or evidence each round (not repeat prior content verbatim)
- Cannot declare convergence — only SOPHIA can

### 6.2 SOPHIA

**Model:** `claude-sonnet-4-6`

**Role:** Adversarial critic and ethics governor

**Inputs per round:**
- The debate topic
- Full conversation history
- LEON's current recommendation (from the preceding LEON round)

**Output path 1 — Review (`SophiaReviewChunk`):**

| Field | Type | Description |
|-------|------|-------------|
| `quality_score` | float | 0.0–10.0 |
| `flags` | Flag[] | `{severity, claim, description}` |
| `summary` | string | Brief review summary |

Emitted when quality < 7.0 OR any blocking flags remain.

**Output path 2 — Convergence (`SophiaConvergenceChunk`):**

| Field | Type | Description |
|-------|------|-------------|
| `quality_score` | float | ≥ 7.0 |
| `final_recommendation` | string | Synthesis-approved recommendation |
| `key_tradeoff` | string | Explicit cost/trade-off accepted |
| `open_advisories` | string[] | Remaining advisory items |
| `achievement_steps` | AchievementStep[] | `{title, description, timeline, owner}` |
| `predicted_metrics` | PredictedMetric[] | `{label, value, confidence}` |
| `predicted_narrative` | string | Plain-English outcome description |
| `overall_confidence` | float | 0.0–1.0 |

Emitted only when quality ≥ 7.0 **and** zero blocking flags remain.

**Behavioral constraints:**
- Cannot approve analysis with any unresolved blocking flags
- Cannot score below 7.0 and emit convergence
- Must raise a blocking flag for any unsupported claim
- Must raise a blocking flag for any ethical concern
- Advisory flags for risks that don't block convergence but should be noted

---

## 7. Data Model

### DebateSession

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string (PK, unique) | UUID or nanoid |
| `topic` | string | The debate topic |
| `status` | enum: `active` / `converged` | Current state |
| `created_at` | string (ISO 8601) | Creation timestamp |

### DebateRound

| Field | Type | Description |
|-------|------|-------------|
| `id` | int (PK) | Auto-increment |
| `session_id` | string (FK → DebateSession, indexed) | Parent session |
| `round` | int | Round number (1-based) |
| `agent` | enum: `leon` / `sophia` | Which agent |
| `content` | text | Full response text |

### LeonEvolution

| Field | Type | Description |
|-------|------|-------------|
| `id` | int (PK) | Auto-increment |
| `session_id` | string (FK, indexed) | Parent session |
| `round` | int | Round number |
| `recommendation_snapshot` | text | LEON's recommendation at this round |
| `evidence_count` | int | Count of evidence items |
| `claims_added` | JSON (string[]) | New claims this round |
| `claims_resolved` | JSON (string[]) | Resolved flags this round |
| `scope_keywords` | JSON (string[]) | New scope terms |
| `confidence_score` | float | LEON's self-confidence (0.0–1.0) |
| `quality_score` | float | SOPHIA's score for this round |

### Flag

| Field | Type | Description |
|-------|------|-------------|
| `id` | int (PK) | Auto-increment |
| `session_id` | string (FK, indexed) | Parent session |
| `round` | int | Round when raised |
| `severity` | enum: `blocking` / `advisory` | Flag type |
| `claim` | string | The claim that triggered the flag |
| `description` | string | Explanation of the issue |
| `resolved` | bool | Whether LEON addressed it |
| `resolved_round` | int (nullable) | Round when resolved |

---

## 8. API Specification

### POST /api/debate/start

**Request body:**
```json
{ "topic": "string" }
```

**Response 200:**
```json
{ "session_id": "string" }
```

---

### GET /api/debate/{session_id}/stream

**Response:** `text/event-stream`

Event format: `data: <JSON>\n\n`

Events emitted in order:

```
data: {"type": "round_start", "round": 1, "agent": "leon"}
data: {"type": "token", "text": "Based on..."}
...
data: {"type": "round_start", "round": 1, "agent": "sophia"}
data: {"type": "token", "text": "I find..."}
data: {"type": "flag", "severity": "blocking", "claim": "...", "description": "..."}
data: {"type": "quality_score", "score": 5.2}
data: {"type": "round_start", "round": 2, "agent": "leon"}
...
data: {"type": "convergence", "quality_score": 7.4, "final_recommendation": "...", ...}
```

---

### GET /api/debate/{session_id}/state

**Response 200:**
```json
{
  "session": { "session_id": "...", "topic": "...", "status": "converged" },
  "rounds": [
    { "round": 1, "agent": "leon", "content": "...", "flags": [] }
  ],
  "convergence": { ... } // present if status == "converged"
}
```

---

### GET /api/debate/{session_id}/evolution

**Response 200:**
```json
[
  {
    "round": 1,
    "recommendation_snapshot": "...",
    "evidence_count": 3,
    "claims_added": ["..."],
    "scope_keywords": ["..."],
    "confidence_score": 0.6,
    "quality_score": 4.8
  }
]
```

---

### GET /health

**Response 200:**
```json
{ "status": "ok" }
```

---

## 9. Frontend Requirements

### 9.1 Layout

The UI shall have four primary areas:

1. **TopBar** — Displays the current topic and a status indicator (`Ready` / `Debating…` / `Converged`)
2. **Sidebar** — Switchable between Timeline tab (round list) and Evolution tab (analytics)
3. **Detail Panel** — Displays the content of the selected round
4. **InputBar** — Topic text input, Start Debate button, New Debate button

### 9.2 Timeline Sidebar

- Each round is listed with: agent badge (LEON blue / SOPHIA red), round number, quality score (SOPHIA rounds), streaming indicator, blocking flag count badge
- Clicking a round updates the Detail Panel to show that round's content
- The most recently started round is selected by default

### 9.3 Detail Panel

- Shows agent badge, round number, and quality score bar
- Streams text with a blinking cursor while the round is active
- Displays flags inline with severity styling (blocking: red left border, advisory: yellow left border)

### 9.4 Evolution Panel

Five charts (Recharts + SVG):
- Score Timeline (line chart, round vs. quality score)
- Evidence Growth (horizontal bar chart, cumulative evidence per round)
- Scope Map (SVG knowledge graph, topic nodes per round)
- Position Diff (text diff of recommendation per round)
- Radar Chart (six-axis, Round 1 vs. latest round)

### 9.5 Convergence Screen

Displayed when the `convergence` SSE event is received. Must show:
- Final Recommendation with quality score badge
- Key Trade-off (one sentence)
- Open Advisories (bulleted list)
- Achievement Guide (step cards with title, description, timeline, owner)
- Predicted Outcome (3 metric cards + narrative + confidence %)
- Export Decision button (downloads Markdown)
- View Full Debate button (scrolls to Round 1)
- New Debate button (resets to idle)

### 9.6 State Machine

The frontend tracks three phases:

| Phase | Condition |
|-------|-----------|
| `idle` | No active debate |
| `running` | SSE stream open, rounds accumulating |
| `converged` | Convergence event received, stream closed |

Transitions:
- `idle` → `running`: on `POST /api/debate/start` success and SSE stream opened
- `running` → `converged`: on `convergence` SSE event received
- Any → `idle`: on "New Debate" button click (stream closed if open)

### 9.7 PWA

The app shall be configured as a PWA with:
- A web manifest (`name`, `short_name`, `start_url`, `display: standalone`)
- A service worker with auto-update registration
- An app icon (SVG, minimum 512×512)
- Cache-control headers preventing the service worker file from being cached immutably

---

## 10. Deployment Requirements

### 10.1 Local Development

**DR-01** — `docker-compose up` shall start the full stack (PostgreSQL, backend, frontend) with a single command.

**DR-02** — The backend shall support live reload in development (`--reload` flag).

**DR-03** — `ANTHROPIC_API_KEY` shall be read from a `.env` file in local development. The compose file shall fail fast with a descriptive error if it is absent.

### 10.2 Production (AWS EKS)

**DR-04** — Each component (backend, frontend) shall have its own Docker image built via multi-stage build.

**DR-05** — Images shall be stored in AWS ECR.

**DR-06** — The backend deployment shall have a minimum of 2 replicas.

**DR-07** — The frontend deployment shall have a minimum of 2 replicas.

**DR-08** — The ALB Ingress shall route `/api` to the backend service and `/` to the frontend service.

**DR-09** — The ALB idle timeout shall be 3600 seconds.

**DR-10** — The ALB target group shall have sticky sessions enabled with a 3600-second duration.

**DR-11** — The backend HPA shall scale between 2 and 10 pods based on 70% CPU utilization.

**DR-12** — All containers shall have CPU and memory requests and limits defined.

**DR-13** — The backend shall have readiness and liveness probes on `GET /health`.

### 10.3 CI/CD

**DR-14** — Every pull request to `main` shall run the full test suite (pytest + vitest) and fail the build if any test fails.

**DR-15** — Every push to `main` shall trigger a build and deploy pipeline.

**DR-16** — The deploy pipeline shall authenticate to AWS via OIDC using a scoped IAM role — no stored access keys.

**DR-17** — The pipeline shall build both images, tag them with the git short SHA, push to ECR, and apply all Kubernetes manifests.

**DR-18** — The pipeline shall wait for both deployments to roll out successfully before completing.

---

## 11. Out of Scope

The following are explicitly not part of version 1.0:

- **User authentication** — No login, no user accounts, no access control
- **Multi-user collaboration** — Sessions are single-user; no shared session views
- **Custom agent personas** — LEON and SOPHIA have fixed roles; no persona configuration UI
- **Agent model selection** — Model is fixed to `claude-sonnet-4-6`; no model picker
- **Debate resumption** — In-progress debates cannot be resumed after a browser refresh (session state is stored server-side but the SSE stream is not re-attachable)
- **Debate comparison** — No side-by-side comparison of multiple debate sessions
- **LEON round limit configuration** — Round limit is removed by design; no admin knob to cap it
- **Custom convergence thresholds** — The 7.0 quality score threshold is not user-configurable in v1
- **Internationalization** — English only
- **Analytics dashboard** — No cross-session aggregate reporting
