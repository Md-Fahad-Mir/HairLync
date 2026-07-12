#!/bin/bash
# ─── rollback.sh ──────────────────────────────────────────────────────
# Roll HairIQ production back to a previous image tag (git SHA) in ECR.
# Usage:  REGISTRY=<acct>.dkr.ecr.eu-north-1.amazonaws.com \
#         EC2_HOST=13.48.88.3 ./rollback.sh <git-sha> [service...]
#
# With no services given, all services are rolled back (original behavior).
#
# NOTE: since CI builds images selectively, a given commit SHA only has
# images for the services that changed in that commit. Roll back per
# service to the last SHA that BUILT that service (check ECR image tags:
#   aws ecr describe-images --repository-name hairiq-<svc> \
#     --query 'sort_by(imageDetails,&imagePushedAt)[-5:].imageTags')
# A missing image fails the pull step and the rollback aborts before
# any container is touched.
set -euo pipefail

VALID_SERVICES=(backend ai admin landing)  # docker compose service names

ROLLBACK_TAG="${1:?Usage: ./rollback.sh <git-sha-or-tag> [service...]}"
shift

if ! printf '%s' "$ROLLBACK_TAG" | grep -Eq '^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$'; then
  echo "ERROR: '$ROLLBACK_TAG' is not a valid image tag." >&2
  exit 2
fi

DEPLOY_ALL=false
SELECTED=()
if [ "$#" -eq 0 ] || { [ "$#" -eq 1 ] && [ "$1" = "all" ]; }; then
  DEPLOY_ALL=true
  SELECTED=("${VALID_SERVICES[@]}")
else
  for arg in "$@"; do
    valid=false
    for s in "${VALID_SERVICES[@]}"; do
      [ "$arg" = "$s" ] && valid=true
    done
    if ! $valid; then
      echo "ERROR: unknown service '$arg'. Valid: ${VALID_SERVICES[*]} (or 'all')." >&2
      exit 2
    fi
    duplicate=false
    for s in ${SELECTED[@]+"${SELECTED[@]}"}; do
      [ "$arg" = "$s" ] && duplicate=true
    done
    $duplicate || SELECTED+=("$arg")
  done
  [ "${#SELECTED[@]}" -eq "${#VALID_SERVICES[@]}" ] && DEPLOY_ALL=true
fi

PROJECT_NAME="${PROJECT_NAME:-hairiq}"
REGISTRY="${REGISTRY:?REGISTRY env var required (your ECR registry URL)}"
EC2_HOST="${EC2_HOST:?EC2_HOST env var required}"
AWS_REGION="${AWS_REGION:-eu-north-1}"

echo "▶ Rolling back HairIQ services [${SELECTED[*]}] to image tag: $ROLLBACK_TAG"

if $DEPLOY_ALL; then
  UP_ARGS="--remove-orphans"
  SERVICE_ARGS=""
else
  # --no-deps: never recreate unaffected dependency services.
  UP_ARGS="--no-deps"
  SERVICE_ARGS="${SELECTED[*]}"
fi

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

  \$COMPOSE pull $SERVICE_ARGS
  \$COMPOSE up -d --force-recreate $UP_ARGS $SERVICE_ARGS

  echo "HairIQ rollback of [${SELECTED[*]}] to $ROLLBACK_TAG complete."
  \$COMPOSE ps
EOF
