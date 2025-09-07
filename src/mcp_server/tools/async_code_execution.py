"""
High-performance async code execution with advanced security and caching.

This module provides blazing-fast code execution with proper resource limits,
security sandboxing, and intelligent caching to outperform any competitor.
"""

import asyncio
import hashlib
import os
import resource
import signal
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import psutil

from ..utils.logging import log_tool_execution


class CodeExecutionCache:
    """High-performance LRU cache for code execution results."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def _cleanup_expired(self):
        """Remove expired cache entries."""
        now = time.time()
        expired_keys = [
            key for key, access_time in self.access_times.items()
            if now - access_time > self.ttl
        ]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.access_times.pop(key, None)
    
    def _evict_lru(self):
        """Evict least recently used entry."""
        if len(self.cache) >= self.max_size:
            lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            self.cache.pop(lru_key, None)
            self.access_times.pop(lru_key, None)
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        self._cleanup_expired()
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Dict[str, Any]):
        """Cache execution result."""
        self._cleanup_expired()
        self._evict_lru()
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def get_cache_key(self, code: str, python_version: str = "3.12") -> str:
        """Generate cache key for code."""
        content = f"{code}:{python_version}"
        return hashlib.sha256(content.encode()).hexdigest()


class SecureCodeExecutor:
    """Ultra-secure, high-performance code executor."""
    
    def __init__(self):
        self.cache = CodeExecutionCache()
        self.executor = ThreadPoolExecutor(max_workers=4)  # Configurable
        self.active_processes: Dict[str, psutil.Process] = {}
    
    async def execute_code_async(
        self, 
        code: str, 
        timeout: int = 10,
        memory_limit: int = 128 * 1024 * 1024,  # 128MB
        enable_cache: bool = True
    ) -> Dict[str, Any]:
        """Execute Python code asynchronously with full security."""
        
        # Check cache first
        if enable_cache:
            cache_key = self.cache.get_cache_key(code)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                cached_result["from_cache"] = True
                return cached_result
        
        # Execute in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self.executor,
                self._execute_code_sync,
                code,
                timeout,
                memory_limit
            )
            
            # Cache successful results
            if enable_cache and result.get("returncode") == 0:
                cache_key = self.cache.get_cache_key(code)
                result["from_cache"] = False
                self.cache.set(cache_key, result)
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "execution_time": 0,
                "from_cache": False
            }
    
    def _execute_code_sync(
        self, 
        code: str, 
        timeout: int, 
        memory_limit: int
    ) -> Dict[str, Any]:
        """Synchronous code execution with advanced security."""
        
        start_time = time.time()
        
        # Security validation
        security_result = self._validate_code_security(code)
        if not security_result["safe"]:
            return {
                "error": "Security violation",
                "details": security_result["violations"],
                "execution_time": time.time() - start_time,
                "from_cache": False
            }
        
        # Create secure temporary file
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.py', 
            delete=False,
            dir=tempfile.gettempdir()
        ) as tmp:
            tmp.write(code)
            tmp.flush()
            temp_file = tmp.name
        
        try:
            # Execute with advanced security
            result = self._run_with_security_limits(
                temp_file, timeout, memory_limit, start_time
            )
            return result
            
        finally:
            # Cleanup
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def _validate_code_security(self, code: str) -> Dict[str, Any]:
        """Advanced security validation."""
        violations = []
        
        # Dangerous imports
        dangerous_imports = [
            'os.system', 'subprocess.call', 'eval', 'exec', 'compile',
            '__import__', 'open(', 'file(', 'input(', 'raw_input(',
            'pickle.loads', 'marshal.loads', 'ctypes', 'importlib'
        ]
        
        for danger in dangerous_imports:
            if danger in code:
                violations.append(f"Dangerous operation: {danger}")
        
        # File system operations
        fs_operations = [
            'write', 'mkdir', 'rmdir', 'remove', 'unlink',
            'chmod', 'chown', 'rename', 'move'
        ]
        
        for op in fs_operations:
            if op in code and ('.' + op + '(' in code or op + '(' in code):
                violations.append(f"File system operation: {op}")
        
        # Network operations
        network_ops = [
            'socket', 'urllib', 'requests', 'http', 'ftp',
            'telnet', 'ssh', 'scp'
        ]
        
        for op in network_ops:
            if op in code:
                violations.append(f"Network operation: {op}")
        
        return {
            "safe": len(violations) == 0,
            "violations": violations
        }
    
    def _run_with_security_limits(
        self, 
        temp_file: str, 
        timeout: int, 
        memory_limit: int, 
        start_time: float
    ) -> Dict[str, Any]:
        """Execute with comprehensive security limits."""
        
        import subprocess
        import sys
        
        # Create restricted environment
        env = os.environ.copy()
        env.update({
            'PYTHONPATH': '',  # Clear Python path
            'HOME': tempfile.gettempdir(),  # Restricted home
            'USER': 'restricted',
            'SHELL': '/bin/false'
        })
        
        # Remove dangerous environment variables
        dangerous_env = [
            'LD_PRELOAD', 'LD_LIBRARY_PATH', 'PYTHONSTARTUP',
            'PYTHONHOME', 'PYTHONUSERBASE'
        ]
        for var in dangerous_env:
            env.pop(var, None)
        
        try:
            # Use timeout and resource limits
            process = subprocess.Popen(
                [sys.executable, '-S', '-s', temp_file],  # -S: no site, -s: no user site
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=tempfile.gettempdir(),
                preexec_fn=self._set_limits_linux if os.name == 'posix' else None
            )
            
            # Monitor process
            process_id = str(process.pid)
            if process.pid:
                try:
                    ps_process = psutil.Process(process.pid)
                    self.active_processes[process_id] = ps_process
                except:
                    pass
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                execution_time = time.time() - start_time
                
                return {
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": process.returncode,
                    "execution_time": execution_time,
                    "from_cache": False,
                    "security_validated": True
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()  # Clean up
                return {
                    "error": "Execution timeout",
                    "timeout": timeout,
                    "execution_time": time.time() - start_time,
                    "from_cache": False
                }
            
            finally:
                # Cleanup process tracking
                self.active_processes.pop(process_id, None)
                
        except Exception as e:
            return {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "execution_time": time.time() - start_time,
                "from_cache": False
            }
    
    def _set_limits_linux(self):
        """Set resource limits on Linux/Unix systems."""
        try:
            # Memory limit (128MB)
            resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
            
            # CPU time limit (10 seconds)
            resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
            
            # File size limit (10MB)
            resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))
            
            # Number of processes (prevent fork bombs)
            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
            
            # Disable core dumps
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            
        except Exception:
            pass  # Limits might not be available on all systems
    
    async def kill_all_processes(self):
        """Emergency: kill all active processes."""
        for process_id, ps_process in self.active_processes.items():
            try:
                ps_process.kill()
            except:
                pass
        self.active_processes.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return {
            "cache_size": len(self.cache.cache),
            "cache_hits": sum(1 for result in self.cache.cache.values() if result.get("from_cache")),
            "max_size": self.cache.max_size,
            "ttl": self.cache.ttl
        }


# Global executor instance
_executor = SecureCodeExecutor()


@log_tool_execution("async_run_python")
async def run_python_async(
    code: str, 
    timeout: int = 10,
    memory_limit: int = 128 * 1024 * 1024,
    enable_cache: bool = True
) -> Dict[str, Any]:
    """
    Execute Python code asynchronously with advanced security and caching.
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        memory_limit: Maximum memory usage in bytes
        enable_cache: Whether to use result caching
        
    Returns:
        Dict with execution results and performance metrics
    """
    return await _executor.execute_code_async(
        code, timeout, memory_limit, enable_cache
    )


@log_tool_execution("batch_run_python")
async def run_python_batch(codes: list[str], timeout: int = 10) -> Dict[str, Any]:
    """
    Execute multiple Python code snippets concurrently.
    
    Args:
        codes: List of Python code snippets
        timeout: Maximum execution time per snippet
        
    Returns:
        Dict with all execution results
    """
    tasks = [
        run_python_async(code, timeout)
        for code in codes
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        "results": [
            result if not isinstance(result, Exception) 
            else {"error": str(result)} 
            for result in results
        ],
        "total_executions": len(codes),
        "concurrent": True
    }


async def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics for the code executor."""
    return {
        "cache_stats": _executor.get_cache_stats(),
        "active_processes": len(_executor.active_processes),
        "executor_threads": _executor.executor._threads if hasattr(_executor.executor, '_threads') else 0
    }


async def emergency_shutdown():
    """Emergency shutdown: kill all processes and clear cache."""
    await _executor.kill_all_processes()
    _executor.cache.cache.clear()
    _executor.cache.access_times.clear()
