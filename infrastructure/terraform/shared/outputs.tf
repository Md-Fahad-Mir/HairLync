output "ec2_public_ip" {
  value       = aws_eip.static_ip.public_ip
  description = "Elastic IP address of the HairIQ EC2 instance"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.media.bucket
  description = "S3 bucket name"
}

output "cloudfront_domain_name" {
  value       = aws_cloudfront_distribution.media.domain_name
  description = "CloudFront distribution domain for media (set as AWS_S3_CUSTOM_DOMAIN in the backend env)"
}

output "cloudfront_distribution_id" {
  value       = aws_cloudfront_distribution.media.id
  description = "CloudFront distribution ID (for cache invalidations)"
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "RDS instance endpoint"
  sensitive   = true
}

output "rds_username" {
  value       = aws_db_instance.postgres.username
  description = "RDS username"
  sensitive   = true
}

output "security_group_id" {
  value       = aws_security_group.app_sg.id
  description = "Application security group ID"
}
