#!/bin/bash
set -euo pipefail
# Oracle step 02_implement: apply impl patch + commit.
REPO="/code"
if [ ! -d "$REPO" ]; then
  echo "ERROR: repo root missing: $REPO" >&2
  exit 1
fi
cd "$REPO"


if [ -z "$(git config user.email || true)" ]; then
  git config user.email "dev@example.com"
fi
if [ -z "$(git config user.name || true)" ]; then
  git config user.name "Dev"
fi

git rev-parse HEAD > /tmp/base_commit.txt
echo "base_commit=$(cat /tmp/base_commit.txt)"

if [ ! -f /solution/impl.patch ]; then
  echo "ERROR: /solution/impl.patch missing" >&2
  exit 1
fi

git apply --whitespace=nowarn /solution/impl.patch \
  || patch --fuzz=5 -p1 -i /solution/impl.patch

git add -A
if git diff --cached --quiet; then
  echo "WARNING: no staged changes after impl patch" >&2
  exit 1
fi
git commit -m "initial implementation"
git status --short
echo "Implementation committed: $(git rev-parse --short HEAD)"
