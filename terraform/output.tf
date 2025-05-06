output "instance_id" {
  value = docker_container.localstack.name
  description = "This EC2 instance ID running the job"
}

output "s3_output" {
  value = local.s3_bucket
  description = "S3 bucket for KG job I/O"
  sensitive = false
}

output "launch_template_id" {
  value = aws_launch_template.kggen_lt.id
  description = "Predefined Launch Template ID"
}