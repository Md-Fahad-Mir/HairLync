#!/bin/bash
# ─── deploy.sh ────────────────────────────────────────────────────────
# Full HairIQ deployment script: Terraform → Ansible → Docker Compose
# Usage: ./deploy.sh [production|staging]
set -euo pipefail

ENV="${1:-production}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  HairIQ — Deploying to: $ENV"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ "$ENV" != "production" && "$ENV" != "staging" ]]; then
  echo "Error: environment must be 'production' or 'staging'"
  exit 1
fi

# Step 1: Provision infrastructure (if needed)
echo ""
echo "▶ Step 1: Terraform apply ($ENV)"
cd "$DEPLOY_DIR/../infrastructure/terraform/environments/$ENV"
terraform init
terraform apply -auto-approve

# Step 2: Configure server
echo ""
echo "▶ Step 2: Ansible configure ($ENV)"
cd "$DEPLOY_DIR/../infrastructure/ansible"
ansible-playbook \
  -i "inventories/$ENV/hosts" \
  -e "env=$ENV" \
  playbooks/site.yml

echo ""
echo "✓ HairIQ deployment to $ENV complete!"
