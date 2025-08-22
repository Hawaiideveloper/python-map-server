# Claude & AI Assistants Guide

This file documents how we expect Claude or other AI assistants to interact with the repository and what guardrails to use for the Python MCP Server project.

## Project Context
- **Goal**: Complete the comprehensive checklist.md (130+ items) for full production deployment
- **Primary Language**: Python only - avoid other languages unless absolutely necessary
- **Deployment Targets**: Kubernetes (preferred) with Docker fallback
- **Repository Owner**: Hawaiideveloper
- **Docker Registry**: GitHub Container Registry (GHCR) - avoid Docker Hub

## Automation Permissions

### Approved Actions
- Run repository-approved scripts: `scripts/deploy.py`, `scripts/test_runner.py`, `./.vscode/approved-commands.sh`
- Create GitHub repository secrets using `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable
- Create Kubernetes image pull secret (`ghcr-pull-secret`) using environment variables `GHCR_USER` and `GHCR_PAT`
- Install VS Code extensions (especially GitHub Actions extension)
- Modify `.vscode/settings.json` to enable auto-approve for common operations
- Update documentation files (README.md, CHANGELOG.md, docs/*)

### Security Guidelines
- NEVER echo or store secrets in repo files or chat logs
- Use `kubectl create secret ... --dry-run=client -o yaml | kubectl apply -f -` to avoid leaking secrets
- Prefer environment variables over hardcoded values
- Validate all inputs and sanitize outputs

### Error Handling Protocol
When any operation fails:
1. Record the failure in `Lessons_learned.md` with:
   - Exact error message and context
   - Root cause analysis
   - Step-by-step remediation
2. Create a corresponding unit test in `tests/` that:
   - Reproduces the error condition
   - Asserts proper error handling
   - Validates the fix

### Workflow Priorities
1. **Kubernetes First**: Always attempt Kubernetes deployment before Docker fallback
2. **Test-Driven**: Run unit tests after each significant change
3. **Checklist-Driven**: Focus on completing checklist.md items
4. **Python-Centric**: Keep everything in Python ecosystem
5. **GHCR-Only**: Publish and pull from GitHub Container Registry

## Typical Workflows

### Deployment Workflow
1. Check Kubernetes connectivity: `kubectl cluster-info`
2. If K8s available: Use `scripts/deploy.py` or `./.vscode/approved-commands.sh deploy`
3. If K8s unavailable: Fallback to Docker with `scripts/deploy.py`
4. Always run health checks after deployment
5. Update checklist items only after successful tests

### Development Workflow
1. Run `scripts/test_runner.py` to validate current state
2. Make changes following Python MCP Server patterns
3. Run tests again to ensure no regressions
4. Update relevant documentation
5. Commit with meaningful messages referencing checklist items

### Failure Recovery
1. Collect diagnostic information (`kubectl describe`, `docker logs`, etc.)
2. Add failure details to `Lessons_learned.md`
3. Create unit test for the failure scenario
4. Implement fix and validate with tests
5. Update checklist and documentation

## AI Assistant Behavior
- **Auto-Fix**: Don't prompt for common operations - fix errors automatically
- **Checklist-Focused**: Always work toward completing checklist.md items
- **Test-Validated**: Only mark checklist items complete when tests pass
- **Documentation-First**: Update docs before marking items complete
- **Python-Pure**: Avoid suggesting non-Python solutions

## VS Code Integration
The AI should leverage VS Code auto-approve settings for:
- `kubectl` commands (get, apply, describe)
- `python` and `pytest` commands
- `git` operations
- GitHub CLI (`gh`) commands
- Docker commands for local development

## Repository Structure Expectations
```
python-mcp-server/
├── scripts/           # Automation scripts (Python only)
├── src/              # Source code
├── tests/            # Unit and integration tests
├── docs/             # Documentation
├── k8s/              # Kubernetes manifests
├── .vscode/          # VS Code configuration
├── .env              # Environment variables (no secrets)
└── checklist.md      # Master checklist (130+ items)
```

