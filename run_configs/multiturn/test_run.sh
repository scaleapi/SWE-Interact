#!/bin/bash
set -euo pipefail

# Load shared credentials.
set -a
source "$(dirname "$0")/../../harbor/.env"
set +a

export SIM_USER_MODEL="openai/gpt-5.5"
export LITELLM_API_KEY="${OPENAI_API_KEY}"
export LITELLM_BASE_URL="https://api.openai.com"

HARBOR_BIN="${HARBOR_BIN:-harbor}"

DATASET="$(basename "$(dirname "$0")")"
JOB_NAME="$(basename "$0" .sh)"

"$HARBOR_BIN" run \
  --yes \
  --env-file harbor/.env \
  -p "./data/${DATASET}" \
  -i "deepswe_arcane-drift-detection-baselines" \
  -i "rf_task-69391d8d1ce51c407be1e531" \
  -i "swebenchpro_instance_ansible__ansible-4c5ce5a1a9e79a845aff4978cfeb72a0d4ecf7d6-v1055803c3a812189a1133297f7f5468579283f86" \
  -a codex \
  -m "openai/gpt-5.5" \
  -k 1 \
  -e modal \
  --force-build \
  -r 3 \
  --ak reasoning_effort=high \
  -o "results/${DATASET}" \
  --job-name "${JOB_NAME}"
