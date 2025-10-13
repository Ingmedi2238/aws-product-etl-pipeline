# Get current AWS account ID and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Generate random suffix for unique naming
resource "random_id" "suffix" {
  byte_length = 4
}

# Create unique names with random suffix to avoid conflicts
locals {
  account_id                = data.aws_caller_identity.current.account_id
  region                   = data.aws_region.current.name
  random_suffix            = random_id.suffix.hex
  unique_s3_bucket_name    = "${var.s3_bucket_name}-${local.random_suffix}"
  unique_athena_bucket_name = "${var.athena_results_bucket}-${local.random_suffix}"
}

# IAM Roles and Policies
module "iam" {
  source = "./modules/iam"

  project_name             = var.project_name
  environment             = var.environment
  s3_bucket_name          = local.unique_s3_bucket_name
  athena_results_bucket   = local.unique_athena_bucket_name
  account_id              = local.account_id
}

# S3 Buckets
module "s3" {
  source = "./modules/s3"

  project_name             = var.project_name
  environment             = var.environment
  s3_bucket_name          = local.unique_s3_bucket_name
  athena_results_bucket   = local.unique_athena_bucket_name
}

# Lambda Function
module "lambda" {
  source = "./modules/lambda"

  project_name        = var.project_name
  environment         = var.environment
  s3_bucket_name      = local.unique_s3_bucket_name
  lambda_role_arn     = module.iam.lambda_role_arn
  memory_size         = var.lambda_memory_size
  timeout             = var.lambda_timeout
}

# Glue Database and Crawler
module "glue" {
  source = "./modules/glue"

  project_name        = var.project_name
  environment         = var.environment
  s3_bucket_name      = local.unique_s3_bucket_name
  glue_database_name  = var.glue_database_name
  glue_crawler_name   = var.glue_crawler_name
  glue_role_arn       = module.iam.glue_role_arn

  depends_on = [module.s3]
}

# Athena Workgroup
module "athena" {
  source = "./modules/athena"

  project_name              = var.project_name
  environment              = var.environment
  athena_workgroup_name    = var.athena_workgroup_name
  athena_results_bucket    = local.unique_athena_bucket_name

  depends_on = [module.s3]
}