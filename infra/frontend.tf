# S3 Bucket — Stores the built Vue frontend files (HTML, JS, CSS)
# =============================================================================

resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project_name}-frontend"

  tags = { Name = "${var.project_name}-frontend" }
}

# Block ALL public access to the bucket
# Only CloudFront can read from it (via the bucket policy below)
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# =============================================================================
# CloudFront — CDN (Content Delivery Network)
# This is a single public URL for the entire app
# It routes requests to either S3 (frontend) or Lambda (API)
# Also caches static files at edge locations worldwide for speed
# =============================================================================

# Origin Access Control — secure way for CloudFront to read from S3
resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "${var.project_name}-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html" # Serve index.html when hitting the root URL

  # --- Origin 1: S3 bucket for static frontend files ---
  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "s3"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }

  # --- Origin 2: API Gateway for the Django API ---
  origin {
    domain_name = "${aws_apigatewayv2_api.api.id}.execute-api.${var.aws_region}.amazonaws.com"
    origin_id   = "api"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # --- Route /api/* requests to Lambda ---
  # No caching (TTL = 0) because API responses are dynamic
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    target_origin_id = "api" # Send to Lambda origin
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods   = ["GET", "HEAD"]

    forwarded_values {
      query_string = true                           # Pass query params to Lambda
      headers      = ["Authorization", "Content-Type"] # Pass auth + content type headers

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0 # No caching for API
    default_ttl            = 0
    max_ttl                = 0
  }

  # --- Route everything else to S3 (Vue app) ---
  # Cache static files for up to 24 hours
  default_cache_behavior {
    target_origin_id = "s3" # Send to S3 origin
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]

    forwarded_values {
      query_string = false # Static files don't need query params

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600  # Cache for 1 hour
    max_ttl                = 86400 # Max cache: 24 hours
  }

  # --- SPA fallback ---
  # When someone navigates directly to /posts/3, S3 returns 403/404
  # because there's no file at that path. These rules return index.html
  # instead, so Vue Router can handle the route client-side
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  # No geo restrictions — available worldwide
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # Use the default CloudFront SSL certificate (*.cloudfront.net)
  # Where to for a custom domain + ACM certificate later
  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = { Name = "${var.project_name}-cdn" }
}

# =============================================================================
# S3 Bucket Policy — Only CloudFront can read from the bucket
# Without this, nobody can access the files (because public access is blocked)
# =============================================================================
resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowCloudFront"
      Effect = "Allow"
      Principal = {
        Service = "cloudfront.amazonaws.com"
      }
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.frontend.arn}/*" # All files in the bucket
      Condition = {
        StringEquals = {
          "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn # Only OUR CloudFront
        }
      }
    }]
  })
}
