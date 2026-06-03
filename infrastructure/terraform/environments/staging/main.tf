# ─── HairIQ Staging Environment ───────────────────────────────────────
module "infra" {
  source = "../../shared"

  project_name = "hairiq"
  environment  = "staging"
  region       = "eu-north-1"
  aws_profile  = "default"
  domain       = "staging.hairiq.io"

  # Compute — smaller for staging
  instance_type   = "t3.small"
  ami             = "ami-XXXXXXXXXXXXXXXXX"
  public_key_path = "~/.ssh/id_rsa.pub"

  # Database
  db_username          = var.db_username
  db_password          = var.db_password
  db_instance_class    = "db.t3.micro"
  db_allocated_storage = 10

  # Storage
  bucket_name = "hairiq-media-staging"

  # Networking
  allowed_ssh_cidrs = ["YOUR.PUBLIC.IP/32"]
}

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
