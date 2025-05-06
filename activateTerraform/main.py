import sys
import os
import argparse
from tfManager import TfManager
import shutil


def main():
    p = argparse.ArgumentParser("KGGen Submitter")
    p.add_argument("pdf_path", help="Path to PDF")
    args = p.parse_args()

    pdf_path = args.pdf_path
    if not os.path.isfile(pdf_path):
        sys.exit(f"[ERROR] File not found: {pdf_path}")

    # Copy PDF into terraform/data/input.pdf，
    tf_data = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../terraform/data")
    )
    os.makedirs(tf_data, exist_ok=True)
    dst_input = os.path.join(tf_data, "input.pdf")
    if os.path.isdir(dst_input):
        shutil.rmtree(dst_input)
    elif os.path.exists(dst_input):
        os.remove(dst_input)
    shutil.copyfile(pdf_path, dst_input)

    # 2) run Terraform Script：LocalStack, S3 bucket, KGGen job
    TfManager.ensure_infra()

    # 3) Copy result from terraform/data/output  ./results result
    src_out = os.path.join(tf_data, "output")
    dst_dir = os.path.abspath("./results")
    os.makedirs(dst_dir, exist_ok=True)
    if os.path.isdir(src_out):
        for fname in os.listdir(src_out):
            shutil.copyfile(
                os.path.join(src_out, fname),
                os.path.join(dst_dir, fname)
            )
    else:
        print("[WARN] 没有在 terraform/data/output 找到任何文件")

    print(f"[DONE] Results have been copied to {dst_dir}")


if __name__ == "__main__":
    main()
