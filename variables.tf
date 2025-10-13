variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "shop-etl"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "eu-west-1"
}

variable "aws_profile" {
  description = "AWS CLI profile to use"
  type        = string
  default     = "frank-aws-starter-profile"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for data storage"
  type        = string
  default     = "shop-etl-de-101"
}

variable "athena_results_bucket" {
  description = "S3 bucket for Athena query results"
  type        = string
  default     = "shop-etl-athena-results"
}

variable "lambda_memory_size" {
  description = "Memory size for Lambda function"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Timeout for Lambda function in seconds"
  type        = number
  default     = 300
}

variable "glue_database_name" {
  description = "Name for the Glue database"
  type        = string
  default     = "shop_products_db"
}

variable "glue_crawler_name" {
  description = "Name for the Glue crawler"
  type        = string
  default     = "shop-products-crawler"
}

variable "athena_workgroup_name" {
  description = "Name for the Athena workgroup"
  type        = string
  default     = "shop-etl-workgroup"
}