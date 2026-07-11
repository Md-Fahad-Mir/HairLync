# ─── EC2 Instance Profile ─────────────────────────────────────────────
# Attaches an IAM role to the EC2 box so it can pull images from ECR using
# temporary, auto-rotating credentials from instance metadata (IMDS) —
# NO static AWS keys ever live on the server.

data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2" {
  name               = "${var.project_name}-${var.environment}-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json

  tags = {
    Name        = "${var.project_name}-${var.environment}-ec2-role"
    Environment = var.environment
  }
}

# Read-only ECR: the server may pull/authenticate, but never push/delete.
resource "aws_iam_role_policy_attachment" "ec2_ecr_read" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# SSM: lets the agent register so CI can run deploys without inbound SSH.
resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# S3 media: lets the backend container upload and manage user media via
# the EC2 instance profile, without static AWS keys on the server.
data "aws_iam_policy_document" "ec2_s3_media" {
  statement {
    actions = [
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
    ]
    resources = [
      "arn:aws:s3:::${var.bucket_name}",
    ]
  }

  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:ListMultipartUploadParts",
      "s3:PutObject",
    ]
    resources = [
      "arn:aws:s3:::${var.bucket_name}/media/*",
    ]
  }
}

resource "aws_iam_role_policy" "ec2_s3_media" {
  name   = "${var.project_name}-${var.environment}-ec2-s3-media"
  role   = aws_iam_role.ec2.id
  policy = data.aws_iam_policy_document.ec2_s3_media.json
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project_name}-${var.environment}-ec2-profile"
  role = aws_iam_role.ec2.name
}
