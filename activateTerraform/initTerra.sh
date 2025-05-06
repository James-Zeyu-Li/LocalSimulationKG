#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$SCRIPT_DIR/../terraform"

# run LocalStack in docker, EC2, IAM, and S3
terraform -chdir="$TF_DIR" init
terraform -chdir="$TF_DIR" apply \
  -target=docker_container.localstack \
  -auto-approve
  
# launch terraform main
terraform -chdir="$TF_DIR" apply \
  -auto-approve

