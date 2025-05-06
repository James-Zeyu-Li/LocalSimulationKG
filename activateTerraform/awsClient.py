# aws_client.py

import boto3
from config import AWSConfig


class AWSClient:
    def __init__(self, cfg: AWSConfig):
        session = boto3.Session(
            aws_access_key_id=cfg.AWS_ACCESS_KEY,
            aws_secret_access_key=cfg.AWS_SECRET_KEY,
            region_name=cfg.AWS_REGION,
        )
        self.s3 = session.client(
            "s3",
            endpoint_url=cfg.LOCALSTACK_URL,
            config=boto3.session.Config(s3={'addressing_style': 'path'})
        )
        self.ec2 = session.client(
            "ec2",
            endpoint_url=cfg.LOCALSTACK_URL
        )
