# HairIQ Disaster Recovery Plan

## Recovery Time Objectives

| Scenario | RTO | RPO |
|----------|-----|-----|
| Container crash | < 1 min | 0 (restart) |
| Bad deployment | < 5 min | 0 (rollback) |
| EC2 failure | < 30 min | ~24h (RDS backup) |
| RDS failure | < 1 hour | 24h (daily snapshots) |
| Region outage | < 4 hours | 24h |

---

## Scenario 1: Bad Deployment (Most Common)

```bash
# Find the last working image SHA in GitHub Actions
# Then rollback all services:
export PROJECT_NAME=hairiq
export DOCKERHUB_USERNAME=yourusername
export EC2_HOST=your.ec2.ip
make rollback TAG=<last-good-sha>
```

---

## Scenario 2: Container Keeps Crashing

```bash
# SSH to EC2
ssh ubuntu@your.ec2.ip

# Check logs
cd /home/ubuntu/hairiq
docker compose -f docker-compose.prod.yml logs --tail=100 backend

# Restart single service
docker compose -f docker-compose.prod.yml restart backend

# Force recreate
docker compose -f docker-compose.prod.yml up -d --force-recreate backend
```

---

## Scenario 3: EC2 Instance Failure

1. **Terminate the broken instance** (if needed)
2. **Provision a new EC2**:
   ```bash
   make tf-apply ENV=production
   # Note the new Elastic IP (or it may be the same EIP re-attached)
   ```
3. **Configure the new server**:
   ```bash
   # Update inventory with new IP if needed
   nano infrastructure/ansible/inventories/production/hosts
   make ansible-prod
   ```
4. **The CI/CD pipeline will deploy on next push**, or trigger manually via GitHub Actions.

> The RDS and S3 data are independent of EC2 — they survive EC2 replacement.

---

## Scenario 4: RDS Database Failure

```bash
# Check RDS status in AWS Console or:
aws rds describe-db-instances --db-instance-identifier hairiq-production-db

# Restore from latest automated backup (AWS Console → RDS → Restore)
# Update DB_HOST in backend .env to point to new RDS endpoint
# Redeploy backend service
```

**RDS automated backups** are enabled with 7-day retention in production.

---

## Scenario 5: S3 Bucket Accidental Deletion

```bash
# Re-provision S3 bucket via Terraform
make tf-apply ENV=production
# Terraform will recreate the bucket (data is gone if not versioned)
```

**Recommendation**: Enable S3 versioning:
```hcl
resource "aws_s3_bucket_versioning" "media" {
  bucket = aws_s3_bucket.media.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

---

## Preventive Measures Checklist

- [ ] Enable RDS automated backups (7 days retention)
- [ ] Enable S3 versioning on media bucket
- [ ] Store Terraform state in S3 with versioning
- [ ] Set up CloudWatch alarms for EC2 CPU > 80%
- [ ] Set up CloudWatch alarms for RDS storage < 20%
- [ ] Use GitHub Actions environment protection rules for production
- [ ] Rotate all credentials every 90 days
- [ ] Test disaster recovery quarterly
