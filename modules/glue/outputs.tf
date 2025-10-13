output "database_name" {
  description = "Name of the Glue database"
  value       = aws_glue_catalog_database.products_database.name
}

output "database_arn" {
  description = "ARN of the Glue database"
  value       = aws_glue_catalog_database.products_database.arn
}

output "crawler_name" {
  description = "Name of the Glue crawler"
  value       = aws_glue_crawler.products_crawler.name
}

output "crawler_arn" {
  description = "ARN of the Glue crawler"
  value       = aws_glue_crawler.products_crawler.arn
}

output "expected_table_name" {
  description = "Expected table name (created by crawler)"
  value       = local.table_name
}