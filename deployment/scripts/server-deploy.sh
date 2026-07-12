#!/bin/bash
# ─── server-deploy.sh ─────────────────────────────────────────────────
# Runs ON the EC2 box (invoked by CI via SSM, or manually). Authenticates
# to ECR via the instance profile, pulls ONLY the requested service
# images, recreates ONLY the requested services, runs Django migrations
# when the backend is among them, and waits for the deployed containers
# to become healthy.
#
# Usage:
#   server-deploy.sh <service> [service...]   services: backend ai admin landing
#   server-deploy.sh all
#
# Required env: REGISTRY, IMAGE_TAG.
# Optional env: AWS_REGION (default eu-north-1),
#               HEALTH_TIMEOUT_SECONDS (default 180).
#
# The image tags in the production compose file interpolate ${IMAGE_TAG}.
# CI only builds images for the services it deploys, so this script must
# never pull or recreate a service that is not in the requested list —
# its ${IMAGE_TAG} image may not exist for the current commit.
set -Eeuo pipefail

VALID_SERVICES=(backend ai admin landing)  # docker compose service names

usage() {
  echo "Usage: $0 <service> [service...] | all" >&2
  echo "Valid services: ${VALID_SERVICES[*]}" >&2
}

# ── Argument parsing & validation (before touching Docker or AWS) ─────
if [ "$#" -eq 0 ]; then
  echo "ERROR: no services specified." >&2
  usage
  exit 2
fi

DEPLOY_ALL=false
SELECTED=()
if [ "$#" -eq 1 ] && [ "$1" = "all" ]; then
  DEPLOY_ALL=true
  SELECTED=("${VALID_SERVICES[@]}")
else
  for arg in "$@"; do
    if [ "$arg" = "all" ]; then
      echo "ERROR: 'all' must be the only argument." >&2
      usage
      exit 2
    fi
    valid=false
    for s in "${VALID_SERVICES[@]}"; do
      [ "$arg" = "$s" ] && valid=true
    done
    if ! $valid; then
      echo "ERROR: unknown service '$arg'." >&2
      usage
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

: "${REGISTRY:?REGISTRY env var required}"
: "${IMAGE_TAG:?IMAGE_TAG env var required}"
AWS_REGION="${AWS_REGION:-eu-north-1}"
HEALTH_TIMEOUT_SECONDS="${HEALTH_TIMEOUT_SECONDS:-180}"
export PATH="$PATH:/usr/local/bin"
export REGISTRY IMAGE_TAG

compose() {
  docker compose \
    -f deployment/compose/docker-compose.base.yml \
    -f deployment/compose/production/docker-compose.yml \
    "$@"
}

print_diagnostics() {
  status=$?
  if [ "$status" -eq 0 ]; then
    return
  fi

  echo "Deploy failed with exit code $status" >&2
  echo "Docker compose service status:" >&2
  compose ps >&2 || true
  echo "Logs of the services in this deploy (last 200 lines):" >&2
  compose logs --tail=200 ${SELECTED[@]+"${SELECTED[@]}"} >&2 || true

  exit "$status"
}
trap print_diagnostics EXIT

cd /home/ubuntu/hairiq

# Cross-check the requested names against the real compose service names.
COMPOSE_SERVICES="$(compose config --services)"
for svc in "${SELECTED[@]}"; do
  if ! printf '%s\n' "$COMPOSE_SERVICES" | grep -qx "$svc"; then
    echo "ERROR: '$svc' is not a docker compose service. Available:" >&2
    printf '%s\n' "$COMPOSE_SERVICES" >&2
    exit 2
  fi
done

echo "▶ Deploying services: ${SELECTED[*]} (tag: $IMAGE_TAG)"

# Authenticate Docker to ECR using the EC2 instance profile (no static keys).
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

# Reclaim disk from old layers before pulling new ones.
docker system prune -af --filter "until=24h" || true

# Pull only the images for the services being deployed.
compose pull "${SELECTED[@]}"

if $DEPLOY_ALL; then
  compose up -d --force-recreate --remove-orphans
else
  # --no-deps: never touch dependencies (e.g. admin depends_on backend).
  # Unaffected services keep running their current containers and images.
  compose up -d --force-recreate --no-deps "${SELECTED[@]}"
fi

# ── Django migrations: only when the backend is part of this deploy ───
backend_selected=false
for svc in "${SELECTED[@]}"; do
  [ "$svc" = "backend" ] && backend_selected=true
done
if $backend_selected; then
  echo "▶ Running Django migrations (backend is in this deploy)..."
  compose exec -T backend python manage.py migrate --noinput
else
  echo "▷ Backend not in this deploy — skipping Django migrations."
fi

# ── Health gate: wait for each deployed service to become healthy ─────
wait_healthy() {
  local svc="$1" deadline=$((SECONDS + HEALTH_TIMEOUT_SECONDS)) cid state health
  cid="$(compose ps -q "$svc")"
  if [ -z "$cid" ]; then
    echo "✗ $svc: no container found after 'up'" >&2
    return 1
  fi
  while :; do
    state="$(docker inspect -f '{{.State.Status}}' "$cid")"
    health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid")"
    case "$state/$health" in
      running/healthy)
        echo "✓ $svc is healthy"
        return 0
        ;;
      running/none)
        echo "✓ $svc is running (no healthcheck defined — container state only)"
        return 0
        ;;
      exited/*|dead/*)
        echo "✗ $svc container is $state" >&2
        return 1
        ;;
    esac
    if [ "$SECONDS" -ge "$deadline" ]; then
      echo "✗ $svc not healthy after ${HEALTH_TIMEOUT_SECONDS}s (state=$state, health=$health)" >&2
      echo "Last healthcheck attempts:" >&2
      docker inspect -f '{{range .State.Health.Log}}{{.End}} exit={{.ExitCode}} {{.Output}}{{end}}' "$cid" 2>/dev/null | tail -5 >&2 || true
      return 1
    fi
    sleep 5
  done
}

echo "▶ Waiting for deployed services to become healthy (timeout: ${HEALTH_TIMEOUT_SECONDS}s each)..."
UNHEALTHY=()
for svc in "${SELECTED[@]}"; do
  wait_healthy "$svc" || UNHEALTHY+=("$svc")
done
if [ "${#UNHEALTHY[@]}" -gt 0 ]; then
  echo "✗ Deploy failed — unhealthy services: ${UNHEALTHY[*]}" >&2
  exit 1
fi

compose ps
echo "✓ Deploy complete. Services deployed: ${SELECTED[*]} (tag: $IMAGE_TAG)"
