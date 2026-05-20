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
