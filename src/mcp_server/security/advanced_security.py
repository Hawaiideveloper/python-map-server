"""
Advanced security hardening system for production deployment.

This module provides comprehensive security measures to prevent
exploitation and ensure the server remains secure under attack.
"""

import ast
import hashlib
import os
import re
import subprocess
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import secrets
import string

from ..utils.logging import setup_logger

logger = setup_logger("advanced_security")


class SecurityValidator:
    """Advanced code security validation."""
    
    def __init__(self):
        self.dangerous_patterns = self._load_dangerous_patterns()
        self.security_cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = 10000
        
    def _load_dangerous_patterns(self) -> Dict[str, List[str]]:
        """Load comprehensive dangerous code patterns."""
        return {
            "command_injection": [
                r"subprocess\.(?:run|call|check_output|Popen|check_call)",
                r"os\.system\(",
                r"os\.popen\(",
                r"os\.spawn[a-z]*\(",
                r"commands\.[a-z]+\(",
                r"getattr\([^,]+,\s*['\"](?:system|popen|spawn)['\"]",
                r"eval\(",
                r"exec\(",
                r"compile\(",
                r"__import__\(",
                r"importlib\.import_module\(",
            ],
            "file_system": [
                r"open\([^,)]*[,)].*['\"]w",  # Write operations
                r"\.write\(",
                r"\.writelines\(",
                r"\.mkdir\(",
                r"\.rmdir\(",
                r"\.remove\(",
                r"\.unlink\(",
                r"\.rename\(",
                r"\.move\(",
                r"\.chmod\(",
                r"\.chown\(",
                r"shutil\.[a-z]+\(",
            ],
            "network": [
                r"socket\.",
                r"urllib\.",
                r"requests\.",
                r"http\.",
                r"ftp\.",
                r"telnet\.",
                r"ssh\.",
                r"scp\.",
                r"paramiko\.",
            ],
            "serialization": [
                r"pickle\.load",
                r"pickle\.loads",
                r"marshal\.load",
                r"marshal\.loads",
                r"dill\.load",
                r"yaml\.load\(",  # Without safe_load
            ],
            "reflection": [
                r"getattr\(",
                r"setattr\(",
                r"hasattr\(",
                r"delattr\(",
                r"vars\(",
                r"globals\(",
                r"locals\(",
                r"__[a-z]+__",  # Dunder methods
            ],
            "dangerous_builtins": [
                r"\b(?:exec|eval|compile|__import__|input|raw_input)\s*\(",
                r"type\([^,)]+,\s*\([^)]*\),\s*{",  # Dynamic class creation
                r"property\([^)]*lambda",  # Property with lambda
            ]
        }
    
    def validate_code_security(self, code: str) -> Dict[str, Any]:
        """Comprehensive security validation of Python code."""
        # Check cache first
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        if code_hash in self.security_cache:
            cached_result = self.security_cache[code_hash]
            cached_result["from_cache"] = True
            return cached_result
        
        violations = []
        severity = "safe"
        
        # AST-based analysis
        ast_violations = self._analyze_ast(code)
        violations.extend(ast_violations)
        
        # Pattern-based analysis
        pattern_violations = self._analyze_patterns(code)
        violations.extend(pattern_violations)
        
        # Import analysis
        import_violations = self._analyze_imports(code)
        violations.extend(import_violations)
        
        # Determine overall severity
        if any(v["severity"] == "critical" for v in violations):
            severity = "critical"
        elif any(v["severity"] == "high" for v in violations):
            severity = "high"
        elif any(v["severity"] == "medium" for v in violations):
            severity = "medium"
        elif violations:
            severity = "low"
        
        result = {
            "safe": severity in ["safe", "low"],
            "severity": severity,
            "violations": violations,
            "code_hash": code_hash,
            "timestamp": time.time(),
            "from_cache": False
        }
        
        # Cache result (limit cache size)
        if len(self.security_cache) >= self.max_cache_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self.security_cache.keys(),
                key=lambda k: self.security_cache[k]["timestamp"]
            )[:1000]
            for key in oldest_keys:
                self.security_cache.pop(key, None)
        
        self.security_cache[code_hash] = result
        return result
    
    def _analyze_ast(self, code: str) -> List[Dict[str, Any]]:
        """AST-based security analysis."""
        violations = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [{
                "type": "syntax_error",
                "message": f"Syntax error: {e}",
                "severity": "high",
                "line": getattr(e, 'lineno', 0)
            }]
        
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.violations = []
            
            def visit_Call(self, node):
                # Check function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in ["eval", "exec", "compile", "__import__"]:
                        self.violations.append({
                            "type": "dangerous_builtin",
                            "message": f"Dangerous builtin function: {func_name}",
                            "severity": "critical",
                            "line": node.lineno
                        })
                elif isinstance(node.func, ast.Attribute):
                    # Check for os.system, subprocess.run, etc.
                    if (isinstance(node.func.value, ast.Name) and 
                        node.func.value.id in ["os", "subprocess", "commands"]):
                        
                        method = node.func.attr
                        if method in ["system", "popen", "run", "call", "check_output"]:
                            self.violations.append({
                                "type": "command_injection",
                                "message": f"Command execution: {node.func.value.id}.{method}",
                                "severity": "critical",
                                "line": node.lineno
                            })
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                for name in node.names:
                    if name.name in ["subprocess", "os", "commands", "pickle", "marshal"]:
                        self.violations.append({
                            "type": "dangerous_import",
                            "message": f"Potentially dangerous import: {name.name}",
                            "severity": "medium",
                            "line": node.lineno
                        })
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module in ["subprocess", "os", "commands", "pickle", "marshal"]:
                    imported_names = [alias.name for alias in node.names]
                    self.violations.append({
                        "type": "dangerous_import",
                        "message": f"Dangerous import from {node.module}: {imported_names}",
                        "severity": "medium",
                        "line": node.lineno
                    })
                self.generic_visit(node)
        
        visitor = SecurityVisitor()
        visitor.visit(tree)
        violations.extend(visitor.violations)
        
        return violations
    
    def _analyze_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Pattern-based security analysis."""
        violations = []
        
        for category, patterns in self.dangerous_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, code, re.IGNORECASE))
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    
                    severity = self._get_pattern_severity(category, pattern)
                    
                    violations.append({
                        "type": f"pattern_{category}",
                        "message": f"Dangerous pattern detected: {match.group()}",
                        "severity": severity,
                        "line": line_num,
                        "pattern": pattern
                    })
        
        return violations
    
    def _analyze_imports(self, code: str) -> List[Dict[str, Any]]:
        """Analyze import statements for security risks."""
        violations = []
        
        dangerous_modules = {
            "subprocess": "critical",
            "os": "high",
            "commands": "critical",
            "pickle": "high",
            "marshal": "high",
            "ctypes": "critical",
            "imp": "medium",
            "importlib": "medium",
            "socket": "medium",
            "urllib": "medium",
            "requests": "low",
            "paramiko": "medium",
            "fabric": "medium",
        }
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith(('import ', 'from ')):
                for module, severity in dangerous_modules.items():
                    if f" {module}" in line or line.startswith(f"import {module}"):
                        violations.append({
                            "type": "dangerous_module_import",
                            "message": f"Import of potentially dangerous module: {module}",
                            "severity": severity,
                            "line": i,
                            "module": module
                        })
        
        return violations
    
    def _get_pattern_severity(self, category: str, pattern: str) -> str:
        """Determine severity based on category and pattern."""
        severity_map = {
            "command_injection": "critical",
            "file_system": "high",
            "network": "medium",
            "serialization": "high",
            "reflection": "medium",
            "dangerous_builtins": "critical"
        }
        return severity_map.get(category, "medium")


class SandboxManager:
    """Advanced sandboxing for code execution."""
    
    def __init__(self):
        self.sandbox_dir = Path(tempfile.gettempdir()) / "mcp_sandbox"
        self.sandbox_dir.mkdir(exist_ok=True)
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}
    
    def create_sandbox(self, execution_id: str) -> Dict[str, Any]:
        """Create isolated sandbox for code execution."""
        sandbox_id = f"sandbox_{execution_id}_{secrets.token_hex(8)}"
        sandbox_path = self.sandbox_dir / sandbox_id
        sandbox_path.mkdir(mode=0o755)
        
        # Create restricted environment
        env = self._create_restricted_environment()
        
        # Set up resource limits
        limits = self._get_resource_limits()
        
        sandbox_info = {
            "id": sandbox_id,
            "path": str(sandbox_path),
            "env": env,
            "limits": limits,
            "created_at": time.time(),
            "active": True
        }
        
        self.active_sandboxes[sandbox_id] = sandbox_info
        return sandbox_info
    
    def _create_restricted_environment(self) -> Dict[str, str]:
        """Create restricted environment variables."""
        # Start with minimal environment
        env = {
            "PATH": "/usr/bin:/bin",
            "PYTHONPATH": "",
            "HOME": str(self.sandbox_dir),
            "USER": "sandbox",
            "SHELL": "/bin/false",
            "TMPDIR": str(self.sandbox_dir),
            "TEMP": str(self.sandbox_dir),
            "TMP": str(self.sandbox_dir),
        }
        
        # Remove dangerous environment variables
        dangerous_vars = [
            "LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONSTARTUP",
            "PYTHONHOME", "PYTHONUSERBASE", "PYTHONEXECUTABLE",
            "PYTHONIOENCODING", "PYTHONHASHSEED"
        ]
        
        for var in dangerous_vars:
            env.pop(var, None)
        
        return env
    
    def _get_resource_limits(self) -> Dict[str, Any]:
        """Get resource limits for sandbox."""
        return {
            "memory_mb": 128,
            "cpu_time_seconds": 10,
            "wall_time_seconds": 30,
            "file_size_mb": 10,
            "processes": 5,
            "files": 100,
            "network": False,
            "file_write": False
        }
    
    def cleanup_sandbox(self, sandbox_id: str) -> bool:
        """Clean up sandbox after execution."""
        if sandbox_id not in self.active_sandboxes:
            return False
        
        sandbox_info = self.active_sandboxes[sandbox_id]
        sandbox_path = Path(sandbox_info["path"])
        
        try:
            # Remove all files in sandbox
            if sandbox_path.exists():
                import shutil
                shutil.rmtree(sandbox_path, ignore_errors=True)
            
            # Mark as inactive
            sandbox_info["active"] = False
            sandbox_info["cleaned_at"] = time.time()
            
            # Remove from active sandboxes
            del self.active_sandboxes[sandbox_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Sandbox cleanup error: {e}")
            return False
    
    def cleanup_old_sandboxes(self, max_age_seconds: int = 3600):
        """Clean up sandboxes older than max_age_seconds."""
        current_time = time.time()
        old_sandboxes = [
            sandbox_id for sandbox_id, info in self.active_sandboxes.items()
            if current_time - info["created_at"] > max_age_seconds
        ]
        
        for sandbox_id in old_sandboxes:
            self.cleanup_sandbox(sandbox_id)
        
        return len(old_sandboxes)


class SecurityAuditor:
    """Security auditing and monitoring."""
    
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
        self.max_log_size = 10000
        self.alert_thresholds = {
            "failed_validations_per_minute": 10,
            "critical_violations_per_hour": 5,
            "sandbox_failures_per_hour": 3
        }
        self.security_metrics = {
            "total_validations": 0,
            "failed_validations": 0,
            "critical_violations": 0,
            "sandbox_failures": 0,
            "last_alert_time": 0
        }
    
    def log_security_event(
        self, 
        event_type: str, 
        details: Dict[str, Any],
        severity: str = "info"
    ):
        """Log security event for auditing."""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "severity": severity,
            "details": details,
            "source_ip": details.get("source_ip", "unknown")
        }
        
        self.audit_log.append(event)
        
        # Limit log size
        if len(self.audit_log) > self.max_log_size:
            self.audit_log = self.audit_log[-self.max_log_size//2:]
        
        # Update metrics
        self._update_metrics(event_type, severity)
        
        # Check for alerts
        self._check_security_alerts()
        
        logger.info(f"Security event: {event_type} ({severity})")
    
    def _update_metrics(self, event_type: str, severity: str):
        """Update security metrics."""
        if event_type == "code_validation":
            self.security_metrics["total_validations"] += 1
            if severity in ["high", "critical"]:
                self.security_metrics["failed_validations"] += 1
        
        if severity == "critical":
            self.security_metrics["critical_violations"] += 1
        
        if event_type == "sandbox_failure":
            self.security_metrics["sandbox_failures"] += 1
    
    def _check_security_alerts(self):
        """Check if security alert thresholds are exceeded."""
        current_time = time.time()
        
        # Only check alerts once per minute
        if current_time - self.security_metrics["last_alert_time"] < 60:
            return
        
        # Check recent events
        recent_events = [
            event for event in self.audit_log
            if current_time - event["timestamp"] < 3600  # Last hour
        ]
        
        # Count different types of events
        failed_validations_recent = len([
            e for e in recent_events
            if e["type"] == "code_validation" and e["severity"] in ["high", "critical"]
            and current_time - e["timestamp"] < 60  # Last minute
        ])
        
        critical_violations_recent = len([
            e for e in recent_events
            if e["severity"] == "critical"
        ])
        
        sandbox_failures_recent = len([
            e for e in recent_events
            if e["type"] == "sandbox_failure"
        ])
        
        # Check thresholds
        alerts = []
        
        if failed_validations_recent >= self.alert_thresholds["failed_validations_per_minute"]:
            alerts.append({
                "type": "high_validation_failures",
                "count": failed_validations_recent,
                "threshold": self.alert_thresholds["failed_validations_per_minute"]
            })
        
        if critical_violations_recent >= self.alert_thresholds["critical_violations_per_hour"]:
            alerts.append({
                "type": "high_critical_violations",
                "count": critical_violations_recent,
                "threshold": self.alert_thresholds["critical_violations_per_hour"]
            })
        
        if sandbox_failures_recent >= self.alert_thresholds["sandbox_failures_per_hour"]:
            alerts.append({
                "type": "high_sandbox_failures",
                "count": sandbox_failures_recent,
                "threshold": self.alert_thresholds["sandbox_failures_per_hour"]
            })
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Security alert: {alert}")
            self.log_security_event(
                "security_alert",
                alert,
                "critical"
            )
        
        self.security_metrics["last_alert_time"] = current_time
    
    def get_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate security report for the last N hours."""
        current_time = time.time()
        cutoff_time = current_time - (hours * 3600)
        
        recent_events = [
            event for event in self.audit_log
            if event["timestamp"] > cutoff_time
        ]
        
        # Analyze events
        event_counts = {}
        severity_counts = {}
        source_ips = {}
        
        for event in recent_events:
            event_type = event["type"]
            severity = event["severity"]
            source_ip = event["details"].get("source_ip", "unknown")
            
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            source_ips[source_ip] = source_ips.get(source_ip, 0) + 1
        
        return {
            "period_hours": hours,
            "total_events": len(recent_events),
            "event_types": event_counts,
            "severity_distribution": severity_counts,
            "top_source_ips": dict(sorted(source_ips.items(), key=lambda x: x[1], reverse=True)[:10]),
            "metrics": self.security_metrics.copy(),
            "alert_thresholds": self.alert_thresholds.copy()
        }


# Global instances
_security_validator = SecurityValidator()
_sandbox_manager = SandboxManager()
_security_auditor = SecurityAuditor()


def validate_code_security(code: str, source_ip: str = "unknown") -> Dict[str, Any]:
    """Validate code security with comprehensive checks."""
    result = _security_validator.validate_code_security(code)
    
    # Log security event
    _security_auditor.log_security_event(
        "code_validation",
        {
            "code_hash": result["code_hash"],
            "severity": result["severity"],
            "violations_count": len(result["violations"]),
            "source_ip": source_ip
        },
        result["severity"]
    )
    
    return result


def create_execution_sandbox(execution_id: str) -> Dict[str, Any]:
    """Create secure sandbox for code execution."""
    return _sandbox_manager.create_sandbox(execution_id)


def cleanup_execution_sandbox(sandbox_id: str) -> bool:
    """Clean up execution sandbox."""
    return _sandbox_manager.cleanup_sandbox(sandbox_id)


def get_security_status() -> Dict[str, Any]:
    """Get current security status."""
    return {
        "validator": {
            "cache_size": len(_security_validator.security_cache),
            "max_cache_size": _security_validator.max_cache_size
        },
        "sandbox_manager": {
            "active_sandboxes": len(_sandbox_manager.active_sandboxes),
            "sandbox_dir": str(_sandbox_manager.sandbox_dir)
        },
        "auditor": {
            "audit_log_size": len(_security_auditor.audit_log),
            "metrics": _security_auditor.security_metrics.copy()
        }
    }


def get_security_report(hours: int = 24) -> Dict[str, Any]:
    """Generate comprehensive security report."""
    return _security_auditor.get_security_report(hours)


def cleanup_old_sandboxes(max_age_seconds: int = 3600) -> int:
    """Clean up old sandboxes."""
    return _sandbox_manager.cleanup_old_sandboxes(max_age_seconds)
