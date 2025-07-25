"""
Centralized logging and monitoring for the Python MCP Server.

This module provides structured logging, metrics collection, and monitoring
capabilities for all MCP tools and operations.
"""

import logging
import time
import json
import os
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime
from pathlib import Path

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Create formatters
json_formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
)

console_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Setup loggers
def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Create a structured logger for the application."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (JSON format for parsing)
    file_handler = logging.FileHandler(LOG_DIR / f"{name}.log")
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    return logger

# Application loggers
server_logger = setup_logger("mcp_server")
security_logger = setup_logger("security")
tool_logger = setup_logger("tools")
performance_logger = setup_logger("performance")

class MetricsCollector:
    """Collect and track metrics for the MCP server."""
    
    def __init__(self):
        self.metrics = {
            "tool_executions": {},
            "execution_times": {},
            "error_counts": {},
            "security_violations": 0,
            "total_requests": 0,
            "start_time": time.time()
        }
        
    def record_tool_execution(self, tool_name: str, execution_time: float, success: bool):
        """Record metrics for tool execution."""
        if tool_name not in self.metrics["tool_executions"]:
            self.metrics["tool_executions"][tool_name] = {"success": 0, "failure": 0}
            self.metrics["execution_times"][tool_name] = []
        
        if success:
            self.metrics["tool_executions"][tool_name]["success"] += 1
        else:
            self.metrics["tool_executions"][tool_name]["failure"] += 1
            
        self.metrics["execution_times"][tool_name].append(execution_time)
        self.metrics["total_requests"] += 1
        
    def record_security_violation(self, violation_type: str):
        """Record security violation."""
        self.metrics["security_violations"] += 1
        security_logger.warning(f"Security violation: {violation_type}")
        
    def record_error(self, error_type: str):
        """Record error occurrence."""
        if error_type not in self.metrics["error_counts"]:
            self.metrics["error_counts"][error_type] = 0
        self.metrics["error_counts"][error_type] += 1
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        uptime = time.time() - self.metrics["start_time"]
        
        # Calculate averages
        avg_times = {}
        for tool, times in self.metrics["execution_times"].items():
            if times:
                avg_times[tool] = sum(times) / len(times)
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.metrics["total_requests"],
            "tool_executions": self.metrics["tool_executions"],
            "average_execution_times": avg_times,
            "error_counts": self.metrics["error_counts"],
            "security_violations": self.metrics["security_violations"],
            "requests_per_second": self.metrics["total_requests"] / max(uptime, 1)
        }

# Global metrics collector
metrics = MetricsCollector()

def log_tool_execution(tool_name: str):
    """Decorator to log tool execution with metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            request_id = f"{tool_name}_{int(start_time * 1000)}"
            
            tool_logger.info(f"Starting {tool_name} execution", extra={
                "request_id": request_id,
                "tool": tool_name,
                "args_count": len(args),
                "kwargs": list(kwargs.keys())
            })
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                success = result.get("status") == "success" if isinstance(result, dict) else True
                
                metrics.record_tool_execution(tool_name, execution_time, success)
                
                tool_logger.info(f"Completed {tool_name} execution", extra={
                    "request_id": request_id,
                    "tool": tool_name,
                    "execution_time": execution_time,
                    "success": success
                })
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                metrics.record_tool_execution(tool_name, execution_time, False)
                metrics.record_error(type(e).__name__)
                
                tool_logger.error(f"Failed {tool_name} execution", extra={
                    "request_id": request_id,
                    "tool": tool_name,
                    "execution_time": execution_time,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                
                raise
        return wrapper
    return decorator

def log_http_request(endpoint: str):
    """Decorator to log HTTP requests."""
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            start_time = time.time()
            client_ip = request.client.host if request.client else "unknown"
            
            server_logger.info(f"HTTP request to {endpoint}", extra={
                "endpoint": endpoint,
                "client_ip": client_ip,
                "method": request.method,
                "user_agent": request.headers.get("user-agent", "unknown")
            })
            
            try:
                response = await func(request, *args, **kwargs)
                execution_time = time.time() - start_time
                
                server_logger.info(f"HTTP response from {endpoint}", extra={
                    "endpoint": endpoint,
                    "client_ip": client_ip,
                    "execution_time": execution_time,
                    "status_code": getattr(response, 'status_code', 200)
                })
                
                return response
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                server_logger.error(f"HTTP error at {endpoint}", extra={
                    "endpoint": endpoint,
                    "client_ip": client_ip,
                    "execution_time": execution_time,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                
                raise
        return wrapper
    return decorator

def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security-related events."""
    security_logger.warning(f"Security event: {event_type}", extra={
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        **details
    })
    
    metrics.record_security_violation(event_type)

def log_performance_warning(operation: str, execution_time: float, threshold: float = 5.0):
    """Log performance warnings for slow operations."""
    if execution_time > threshold:
        performance_logger.warning(f"Slow operation detected: {operation}", extra={
            "operation": operation,
            "execution_time": execution_time,
            "threshold": threshold
        })

def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics.get_metrics(),
        "log_files": [str(f) for f in LOG_DIR.glob("*.log")],
        "system_info": {
            "python_version": os.sys.version,
            "platform": os.name,
            "working_directory": os.getcwd()
        }
    }

# Health check function
def health_check() -> Dict[str, Any]:
    """Perform system health check."""
    try:
        # Check log directory
        log_dir_writable = os.access(LOG_DIR, os.W_OK)
        
        # Check metrics
        current_metrics = metrics.get_metrics()
        
        # Determine health status
        is_healthy = (
            log_dir_writable and
            current_metrics["security_violations"] < 100 and  # Reasonable threshold
            current_metrics["total_requests"] >= 0
        )
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "log_directory_writable": log_dir_writable,
                "metrics_available": bool(current_metrics),
                "security_violations": current_metrics["security_violations"]
            },
            "metrics_summary": {
                "total_requests": current_metrics["total_requests"],
                "uptime_seconds": current_metrics["uptime_seconds"],
                "requests_per_second": current_metrics["requests_per_second"]
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
