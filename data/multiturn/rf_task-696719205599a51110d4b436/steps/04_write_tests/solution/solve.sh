#!/bin/bash
set -euo pipefail
# Oracle step 04_write_tests: apply test patch + separate commit.
REPO="/src"
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


if [ ! -f /solution/tests.patch ]; then
  echo "ERROR: /solution/tests.patch missing" >&2
  exit 1
fi

git apply --whitespace=nowarn /solution/tests.patch \
  || patch --fuzz=5 -p1 -i /solution/tests.patch

git add -A
if git diff --cached --quiet; then
  echo "ERROR: no staged changes after test patch" >&2
  exit 1
fi
git commit -m "add tests"
git status --short
echo "Tests committed: $(git rev-parse --short HEAD)"
