# config.py

from dataclasses import dataclass


@dataclass(frozen=True)
class AWSConfig:
    LOCALSTACK_URL: str = "http://localhost:4566"
    AWS_REGION: str = "us-west-2"
    AWS_ACCESS_KEY: str = "test"
    AWS_SECRET_KEY: str = "test"


TF_LAUNCH_TEMPLATE_KEY = "launch_template_id"
TF_S3_BUCKET_KEY = "s3_output"
