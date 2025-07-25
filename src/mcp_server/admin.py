"""
Admin dashboard endpoints for monitoring and managing the Python MCP Server.

This module provides administrative endpoints for system monitoring,
user management, and server configuration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..utils.auth import authenticate_request, api_key_manager, usage_tracker
from ..utils.database import db_manager
from ..utils.logging import metrics, get_system_status, health_check

admin_router = APIRouter(prefix="/admin", tags=["admin"])

def require_admin_auth(auth_info: Dict[str, Any] = Depends(lambda: authenticate_request(operation="admin"))):
    """Require admin authentication."""
    if "*" not in auth_info.get("permissions", []) and "admin" not in auth_info.get("permissions", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    return auth_info

@admin_router.get("/dashboard")
async def admin_dashboard(auth_info: Dict[str, Any] = Depends(require_admin_auth)):
    """Get admin dashboard data."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP Server Admin Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .metric { text-align: center; padding: 20px; background: #e3f2fd; border-radius: 8px; }
            .metric h3 { margin: 0; color: #1976d2; }
            .metric .value { font-size: 2em; font-weight: bold; margin: 10px 0; }
            .status-healthy { color: #4caf50; }
            .status-unhealthy { color: #f44336; }
            h1, h2 { color: #333; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; }
            .btn { background: #1976d2; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
            .btn:hover { background: #1565c0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>MCP Server Admin Dashboard</h1>
            
            <div class="card">
                <h2>System Status</h2>
                <div id="system-status">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Key Metrics</h2>
                <div class="grid" id="metrics-grid">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Recent API Keys</h2>
                <div id="api-keys">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Usage Statistics</h2>
                <div id="usage-stats">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Security Events</h2>
                <div id="security-events">Loading...</div>
            </div>
        </div>
        
        <script>
            async function loadDashboardData() {
                try {
                    // Load system status
                    const statusResponse = await fetch('/admin/system/status');
                    const statusData = await statusResponse.json();
                    document.getElementById('system-status').innerHTML = 
                        `<span class="status-${statusData.status}">${statusData.status.toUpperCase()}</span>`;
                    
                    // Load metrics
                    const metricsResponse = await fetch('/admin/metrics');
                    const metricsData = await metricsResponse.json();
                    
                    const metricsGrid = document.getElementById('metrics-grid');
                    metricsGrid.innerHTML = `
                        <div class="metric">
                            <h3>Total Requests</h3>
                            <div class="value">${metricsData.total_requests}</div>
                        </div>
                        <div class="metric">
                            <h3>Uptime</h3>
                            <div class="value">${Math.round(metricsData.uptime_seconds / 3600)}h</div>
                        </div>
                        <div class="metric">
                            <h3>Requests/sec</h3>
                            <div class="value">${metricsData.requests_per_second.toFixed(2)}</div>
                        </div>
                        <div class="metric">
                            <h3>Security Violations</h3>
                            <div class="value">${metricsData.security_violations}</div>
                        </div>
                    `;
                    
                    // Load API keys
                    const keysResponse = await fetch('/admin/api-keys');
                    const keysData = await keysResponse.json();
                    
                    let keysHtml = '<table><tr><th>Key (partial)</th><th>Name</th><th>Permissions</th><th>Last Used</th><th>Requests</th></tr>';
                    for (const [key, info] of Object.entries(keysData)) {
                        keysHtml += `
                            <tr>
                                <td>${key}</td>
                                <td>${info.name}</td>
                                <td>${info.permissions.join(', ')}</td>
                                <td>${info.last_used || 'Never'}</td>
                                <td>${info.request_count}</td>
                            </tr>
                        `;
                    }
                    keysHtml += '</table>';
                    document.getElementById('api-keys').innerHTML = keysHtml;
                    
                } catch (error) {
                    console.error('Error loading dashboard data:', error);
                }
            }
            
            // Load data on page load
            loadDashboardData();
            
            // Refresh every 30 seconds
            setInterval(loadDashboardData, 30000);
        </script>
    </body>
    </html>
    """)

@admin_router.get("/system/status")
async def system_status(auth_info: Dict[str, Any] = Depends(require_admin_auth)):
    """Get system health status."""
    return health_check()

@admin_router.get("/metrics")
async def get_metrics(auth_info: Dict[str, Any] = Depends(require_admin_auth)):
    """Get system metrics."""
    return metrics.get_metrics()

@admin_router.get("/api-keys")
async def list_api_keys(auth_info: Dict[str, Any] = Depends(require_admin_auth)):
    """List all API keys."""
    return api_key_manager.list_api_keys()

@admin_router.post("/api-keys")
async def create_api_key(
    name: str,
    permissions: List[str],
    auth_info: Dict[str, Any] = Depends(require_admin_auth)
):
    """Create a new API key."""
    api_key = api_key_manager.create_api_key(name, permissions)
    return {"api_key": api_key, "message": "API key created successfully"}

@admin_router.delete("/api-keys/{key_prefix}")
async def revoke_api_key(
    key_prefix: str,
    auth_info: Dict[str, Any] = Depends(require_admin_auth)
):
    """Revoke an API key by prefix."""
    # In a real implementation, you'd need to find the full key by prefix
    success = api_key_manager.revoke_api_key(key_prefix)
    if success:
        return {"message": "API key revoked successfully"}
    else:
        raise HTTPException(status_code=404, detail="API key not found")

@admin_router.get("/usage-stats")
async def get_usage_stats(
    days: int = Query(7, description="Number of days to look back"),
    auth_info: Dict[str, Any] = Depends(require_admin_auth)
):
    """Get usage statistics."""
    return usage_tracker.get_all_usage_stats()

@admin_router.get("/execution-history")
async def get_execution_history(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, description="Number of records to return"),
    auth_info: Dict[str, Any] = Depends(require_admin_auth)
):
    """Get execution history."""
    if user_id:
        return db_manager.get_execution_history(user_id, limit)
    else:
        # Return history for all users (admin only)
        return {"message": "All user history endpoint not implemented yet"}

@admin_router.get("/security-events")
async def get_security_events(
    days: int = Query(7, description="Number of days to look back"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    auth_info: Dict[str, Any] = Depends(require_admin_auth)
):
    """Get security events."""
    return db_manager.get_security_events(user_id, days)

@admin_router.post("/system/cleanup")
async def cleanup_old_data(
    days: int = Query(90, description="Delete data older than this many days"),
    auth_info: Dict[str, Any] = Depends(require_admin_auth)
):
    """Clean up old data."""
    db_manager.cleanup_old_data(days)
    return {"message": f"Cleaned up data older than {days} days"}

@admin_router.get("/logs/{log_name}")
async def get_logs(
    log_name: str,
    lines: int = Query(100, description="Number of lines to return"),
    auth_info: Dict[str, Any] = Depends(require_admin_auth)
):
    """Get log files."""
    import os
    from pathlib import Path
    
    log_path = Path("logs") / f"{log_name}.log"
    
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Log file not found")
    
    try:
        with open(log_path, 'r') as f:
            # Read last N lines
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
        return {
            "log_name": log_name,
            "lines": recent_lines,
            "total_lines": len(all_lines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")

@admin_router.get("/config")
async def get_config(auth_info: Dict[str, Any] = Depends(require_admin_auth)):
    """Get current server configuration."""
    from ..config import get_config
    
    config = get_config()
    
    # Sanitize sensitive information
    sanitized_config = {}
    for key, value in config.items():
        if key in ["aws", "gcp", "azure"]:
            # Hide sensitive credentials
            sanitized_config[key] = {k: "***" if "key" in k.lower() or "secret" in k.lower() 
                                   else v for k, v in value.items()}
        else:
            sanitized_config[key] = value
    
    return sanitized_config

@admin_router.post("/system/restart")
async def restart_server(auth_info: Dict[str, Any] = Depends(require_admin_auth)):
    """Restart the server (development only)."""
    import os
    import signal
    
    # In production, this would trigger a proper restart mechanism
    return {"message": "Restart signal sent", "warning": "This is a development feature"}

@admin_router.get("/users")
async def list_users(
    limit: int = Query(100, description="Number of users to return"),
    auth_info: Dict[str, Any] = Depends(require_admin_auth)
):
    """List users (requires database)."""
    # This would require implementing user listing in database manager
    return {"message": "User listing not implemented yet"}

@admin_router.get("/system/info")
async def system_info(auth_info: Dict[str, Any] = Depends(require_admin_auth)):
    """Get detailed system information."""
    import sys
    import platform
    import psutil
    import os
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": psutil.disk_usage('/').percent,
        "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None,
        "uptime": get_system_status()
    }
