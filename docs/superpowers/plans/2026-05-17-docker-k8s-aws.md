# Docker / Kubernetes / AWS Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Containerise LEON·SOPHIA (FastAPI backend + React frontend) and deploy to AWS EKS with GitHub Actions CI/CD, while keeping local dev working via Docker Compose.

**Architecture:** Two Docker images — backend (Python multi-stage, uvicorn) and frontend (Node build + nginx static). Kubernetes manifests target AWS EKS. An ALB Ingress routes `/api/*` to the backend service and `/*` to the frontend service; sticky sessions on all target groups fix the SSE long-lived connection problem. GitHub Actions builds images on push to `main`, pushes to ECR via OIDC (no stored AWS keys), and rolls out to EKS. Local dev runs natively (existing workflow) or via `docker-compose up`.

**Tech Stack:** Docker 24+, docker-compose v2, Kubernetes 1.29+, eksctl 0.180+, AWS (EKS, ECR, RDS PostgreSQL 16, ALB, Secrets Manager), GitHub Actions (OIDC), nginx:alpine, Helm 3 (ALB controller only)

---

## File Map

Files to **create** (all new — no existing files deleted):

```
backend/
  Dockerfile
  .dockerignore
frontend/
  Dockerfile
  .dockerignore
  nginx.conf
docker-compose.yml
k8s/
  namespace.yaml
  configmap.yaml
  secret.yaml              ← template only, no real values committed
  backend-deployment.yaml
  backend-service.yaml
  frontend-deployment.yaml
  frontend-service.yaml
  ingress.yaml
  hpa.yaml
infra/
  eks-cluster.yaml
  ecr-setup.sh
  rds-setup.sh
  alb-controller-setup.sh
  config.env.example
  README.md
.github/
  workflows/
    test.yml
    deploy.yml
```

Files to **modify**:
- `frontend/vite.config.ts` — add `port: 5175`, make proxy target env-configurable
- `.gitignore` — add `infra/config.env`

---

### Task 1: Backend Dockerfile + .dockerignore

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`

**Context:** The backend is a FastAPI app started with `uvicorn main:app`. It reads `ANTHROPIC_API_KEY` and `DATABASE_URL` from env vars. The `/health` endpoint returns `{"status":"ok"}`.

- [ ] **Step 1: Create `backend/.dockerignore`**

```
.venv/
__pycache__/
*.pyc
*.pyo
*.db
.env
tests/
*.egg-info/
.pytest_cache/
dist/
```

- [ ] **Step 2: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Build the image and verify it starts**

Run from the repo root:
```bash
docker build -t leon-sophia-backend ./backend
docker run --rm -d --name test-backend \
  -p 8001:8000 \
  -e ANTHROPIC_API_KEY=test \
  -e DATABASE_URL=sqlite:///./test.db \
  leon-sophia-backend
sleep 3
curl -sf http://localhost:8001/health
docker stop test-backend
```

Expected output: `{"status":"ok"}`

- [ ] **Step 4: Commit**

```bash
git add backend/Dockerfile backend/.dockerignore
git commit -m "feat: backend Dockerfile — multi-stage python:3.12-slim"
```

---

### Task 2: Frontend Dockerfile + nginx.conf + .dockerignore

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`
- Create: `frontend/.dockerignore`

**Context:** The frontend is a React/Vite PWA. `npm run build` produces `dist/`. The ALB Ingress (not nginx) routes `/api/*` to the backend service — nginx only serves static files. The SPA needs a catch-all fallback to `index.html`.

- [ ] **Step 1: Create `frontend/.dockerignore`**

```
node_modules/
dist/
.env*.local
```

- [ ] **Step 2: Create `frontend/nginx.conf`**

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;

    # Cache hashed static assets forever
    location ~* \.(js|css|png|svg|ico|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback — React Router handles all paths client-side
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 3: Create `frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 4: Build the image and verify it serves**

Run from the repo root:
```bash
docker build -t leon-sophia-frontend ./frontend
docker run --rm -d --name test-frontend -p 8082:80 leon-sophia-frontend
sleep 2
curl -sf http://localhost:8082 | grep -q "LEON" && echo "PASS: HTML contains LEON"
docker stop test-frontend
```

Expected output: `PASS: HTML contains LEON`

- [ ] **Step 5: Commit**

```bash
git add frontend/Dockerfile frontend/.dockerignore frontend/nginx.conf
git commit -m "feat: frontend Dockerfile — node:20 build + nginx:alpine static serve"
```

---

### Task 3: Update vite.config.ts — port 5175 + env-configurable proxy

**Files:**
- Modify: `frontend/vite.config.ts`

**Context:** The user has something else on port 5173. The proxy target must be configurable so docker-compose can point it at the `backend` container (`http://backend:8000`) while native dev still uses `http://localhost:8000`. The `process.env` read in `vite.config.ts` is Node.js context (not browser), so it reads the shell env at dev-server startup.

- [ ] **Step 1: Update `frontend/vite.config.ts`**

Replace the entire file:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'LEON · SOPHIA',
        short_name: 'LEON·SOPHIA',
        start_url: '/',
        display: 'standalone',
        background_color: '#f6f8fa',
        theme_color: '#0969da',
        icons: [{ src: '/icon-512.svg', sizes: '512x512', type: 'image/svg+xml' }]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: []
      }
    })
  ],
  server: {
    port: 5175,
    proxy: {
      '/api': process.env.VITE_API_TARGET || 'http://localhost:8000'
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/tests/setup.ts']
  }
})
```

- [ ] **Step 2: Run the existing test suite to confirm nothing broke**

```bash
cd frontend && npm test -- --run
```

Expected output:
```
Test Files  2 passed (2)
     Tests  4 passed (4)
```

- [ ] **Step 3: Commit**

```bash
git add frontend/vite.config.ts
git commit -m "feat: vite dev server on port 5175, env-configurable API proxy target"
```

---

### Task 4: docker-compose.yml

**Files:**
- Create: `docker-compose.yml` (repo root)

**Context:** Three services — `db` (postgres:16), `backend` (FastAPI with live-reload), `frontend` (Vite dev server). The frontend service uses a named volume for `node_modules` to avoid native-module conflicts between host and container. `VITE_API_TARGET=http://backend:8000` makes Vite proxy to the correct container.

- [ ] **Step 1: Create `docker-compose.yml` in the repo root**

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD:-devpassword}
      POSTGRES_DB: leonsophia
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    environment:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD:-devpassword}@db:5432/leonsophia
      FRONTEND_ORIGIN: http://localhost:5175
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    image: node:20-alpine
    working_dir: /app
    ports:
      - "5175:5175"
    environment:
      VITE_API_TARGET: http://backend:8000
    volumes:
      - ./frontend:/app
      - frontend_node_modules:/app/node_modules
    command: sh -c "npm install && npm run dev -- --host 0.0.0.0"
    depends_on:
      - backend

volumes:
  postgres_data:
  frontend_node_modules:
```

- [ ] **Step 2: Validate the compose file syntax**

```bash
docker-compose config
```

Expected: YAML output with no errors.

- [ ] **Step 3: Smoke-test the stack**

Create a minimal `.env` file in the repo root (if not present):
```bash
echo "ANTHROPIC_API_KEY=test-key-placeholder" > .env
```

Then:
```bash
docker-compose up -d --build
sleep 15
curl -sf http://localhost:8000/health
```

Expected: `{"status":"ok"}`

```bash
docker-compose down
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: docker-compose — postgres + backend (reload) + frontend (vite dev)"
```

---

### Task 5: Kubernetes — namespace, ConfigMap, Secret template

**Files:**
- Create: `k8s/namespace.yaml`
- Create: `k8s/configmap.yaml`
- Create: `k8s/secret.yaml`

**Context:** All K8s resources live in the `leon-sophia` namespace. The ConfigMap holds non-sensitive config (`FRONTEND_ORIGIN`). The Secret template has `${PLACEHOLDER}` values — CI/CD substitutes real values via `envsubst` at deploy time. Never commit real secret values.

- [ ] **Step 1: Create `k8s/namespace.yaml`**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: leon-sophia
```

- [ ] **Step 2: Create `k8s/configmap.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: leon-sophia-config
  namespace: leon-sophia
data:
  FRONTEND_ORIGIN: "${FRONTEND_ORIGIN}"
```

- [ ] **Step 3: Create `k8s/secret.yaml`**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: leon-sophia-secrets
  namespace: leon-sophia
type: Opaque
stringData:
  ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}"
  DATABASE_URL: "postgresql://postgres:${DB_PASSWORD}@${DB_HOST}:5432/leonsophia"
```

- [ ] **Step 4: Validate with dry-run (requires kubectl)**

```bash
kubectl apply --dry-run=client -f k8s/namespace.yaml
```

Expected: `namespace/leon-sophia created (dry run)`

For configmap and secret, dry-run will fail because `${...}` are literal (not substituted). That's expected — they require envsubst before applying. Confirm the YAML is valid:

```bash
python3 -c "import yaml; yaml.safe_load(open('k8s/configmap.yaml'))" && echo "valid YAML"
python3 -c "import yaml; yaml.safe_load(open('k8s/secret.yaml'))" && echo "valid YAML"
```

Expected: `valid YAML` for both.

- [ ] **Step 5: Commit**

```bash
git add k8s/namespace.yaml k8s/configmap.yaml k8s/secret.yaml
git commit -m "feat: k8s namespace, ConfigMap, Secret template"
```

---

### Task 6: Kubernetes — backend Deployment + Service

**Files:**
- Create: `k8s/backend-deployment.yaml`
- Create: `k8s/backend-service.yaml`

**Context:** `${ECR_REGISTRY}` and `${IMAGE_TAG}` are substituted by CI/CD using `envsubst '${ECR_REGISTRY} ${IMAGE_TAG}'` before `kubectl apply`. The readiness probe hits `/health` before the pod receives traffic. Secrets are mounted as env vars from the `leon-sophia-secrets` Secret.

- [ ] **Step 1: Create `k8s/backend-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: leon-sophia
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: ${ECR_REGISTRY}/leon-sophia-backend:${IMAGE_TAG}
          ports:
            - containerPort: 8000
          env:
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef:
                  name: leon-sophia-secrets
                  key: ANTHROPIC_API_KEY
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: leon-sophia-secrets
                  key: DATABASE_URL
            - name: FRONTEND_ORIGIN
              valueFrom:
                configMapKeyRef:
                  name: leon-sophia-config
                  key: FRONTEND_ORIGIN
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
```

- [ ] **Step 2: Create `k8s/backend-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: leon-sophia
spec:
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: ClusterIP
```

- [ ] **Step 3: Validate YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('k8s/backend-deployment.yaml'))" && echo "deployment: valid"
python3 -c "import yaml; yaml.safe_load(open('k8s/backend-service.yaml'))" && echo "service: valid"
```

Expected: `deployment: valid` and `service: valid`

- [ ] **Step 4: Commit**

```bash
git add k8s/backend-deployment.yaml k8s/backend-service.yaml
git commit -m "feat: k8s backend Deployment (2 replicas, health probes) + ClusterIP Service"
```

---

### Task 7: Kubernetes — frontend Deployment + Service

**Files:**
- Create: `k8s/frontend-deployment.yaml`
- Create: `k8s/frontend-service.yaml`

**Context:** The frontend is a stateless nginx container serving the pre-built React SPA. No secrets needed. The readiness probe hits `/` (nginx returns 200 immediately once started).

- [ ] **Step 1: Create `k8s/frontend-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: leon-sophia
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: ${ECR_REGISTRY}/leon-sophia-frontend:${IMAGE_TAG}
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 3
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 20
```

- [ ] **Step 2: Create `k8s/frontend-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: leon-sophia
spec:
  selector:
    app: frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

- [ ] **Step 3: Validate YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('k8s/frontend-deployment.yaml'))" && echo "deployment: valid"
python3 -c "import yaml; yaml.safe_load(open('k8s/frontend-service.yaml'))" && echo "service: valid"
```

Expected: `deployment: valid` and `service: valid`

- [ ] **Step 4: Commit**

```bash
git add k8s/frontend-deployment.yaml k8s/frontend-service.yaml
git commit -m "feat: k8s frontend Deployment (2 replicas, nginx) + ClusterIP Service"
```

---

### Task 8: Kubernetes — Ingress (ALB + sticky sessions) + HPA

**Files:**
- Create: `k8s/ingress.yaml`
- Create: `k8s/hpa.yaml`

**Context:** The ALB Ingress routes `/api` → backend service and `/` → frontend service. Two critical annotations: `idle_timeout.timeout_seconds=3600` prevents the ALB from dropping SSE connections after 60s (default). `stickiness.enabled=true` ensures the `/api/debate/{id}/stream` SSE request hits the same pod that handled the `POST /api/debate/start`. The HPA scales backend pods between 2 and 10 based on CPU.

- [ ] **Step 1: Create `k8s/ingress.yaml`**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: leon-sophia
  namespace: leon-sophia
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    # Prevent ALB from closing SSE connections after the default 60s idle timeout
    alb.ingress.kubernetes.io/load-balancer-attributes: idle_timeout.timeout_seconds=3600
    # Sticky sessions: routes all requests from one client to the same backend pod
    alb.ingress.kubernetes.io/target-group-attributes: stickiness.enabled=true,stickiness.lb_cookie.duration_seconds=3600
    # Uncomment and fill in ACM_CERT_ARN to enable HTTPS for a custom domain:
    # alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:REGION:ACCOUNT:certificate/CERT-ID
    # alb.ingress.kubernetes.io/ssl-redirect: "443"
spec:
  rules:
    - http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
```

- [ ] **Step 2: Create `k8s/hpa.yaml`**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: leon-sophia
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

- [ ] **Step 3: Validate YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('k8s/ingress.yaml'))" && echo "ingress: valid"
python3 -c "import yaml; yaml.safe_load(open('k8s/hpa.yaml'))" && echo "hpa: valid"
```

Expected: `ingress: valid` and `hpa: valid`

- [ ] **Step 4: Commit**

```bash
git add k8s/ingress.yaml k8s/hpa.yaml
git commit -m "feat: k8s ALB Ingress (sticky sessions, 3600s idle timeout) + HPA"
```

---

### Task 9: AWS infrastructure scripts

**Files:**
- Create: `infra/eks-cluster.yaml`
- Create: `infra/ecr-setup.sh`
- Create: `infra/rds-setup.sh`
- Create: `infra/alb-controller-setup.sh`
- Create: `infra/config.env.example`

**Context:** These scripts are run once by a human operator before the first deploy. They are idempotent — safe to re-run. All scripts `source "$(dirname "$0")/config.env"` to read operator-supplied values. `config.env` is gitignored (added in Task 12).

- [ ] **Step 1: Create `infra/config.env.example`**

```bash
# Copy this file to infra/config.env and fill in your values.
# infra/config.env is gitignored — never commit real values.

AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
CLUSTER_NAME=leon-sophia
DB_PASSWORD=change-me-to-a-strong-password
```

- [ ] **Step 2: Create `infra/eks-cluster.yaml`**

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: leon-sophia
  region: us-east-1   # Change to match your AWS_REGION

managedNodeGroups:
  - name: workers
    instanceType: t3.medium
    minSize: 2
    maxSize: 4
    desiredCapacity: 2
    volumeSize: 20
    amiFamily: AmazonLinux2

iam:
  withOIDC: true   # Required for ALB controller and GitHub Actions OIDC
```

- [ ] **Step 3: Create `infra/ecr-setup.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/config.env"

for repo in leon-sophia-backend leon-sophia-frontend; do
  aws ecr create-repository \
    --repository-name "$repo" \
    --region "$AWS_REGION" \
    --image-scanning-configuration scanOnPush=true \
    2>/dev/null && echo "Created: $repo" || echo "Already exists: $repo"
done

echo ""
echo "ECR registry: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
echo "Add this as GitHub Variable AWS_ACCOUNT_ID and AWS_REGION."
```

- [ ] **Step 4: Create `infra/rds-setup.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/config.env"

VPC_ID=$(aws eks describe-cluster \
  --name "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --query "cluster.resourcesVpcConfig.vpcId" \
  --output text)

echo "Using VPC: $VPC_ID"

SUBNET_IDS=$(aws ec2 describe-subnets \
  --filters \
    "Name=vpc-id,Values=$VPC_ID" \
    "Name=tag:kubernetes.io/role/internal-elb,Values=1" \
  --query "Subnets[*].SubnetId" \
  --region "$AWS_REGION" \
  --output text | tr '\t' ',')

aws rds create-db-subnet-group \
  --db-subnet-group-name leon-sophia-db \
  --db-subnet-group-description "Leon-Sophia RDS subnet group" \
  --subnet-ids $SUBNET_IDS \
  --region "$AWS_REGION" \
  2>/dev/null || echo "Subnet group already exists — skipping."

aws rds create-db-instance \
  --db-instance-identifier leon-sophia-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version "16" \
  --master-username postgres \
  --master-user-password "$DB_PASSWORD" \
  --db-name leonsophia \
  --db-subnet-group-name leon-sophia-db \
  --no-publicly-accessible \
  --storage-type gp3 \
  --allocated-storage 20 \
  --region "$AWS_REGION" \
  2>/dev/null || echo "RDS instance already exists — skipping."

echo ""
echo "Waiting for RDS to be available (takes ~5 min)..."
aws rds wait db-instance-available --db-instance-identifier leon-sophia-db --region "$AWS_REGION"

DB_HOST=$(aws rds describe-db-instances \
  --db-instance-identifier leon-sophia-db \
  --region "$AWS_REGION" \
  --query "DBInstances[0].Endpoint.Address" \
  --output text)

echo "RDS endpoint: $DB_HOST"
echo "Add DB_HOST=$DB_HOST as a GitHub Secret."
echo "Add DB_PASSWORD as a GitHub Secret."
```

- [ ] **Step 5: Create `infra/alb-controller-setup.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/config.env"

# Download and create IAM policy
curl -sLo /tmp/alb-iam-policy.json \
  https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.0/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file:///tmp/alb-iam-policy.json \
  --region "$AWS_REGION" \
  2>/dev/null || echo "IAM policy already exists — skipping."

# Create IRSA (IAM Role for Service Account)
eksctl create iamserviceaccount \
  --cluster="$CLUSTER_NAME" \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name "AmazonEKSLoadBalancerControllerRole-${CLUSTER_NAME}" \
  --attach-policy-arn="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy" \
  --approve \
  --region "$AWS_REGION"

VPC_ID=$(aws eks describe-cluster \
  --name "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --query "cluster.resourcesVpcConfig.vpcId" \
  --output text)

# Install via Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName="$CLUSTER_NAME" \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region="$AWS_REGION" \
  --set vpcId="$VPC_ID"

echo ""
echo "Verify: kubectl get deployment -n kube-system aws-load-balancer-controller"
```

- [ ] **Step 6: Make scripts executable and validate bash syntax**

```bash
chmod +x infra/ecr-setup.sh infra/rds-setup.sh infra/alb-controller-setup.sh
bash -n infra/ecr-setup.sh && echo "ecr-setup.sh: syntax ok"
bash -n infra/rds-setup.sh && echo "rds-setup.sh: syntax ok"
bash -n infra/alb-controller-setup.sh && echo "alb-controller-setup.sh: syntax ok"
```

Expected: all three print `syntax ok`

- [ ] **Step 7: Commit**

```bash
git add infra/
git commit -m "feat: AWS infra scripts — EKS cluster spec, ECR, RDS, ALB controller"
```

---

### Task 10: infra/README.md — operator setup guide

**Files:**
- Create: `infra/README.md`

**Context:** This document is the operator's step-by-step guide for the one-time AWS setup and the GitHub repository configuration required before CI/CD can deploy.

- [ ] **Step 1: Create `infra/README.md`**

```markdown
# AWS Infrastructure Setup

One-time setup for LEON·SOPHIA on AWS EKS. Run each step in order.

## Prerequisites

Install these tools before starting:
- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) — configured with an IAM user/role that has AdministratorAccess
- [eksctl](https://eksctl.io/installation/) v0.180+
- [kubectl](https://kubernetes.io/docs/tasks/tools/) v1.29+
- [Helm](https://helm.sh/docs/intro/install/) v3+
- Docker Desktop

Verify:
```bash
aws --version && eksctl version && kubectl version --client && helm version
```

## Step 1: Configure

```bash
cp infra/config.env.example infra/config.env
# Edit infra/config.env — set AWS_REGION, AWS_ACCOUNT_ID, CLUSTER_NAME, DB_PASSWORD
```

## Step 2: Create EKS Cluster (~15 min)

```bash
# Substitute your region into the cluster spec first:
sed "s/us-east-1/$AWS_REGION/" infra/eks-cluster.yaml | eksctl create cluster -f -
```

Verify:
```bash
kubectl get nodes
```
Expected: 2 nodes in `Ready` state.

## Step 3: Create ECR Repositories

```bash
source infra/config.env
bash infra/ecr-setup.sh
```

## Step 4: Create RDS PostgreSQL (~5 min)

```bash
bash infra/rds-setup.sh
```

Copy the printed `DB_HOST` value — you'll need it in Step 7.

## Step 5: Install ALB Ingress Controller

```bash
bash infra/alb-controller-setup.sh
```

Verify (wait ~1 min):
```bash
kubectl get deployment -n kube-system aws-load-balancer-controller
```
Expected: `READY 1/1`

## Step 6: Create GitHub Actions IAM Role (OIDC)

The deploy workflow uses OIDC — no long-lived AWS keys stored in GitHub.

```bash
source infra/config.env

# Create the OIDC provider (once per AWS account)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  2>/dev/null || echo "OIDC provider already exists"

# Create the deploy role — replace YOUR_GITHUB_ORG/YOUR_REPO below
GITHUB_REPO="vazidev/leon-sophia-system"

cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:${GITHUB_REPO}:ref:refs/heads/main"
      }
    }
  }]
}
EOF

aws iam create-role \
  --role-name leon-sophia-github-deploy \
  --assume-role-policy-document file:///tmp/trust-policy.json

# Attach policies: ECR push + EKS access
aws iam attach-role-policy \
  --role-name leon-sophia-github-deploy \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

aws iam attach-role-policy \
  --role-name leon-sophia-github-deploy \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy

# Grant kubectl access in EKS
eksctl create iamidentitymapping \
  --cluster "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --arn "arn:aws:iam::${AWS_ACCOUNT_ID}:role/leon-sophia-github-deploy" \
  --group system:masters \
  --username github-actions
```

## Step 7: Configure GitHub Repository

Go to your repo → **Settings → Secrets and variables → Actions**.

**Secrets** (sensitive — never logged):
| Name | Value |
|------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (`sk-ant-...`) |
| `DB_PASSWORD` | The password you set in `config.env` |
| `DB_HOST` | The RDS endpoint printed by `rds-setup.sh` |

**Variables** (non-sensitive):
| Name | Value |
|------|-------|
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |
| `AWS_REGION` | e.g. `us-east-1` |
| `CLUSTER_NAME` | `leon-sophia` (or whatever you set) |
| `DOMAIN` | *(optional)* Your custom domain, e.g. `debate.example.com` |

## Step 8: First Deploy

Push to `main` — GitHub Actions will build images, push to ECR, and deploy to EKS.

Monitor:
```bash
kubectl get pods -n leon-sophia -w
kubectl get ingress -n leon-sophia
```

The ALB hostname appears under `ADDRESS` in the ingress output (~2 min after deploy). Open it in a browser.

## Optional: Custom Domain + HTTPS

1. Create an ACM certificate for your domain in the same region as EKS.
2. Set `DOMAIN` GitHub Variable to your domain.
3. Uncomment the two ACM annotations in `k8s/ingress.yaml` and set the cert ARN.
4. Create a CNAME or A-alias record in Route 53 pointing to the ALB hostname.
```

- [ ] **Step 2: Verify the document covers all spec requirements**

Read through the README and confirm:
- EKS cluster creation: ✓ (Step 2)
- ECR setup: ✓ (Step 3)
- RDS setup: ✓ (Step 4)
- ALB controller: ✓ (Step 5)
- OIDC/IAM for CI/CD: ✓ (Step 6)
- GitHub Secrets/Variables: ✓ (Step 7)
- First deploy: ✓ (Step 8)
- Custom domain + HTTPS: ✓ (Optional section)

- [ ] **Step 3: Commit**

```bash
git add infra/README.md
git commit -m "docs: infra/README.md — step-by-step AWS setup and first-deploy guide"
```

---

### Task 11: GitHub Actions — test.yml

**Files:**
- Create: `.github/workflows/test.yml`

**Context:** Runs on every PR against `main` and is callable from `deploy.yml` via `workflow_call`. Two parallel jobs: backend (pytest) and frontend (vitest). Both use dependency caching.

- [ ] **Step 1: Create `.github/workflows/test.yml`**

```yaml
name: Test

on:
  pull_request:
    branches: [main]
  workflow_call: {}

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        run: pip install -r requirements.txt
        working-directory: backend

      - name: Run pytest
        run: pytest --tb=short -q
        working-directory: backend

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci
        working-directory: frontend

      - name: Run vitest
        run: npm test -- --run
        working-directory: frontend
```

- [ ] **Step 2: Validate YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))" && echo "valid YAML"
```

Expected: `valid YAML`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/test.yml
git commit -m "feat: GitHub Actions test.yml — pytest + vitest on PRs and workflow_call"
```

---

### Task 12: GitHub Actions — deploy.yml + .gitignore update

**Files:**
- Create: `.github/workflows/deploy.yml`
- Modify: `.gitignore`

**Context:** Runs on push to `main`. Calls `test.yml` first (fails fast). Then authenticates to AWS via OIDC (no stored keys), builds both images, tags with the git SHA, pushes to ECR, substitutes image tags in K8s manifests via `envsubst`, applies all manifests, and waits for rollout. `infra/config.env` must be gitignored.

- [ ] **Step 1: Create `.github/workflows/deploy.yml`**

```yaml
name: Deploy

on:
  push:
    branches: [main]

permissions:
  id-token: write   # Required for OIDC
  contents: read

jobs:
  test:
    uses: ./.github/workflows/test.yml

  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC — no stored keys)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ vars.AWS_ACCOUNT_ID }}:role/leon-sophia-github-deploy
          aws-region: ${{ vars.AWS_REGION }}

      - name: Log in to ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set image vars
        run: |
          echo "IMAGE_TAG=$(git rev-parse --short HEAD)" >> $GITHUB_ENV
          echo "ECR_REGISTRY=${{ vars.AWS_ACCOUNT_ID }}.dkr.ecr.${{ vars.AWS_REGION }}.amazonaws.com" >> $GITHUB_ENV

      - name: Build and push backend image
        run: |
          docker build -t $ECR_REGISTRY/leon-sophia-backend:$IMAGE_TAG ./backend
          docker push $ECR_REGISTRY/leon-sophia-backend:$IMAGE_TAG

      - name: Build and push frontend image
        run: |
          docker build -t $ECR_REGISTRY/leon-sophia-frontend:$IMAGE_TAG ./frontend
          docker push $ECR_REGISTRY/leon-sophia-frontend:$IMAGE_TAG

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig \
            --name ${{ vars.CLUSTER_NAME }} \
            --region ${{ vars.AWS_REGION }}

      - name: Apply namespace and ConfigMap
        run: |
          kubectl apply -f k8s/namespace.yaml
          if [ -n "${{ vars.DOMAIN }}" ]; then
            export FRONTEND_ORIGIN="https://${{ vars.DOMAIN }}"
          else
            export FRONTEND_ORIGIN="http://pending-alb-hostname"
          fi
          envsubst '${FRONTEND_ORIGIN}' < k8s/configmap.yaml | kubectl apply -f -

      - name: Apply secrets
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          DB_HOST: ${{ secrets.DB_HOST }}
        run: |
          envsubst '${ANTHROPIC_API_KEY} ${DB_PASSWORD} ${DB_HOST}' \
            < k8s/secret.yaml | kubectl apply -f -

      - name: Deploy workloads
        run: |
          envsubst '${ECR_REGISTRY} ${IMAGE_TAG}' < k8s/backend-deployment.yaml  | kubectl apply -f -
          kubectl apply -f k8s/backend-service.yaml
          envsubst '${ECR_REGISTRY} ${IMAGE_TAG}' < k8s/frontend-deployment.yaml | kubectl apply -f -
          kubectl apply -f k8s/frontend-service.yaml
          kubectl apply -f k8s/ingress.yaml
          kubectl apply -f k8s/hpa.yaml

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/backend  -n leon-sophia --timeout=300s
          kubectl rollout status deployment/frontend -n leon-sophia --timeout=300s

      - name: Print ALB URL
        run: |
          sleep 20
          echo "ALB hostname:"
          kubectl get ingress leon-sophia -n leon-sophia \
            -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
          echo ""
```

- [ ] **Step 2: Validate YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))" && echo "valid YAML"
```

Expected: `valid YAML`

- [ ] **Step 3: Add `infra/config.env` to .gitignore**

Open `.gitignore` and add these lines at the end:

```
# AWS infra operator config — contains DB_PASSWORD, never commit
infra/config.env
```

- [ ] **Step 4: Commit everything and push**

```bash
git add .github/workflows/deploy.yml .gitignore
git commit -m "feat: GitHub Actions deploy.yml — OIDC auth, ECR push, EKS rollout"
git push origin main
```

- [ ] **Step 5: Verify workflows appear on GitHub**

Open `https://github.com/vazidev/leon-sophia-system/actions` in a browser.

Expected: the push triggered the "Deploy" workflow. It will fail at the `Configure AWS credentials` step until the AWS infra setup (infra/README.md) is complete — that's expected.
```

---

**Self-review running now.**

**Spec coverage check:**
- §1 Docker images: Tasks 1 + 2 ✓
- §3a Local dev native: no change needed (existing workflow unchanged) ✓
- §3b Docker Compose port 5175: Task 4 ✓
- §3b VITE_API_TARGET: Task 3 ✓
- §4a Backend multi-stage Dockerfile: Task 1 ✓
- §4b Frontend nginx.conf with static serve: Task 2 ✓
- §5 K8s manifests (all 9 files): Tasks 5–8 ✓
- §5a sticky sessions annotation: Task 8 ✓
- §5b Secret template / envsubst: Tasks 5 + 12 ✓
- §6 AWS infra scripts (eksctl, ECR, RDS, ALB): Task 9 ✓
- §7a test.yml: Task 11 ✓
- §7b deploy.yml (OIDC, envsubst, rollout): Task 12 ✓
- §8 config variables / .gitignore: Tasks 3 + 12 ✓
- §9 infra/README.md: Task 10 ✓
- §10 PWA: no change needed (nginx serves dist/ which already has sw.js) ✓
- §11 DB migration note: covered by existing `create_db()` call ✓

**Placeholder scan:** No TBDs, no "add appropriate" hedges. All code blocks complete.

**Type consistency:** `envsubst '${VAR}' < file | kubectl apply -f -` pattern used consistently in Task 5, Task 12. Secret key names (`ANTHROPIC_API_KEY`, `DATABASE_URL`) consistent between Task 5 (secret.yaml) and Task 6 (deployment secretKeyRef).
