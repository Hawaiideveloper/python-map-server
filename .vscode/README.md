## VS Code workspace tasks

This workspace defines a few useful tasks to run common workflows locally. These are workspace-local and do not change your global VS Code settings.

Available tasks:

- `Make k8s scripts executable` — sets execute bit on `k8s/deploy.sh` and `k8s/manage.sh`.
- `Run k8s checklist tests` — runs `pytest tests/test_k8s_deployment_checklist.py` which validates manifests and will mark checklist boxes in `k8s/README.md` when tests pass.
- `Deploy Python MCP Server (k8s)` — runs the deployment script `./k8s/deploy.sh` against your current kube context.
- `Port-forward MCP (3011)` — runs `kubectl port-forward` to expose the service locally on port 3011 (background task).

Security notes:
- Tasks run shell commands from the repository. Review `/.vscode/tasks.json` before running.
- These tasks do not store or transmit secrets. They rely on your local `kubectl` credentials and environment.

How to run:
1. Open the Command Palette (Cmd+Shift+P) and pick `Tasks: Run Task`.
2. Choose the task you want to execute.

If you want these wired into keyboard shortcuts or CI, let me know and I can add suggested configurations.
