#!/bin/bash
# ─── configure-server.sh ──────────────────────────────────────────────
# Run Ansible to configure a HairIQ server for a given environment.
# Usage: ./configure-server.sh [production|staging]
set -euo pipefail

ENV="${1:-staging}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")/../infrastructure/ansible"

echo "▶ Configuring HairIQ $ENV server with Ansible..."

cd "$ANSIBLE_DIR"
ansible-playbook \
  -i "inventories/$ENV/hosts" \
  -e "env=$ENV" \
  playbooks/site.yml

echo "✓ HairIQ server configuration complete for $ENV"
