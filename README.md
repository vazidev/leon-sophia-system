# LEON · SOPHIA — Dual-Agent Debate System

A live AI debate app where two specialized agents argue every angle of a question until they reach a high-confidence answer — or keep going until they do.

**LEON** builds the case. **SOPHIA** tears it apart. They loop until SOPHIA scores the analysis ≥ 7.0/10 with zero blocking flags. That's convergence.

---

## What It Does

Enter any question, decision, or topic. Two Claude-powered agents debate it in real time:

- **LEON** proposes a structured recommendation with evidence and claims
- **SOPHIA** critiques it — flags unsupported claims, bias, ethical issues, scope gaps
- LEON deepens the analysis, addressing each flag
- The loop continues until the quality threshold is met
- On convergence: a final recommendation, implementation roadmap, and predicted outcomes are delivered

Everything streams live. You watch the debate happen token by token.

---

## Quick Start

### Local (native)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-ant-... uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev   # http://localhost:5175
```

### Docker Compose

```bash
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY
docker-compose up
# Frontend: http://localhost:5175 | Backend: http://localhost:8000
```

---

## Architecture

```
┌──────────────────────────────────────────────┐
│  Browser (React PWA)                         │
│  ┌──────────┬────────────────┬─────────────┐ │
│  │ Timeline │  Live stream   │  Evolution  │ │
│  │ sidebar  │  detail panel  │  analytics  │ │
│  └──────────┴────────────────┴─────────────┘ │
└───────────────────┬──────────────────────────┘
                    │ SSE + REST
┌───────────────────┴──────────────────────────┐
│  FastAPI backend (Python 3.12)               │
│  ┌──────────────────────────────────────────┐│
│  │  Orchestrator — infinite deepening loop  ││
│  │  LEON agent ←──────────────► SOPHIA agent││
│  └──────────────────────────────────────────┘│
│  SQLModel (SQLite dev / PostgreSQL prod)      │
└──────────────────────────────────────────────┘
```

**Backend endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Health check |
| `POST` | `/api/debate/start` | Create session |
| `GET` | `/api/debate/{id}/stream` | SSE live event stream |
| `GET` | `/api/debate/{id}/state` | Full session snapshot |
| `GET` | `/api/debate/{id}/evolution` | LEON's evolution history |

---

## Project Structure

```
leon-sophia-system/
├── backend/                   # FastAPI app
│   ├── agents/                # LEON and SOPHIA agent logic
│   ├── models/                # SQLModel database models
│   ├── orchestrator.py        # Infinite deepening loop
│   └── main.py                # Routes + CORS + lifespan
├── frontend/                  # React + Vite PWA
│   └── src/
│       ├── components/        # UI components
│       ├── hooks/             # useDebate, useEvolution
│       └── types/             # TypeScript interfaces
├── k8s/                       # Kubernetes manifests (EKS)
├── infra/                     # AWS setup scripts + README
├── .github/workflows/         # CI/CD (test + deploy)
├── agents/                    # Agent identity files
├── templates/                 # Output scaffolding
└── docs/                      # Specs, plans, user manual, PRD
```

---

## Docs

| Document | Purpose |
|----------|---------|
| [User Manual](docs/USER_MANUAL.md) | How to use the app |
| [Features](docs/FEATURES.md) | Capabilities overview |
| [PRD](docs/PRD.md) | Product requirements |
| [infra/README.md](infra/README.md) | AWS deployment setup |

---

## Convergence Criteria

The loop exits only when **both** conditions are true:

1. SOPHIA's quality score ≥ **7.0 / 10**
2. **Zero blocking flags** remain unresolved

There is no round limit. There is no deadlock. Disagreement deepens the analysis — it never stops it.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI 0.115, uvicorn |
| AI | Anthropic Claude (claude-sonnet-4-6) |
| Database | SQLite (dev), PostgreSQL 16 (prod) |
| ORM | SQLModel |
| Streaming | SSE via sse-starlette |
| Frontend | React 18, TypeScript, Vite |
| Charts | Recharts |
| PWA | vite-plugin-pwa |
| Container | Docker multi-stage (python:3.12-slim, nginx:alpine) |
| Orchestration | Kubernetes on AWS EKS |
| CI/CD | GitHub Actions (OIDC auth, no stored AWS keys) |

---

## Development

```bash
# Run all tests
cd backend && pytest --tb=short
cd frontend && npm test -- --run

# Lint / type-check
cd frontend && npx tsc --noEmit
```
