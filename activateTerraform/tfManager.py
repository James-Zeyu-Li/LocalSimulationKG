# activateTerraform/tfManager.py
import subprocess
import sys
import os
import re

from config import TF_S3_BUCKET_KEY


class TfManager:
    # Directory containing Terraform configs
    TF_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../terraform")
    )

    @staticmethod
    def ensure_infra(script_path: str = "./initTerra.sh") -> None:
        try:
            subprocess.run([script_path], check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(f"[TF ERROR] init infra failed: {e}")

    @staticmethod
    def load_output(key: str) -> str:
        cmd = [
            "terraform",
            "output",
            "-no-color",
            "-raw",
            key
        ]
        try:
            out = subprocess.check_output(cmd, cwd=TfManager.TF_DIR)
            return out.decode().strip()
        except subprocess.CalledProcessError as e:
            sys.exit(f"[TF ERROR] load output '{key}' failed: {e}")

    @classmethod
    def get_s3_bucket_name(cls) -> str:
        # Retrieve and validate the S3 bucket name from Terraform outputs.
        bucket = cls.load_output(TF_S3_BUCKET_KEY)
        if not bucket or not re.fullmatch(r"[A-Za-z0-9.\-_]{1,255}", bucket):
            sys.exit(f"[TF ERROR] Invalid S3 bucket name: {bucket}")
        return bucket
