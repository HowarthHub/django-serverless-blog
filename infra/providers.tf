terraform {
  required_version = ">= 1.0"

  # Remote state — stored in S3 so both local and CI share the same state
  # DynamoDB table prevents two deploys running at the same time
  backend "s3" {
    bucket         = "django-serverless-blog-tf-state"
    key            = "terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "django-serverless-blog-tf-lock"
    encrypt        = true
  }

  # Define which providers (cloud platforms) we need
  required_providers {
    aws = {
      source  = "hashicorp/aws" # Official AWS provider from HashiCorp
      version = "~> 5.0"        # Use any 5.x version
    }
  }
}

# Configure the AWS provider with our chosen region
provider "aws" {
  region = var.aws_region
}
