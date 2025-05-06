# localstack docker
resource "docker_container" "localstack" {
  image = "localstack/localstack:latest"
  name  = "localstack"
  env   = [
    "SERVICES=s3,ec2,iam",
    "DEBUG=1",
  ]
  ports {
    internal = 4566
    external = 4566
  }
}

# S3 bucket
resource "aws_s3_bucket" "create_bucket" {
  provider   = aws
  bucket     = var.s3_bucket
  depends_on = [ docker_container.localstack ]
}

resource "docker_container" "kggen_job" {
  name       = "kggen-job-${local.job_id}"
  image      = "kggen-ollama:with-phi4"
  depends_on = [
    docker_container.localstack,
    aws_s3_bucket.create_bucket,
  ]

  volumes {
    host_path      = abspath("${path.module}/data")
    container_path = "/data"
  }
  env = [
    "AWS_ACCESS_KEY_ID=test",
    "AWS_SECRET_ACCESS_KEY=test",
    "AWS_DEFAULT_REGION=us-west-2",
  ]
  entrypoint = ["/app/newIngestion.sh"]
  command    = [
    "s3://${local.s3_bucket}/input/${local.job_id}.pdf",
    "/data/output/${local.job_id}"
  ]
  wait       = false
  must_run   = false
}


# IAM role & profile for EC2 access to S3
resource "aws_iam_role" "ec2_role" {
  name               = "ec2-s3-access"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}


# Launch Template for EC2 implementation
resource "aws_launch_template" "kggen_lt" {
  name_prefix   = "kggen-lt-"
  image_id      = var.ami_id
  instance_type = "t3.small"

  iam_instance_profile { name = aws_iam_instance_profile.ec2_profile.name }
  user_data     = file("${path.module}/user_data.sh")
}
