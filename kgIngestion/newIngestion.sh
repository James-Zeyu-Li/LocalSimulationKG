#!/usr/bin/env bash
set -euo pipefail

INPUT="$1"
OUTDIR="$2"

# catch SIGTERM and SIGINT signals to clean up before exiting
function _cleanup() {
  echo "Received termination signal, exiting early"
  touch "$OUTDIR/this_was_interrupted"
  kill "$OLLAMA_PID" 2>/dev/null || true
  exit 2
}
trap _cleanup SIGTERM SIGINT

echo "=== Starting PDF processing ==="
echo " Input: $INPUT"
echo " Output dir: $OUTDIR"

mkdir -p "$OUTDIR"

# Start Ollama and run uv
ollama serve >> /var/log/ollama.log 2>&1 &
OLLAMA_PID=$!
sleep 5

echo "--- Pulling phi4 model if needed…"
if ! ollama ls | grep -q '^phi4\$'; then
  ollama pull phi4
fi

uv run main.py --only 3 -o "$OUTDIR" "$INPUT"
kill "$OLLAMA_PID"

echo "=== PDF processing finished ==="
