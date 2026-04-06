# Outputs are printed after "terraform apply" completes
# They give you the URLs and info you need to access your deployed app

output "lambda_function_url" {
  description = "Lambda function URL for the Django API"
  value       = aws_lambda_function_url.api.function_url
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain (your site URL)"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "s3_bucket_name" {
  description = "S3 bucket for frontend deployment"
  value       = aws_s3_bucket.frontend.bucket
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.main.address
}
