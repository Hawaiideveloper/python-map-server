# Lessons Learned During Kubernetes Deployment

This document captures concrete failures, their root causes, and the corrective actions taken while deploying the Python MCP Server to a kubeadm cluster.

1. Docker daemon unavailable
   - Symptom: Local image build failed with "Cannot connect to the Docker daemon".
   - Root cause: CI/deployment environment lacked Docker or user was not running Docker locally.
   - Fix: Add `SKIP_LOCAL_BUILD` behavior to `k8s/deploy.sh` to allow cluster-only deploys.
   - Test: Unit test verifies `deploy.sh` returns a clear message when docker is missing.

2. Mis-indented YAML annotations
   - Symptom: kubectl rejected manifests with strict decoder errors (unknown field `metadata.prometheus.io/path`).
   - Root cause: Prometheus annotations were placed at the wrong YAML level or keys were mis-quoted.
   - Fix: Consolidate annotations under `metadata.annotations` and validate manifests with `kubectl apply --dry-run=client -f`.
   - Test: Add a test checklist entry that validates `k8s/service.yaml` parses cleanly with kubectl client dry-run.

3. Incompatible `kubectl` options
   - Symptom: `kubectl` versions differ; `--short` or other flags may not be available.
   - Root cause: Script relied on non-portable flags.
   - Fix: Use feature-detection and fallback behavior in scripts.
   - Test: Add a unit test that simulates `kubectl version` output and ensures script handles it.

4. Tight coupling between build and deploy
   - Symptom: Deployment scripts attempted to build images locally before applying manifests.
   - Root cause: Developer convenience assumption that Docker is always available.
   - Fix: Decouple build and deploy; allow `SKIP_LOCAL_BUILD` and recommend CI-driven image builds for production.
   - Test: Confirm that `k8s/deploy.sh` with `SKIP_LOCAL_BUILD=1` proceeds to apply manifests.

5. Tests that modify docs
   - Symptom: Tests that write back to README can be surprising and change tracked files.
   - Root cause: Tests were designed to mark checkboxes on pass.
   - Fix: Limit tests that mutate tracked files to optional developer flows; prefer generating `checklist-results.json` instead.

Additions:
- Add `tests/test_checklist_and_docs.py` to verify the presence and format of `checklist.md` and `Lessons_learned.md`.
- Use `kubectl` dry-run client checks to validate YAML.

6. GHCR 403 Forbidden when pulling image
    - Symptom: Pods fail to start with errors like:
       "Failed to pull image \"ghcr.io/hawaiideveloper/python-mcp-server:latest\": ... failed to authorize: failed to fetch oauth token ... 403 Forbidden"
    - Root causes (common):
       - No image pull secret present in the target namespace or Deployment doesn't reference it.
       - The Personal Access Token (PAT) used lacks the required `read:packages` scope.
       - The GHCR package visibility or organization permissions prevent anonymous pulls; repository-level permissions not granted to the token.
       - Using the wrong username (use your GitHub username) when creating the docker-registry secret.
    - Fixes applied / recommended:
       1. Ensure `k8s/deployment.yaml` includes `imagePullSecrets:` with the secret name (we use `ghcr-pull-secret`). The current repo `k8s/deployment.yaml` already includes this, but the secret must exist in the cluster namespace.
       2. Create the secret locally using a PAT with `read:packages` scope (recommended command):
            ```bash
            export GHCR_USER="<your-github-username>"
            export GHCR_PAT="<your-personal-access-token-with-read:packages-scope>"
            kubectl create secret docker-registry ghcr-pull-secret \
               --docker-server=ghcr.io \
               --docker-username="$GHCR_USER" \
               --docker-password="$GHCR_PAT" \
               --docker-email="you@example.com" \
               -n python-mcp-server
            ```
            Note: Do not paste the PAT into chat. Export as env vars locally or use your OS secret manager.
       3. If your image is owned by an organization, ensure the PAT has access to the organization's packages (or use a token from a user that has access). For org packages you may need to set package permissions or use a token with repo scope if packages are private to repos.
       4. Apply manifests again (skip local build):
            ```bash
            SKIP_LOCAL_BUILD=1 ./.vscode/approved-commands.sh deploy
            ```
       5. If you still see ImagePullBackOff or 403, inspect the pod and secret:
            ```bash
            kubectl describe pod $(kubectl get pods -n python-mcp-server -l app.kubernetes.io/name=python-mcp-server -o jsonpath='{.items[0].metadata.name}') -n python-mcp-server
            kubectl get secret ghcr-pull-secret -n python-mcp-server -o yaml
            ```
    - Test: After creating the secret, a successful test is that pods pull the image and transition to `Running` (no ImagePullBackOff). To validate quickly:
       ```bash
       kubectl get pods -n python-mcp-server
       kubectl describe pod <pod-name> -n python-mcp-server
       kubectl logs <pod-name> -n python-mcp-server --tail=200
       ```
    - Notes:
       - For CI (GitHub Actions) use a repository secret with `GITHUB_TOKEN` or a PAT configured with `read:packages` and pass it to a workflow step that creates the `ghcr-pull-secret` in the cluster before deployment.
       - Making images public is the simplest fix for infra without secrets but may not be acceptable for private projects.

7. Read-only filesystem preventing directory creation
   - Symptom: Container crashes with error:
     "OSError: [Errno 30] Read-only file system: '/app/data'"
   - Root cause: Application code tries to create directories in `/app/data` but the security context sets `readOnlyRootFilesystem: true` which prevents any writes to the container filesystem.
   - Fix: Add volume mounts for all directories the application needs to write to:
     ```yaml
     volumeMounts:
     - name: data
       mountPath: /app/data
     volumes:
     - name: data
       emptyDir:
         sizeLimit: 1Gi
     ```
   - Test: Pod should start successfully and logs should not show filesystem errors.
   - Preventive measure: Audit application startup code to identify all directories it creates and ensure they have corresponding volume mounts in the deployment.

