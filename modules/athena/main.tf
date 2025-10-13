# Athena workgroup
resource "aws_athena_workgroup" "main" {
  name         = var.athena_workgroup_name
  force_destroy = true

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${var.athena_results_bucket}/query-results/"
    }
  }

  tags = {
    Name        = "${var.project_name}-workgroup"
    Environment = var.environment
  }
}
