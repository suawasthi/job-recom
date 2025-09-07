"""
Gunicorn configuration file for production deployment
This file provides optimized settings for serving the FastAPI application
"""

import os
import multiprocessing

# Server socket
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
backlog = 2048

# Worker processes
workers = os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ai-job-platform-api"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure for HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Server hooks
def on_starting(server):
    server.log.info("🚀 Starting AI Job Platform API with Gunicorn")

def on_reload(server):
    server.log.info("🔄 Reloading AI Job Platform API")

def worker_int(worker):
    worker.log.info("👷 Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("🔧 Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("✅ Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("🎯 Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("💥 Worker aborted (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("🔄 Forked child, re-executing.")

def when_ready(server):
    server.log.info("✅ Server is ready. Spawning workers")

def worker_exit(server, worker):
    server.log.info("👋 Worker exited (pid: %s)", worker.pid)

def on_exit(server):
    server.log.info("👋 Server exiting")

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning
preload_app = True
sendfile = True
reuse_port = True

# Environment variables
raw_env = [
    "PYTHONPATH=/app",
    "ENVIRONMENT=production"
]

