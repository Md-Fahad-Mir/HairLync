# ─── Bootstrap Variables ──────────────────────────────────────────────

variable "project_name" {
  description = "Project name used for naming/tagging"
  type        = string
  default     = "hairiq"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "aws_profile" {
  description = "AWS CLI profile name"
  type        = string
  default     = "default"
}

variable "state_bucket_name" {
  description = "Globally-unique S3 bucket name for Terraform remote state (e.g. hairiq-tfstate-<random>)"
  type        = string
}

variable "ecr_repositories" {
  description = "ECR repositories to create (one per service)"
  type        = list(string)
  default     = ["hairiq-backend", "hairiq-ai", "hairiq-landing", "hairiq-admin"]
}
