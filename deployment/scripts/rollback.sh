#!/bin/bash
# ─── rollback.sh ──────────────────────────────────────────────────────
# Roll HairIQ production back to a previous image tag (git SHA) in ECR.
# Usage:  REGISTRY=<acct>.dkr.ecr.eu-north-1.amazonaws.com \
#         EC2_HOST=13.48.88.3 ./rollback.sh <git-sha>
set -euo pipefail

ROLLBACK_TAG="${1:?Usage: ./rollback.sh <git-sha-or-tag>}"
PROJECT_NAME="${PROJECT_NAME:-hairiq}"
REGISTRY="${REGISTRY:?REGISTRY env var required (your ECR registry URL)}"
EC2_HOST="${EC2_HOST:?EC2_HOST env var required}"
AWS_REGION="${AWS_REGION:-eu-north-1}"

echo "▶ Rolling back HairIQ to image tag: $ROLLBACK_TAG"

ssh -i ~/.ssh/id_rsa "ubuntu@$EC2_HOST" << EOF
  set -euo pipefail
  cd /home/ubuntu/$PROJECT_NAME
  export PATH=\$PATH:/usr/local/bin
  export REGISTRY='$REGISTRY'
  export IMAGE_TAG='$ROLLBACK_TAG'

  # Authenticate to ECR via the instance profile, then redeploy the tag.
  aws ecr get-login-password --region $AWS_REGION \
    | docker login --username AWS --password-stdin "$REGISTRY"

  COMPOSE="docker compose \
    -f deployment/compose/docker-compose.base.yml \
    -f deployment/compose/production/docker-compose.yml"

  \$COMPOSE pull
  \$COMPOSE up -d --force-recreate --remove-orphans

  echo "HairIQ rollback to $ROLLBACK_TAG complete."
  \$COMPOSE ps
EOF
