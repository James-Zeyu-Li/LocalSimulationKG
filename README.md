# LocalSimulationKG, AWS LocalStack Terraform simulation

- **This setup is a simulate of having an AWS S3 → EC2 (Docker) → S3 on local machine using LocalStack, Terraform, and Docker.**
- Docker, Terraform, boto3 needs to be installed
- There are still errors, EC2 is simulation, Knowledge graph generation is not working.
- venv environment needs to be activated for boto3.
## 1. Repository Structure
```
project-root/
├── kgIngestion/             
│   ├── Dockerfile           # Builds kggen-ollama:with-phi4 image
│   ├── newIngestion.sh      # Entrypoint
│   ├── main.py        
│   ├── pdf.py          
│   ├── graph.py          
│   ├── pyproject.toml      
│   └── uv.lock              
│
├── pdf/
│   ├── fema_nims_doctrine-2017.pdf  # Sample PDF for testing
│   └── get_data.sh                  # Helper to download PDFs
│ 
├── terraform/               # Terraform configs for LocalStack + job
│   ├── provider.tf          # AWS, Docker, Time providers
│   ├── variables.tf         # Variables: ami_id, s3_bucket
│   ├── locals.tf            # job_id, s3_input_uri, s3_output_uri
│   ├── main.tf              # localstack, S3 bucket, kggen_job, IAM, Launch Template
│   ├── output.tf            # Terraform outputs
│   ├── terraform.tfvars     # Default variable values
│   └── user_data.sh         # Sample EC2 user-data
│
└── activateTerraform/       # Glue scripts + Python job submitter
    ├── initTerra.sh         # Terraform init/apply
    ├── main.py              # PDF → terraform/data → apply → collect results
    ├── tfManager.py         # Helper function, run initTerra.sh
    ├── awsClient.py         # Boto3-based S3 & EC2 clients pointing at LocalStack
    ├── config.py            # LocalStack endpoint & Terraform-output keys
    └── results/             # Collected JSON outputs
```

## 2. Docker Container for Ingestion

- The **KGGen** and **Phi4** processing logic is from another team member Kieran's github repo. Altered the Apptainer container construction to a docker construction which fits better to the AWS and LocalStack environment. 
- **Dockerfile** installs system packages, Python and UV, Ollama CLI, pulls phi4 model, copies ingestion code, and sets `/app/newIngestion.sh` as the entrypoint.
	- Repository from Kieran: `https://github.com/Saskapult/graph-ingestion-playground/tree/main`

- **Build Container**
```
cd kgIngestion 
docker build -t kggen-ollama:with-phi4 .

# check if the docker exists
docker images | grep kggen-ollama:with-phi4

#manually run docker (testing purpose)
docker run --rm -it \
  -v "$(pwd)/terraform/data:/data:rw" \
  kggen-ollama:with-phi4 \
  /data/input.pdf /data/output

```

## 3. Provision LocalStack and Job Container via Terraform
- **provider.tf**: configures AWS CLI to use LocalStack endpoints, plus Docker and Time providers points to localhost:4566
- **variable.tf**: defines `ami_id` (placeholder) and `s3_bucket` (e.g. `my-bucket`).
- **locals.tf**: uses `time_static` to create a consistent `job_id`; constructs S3 URIs.
- **main.tf**:
    - `docker_container.localstack`: spins up the LocalStack container (S3, EC2, IAM).
    - `aws_s3_bucket.create_bucket`: creates the S3 bucket in LocalStack.
    - IAM Role, Instance Profile, and `aws_launch_template.kggen_lt`: placeholders for possible real EC2 deployment.
- **output.tf**: exposes `instance_id`, `launch_template_id`, and `s3_output` bucket name.
- **terraform.tfvars**：ami_id
- **user_data.sh**: sample script for a real EC2 instance to pull data, run Docker, upload results, then shut down.

- **Start Terraform and LocalStack** (Optional, manual test)
```
cd terraform
# initialize terraform
terraform init

# Run localstack, simulate S3, EC2
terraform apply \
  -target=docker_container.localstack \
  -auto-approve

# Create resources
terraform apply -auto-approve

#check the output
terraform output
```
## 4. Python to mimic initiate from Arbutus
- **initTerra.sh:**
	- Equivalent to manually run init and apply, after having the script run the bash file in this folder could replace the above manual steps
	- `terraform init` + `terraform apply`
- **activateTerraform/main.py**：(This needs to be updated, currently sending the route, not the file)
    1. `TfManager.ensure_infra()`, spins up LocalStack & job container
    2. `TfManager.get_s3_bucket_name()`, reads the bucket name from Terraform outputs
    3. Upload the PDF to `s3://<bucket>/input/<job_id>.pdf` via the Boto3 client
    4. Run `initTerra.sh` through `TfManager.ensure_infra()`
	5. Call `TfManager.ensure_infra()` to spin up LocalStack, create bucket, run `kggen_job`
    6. Download the generated JSON back out of S3 into `./results/<job_id>/`

- **activateTerraform/tfManager.py**：helper function to run `./initTerra.sh` 
```
cd ../activateTerraform
# The next command includes this command
# ./initTerra.sh

python3 main.py ../pdf/fema_nims_doctrine-2017.pdf
```

## 5. Clear and delete
```
cd ../terraform
terraform destroy -auto-approve
docker rm -f localstack
```

## 6. Problem
- Currently the output of knowledge graph generating is empty
```
{
  "entities": [],
  "edges": [],
  "relations": []
}
```
- Problem output
```
Process chunk 1/429
        Error in kg.generate: litellm.APIConnectionError: OllamaException - {"error":"model requires more system memory (11.2 GiB) than is available (7.6 GiB)"}
        Chunk processed in 0.15s
        Saving as '/data/output/20250508101826/chunk-0-0-3.json'
Process chunk 2/429
        Error in kg.generate: litellm.APIConnectionError: OllamaException - {"error":"model requires more system memory (11.2 GiB) than is available (7.6 GiB)"}
        Chunk processed in 0.10s
        Saving as '/data/output/20250508101826/chunk-1-2-3.json'
Process chunk 3/429
        Error in kg.generate: litellm.APIConnectionError: OllamaException - {"error":"model requires more system memory (11.2 GiB) than is available (7.6 GiB)"}
        Chunk processed in 0.10s
        Saving as '/data/output/20250508101826/chunk-2-2-5.json'
```

- Seems like don't have enough memory, which haven't been figured yet, could also be a docker construction issue.  