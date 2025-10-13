# Glue database
resource "aws_glue_catalog_database" "products_database" {
  name        = var.glue_database_name
  description = "Database for product data from ETL pipeline"

  tags = {
    Name        = "${var.project_name}-database"
    Environment = var.environment
  }
}

# Glue crawler
resource "aws_glue_crawler" "products_crawler" {
  database_name = aws_glue_catalog_database.products_database.name
  name          = var.glue_crawler_name
  role          = var.glue_role_arn

  s3_target {
    path = "s3://${var.s3_bucket_name}/products/"
  }

  # Run the crawler on a schedule (optional)
  # schedule = "cron(0 12 * * ? *)" # Daily at noon

  tags = {
    Name        = "${var.project_name}-crawler"
    Environment = var.environment
  }
}

# Output the table name for reference (will be created by crawler)
locals {
  table_name = "products"
}