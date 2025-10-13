variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)" # whatever you like
  type        = string
}

variable "athena_workgroup_name" {
  description = "Name for the Athena workgroup"
  type        = string
}

variable "athena_results_bucket" {
  description = "S3 bucket for Athena query results"
  type        = string
}