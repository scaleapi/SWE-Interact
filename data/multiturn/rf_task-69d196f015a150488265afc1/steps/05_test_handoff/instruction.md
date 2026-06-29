You're working in a C++ repository at `/app/source`.

This is the final handoff step. Do not make intentional implementation changes.

Save the local status for handoff:

```bash
set -euo pipefail
cd /app/source
mkdir -p /logs/agent
git status --short > /logs/agent/test-handoff-status.txt
```
