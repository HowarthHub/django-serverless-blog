terraform {
  required_version = ">= 1.0"

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
