#!/bin/bash
# ─── server-deploy.sh ─────────────────────────────────────────────────
# Runs ON the EC2 box (invoked by CI via SSM, or manually). Authenticates
# to ECR via the instance profile, pulls the requested image tag, restarts
# the stack, and runs migrations.
# Required env: REGISTRY, IMAGE_TAG.  Optional: AWS_REGION (default eu-north-1).
set -euo pipefail

: "${REGISTRY:?REGISTRY env var required}"
: "${IMAGE_TAG:?IMAGE_TAG env var required}"
AWS_REGION="${AWS_REGION:-eu-north-1}"
export PATH="$PATH:/usr/local/bin"
export REGISTRY IMAGE_TAG

cd /home/ubuntu/hairiq

# Authenticate Docker to ECR using the EC2 instance profile (no static keys).
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

COMPOSE="docker compose \
  -f deployment/compose/docker-compose.base.yml \
  -f deployment/compose/production/docker-compose.yml"

# Reclaim disk from old layers before pulling new ones.
docker system prune -af --filter "until=24h" || true

# Pull the images for this exact tag, recreate containers, migrate.
$COMPOSE pull
$COMPOSE up -d --force-recreate --remove-orphans
$COMPOSE exec -T backend python manage.py migrate --noinput

$COMPOSE ps
