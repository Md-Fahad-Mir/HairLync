#!/bin/bash
# ─── rollback.sh ──────────────────────────────────────────────────────
# Roll back HairIQ to the previous Docker image tag on production.
# Usage: ./rollback.sh <image-sha-or-tag>
# Example: ./rollback.sh abc1234
set -euo pipefail

ROLLBACK_TAG="${1:?Usage: ./rollback.sh <image-sha-or-tag>}"
PROJECT_NAME="${PROJECT_NAME:?PROJECT_NAME env var required}"
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:?DOCKERHUB_USERNAME env var required}"
EC2_HOST="${EC2_HOST:?EC2_HOST env var required}"

echo "▶ Rolling back HairIQ to tag: $ROLLBACK_TAG"

ssh -i ~/.ssh/id_rsa "ubuntu@$EC2_HOST" << EOF
  set -e
  cd /home/ubuntu/$PROJECT_NAME

  # Update image tags in compose (quick inline replace)
  export IMAGE_TAG=$ROLLBACK_TAG
  docker compose -f docker-compose.prod.yml pull
  docker compose -f docker-compose.prod.yml up -d --force-recreate --remove-orphans
  
  echo "HairIQ rollback to $ROLLBACK_TAG complete."
  docker compose -f docker-compose.prod.yml ps
EOF
