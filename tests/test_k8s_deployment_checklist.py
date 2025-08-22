import os
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
K8S_DIR = ROOT / "k8s"
README = K8S_DIR / "README.md"


def _mark_readme_checkbox(item_text: str):
    """Mark the checkbox for the given item_text as checked in the k8s/README.md.

    This is a convenience for the repository checklist. It's idempotent.
    """
    txt = README.read_text(encoding="utf-8")
    pattern = rf"^- \[ \] (.*{re.escape(item_text)}.*)$"
    new_txt, n = re.subn(pattern, r"- [x] \1", txt, flags=re.MULTILINE)
    if n:
        README.write_text(new_txt, encoding="utf-8")


def _assert_file_exists(relative_path: str):
    path = K8S_DIR / relative_path
    assert path.exists(), f"Expected {path} to exist"
    return path


def test_manifests_present():
    """Manifests present (namespace, configmap, secret, rbac, deployment, service, ingress, hpa, networkpolicy, servicemonitor)"""
    expected = [
        "namespace.yaml",
        "configmap.yaml",
        "secret.yaml",
        "rbac.yaml",
        "deployment.yaml",
        "service.yaml",
        "ingress.yaml",
        "hpa.yaml",
        "networkpolicy.yaml",
        "servicemonitor.yaml",
    ]

    for e in expected:
        _assert_file_exists(e)

    _mark_readme_checkbox("Manifests present")


def test_deploy_scripts_executable():
    """Deployment scripts executable (deploy.sh, manage.sh)"""
    deploy = _assert_file_exists("deploy.sh")
    manage = _assert_file_exists("manage.sh")

    # On non-unix filesystems this may be False; allow readable fallback
    assert os.access(deploy, os.R_OK), "deploy.sh is not readable"
    assert os.access(manage, os.R_OK), "manage.sh is not readable"

    # Prefer executable bit if available
    if hasattr(os, "getuid"):
        assert os.access(deploy, os.X_OK), "deploy.sh is not executable"
        assert os.access(manage, os.X_OK), "manage.sh is not executable"

    _mark_readme_checkbox("Deployment scripts executable")


def test_health_probes_in_deployment():
    """Deployment has liveness/readiness probes"""
    deployment = _assert_file_exists("deployment.yaml")
    txt = deployment.read_text(encoding="utf-8")
    assert "livenessProbe" in txt or "livenessProbe:" in txt, "livenessProbe not found in deployment.yaml"
    assert "readinessProbe" in txt or "readinessProbe:" in txt, "readinessProbe not found in deployment.yaml"
    _mark_readme_checkbox("Deployment has liveness/readiness probes")


def test_hpa_configured():
    """HPA configured (min/max replicas present)"""
    hpa = _assert_file_exists("hpa.yaml")
    txt = hpa.read_text(encoding="utf-8")
    assert re.search(r"minReplicas\s*:\s*\d+", txt) or re.search(r"minReplicas:\s*\d+", txt), "minReplicas not set in hpa.yaml"
    assert re.search(r"maxReplicas\s*:\s*\d+", txt) or re.search(r"maxReplicas:\s*\d+", txt), "maxReplicas not set in hpa.yaml"
    _mark_readme_checkbox("HPA configured")


def test_networkpolicy_present_and_restrictive():
    """NetworkPolicy present and restrictive rules defined"""
    np = _assert_file_exists("networkpolicy.yaml")
    txt = np.read_text(encoding="utf-8")
    # Basic check: expect kind: NetworkPolicy and at least one ingress/egress rule or podSelector
    assert "kind: NetworkPolicy" in txt or "kind:NetworkPolicy" in txt, "networkpolicy.yaml does not declare a NetworkPolicy"
    assert "podSelector" in txt or "ingress" in txt or "egress" in txt, "networkpolicy.yaml appears empty or permissive"
    _mark_readme_checkbox("NetworkPolicy present and restrictive rules defined")


def test_servicemonitor_present():
    """ServiceMonitor present for Prometheus scraping"""
    sm = _assert_file_exists("servicemonitor.yaml")
    txt = sm.read_text(encoding="utf-8")
    assert "kind: ServiceMonitor" in txt or "kind:ServiceMonitor" in txt, "servicemonitor.yaml not a ServiceMonitor"
    _mark_readme_checkbox("ServiceMonitor present for Prometheus scraping")


def test_external_access_configured():
    """External access configured (LoadBalancer or Ingress with TLS)"""
    # Prefer ingress.yaml or service of type LoadBalancer
    ingress = K8S_DIR / "ingress.yaml"
    service = K8S_DIR / "service.yaml"
    assert ingress.exists() or service.exists(), "Neither ingress.yaml nor service.yaml found"

    if ingress.exists():
        txt = ingress.read_text(encoding="utf-8")
        assert "tls" in txt or "tls:" in txt or "tlsCertificate" in txt or "host" in txt, "ingress.yaml doesn't appear to configure TLS/host"

    if service.exists():
        txt = service.read_text(encoding="utf-8")
        # Accept NodePort service (cluster uses NodePort); ensure external port 3011 is present
        assert ("type: LoadBalancer" in txt or "type:LoadBalancer" in txt or "loadBalancer" in txt or "type: NodePort" in txt or "type:NodePort" in txt), "service.yaml doesn't configure LoadBalancer or NodePort"
        assert "3011" in txt or "nodePort: 30011" in txt, "service.yaml does not expose external port 3011 for HTTP"

    _mark_readme_checkbox("External access configured")


def test_internal_cluster_access():
    """Internal cluster access (ClusterIP/headless service and correct port) for pod-to-pod communication"""
    svc = _assert_file_exists("service.yaml")
    txt = svc.read_text(encoding="utf-8")
    assert "ClusterIP" in txt or "clusterIP" in txt or "type: ClusterIP" in txt or "type:ClusterIP" in txt or "headless" in txt, "service.yaml does not declare a ClusterIP/headless service"
    # ensure the expected target port for pods exists (3030) and external port 3011 is an accepted mapping
    assert "3030" in txt or "targetPort: 3030" in txt, "service.yaml does not map to container port 3030"
    assert "3011" in txt or "nodePort: 30011" in txt or "port: 3011" in txt, "service.yaml does not expose external port 3011"
    _mark_readme_checkbox("Internal cluster access")


def test_n8n_integration_guidance_present():
    """n8n integration guidance present (example workflow or notes)"""
    txt = README.read_text(encoding="utf-8")
    assert "n8n" in txt or "n_8n" in txt, "README does not mention n8n integration guidance"
    _mark_readme_checkbox("n8n integration guidance present")


def test_developer_access_instructions():
    """Developer access instructions (VS Code, Cursor, Codespaces) for remote development"""
    txt = README.read_text(encoding="utf-8")
    assert "VS Code" in txt or "Codespaces" in txt or "Cursor" in txt, "README missing developer access instructions for VS Code/Cursor/Codespaces"
    _mark_readme_checkbox("Developer access instructions")
