# ─── HairIQ Production Environment ────────────────────────────────────
# Usage: cd here, then terraform init -backend-config=backend.hcl

module "infra" {
  source = "../../shared"

  project_name = "hairiq"
  environment  = "production"
  region       = "eu-north-1"
  aws_profile  = "default"
  domain       = "hairiq.io"

  # Compute
  instance_type   = "t3.medium"
  ami             = "ami-XXXXXXXXXXXXXXXXX" # Ubuntu 24.04 LTS for your region
  public_key_path = "~/.ssh/id_rsa.pub"

  # Database (use terraform.tfvars or TF_VAR_ env vars for secrets)
  db_username          = var.db_username
  db_password          = var.db_password
  db_instance_class    = "db.t3.micro"
  db_allocated_storage = 20

  # Storage
  bucket_name = "hairiq-media-prod"

  # Networking
  allowed_ssh_cidrs = ["YOUR.PUBLIC.IP/32"] # Replace with your IP
}

# Pass-through variables for secrets
variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

output "server_ip" {
  value = module.infra.ec2_public_ip
}

output "rds_endpoint" {
  value     = module.infra.rds_endpoint
  sensitive = true
}
