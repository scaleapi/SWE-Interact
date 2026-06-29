You're working in a Go repository at `/grafana`.

This is the final handoff step. Do not make intentional implementation changes.

Save the local status for handoff:

```bash
set -euo pipefail
cd /grafana
mkdir -p /logs/agent
git status --short > /logs/agent/test-handoff-status.txt
```
