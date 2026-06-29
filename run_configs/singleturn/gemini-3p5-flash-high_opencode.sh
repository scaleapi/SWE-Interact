#!/bin/bash
set -euo pipefail

# Load shared credentials.
set -a
source "$(dirname "$0")/../../harbor/.env"
set +a

export GOOGLE_GENERATIVE_AI_API_KEY="${GOOGLE_GENERATIVE_AI_API_KEY:-$GEMINI_API_KEY}"

HARBOR_BIN="${HARBOR_BIN:-harbor}"

DATASET="$(basename "$(dirname "$0")")"
JOB_NAME="$(basename "$0" .sh)"

"$HARBOR_BIN" run \
  --yes \
  --env-file harbor/.env \
  -p "./data/${DATASET}" \
  -a opencode \
  -m "google/gemini-3.5-flash" \
  -k 1 \
  -e modal \
  --force-build \
  -n 25 \
  -r 3 \
  -o "results/${DATASET}" \
  --job-name "${JOB_NAME}"
