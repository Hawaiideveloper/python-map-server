"""
Rate limiting and authentication middleware for the Python MCP Server.

This module provides request rate limiting, API key authentication, and
session management for multi-user scenarios.
"""

import secrets
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, DefaultDict, Optional

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


# Rate limiting storage (in-memory for single instance, use Redis for multi-instance)
class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_minute: int = 60, burst_limit: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.clients: DefaultDict[str, dict[str, Any]] = defaultdict(lambda: {
            "requests": deque(),
            "last_request": 0.0
        })

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        now = time.time()
        client_data = self.clients[client_id]  # Dict with 'requests' deque and 'last_request' float

        # Clean old requests (older than 1 minute)
        minute_ago = now - 60
        requests_deque = client_data["requests"]
        while requests_deque and requests_deque[0] < minute_ago:
            requests_deque.popleft()

        # Check rate limits
        request_count = len(requests_deque)

        # Check burst limit
        if request_count >= self.burst_limit:
            # Check if recent requests are too frequent
            if client_data["last_request"] > now - 1:  # Less than 1 second ago
                return False

        # Check per-minute limit
        if request_count >= self.requests_per_minute:
            return False

        # Allow request
        client_data["requests"].append(now)
        client_data["last_request"] = now
        return True

    def get_rate_limit_info(self, client_id: str) -> dict[str, Any]:
        """Get rate limit information for a client."""
        now = time.time()
        client_data = self.clients[client_id]

        # Clean old requests
        minute_ago = now - 60
        while client_data["requests"] and client_data["requests"][0] < minute_ago:
            client_data["requests"].popleft()

        remaining = max(0, self.requests_per_minute - len(client_data["requests"]))
        reset_time = int(client_data["requests"][0] + 60) if client_data["requests"] else int(now)

        return {
            "limit": self.requests_per_minute,
            "remaining": remaining,
            "reset": reset_time,
            "used": len(client_data["requests"])
        }

# API Key management
class APIKeyManager:
    """Manage API keys for authentication."""

    def __init__(self):
        self.api_keys = {}  # In production, use a database
        self.sessions = {}  # Active sessions

        # Create default admin key for development
        self._create_default_keys()

    def _create_default_keys(self):
        """Create default API keys for development."""
        admin_key = "mcp_admin_" + secrets.token_urlsafe(32)
        user_key = "mcp_user_" + secrets.token_urlsafe(32)

        self.api_keys[admin_key] = {
            "name": "Admin Key",
            "permissions": ["*"],  # All permissions
            "created_at": datetime.utcnow(),
            "last_used": None,
            "request_count": 0
        }

        self.api_keys[user_key] = {
            "name": "User Key",
            "permissions": ["run_code", "lint_code", "format_code", "test_code"],
            "created_at": datetime.utcnow(),
            "last_used": None,
            "request_count": 0
        }

        print("Default API Keys created:")
        print(f"Admin Key: {admin_key}")
        print(f"User Key: {user_key}")

    def validate_api_key(self, api_key: str) -> Optional[dict[str, Any]]:
        """Validate an API key and return key info."""
        if api_key in self.api_keys:
            key_info = self.api_keys[api_key]
            key_info["last_used"] = datetime.utcnow()
            key_info["request_count"] += 1
            return key_info
        return None

    def has_permission(self, api_key: str, operation: str) -> bool:
        """Check if API key has permission for operation."""
        key_info = self.validate_api_key(api_key)
        if not key_info:
            return False

        permissions = key_info.get("permissions", [])
        return "*" in permissions or operation in permissions

    def create_api_key(self, name: str, permissions: list[str]) -> str:
        """Create a new API key."""
        api_key = f"mcp_{secrets.token_urlsafe(32)}"
        self.api_keys[api_key] = {
            "name": name,
            "permissions": permissions,
            "created_at": datetime.utcnow(),
            "last_used": None,
            "request_count": 0
        }
        return api_key

    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key."""
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            return True
        return False

    def list_api_keys(self) -> dict[str, dict[str, Any]]:
        """List all API keys (without the actual key values)."""
        return {
            key[:12] + "...": {
                "name": info["name"],
                "permissions": info["permissions"],
                "created_at": info["created_at"].isoformat(),
                "last_used": info["last_used"].isoformat() if info["last_used"] else None,
                "request_count": info["request_count"]
            }
            for key, info in self.api_keys.items()
        }

# Global instances
rate_limiter = RateLimiter()
api_key_manager = APIKeyManager()
security = HTTPBearer()

def get_client_id(request) -> str:
    """Get client identifier for rate limiting."""
    # Use IP address as default client ID
    if hasattr(request, 'client') and request.client:
        return request.client.host
    return "unknown"

def check_rate_limit(request):
    """Middleware to check rate limits."""
    client_id = get_client_id(request)

    if not rate_limiter.is_allowed(client_id):
        rate_info = rate_limiter.get_rate_limit_info(client_id)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": str(rate_info["remaining"]),
                "X-RateLimit-Reset": str(rate_info["reset"])
            }
        )

    return True

def authenticate_request(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    operation: str = "general"
) -> dict[str, Any]:
    """Authenticate request using API key."""
    api_key = credentials.credentials

    # Validate API key
    key_info = api_key_manager.validate_api_key(api_key)
    if not key_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    # Check permissions
    if not api_key_manager.has_permission(api_key, operation):
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions for operation: {operation}"
        )

    return key_info

def optional_auth(
    authorization: Optional[str] = Header(None)
) -> Optional[dict[str, Any]]:
    """Optional authentication for public endpoints."""
    if not authorization:
        return None

    try:
        if authorization.startswith("Bearer "):
            api_key = authorization[7:]
            return api_key_manager.validate_api_key(api_key)
    except Exception:
        pass

    return None

# Session management for stateful operations
class SessionManager:
    """Manage user sessions for stateful operations."""

    def __init__(self):
        self.sessions = {}
        self.session_timeout = 3600  # 1 hour

    def create_session(self, api_key: str) -> str:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "api_key": api_key,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "data": {}
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        """Get session data."""
        if session_id in self.sessions:
            session = self.sessions[session_id]

            # Check if session has expired
            if (datetime.utcnow() - session["last_activity"]).seconds > self.session_timeout:
                del self.sessions[session_id]
                return None

            session["last_activity"] = datetime.utcnow()
            return session
        return None

    def update_session(self, session_id: str, data: dict[str, Any]):
        """Update session data."""
        if session_id in self.sessions:
            self.sessions[session_id]["data"].update(data)
            self.sessions[session_id]["last_activity"] = datetime.utcnow()

    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        now = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if (now - session["last_activity"]).seconds > self.session_timeout
        ]

        for session_id in expired_sessions:
            del self.sessions[session_id]

# Global session manager
session_manager = SessionManager()

# Usage tracking
class UsageTracker:
    """Track API usage for billing/monitoring."""

    def __init__(self):
        self.usage_data: DefaultDict[str, dict[str, Any]] = defaultdict(lambda: {
            "requests": 0,
            "execution_time": 0.0,
            "errors": 0,
            "data_processed": 0,  # bytes
            "tools_used": defaultdict(int)
        })

    def record_usage(self, api_key: str, tool: str, execution_time: float,
                    data_size: int = 0, success: bool = True):
        """Record API usage."""
        usage = self.usage_data[api_key]
        usage["requests"] += 1
        usage["execution_time"] += execution_time
        usage["data_processed"] += data_size
        usage["tools_used"][tool] += 1

        if not success:
            usage["errors"] += 1

    def get_usage_stats(self, api_key: str) -> dict[str, Any]:
        """Get usage statistics for an API key."""
        return dict(self.usage_data.get(api_key, {}))

    def get_all_usage_stats(self) -> dict[str, dict[str, Any]]:
        """Get usage statistics for all API keys."""
        return {key: dict(usage) for key, usage in self.usage_data.items()}

# Global usage tracker
usage_tracker = UsageTracker()
