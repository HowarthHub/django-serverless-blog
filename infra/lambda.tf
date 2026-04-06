# IAM Role — Permissions for the Lambda function
# Lambda needs to "assume" a role to get permissions e.g. logging in user
# =============================================================================
resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-lambda-role"

  # Trust policy: allows the Lambda service to use this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com" # Only Lambda can assume this role
      }
    }]
  })
}

# Attach AWS-managed policies to the role
# BasicExecution = permission to write logs to CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# VPCAccess = permission to create network interfaces in our VPC
# (needed because Lambda runs inside our private subnets)
resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# =============================================================================
# Lambda Function — Our Django API running serverless
# This is where Mangum receives requests and passes them to Django
# =============================================================================
resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-api"
  role          = aws_iam_role.lambda.arn  # Use the IAM role we created above
  handler       = "core.asgi.handler"      # Entry point: Mangum handler in core/asgi.py
  runtime       = "python3.12"             # Python version on Lambda
  architectures = ["arm64"]                # ARM — matches Apple Silicon Docker builds, cheaper on AWS
  timeout       = 30                       # Max execution time in seconds
  memory_size   = 512                      # MB of RAM (also affects CPU allocation)

  filename         = "${path.module}/lambda.zip"                    # The deployment package
  source_code_hash = filebase64sha256("${path.module}/lambda.zip")  # Detects code changes

  # Run Lambda inside our VPC so it can reach RDS
  vpc_config {
    subnet_ids         = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_group_ids = [aws_security_group.lambda.id]
  }

  # Environment variables — same ones we use in .env locally
  # DATABASE_HOST is auto-filled with the RDS address after Terraform creates it
  environment {
    variables = {
      DJANGO_SETTINGS_MODULE = "core.settings"
      SECRET_KEY             = var.django_secret_key
      DEBUG                  = "False"
      DATABASE_NAME          = var.db_name
      DATABASE_USER          = var.db_username
      DATABASE_PASSWORD      = var.db_password
      DATABASE_HOST          = aws_db_instance.main.address # Terraform resolves this
      DATABASE_PORT          = "5432"
      ALLOWED_HOSTS          = "*"
    }
  }

  tags = { Name = "${var.project_name}-api" }
}

# =============================================================================
# API Gateway — HTTP API that routes requests to Lambda
# Simpler and cheaper than REST API Gateway
# =============================================================================
resource "aws_apigatewayv2_api" "api" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
}

# Connect API Gateway to Lambda
resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

# Route all requests to Lambda
resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Deploy the API with auto-deploy
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

# Allow API Gateway to invoke Lambda
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
