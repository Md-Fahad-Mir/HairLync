# HairIQ Deployment Guide

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker | 24+ | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | v2+ | Included with Docker Desktop |
| Terraform | 1.5+ | [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform/install) |
| Ansible | 2.15+ | `pip install ansible` |
| AWS CLI | 2+ | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |

---

## First-Time Setup

### 1. Configure AWS Credentials

```bash
aws configure --profile default
# Enter Access Key, Secret Key, Region (eu-north-1)
```

### 2. Create Environment Files

```bash
# Copy templates and fill in real values
cp deployment/environments/backend.env.example deployment/environments/.env.production.backend
cp deployment/environments/ai.env.example      deployment/environments/.env.production.ai
cp deployment/environments/admin.env.example    deployment/environments/.env.production.admin
cp deployment/environments/landing.env.example  deployment/environments/.env.production.landing

# Edit each file with real credentials
nano deployment/environments/.env.production.backend
```

### 3. Update Terraform Variables

```bash
# Edit the production main.tf with your values
nano infrastructure/terraform/environments/production/main.tf
# - Set domain, ami, allowed_ssh_cidrs
# - Set db_username and db_password via TF_VAR_ env vars
export TF_VAR_db_username="hairiq_admin"
export TF_VAR_db_password="your_strong_password"
```

### 4. Provision Infrastructure

```bash
make tf-apply ENV=production
# Note the output: server IP and RDS endpoint
```

### 5. Update Ansible Inventory

```bash
# Add your EC2 Elastic IP to the inventory
nano infrastructure/ansible/inventories/production/hosts
# Replace YOUR.EC2.ELASTIC.IP with the actual IP from terraform output
```

### 6. Configure the Server

```bash
make ansible-prod
# This installs Docker, Nginx, copies configs, obtains SSL
```

---

## Daily Deployments (CI/CD)

Deployments happen **automatically** on push to `main`:

1. GitHub Actions builds all Docker images
2. Tags them with Git SHA + `latest`
3. Pushes to Docker Hub
4. SSHs to EC2 and runs `docker compose pull && up -d`

**Required GitHub Secrets:**

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `EC2_HOST` | EC2 Elastic IP |
| `EC2_SSH_PRIVATE_KEY` | Private SSH key |

**Required GitHub Variables:**

| Variable | Description |
|----------|-------------|
| `PROJECT_NAME` | `hairiq` |
| `NEXT_PUBLIC_API_URL` | `https://api.hairlync.com` |

---

## Local Development

```bash
make up-local
# Services available at:
# - Backend:   http://localhost:8000
# - AI:        http://localhost:8001
# - Landing:   http://localhost:3000
# - Admin:     http://localhost:3001
```

---

## Rollback

```bash
# Find the previous image SHA in GitHub Actions run history
# Then rollback:
export PROJECT_NAME=hairiq
export DOCKERHUB_USERNAME=yourusername
export EC2_HOST=your.ec2.ip
make rollback TAG=abc1234
```

---

## Environment Variable Management

**Never commit real `.env` files.** Use one of:

1. **Local**: Copy `.env.example` → `.env.production.*`, fill values
2. **CI/CD**: GitHub Secrets → injected at build/deploy time
3. **Production**: AWS Secrets Manager (recommended for teams)

---

## SSL Certificates

SSL is provisioned automatically by the Ansible `certbot` role using Let's Encrypt.

Auto-renewal is handled by the `certbot.timer` systemd timer — no manual action needed.

To force renewal:
```bash
ssh ubuntu@your.ec2.ip "sudo certbot renew --force-renewal"
```
