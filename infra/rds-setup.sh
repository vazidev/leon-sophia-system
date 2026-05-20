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
