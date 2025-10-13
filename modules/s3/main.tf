# Main S3 bucket for data storage
resource "aws_s3_bucket" "data_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    Name        = "${var.project_name}-data-bucket"
    Environment = var.environment
    Purpose     = "Data storage for ETL pipeline"
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "data_bucket_pab" {
  bucket = aws_s3_bucket.data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Athena results bucket
resource "aws_s3_bucket" "athena_results_bucket" {
  bucket = var.athena_results_bucket

  tags = {
    Name        = "${var.project_name}-athena-results-bucket"
    Environment = var.environment
    Purpose     = "Athena query results storage"
  }
}

# Block public access for Athena results
resource "aws_s3_bucket_public_access_block" "athena_results_pab" {
  bucket = aws_s3_bucket.athena_results_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}