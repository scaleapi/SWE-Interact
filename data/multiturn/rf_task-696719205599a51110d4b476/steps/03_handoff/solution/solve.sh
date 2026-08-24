#!/bin/bash
set -euo pipefail
# Oracle step 03_handoff: export change log artifacts; no code edits.
REPO="/app"
if [ ! -d "$REPO" ]; then
  echo "ERROR: repo root missing: $REPO" >&2
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
