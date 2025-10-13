output "s3_bucket_name" {
  description = "Name of the S3 bucket for data storage"
  value       = module.s3.bucket_name
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for data storage"
  value       = module.s3.bucket_arn
}

output "athena_results_bucket_name" {
  description = "Name of the S3 bucket for Athena query results"
  value       = module.s3.athena_results_bucket_name
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.lambda.function_arn
}

output "glue_database_name" {
  description = "Name of the Glue database"
  value       = module.glue.database_name
}

output "glue_crawler_name" {
  description = "Name of the Glue crawler"
  value       = module.glue.crawler_name
}

output "athena_workgroup_name" {
  description = "Name of the Athena workgroup"
  value       = module.athena.workgroup_name
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = module.iam.lambda_role_arn
}

output "glue_role_arn" {
  description = "ARN of the Glue service role"
  value       = module.iam.glue_role_arn
}

output "random_suffix" {
  description = "Random suffix used for resource naming"
  value       = random_id.suffix.hex
}
