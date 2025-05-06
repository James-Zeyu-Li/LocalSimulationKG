#!/usr/bin/env bash
set -eux
aws s3 cp "${local.s3_input_uri}" /data/input.pdf

apt-get update
apt-get install -y docker.io awscli
systemctl start docker

mkdir -p /data
aws s3 cp "${var.s3_input_uri}" /data/input.pdf

docker run --rm -v /data:/mnt/data kggen-ollama:with-phi4 \
  /mnt/data/input.pdf /mnt/data/output

aws s3 cp /mnt/data/output/ "${local.s3_output_uri}" --recursive

shutdown -h now
