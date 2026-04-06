# Variables are inputs to your Terraform config.
# If a variable has a "default", it's optional.
# If it doesn't (like db_password), you MUST provide it via terraform.tfvars or env vars.

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-2" # London
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "django-serverless-blog"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "blog_db"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "postgres"
}

# sensitive = true means Terraform won't print this value in logs or plan output
variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "django_secret_key" {
  description = "Django SECRET_KEY"
  type        = string
  sensitive   = true
}
