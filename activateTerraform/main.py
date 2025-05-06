#!/usr/bin/env python3
import sys
import os
import argparse
import datetime
import subprocess
import shutil

from config import AWSConfig
from awsClient import AWSClient
from tfManager import TfManager


def main():
    p = argparse.ArgumentParser("KGGen Submitter")
    p.add_argument("pdf_path", help="Path to PDF")
    args = p.parse_args()

    pdf_path = args.pdf_path
    if not os.path.isfile(pdf_path):
        sys.exit(f"[ERROR] File not found: {pdf_path}")

    # 1) Start LocalStack + S3 bucket（terraform init/apply）
    TfManager.ensure_infra()

    # 2) from Terraform get S3 bucket name
    bucket = TfManager.get_s3_bucket_name()

    # 3) generate job_id，upload PDF to S3
    job_id = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
    key_in = f"input/{job_id}.pdf"
    print(f">>> Uploading {pdf_path} → s3://{bucket}/{key_in}")
    aws = AWSClient(AWSConfig())
    aws.s3.upload_file(pdf_path, bucket, key_in)

    # 4) prepare local data dir
    tf_dir = TfManager.TF_DIR
    tf_data = os.path.join(tf_dir, "data")
    os.makedirs(tf_data, exist_ok=True)

    # 5) download input PDF from S3
    local_input = os.path.join(tf_data, "input.pdf")
    aws.s3.download_file(bucket, key_in, local_input)

    # 6) run docker container to process the PDF
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{tf_data}:/data:rw",
        "kggen-ollama:with-phi4",
        "/data/input.pdf",
        f"/data/output/{job_id}"
    ]
    print(">>> Processing with:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # 7) copy output files to results dir
    local_out_dir = os.path.join(tf_data, "output", job_id)
    results_dir = os.path.abspath(os.path.join("results", job_id))
    os.makedirs(results_dir, exist_ok=True)

    if os.path.isdir(local_out_dir):
        for fname in os.listdir(local_out_dir):
            src = os.path.join(local_out_dir, fname)
            dst = os.path.join(results_dir, fname)
            print(f">>> Copying {src} → {dst}")
            shutil.copyfile(src, dst)
    else:
        print(f"[WARN] No output found in {local_out_dir}")

    print(f"[DONE] Job {job_id} results → {results_dir}")


if __name__ == "__main__":
    main()
