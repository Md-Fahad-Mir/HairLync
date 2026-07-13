# ─── CloudFront CDN for S3 media ──────────────────────────────────────
# Puts CloudFront in front of the existing S3 media bucket so uploaded
# media (the `media/` prefix) is cached at edge locations and served over
# a stable HTTPS domain.
#
# Access model (chosen): the bucket stays PUBLIC. CloudFront uses the
# bucket's regional REST endpoint as a plain custom origin — no Origin
# Access Control — so the existing direct-S3 URLs keep working unchanged
# and this change is purely additive. Django is pointed at the CloudFront
# domain via AWS_S3_CUSTOM_DOMAIN (see deployment/environments/backend.env.example);
# django-storages then generates media URLs on the CloudFront domain.
#
# Static files are NOT fronted here — they are served by WhiteNoise from
# the Django container, not from S3.
#
# The default *.cloudfront.net domain is used (no ACM cert / Route53).

locals {
  media_origin_id = "${var.project_name}-${var.environment}-s3-media"
}

# AWS-managed cache policy "CachingOptimized" — long TTLs, gzip/brotli,
# ignores cookies/query strings. Ideal for immutable, hash-named media.
data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

# AWS-managed origin request policy that forwards CORS headers to the S3
# origin so cross-origin image requests (from the web/admin apps) succeed.
data "aws_cloudfront_origin_request_policy" "cors_s3" {
  name = "Managed-CORS-S3Origin"
}

# AWS-managed response headers policy that echoes CORS response headers.
data "aws_cloudfront_response_headers_policy" "cors" {
  name = "Managed-CORS-With-Preflight-And-SecurityHeaders"
}

resource "aws_cloudfront_distribution" "media" {
  enabled         = true
  comment         = "${var.project_name}-${var.environment} media CDN (S3: ${aws_s3_bucket.media.bucket})"
  price_class     = "PriceClass_100" # NA + EU edges — matches the eu-north-1 audience
  http_version    = "http2and3"
  is_ipv6_enabled = true

  # Public S3 bucket as a plain custom origin (no OAC — bucket stays public).
  origin {
    domain_name = aws_s3_bucket.media.bucket_regional_domain_name
    origin_id   = local.media_origin_id

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = local.media_origin_id
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true

    cache_policy_id            = data.aws_cloudfront_cache_policy.caching_optimized.id
    origin_request_policy_id   = data.aws_cloudfront_origin_request_policy.cors_s3.id
    response_headers_policy_id = data.aws_cloudfront_response_headers_policy.cors.id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # Default *.cloudfront.net domain + its managed certificate (no ACM).
  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-media-cdn"
    Environment = var.environment
  }
}
