# Create ZIP file for Lambda deployment
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.root}/lambda/etl_function"
  output_path = "${path.root}/lambda/packages/etl_function.zip"
}

# Lambda function
resource "aws_lambda_function" "etl_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-etl-function"
  role            = var.lambda_role_arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.11"
  memory_size     = var.memory_size
  timeout         = var.timeout

  environment {
    variables = {
      S3_BUCKET_NAME = var.s3_bucket_name
    }
  }

  # Add the AWS SDK for Pandas layer
  layers = [
    "arn:aws:lambda:${data.aws_region.current.name}:336392948345:layer:AWSSDKPandas-Python311:13"
  ]

  tags = {
    Name        = "${var.project_name}-etl-function"
    Environment = var.environment
  }

  depends_on = [data.archive_file.lambda_zip]
}

# Get current AWS region
data "aws_region" "current" {}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.etl_function.function_name}"
  retention_in_days = 14

  tags = {
    Name        = "${var.project_name}-lambda-logs"
    Environment = var.environment
  }
}