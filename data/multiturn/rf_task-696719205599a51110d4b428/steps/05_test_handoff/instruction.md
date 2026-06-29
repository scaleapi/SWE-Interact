You're working in a repository at `/calypso`.

This is the final handoff step. Do not make intentional implementation changes.

Save the local status for handoff:

```bash
set -euo pipefail
cd /calypso
mkdir -p /logs/agent
git status --short > /logs/agent/test-handoff-status.txt
```
