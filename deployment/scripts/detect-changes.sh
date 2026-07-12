#!/usr/bin/env bash
# ─── detect-changes.sh ────────────────────────────────────────────────
# CI helper for selective (path-based) deployment. Decides which of the
# four services (backend, ai, admin, landing) are affected by a change
# set, so .github/workflows/deploy.yml builds and deploys only those.
#
# Modes:
#   detect-changes.sh diff <base-sha> <head-sha>
#       Classify `git diff <base> <head>`. Falls back to a full deploy
#       when no reliable base exists (first push, force push, zero SHA).
#   detect-changes.sh manual <selection>
#       Classify a workflow_dispatch input: 'all' or a comma/space
#       separated subset of: backend ai admin landing.
#   detect-changes.sh classify
#       Classify a newline-separated file list from stdin (test mode).
#
# Stdout — GitHub Actions job outputs (key=value):
#   backend|ai|admin|landing  true|false  service affected
#   deploy_all                true|false  full-stack deploy
#   deployment_required       true|false  at least one service affected
#   services                  "all" | "backend ai" | ""  argv for server-deploy.sh
#   infra_changed             true|false  nginx/monitoring/infrastructure files
#                                         changed (applied via Ansible/Terraform,
#                                         NOT by this pipeline)
#   reason                    short human-readable explanation
#   changed_count             number of files classified (diff/classify modes)
# Stderr — per-file classification log.
set -Eeuo pipefail

# Map one changed file to what it affects. First matching pattern wins.
#   backend|ai|admin|landing → that service's image + container
#   all   → every service (whole-pipeline or shared production runtime files)
#   infra → applied by Terraform/Ansible, not by this pipeline
#   none  → cannot affect production images or runtime
classify_path() {
  case "$1" in
    # Whole-pipeline files: the safest scope is a full deploy.
    .github/workflows/deploy.yml)                echo all ;;
    deployment/scripts/server-deploy.sh)         echo all ;;
    deployment/scripts/detect-changes.sh)        echo all ;;
    deployment/compose/docker-compose.base.yml)  echo all ;;
    deployment/compose/production/*)             echo all ;;

    # Per-service source trees (each includes its own Dockerfile).
    services/backend/*)                          echo backend ;;
    services/ai/*)                               echo ai ;;
    services/admin/*)                            echo admin ;;
    services/landing/*)                          echo landing ;;

    # Per-service deployment environment templates.
    deployment/environments/backend.env.example) echo backend ;;
    deployment/environments/ai.env.example)      echo ai ;;
    deployment/environments/admin.env.example)   echo admin ;;
    deployment/environments/landing.env.example) echo landing ;;

    # Not part of the production deploy path.
    deployment/compose/local/*)                  echo none ;;  # dev-only compose
    deployment/compose/staging/*)                echo none ;;  # staging compose
    deployment/scripts/*)                        echo none ;;  # operator tools (rollback, terraform wrappers)
    .github/*)                                   echo none ;;  # pr-checks / staging workflows
    Makefile)                                    echo none ;;  # operator tool, never used by CI
    docs/*|*.md|LICENSE|LICENSE.*|.gitignore)    echo none ;;
    .agents/*|.codex/*|.claude/*|.vscode/*|.idea/*|.editorconfig) echo none ;;

    # Applied via Ansible/Terraform (server/infra config), not via this pipeline.
    deployment/nginx/*)                          echo infra ;;
    deployment/monitoring/*)                     echo infra ;;
    infrastructure/*)                            echo infra ;;

    # Unknown file: we cannot prove it is safe to skip → deploy everything.
    *)                                           echo all ;;
  esac
}

F_BACKEND=false; F_AI=false; F_ADMIN=false; F_LANDING=false
DEPLOY_ALL=false; INFRA=false; CHANGED_COUNT=0
REASON=""

# Classify a newline-separated file list from stdin into the flags above.
classify_list() {
  local f cls
  # `|| [ -n "$f" ]` keeps the last line even without a trailing newline.
  while IFS= read -r f || [ -n "$f" ]; do
    [ -n "$f" ] || continue
    CHANGED_COUNT=$((CHANGED_COUNT + 1))
    cls="$(classify_path "$f")"
    echo "  [${cls}] ${f}" >&2
    case "$cls" in
      backend) F_BACKEND=true ;;
      ai)      F_AI=true ;;
      admin)   F_ADMIN=true ;;
      landing) F_LANDING=true ;;
      all)     DEPLOY_ALL=true ;;
      infra)   INFRA=true ;;
      none)    : ;;
    esac
  done
}

set_all() { F_BACKEND=true; F_AI=true; F_ADMIN=true; F_LANDING=true; DEPLOY_ALL=true; }

emit() {
  # Canonicalize: deploy_all implies every service; every service implies deploy_all.
  if $DEPLOY_ALL; then
    F_BACKEND=true; F_AI=true; F_ADMIN=true; F_LANDING=true
  elif $F_BACKEND && $F_AI && $F_ADMIN && $F_LANDING; then
    DEPLOY_ALL=true
  fi

  local required=false services=""
  if $F_BACKEND || $F_AI || $F_ADMIN || $F_LANDING; then required=true; fi
  if $DEPLOY_ALL; then
    services="all"
  elif $required; then
    $F_BACKEND && services="backend"
    $F_AI      && services="${services:+$services }ai"
    $F_ADMIN   && services="${services:+$services }admin"
    $F_LANDING && services="${services:+$services }landing"
  fi

  {
    echo "backend=$F_BACKEND"
    echo "ai=$F_AI"
    echo "admin=$F_ADMIN"
    echo "landing=$F_LANDING"
    echo "deploy_all=$DEPLOY_ALL"
    echo "deployment_required=$required"
    echo "services=$services"
    echo "infra_changed=$INFRA"
    echo "reason=$REASON"
    echo "changed_count=$CHANGED_COUNT"
  }

  # Human-readable summary for the GitHub Actions run page.
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    {
      echo "### Change detection"
      echo ""
      echo "${REASON}"
      echo ""
      echo "| Service | Affected |"
      echo "|---|---|"
      echo "| backend | $F_BACKEND |"
      echo "| ai | $F_AI |"
      echo "| admin | $F_ADMIN |"
      echo "| landing | $F_LANDING |"
      echo ""
      echo "- Full-stack deploy: **$DEPLOY_ALL**"
      echo "- Deployment required: **$required**"
      echo "- Files classified: **$CHANGED_COUNT**"
      if $INFRA; then
        echo ""
        echo "> ⚠️ Infrastructure/Nginx/monitoring files changed. Those are applied"
        echo "> with Ansible/Terraform (\`make ansible-prod\` / \`make tf-apply\`),"
        echo "> not by this pipeline."
      fi
    } >> "$GITHUB_STEP_SUMMARY"
  fi
}

die() { echo "ERROR: $*" >&2; exit 2; }

MODE="${1:-}"
case "$MODE" in
  diff)
    BASE="${2:-}"; HEAD="${3:-}"
    [ -n "$HEAD" ] || die "usage: $0 diff <base-sha> <head-sha>"
    if [ -z "$BASE" ] || printf '%s' "$BASE" | grep -Eq '^0+$'; then
      REASON="No previous commit to compare against (first push to the branch) — deploying all services for safety."
      echo "${REASON}" >&2
      set_all
    elif ! git rev-parse --quiet --verify "${BASE}^{commit}" >/dev/null; then
      REASON="Base commit ${BASE} is not reachable (force push or shallow history) — deploying all services for safety."
      echo "${REASON}" >&2
      set_all
    else
      REASON="Classified files changed between ${BASE} and ${HEAD}."
      echo "Changed files (${BASE}..${HEAD}):" >&2
      # Capture the diff first so a git failure aborts the job instead of
      # being silently classified as "nothing changed".
      DIFF_FILES="$(git diff --name-only "$BASE" "$HEAD")" || die "git diff ${BASE} ${HEAD} failed"
      classify_list <<< "$DIFF_FILES"
      if [ "$CHANGED_COUNT" -eq 0 ]; then
        REASON="No files changed between ${BASE} and ${HEAD} — nothing to deploy."
      fi
    fi
    emit
    ;;

  manual)
    SELECTION="${2:-}"
    # Normalize and sanitize: the value comes from a workflow_dispatch input,
    # so strip any control characters that could break key=value outputs.
    SELECTION="$(printf '%s' "$SELECTION" | tr '[:upper:]' '[:lower:]' | tr ',\n\r\t' '    ')"
    read -ra TOKENS <<< "$SELECTION" || true
    [ "${#TOKENS[@]}" -gt 0 ] || die "empty service selection; use 'all' or a comma-separated subset of: backend ai admin landing"
    for t in "${TOKENS[@]}"; do
      case "$t" in
        all)
          [ "${#TOKENS[@]}" -eq 1 ] || die "'all' must be the only selection (got: ${TOKENS[*]})"
          set_all
          ;;
        backend) F_BACKEND=true ;;
        ai)      F_AI=true ;;
        admin)   F_ADMIN=true ;;
        landing) F_LANDING=true ;;
        *) die "unknown service '$t'; valid: all backend ai admin landing" ;;
      esac
    done
    REASON="Manual workflow_dispatch selection: ${SELECTION}."
    echo "${REASON}" >&2
    emit
    ;;

  classify)
    REASON="Classified file list from stdin."
    echo "Changed files (stdin):" >&2
    classify_list
    if [ "$CHANGED_COUNT" -eq 0 ]; then
      REASON="Empty change set — nothing to deploy."
    fi
    emit
    ;;

  *)
    die "usage: $0 diff <base-sha> <head-sha> | manual <selection> | classify"
    ;;
esac
