# LEON·SOPHIA — Docker / Kubernetes / AWS Deployment Design

**Date**: 2026-05-17
**Status**: Approved
**Target**: EKS + Managed Node Groups, GitHub Actions CI/CD, configurable region + domain

---

## 1. Overview

Containerise the LEON·SOPHIA app (FastAPI backend + React/Vite frontend) and deploy it to AWS EKS with a full CI/CD pipeline. Local development continues to work via Docker Compose. All region, domain, and cluster variables are configurable — there are no hard-coded AWS-specific values in the manifests.

---

## 2. Architecture

```
Internet
  └─→ Route 53 (optional, configurable domain)
        └─→ ACM TLS certificate (optional, attached when domain is set)
              └─→ AWS Application Load Balancer (ALB)
                    ├─ sticky sessions on /api/debate/*/stream   ← SSE fix
                    ├─→ frontend Service  (nginx pods, 2 replicas)
                    └─→ backend Service   (uvicorn pods, 2 replicas)
                              └─→ RDS PostgreSQL (private subnet, db.t3.micro)

ECR — stores backend + frontend Docker images
Secrets Manager — stores ANTHROPIC_API_KEY and DB password
```

**Why sticky sessions on `/api/debate/*/stream`:** SSE connections are long-lived. Without sticky sessions, the ALB may route the initial `POST /api/debate/start` to pod A and the subsequent `GET /stream` to pod B, which has no session state. The ALB `stickiness` target-group attribute routes both requests to the same pod for the lifetime of the debate.

---

## 3. Local Development

### 3a. Native (existing)
```bash
# Terminal 1
cd backend && uvicorn main:app --reload   # port 8000

# Terminal 2
cd frontend && npm run dev               # port 5175
```

### 3b. Docker Compose
```bash
docker-compose up          # frontend → :5175, backend → :8000, postgres → :5432
docker-compose up --build  # rebuild images
```

`docker-compose.yml` wires:
- `frontend` container: Vite dev server on port 5175
- `backend` container: uvicorn on port 8000, depends on `db`
- `db` container: postgres:16 on port 5432
- Shared `.env` file supplies `ANTHROPIC_API_KEY`

---

## 4. Docker Images

### 4a. Backend (`backend/Dockerfile`)
Multi-stage build:
1. **builder** — `python:3.12-slim`, install deps from `requirements.txt` into `/install`
2. **runtime** — copy `/install`, copy source, run `uvicorn main:app --host 0.0.0.0 --port 8000`

`.dockerignore`: excludes `.venv/`, `__pycache__/`, `*.db`, `.env`, `tests/`

### 4b. Frontend (`frontend/Dockerfile`)
Multi-stage build:
1. **builder** — `node:20-alpine`, `npm ci`, `npm run build` → `dist/`
2. **runtime** — `nginx:alpine`, copy `dist/` to `/usr/share/nginx/html`, custom `nginx.conf`

`nginx.conf` — serves static files, proxies `/api/` to backend service DNS, sets `proxy_buffering off` and `X-Accel-Buffering: no` for SSE.

`.dockerignore`: excludes `node_modules/`, `dist/`, `.env`

---

## 5. Kubernetes Manifests (`k8s/`)

All manifests use namespace `leon-sophia`. Image tags are templated as `${ECR_REGISTRY}/leon-sophia-backend:${IMAGE_TAG}` — substituted by CI/CD via `envsubst` before `kubectl apply`.

| File | Purpose |
|------|---------|
| `namespace.yaml` | Creates `leon-sophia` namespace |
| `configmap.yaml` | `DATABASE_URL`, `FRONTEND_ORIGIN` |
| `secret.yaml` | Template only — `ANTHROPIC_API_KEY`, `DB_PASSWORD` injected by CI |
| `backend-deployment.yaml` | 2 replicas, `resources: requests cpu=250m mem=512Mi, limits cpu=1 mem=1Gi` |
| `backend-service.yaml` | ClusterIP, port 8000 |
| `frontend-deployment.yaml` | 2 replicas, `resources: requests cpu=100m mem=128Mi` |
| `frontend-service.yaml` | ClusterIP, port 80 |
| `ingress.yaml` | ALB Ingress, sticky sessions on `/api/debate/*/stream`, optional TLS |
| `hpa.yaml` | HPA for backend: min 2, max 10, target CPU 70% |

### 5a. Ingress sticky session annotation
```yaml
alb.ingress.kubernetes.io/target-group-attributes: |
  stickiness.enabled=true,stickiness.lb_cookie.duration_seconds=3600
```
Applied only to the backend target group via path-based routing rules.

### 5b. Secrets handling
`k8s/secret.yaml` is a **template** committed to the repo — values are empty placeholders. CI/CD injects real values from GitHub Secrets via `envsubst` at deploy time. The template is never committed with real values.

---

## 6. AWS Infrastructure (`infra/`)

Setup is one-time, manual (not automated by CI/CD). Each script is idempotent.

| File | What it does |
|------|-------------|
| `infra/eks-cluster.yaml` | `eksctl` cluster spec: 2–4 nodes, `t3.medium`, managed node group, OIDC enabled |
| `infra/ecr-setup.sh` | Creates two ECR repos: `leon-sophia-backend`, `leon-sophia-frontend` |
| `infra/rds-setup.sh` | Creates RDS PostgreSQL 16 `db.t3.micro` in the EKS VPC private subnets |
| `infra/alb-controller-setup.sh` | Installs AWS Load Balancer Controller via Helm into EKS |
| `infra/README.md` | Step-by-step: prereqs, order of script execution, how to set GitHub Secrets |

All scripts accept environment variables for region, cluster name, and account ID — no hard-coded values.

---

## 7. CI/CD Pipeline (`.github/workflows/`)

### 7a. `test.yml` — runs on every PR
1. `pytest` (backend)
2. `vitest run` (frontend)

### 7b. `deploy.yml` — runs on push to `main`
```
1. Checkout
2. Run pytest + vitest (fail fast)
3. Configure AWS credentials (OIDC — no long-lived keys)
4. Log in to ECR
5. Build + push backend image  (tag: git SHA)
6. Build + push frontend image (tag: git SHA)
7. Substitute image tags in k8s manifests (envsubst)
8. Inject secrets from GitHub Secrets into secret.yaml (envsubst)
9. kubectl apply -f k8s/
10. kubectl rollout status deployment/backend -n leon-sophia
11. kubectl rollout status deployment/frontend -n leon-sophia
```

**AWS auth in CI:** Uses OIDC (no stored AWS keys). The EKS cluster trusts the GitHub Actions OIDC provider; CI assumes a deploy role scoped to ECR push + EKS apply.

---

## 8. Configuration Variables

All configurable values live in one place: `infra/config.env` (gitignored) and as GitHub Secrets/Variables. Manifests reference them via `envsubst`.

| Variable | Where set | Default |
|----------|-----------|---------|
| `AWS_REGION` | `config.env` + GitHub Variable | *(must set)* |
| `AWS_ACCOUNT_ID` | `config.env` + GitHub Variable | *(must set)* |
| `CLUSTER_NAME` | `config.env` | `leon-sophia` |
| `ANTHROPIC_API_KEY` | GitHub Secret | *(must set)* |
| `DB_PASSWORD` | GitHub Secret | *(must set)* |
| `DOMAIN` | GitHub Variable (optional) | *(ALB DNS used if unset)* |
| `FRONTEND_PORT` | docker-compose only | `5175` |

---

## 9. File Structure (new files only)

```
leon-sophia-system/
├── backend/
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── nginx.conf
├── docker-compose.yml
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml            ← template, no real values
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
├── infra/
│   ├── eks-cluster.yaml       ← eksctl cluster spec
│   ├── ecr-setup.sh
│   ├── rds-setup.sh
│   ├── alb-controller-setup.sh
│   ├── config.env.example     ← template for config.env (gitignored)
│   └── README.md
└── .github/
    └── workflows/
        ├── test.yml
        └── deploy.yml
```

---

## 10. PWA on Production

The React app is a PWA — the service worker caches the app shell. On production, the frontend nginx container serves the `dist/` build (already generated by `vite build`, which includes `sw.js` and `manifest.webmanifest`). No changes needed to the PWA configuration.

---

## 11. Database Migration

On first deploy, the backend's `create_db()` call (in `db.py`) runs `SQLModel.metadata.create_all(engine)` which creates all tables. This is fine for initial setup. For future schema changes, a migration tool (Alembic) should be added — out of scope for this spec.
