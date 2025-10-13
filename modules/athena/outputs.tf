output "workgroup_name" {
  description = "Name of the Athena workgroup"
  value       = aws_athena_workgroup.main.name
}

output "workgroup_arn" {
  description = "ARN of the Athena workgroup"
  value       = aws_athena_workgroup.main.arn
}

output "query_results_location" {
  description = "S3 location for Athena query results"
  value       = "s3://${var.athena_results_bucket}/query-results/"
}