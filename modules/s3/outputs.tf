output "bucket_name" {
  description = "Name of the S3 data bucket"
  value       = aws_s3_bucket.data_bucket.id
}

output "bucket_arn" {
  description = "ARN of the S3 data bucket"
  value       = aws_s3_bucket.data_bucket.arn
}

output "bucket_domain_name" {
  description = "Domain name of the S3 data bucket"
  value       = aws_s3_bucket.data_bucket.bucket_domain_name
}

output "athena_results_bucket_name" {
  description = "Name of the Athena results bucket"
  value       = aws_s3_bucket.athena_results_bucket.id
}

output "athena_results_bucket_arn" {
  description = "ARN of the Athena results bucket"
  value       = aws_s3_bucket.athena_results_bucket.arn
}