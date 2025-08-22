#!/usr/bin/env bash
set -euo pipefail

# Approved commands wrapper
# Usage: approved-commands.sh <action>
# Actions: chmod, test, deploy, port-forward

LOGFILE=".vscode/approved-commands.log"
echo "[$(date -Iseconds)] Starting action: ${1:-none}" >> "$LOGFILE"

action="${1:-}" 
case "$action" in
  chmod)
    echo "[$(date -Iseconds)] Running chmod for k8s scripts" >> "$LOGFILE"
    chmod +x k8s/deploy.sh k8s/manage.sh
    ;;
  test)
    echo "[$(date -Iseconds)] Running pytest for k8s checklist" >> "$LOGFILE"
    # Prefer python -m pytest to avoid PATH issues
    if command -v python3 &> /dev/null; then
      python3 -m pytest tests/test_k8s_deployment_checklist.py -q
    else
      pytest tests/test_k8s_deployment_checklist.py -q
    fi
    ;;
  deploy)
    echo "[$(date -Iseconds)] Running deploy.sh" >> "$LOGFILE"
    ./k8s/deploy.sh
    ;;
  port-forward)
    echo "[$(date -Iseconds)] Starting kubectl port-forward in background" >> "$LOGFILE"
    kubectl port-forward -n python-mcp-server svc/mcp-server-service 3011:3011 &
    PF_PID=$!
    echo "[$(date -Iseconds)] port-forward PID: $PF_PID" >> "$LOGFILE"
    echo "Port-forward started (PID $PF_PID). Use 'kill $PF_PID' to stop." >> "$LOGFILE"
    ;;
  *)
    echo "Unknown action: $action" >&2
    exit 2
    ;;
esac

echo "[$(date -Iseconds)] Completed action: $action" >> "$LOGFILE"
