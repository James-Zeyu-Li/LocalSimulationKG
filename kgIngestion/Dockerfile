FROM ubuntu:22.04

LABEL author="zeyu167 & KSmith" \
    description="Ollama+Phi-4 + UV + gRPC environment for KGGen"

# Environment variables
ENV OLLAMA_HOME=/opt/ollama_storage \
    OLLAMA_MODELS=/opt/ollama_models \
    UV_PROJECT_ENVIRONMENT=/app/venv \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:/usr/local/bin:$PATH"

WORKDIR /app

# install dependencies, python3, pip, and venv
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl wget python3 python3-pip python3-venv pciutils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# copy the requirements file and install the dependencies
COPY pyproject.toml uv.lock /app/
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    python3 -m venv /app/venv && \
    . /app/venv/bin/activate && \
    uv sync --locked --no-dev --no-install-project

# install ollama, and run the server 
RUN mkdir -p $OLLAMA_HOME $OLLAMA_MODELS && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    command -v ollama

RUN ollama serve >> /var/log/ollama-install.log 2>&1 & \
    OLLAMA_PID=$! && \
    sleep 5 && \
    ollama pull phi4 && \
    kill $OLLAMA_PID


RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# copyuvlock and ingestion into the container
COPY . /app

RUN chmod +x /app/newIngestion.sh

ENTRYPOINT ["/app/newIngestion.sh"]
CMD []