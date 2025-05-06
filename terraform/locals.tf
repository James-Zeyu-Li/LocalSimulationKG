resource "time_static" "job_ts" {}

locals {
  job_id = formatdate("YYYYMMDDHHmmss", time_static.job_ts.rfc3339)
  s3_bucket = var.s3_bucket
  s3_input_uri = "s3://${local.s3_bucket}/input/${local.job_id}.pdf"
  s3_output_uri = "s3://${local.s3_bucket}/output/${local.job_id}/"
}
