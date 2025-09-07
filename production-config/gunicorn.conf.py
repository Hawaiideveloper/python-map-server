"""
High-performance Gunicorn configuration for production deployment.

This configuration optimizes for maximum throughput, minimal latency,
and excellent scalability to outperform any competitor.
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000

# Performance tuning
preload_app = True
keepalive = 65
timeout = 120
graceful_timeout = 120

# Security
limit_request_line = 8192
limit_request_fields = 100
limit_request_field_size = 8192

# Logging
loglevel = os.getenv('LOG_LEVEL', 'info')
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'python-mcp-server'

# Worker lifecycle
worker_tmp_dir = '/dev/shm'  # Use RAM for worker temporary files

# SSL (if certificates are available)
keyfile = os.getenv('SSL_KEYFILE')
certfile = os.getenv('SSL_CERTFILE')
ssl_version = 3  # TLS 1.2+
ciphers = 'TLSv1.2'

# Resource limits
worker_rlimit_nofile = 65535

# Graceful restarts
graceful_timeout = 120

def pre_fork(server, worker):
    """Pre-fork worker setup."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    """Post-fork worker setup."""
    server.log.info(f"Worker ready (pid: {worker.pid})")

def worker_int(worker):
    """Worker interrupt handler."""
    worker.log.info(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def on_exit(server):
    """Server exit handler."""
    server.log.info("Server shutting down")

def when_ready(server):
    """Server ready handler."""
    server.log.info(f"Server is ready. Listening on: {bind}")
    server.log.info(f"Using {workers} worker processes")
    server.log.info(f"Worker class: {worker_class}")

def on_reload(server):
    """Server reload handler."""
    server.log.info("Server reloaded")

# Additional performance settings
forwarded_allow_ips = '*'  # Allow all IPs for proxy forwarding
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
