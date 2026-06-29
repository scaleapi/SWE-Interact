#!/bin/bash
set -euo pipefail

# Load shared credentials
set -a
source "$(dirname "$0")/../../harbor/.env"
set +a

HARBOR_BIN="${HARBOR_BIN:-harbor}"

DATASET="$(basename "$(dirname "$0")")"
JOB_NAME="$(basename "$0" .sh)"


"$HARBOR_BIN" run \
  --yes \
  --env-file harbor/.env \
  -p "./data/${DATASET}" \
  -a codex \
  -m "openai/gpt-5.5" \
  -k 1 \
  -e modal \
  -n 25 \
  -r 3 \
  --ak reasoning_effort=high \
  -o "results/${DATASET}" \
  --job-name "${JOB_NAME}"
