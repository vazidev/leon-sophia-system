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
