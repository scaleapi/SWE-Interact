#!/bin/bash
set -euo pipefail
# Oracle step 05_test_handoff: status only; tree must already be clean.
REPO="/workspace"
if [ ! -d "$REPO" ]; then
  echo "ERROR: repo root missing: $REPO" >&2
  exit 1
fi
cd "$REPO"

mkdir -p /logs/agent
git status --short > /logs/agent/test-handoff-status.txt
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERROR: working tree dirty before final handoff" >&2
  git status --short >&2
  exit 1
fi
echo "Final handoff status written; tree clean"
