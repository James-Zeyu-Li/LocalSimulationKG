variable "ami_id" {
  type        = string
  description = "AMI ID，To run docker"
  default     = "ami-0abcdef1234567890"
}

variable "s3_bucket" {
  type = string
  description = "Name of the S3 bucket for IO"
  default = "my-bucket"
}