# HairIQ Infrastructure Guide

## Architecture Overview

```
Internet
   │
   ▼
[Elastic IP] ──► [EC2 t3.medium]
                      │
                   [Nginx]
                    ├── :80/:443 hairlync.com       → :3000 landing
                    ├── :80/:443 api.hairlync.com   → :8000 backend
                    ├── :80/:443 ai.hairlync.com    → :8001 ai
                    └── :80/:443 admin.hairlync.com → :3001 admin
                      │
                 [Docker Compose]
                  ├── hairiq-backend   (Django 6 + Gunicorn + ASGI)
                  ├── hairiq-ai        (FastAPI + Uvicorn)
                  ├── hairiq-landing   (Next.js)
                  └── hairiq-admin     (Next.js)
                      │
                 [AWS Services]
                  ├── RDS PostgreSQL 16 (eu-north-1)
                  └── S3 Bucket (media + static files)
```

## AWS Resources (Terraform-managed)

| Resource | Type | Purpose |
|----------|------|---------|
| EC2 Instance | t3.medium | Application server |
| Elastic IP | EIP | Static public IP |
| RDS PostgreSQL | db.t3.micro | Application database |
| S3 Bucket | Standard | Media + static file storage |
| Security Group | SG | Firewall rules |
| Key Pair | RSA | SSH access |

## Security Group Rules

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Your IP only | SSH |
| 80 | TCP | 0.0.0.0/0 | HTTP (redirects to HTTPS) |
| 443 | TCP | 0.0.0.0/0 | HTTPS |
| 5432 | TCP | Self (SG) | RDS — internal only |

> ⚠️ Port 8000 and 8001 are NOT exposed publicly. All traffic goes through Nginx.

## Terraform State Management

State is stored locally by default. For teams, add S3 backend:

```hcl
# Add to infrastructure/terraform/environments/production/backend.tf
terraform {
  backend "s3" {
    bucket = "hairiq-terraform-state"
    key    = "production/terraform.tfstate"
    region = "eu-north-1"
    encrypt = true
  }
}
```

## Adding a New AWS Region

1. Find the correct Ubuntu 24.04 LTS AMI for the region:
   ```bash
   aws ec2 describe-images --owners 099720109477 \
     --filters "Name=name,Values=ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*" \
     --query 'sort_by(Images,&CreationDate)[-1].ImageId' \
     --region YOUR_REGION
   ```
2. Update `ami` in `infrastructure/terraform/environments/<env>/main.tf`
3. Update `region` in `infrastructure/terraform/environments/<env>/main.tf`

## Scaling Up

To upgrade EC2 instance type:
```bash
# Edit infrastructure/terraform/environments/production/main.tf
# Change instance_type = "t3.medium" to "t3.large"
make tf-apply ENV=production
# EC2 will restart briefly
```

To scale RDS:
```bash
# Change db_instance_class in main.tf
# RDS will undergo maintenance window restart
```
