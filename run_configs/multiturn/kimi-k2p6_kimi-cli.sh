#!/bin/bash
set -euo pipefail

# Load shared credentials
set -a
source "$(dirname "$0")/../../harbor/.env"
set +a

export SIM_USER_MODEL="openai/gpt-5.5"
export LITELLM_API_KEY="${OPENAI_API_KEY}"
export LITELLM_BASE_URL="https://api.openai.com"

HARBOR_BIN="${HARBOR_BIN:-harbor}"

DATASET="$(basename "$(dirname "$0")")"
JOB_NAME="$(basename "$0" .sh)"
KIMI_BASE_URL="${OPENAI_API_BASE:-${OPENAI_BASE_URL:?Set OPENAI_API_BASE or OPENAI_BASE_URL for this OpenAI-compatible model endpoint}}"


"$HARBOR_BIN" run \
  --yes \
  --env-file harbor/.env \
  -p "./data/${DATASET}" \
  -a kimi-cli \
  -m "openai/fireworks_ai/kimi-k2p6" \
  -k 1 \
  -e modal \
  --force-build \
  -n 25 \
  -r 3 \
  --ak base_url="${KIMI_BASE_URL}" \
  -o "results/${DATASET}" \
  --job-name "${JOB_NAME}"
