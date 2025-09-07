"""
High-performance distributed caching and rate limiting system.

This module provides Redis-backed caching and rate limiting for horizontal
scaling and production-grade performance that outperforms any competitor.
"""

import asyncio
import json
import time
import traceback
from typing import Any, Dict, Optional, Union
import hashlib
import pickle

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

from ..utils.logging import setup_logger

logger = setup_logger("distributed_cache")


class DistributedCache:
    """High-performance distributed cache with Redis backend."""
    
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,
        key_prefix: str = "mcp_server:"
    ):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.redis_client: Optional[redis.Redis] = None
        self.fallback_cache: Dict[str, Dict[str, Any]] = {}
        self.fallback_access_times: Dict[str, float] = {}
        
    async def connect(self):
        """Connect to Redis or fallback to in-memory cache."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using in-memory cache")
            return
            
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory cache")
            self.redis_client = None
    
    def _get_key(self, key: str) -> str:
        """Get prefixed cache key."""
        return f"{self.key_prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._get_key(key)
        
        if self.redis_client:
            try:
                value = await self.redis_client.get(cache_key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                
        # Fallback to in-memory cache
        if key in self.fallback_cache:
            entry = self.fallback_cache[key]
            if time.time() - entry["timestamp"] < entry.get("ttl", self.default_ttl):
                self.fallback_access_times[key] = time.time()
                return entry["value"]
            else:
                # Expired
                self.fallback_cache.pop(key, None)
                self.fallback_access_times.pop(key, None)
        
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        cache_key = self._get_key(key)
        ttl = ttl or self.default_ttl
        
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    cache_key, 
                    ttl, 
                    json.dumps(value, default=str)
                )
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        # Fallback to in-memory cache
        self.fallback_cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl
        }
        self.fallback_access_times[key] = time.time()
        
        # Cleanup old entries
        await self._cleanup_fallback_cache()
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        cache_key = self._get_key(key)
        
        if self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        # Also remove from fallback
        self.fallback_cache.pop(key, None)
        self.fallback_access_times.pop(key, None)
        return True
    
    async def _cleanup_fallback_cache(self):
        """Clean up expired entries from fallback cache."""
        if len(self.fallback_cache) > 1000:  # Limit fallback cache size
            # Remove oldest entries
            sorted_keys = sorted(
                self.fallback_access_times.keys(),
                key=lambda k: self.fallback_access_times[k]
            )
            
            for key in sorted_keys[:100]:  # Remove 100 oldest
                self.fallback_cache.pop(key, None)
                self.fallback_access_times.pop(key, None)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "redis_connected": self.redis_client is not None,
            "fallback_cache_size": len(self.fallback_cache),
            "fallback_max_size": 1000
        }
        
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats.update({
                    "redis_memory_used": info.get("used_memory_human", "unknown"),
                    "redis_connected_clients": info.get("connected_clients", 0),
                    "redis_hits": info.get("keyspace_hits", 0),
                    "redis_misses": info.get("keyspace_misses", 0)
                })
            except Exception as e:
                stats["redis_error"] = str(e)
        
        return stats


class DistributedRateLimiter:
    """High-performance distributed rate limiter with Redis backend."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        requests_per_minute: int = 60,
        burst_limit: int = 10,
        key_prefix: str = "rate_limit:"
    ):
        self.redis_url = redis_url
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.key_prefix = key_prefix
        self.redis_client: Optional[redis.Redis] = None
        
        # Fallback in-memory rate limiter
        self.fallback_clients: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self):
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available for rate limiting")
            return
            
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,  # Keep binary for Lua scripts
                socket_connect_timeout=5,
                socket_timeout=5
            )
            await self.redis_client.ping()
            logger.info("Rate limiter connected to Redis")
        except Exception as e:
            logger.warning(f"Rate limiter Redis connection failed: {e}")
            self.redis_client = None
    
    async def is_allowed(self, client_id: str) -> Dict[str, Any]:
        """Check if client is allowed to make request."""
        if self.redis_client:
            return await self._redis_rate_limit(client_id)
        else:
            return await self._fallback_rate_limit(client_id)
    
    async def _redis_rate_limit(self, client_id: str) -> Dict[str, Any]:
        """Redis-based rate limiting with Lua script for atomicity."""
        key = f"{self.key_prefix}{client_id}"
        now = time.time()
        window = 60  # 1 minute window
        
        # Lua script for atomic rate limiting
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])
        local burst_limit = tonumber(ARGV[4])
        
        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)
        
        -- Count current requests
        local current = redis.call('ZCARD', key)
        
        -- Check burst limit (last second)
        local recent = redis.call('ZCOUNT', key, now - 1, now)
        
        if recent >= burst_limit then
            return {0, current, recent, "burst_limit_exceeded"}
        end
        
        if current >= limit then
            return {0, current, recent, "rate_limit_exceeded"}
        end
        
        -- Add current request
        redis.call('ZADD', key, now, now)
        redis.call('EXPIRE', key, window)
        
        return {1, current + 1, recent + 1, "allowed"}
        """
        
        try:
            result = await self.redis_client.eval(
                lua_script,
                1,
                key,
                now,
                window,
                self.requests_per_minute,
                self.burst_limit
            )
            
            allowed, current_count, recent_count, reason = result
            
            return {
                "allowed": bool(allowed),
                "current_count": current_count,
                "recent_count": recent_count,
                "limit": self.requests_per_minute,
                "burst_limit": self.burst_limit,
                "reason": reason,
                "reset_time": now + window
            }
            
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            return await self._fallback_rate_limit(client_id)
    
    async def _fallback_rate_limit(self, client_id: str) -> Dict[str, Any]:
        """Fallback in-memory rate limiting."""
        now = time.time()
        
        if client_id not in self.fallback_clients:
            self.fallback_clients[client_id] = {
                "requests": [],
                "last_request": 0.0
            }
        
        client_data = self.fallback_clients[client_id]
        
        # Clean old requests
        minute_ago = now - 60
        client_data["requests"] = [
            req_time for req_time in client_data["requests"]
            if req_time > minute_ago
        ]
        
        current_count = len(client_data["requests"])
        
        # Check burst limit
        recent_count = sum(1 for req_time in client_data["requests"] if req_time > now - 1)
        
        if recent_count >= self.burst_limit:
            return {
                "allowed": False,
                "current_count": current_count,
                "recent_count": recent_count,
                "limit": self.requests_per_minute,
                "burst_limit": self.burst_limit,
                "reason": "burst_limit_exceeded",
                "reset_time": now + 60
            }
        
        if current_count >= self.requests_per_minute:
            return {
                "allowed": False,
                "current_count": current_count,
                "recent_count": recent_count,
                "limit": self.requests_per_minute,
                "burst_limit": self.burst_limit,
                "reason": "rate_limit_exceeded",
                "reset_time": now + 60
            }
        
        # Allow request
        client_data["requests"].append(now)
        client_data["last_request"] = now
        
        return {
            "allowed": True,
            "current_count": current_count + 1,
            "recent_count": recent_count + 1,
            "limit": self.requests_per_minute,
            "burst_limit": self.burst_limit,
            "reason": "allowed",
            "reset_time": now + 60
        }
    
    async def get_client_info(self, client_id: str) -> Dict[str, Any]:
        """Get detailed client rate limit information."""
        if self.redis_client:
            key = f"{self.key_prefix}{client_id}"
            try:
                now = time.time()
                
                # Get current request count
                await self.redis_client.zremrangebyscore(key, "-inf", now - 60)
                current_count = await self.redis_client.zcard(key)
                recent_count = await self.redis_client.zcount(key, now - 1, now)
                
                return {
                    "client_id": client_id,
                    "current_count": current_count,
                    "recent_count": recent_count,
                    "limit": self.requests_per_minute,
                    "burst_limit": self.burst_limit,
                    "remaining": max(0, self.requests_per_minute - current_count),
                    "reset_time": now + 60
                }
            except Exception as e:
                logger.error(f"Redis client info error: {e}")
        
        # Fallback
        if client_id in self.fallback_clients:
            client_data = self.fallback_clients[client_id]
            now = time.time()
            
            # Clean old requests
            minute_ago = now - 60
            client_data["requests"] = [
                req_time for req_time in client_data["requests"]
                if req_time > minute_ago
            ]
            
            current_count = len(client_data["requests"])
            recent_count = sum(1 for req_time in client_data["requests"] if req_time > now - 1)
            
            return {
                "client_id": client_id,
                "current_count": current_count,
                "recent_count": recent_count,
                "limit": self.requests_per_minute,
                "burst_limit": self.burst_limit,
                "remaining": max(0, self.requests_per_minute - current_count),
                "reset_time": now + 60
            }
        
        return {
            "client_id": client_id,
            "current_count": 0,
            "recent_count": 0,
            "limit": self.requests_per_minute,
            "burst_limit": self.burst_limit,
            "remaining": self.requests_per_minute,
            "reset_time": time.time() + 60
        }


# Global instances
_cache = DistributedCache()
_rate_limiter = DistributedRateLimiter()


async def init_distributed_systems(redis_url: str = "redis://localhost:6379"):
    """Initialize distributed cache and rate limiter."""
    global _cache, _rate_limiter
    
    _cache = DistributedCache(redis_url)
    _rate_limiter = DistributedRateLimiter(redis_url)
    
    await _cache.connect()
    await _rate_limiter.connect()


async def get_cache() -> DistributedCache:
    """Get the global cache instance."""
    return _cache


async def get_rate_limiter() -> DistributedRateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter


async def cache_get(key: str) -> Optional[Any]:
    """Get value from distributed cache."""
    return await _cache.get(key)


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in distributed cache."""
    return await _cache.set(key, value, ttl)


async def cache_delete(key: str) -> bool:
    """Delete value from distributed cache."""
    return await _cache.delete(key)


async def rate_limit_check(client_id: str) -> Dict[str, Any]:
    """Check if client is rate limited."""
    return await _rate_limiter.is_allowed(client_id)


async def get_system_stats() -> Dict[str, Any]:
    """Get comprehensive system statistics."""
    cache_stats = await _cache.get_stats()
    
    return {
        "cache": cache_stats,
        "rate_limiter": {
            "redis_connected": _rate_limiter.redis_client is not None,
            "fallback_clients": len(_rate_limiter.fallback_clients)
        },
        "redis_available": REDIS_AVAILABLE
    }
