#!/usr/bin/env python3
"""
Startup script for AI Job Platform API
This script provides different ways to start the server based on environment
"""

import os
import sys
import argparse
from pathlib import Path

def start_development_server():
    """Start the server in development mode with auto-reload"""
    print("🚀 Starting AI Job Platform API in DEVELOPMENT mode...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("🔄 Auto-reload enabled")
    
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

def start_production_server():
    """Start the server in production mode with Gunicorn"""
    print("🚀 Starting AI Job Platform API in PRODUCTION mode...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("🔧 Using Gunicorn with optimized settings")
    
    import subprocess
    import sys
    
    # Build the gunicorn command
    cmd = [
        sys.executable, "-m", "gunicorn",
        "--config", "gunicorn.conf.py",
        "wsgi:application"
    ]
    
    # Run gunicorn
    subprocess.run(cmd)

def start_uvicorn_production():
    """Start the server in production mode with Uvicorn"""
    print("🚀 Starting AI Job Platform API in PRODUCTION mode...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("🔧 Using Uvicorn with production settings")
    
    import uvicorn
    
    # Get configuration from environment
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    workers = int(os.environ.get("WORKERS", 1))
    
    uvicorn.run(
        "wsgi:application",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        log_level="info"
    )

def main():
    parser = argparse.ArgumentParser(description="Start AI Job Platform API")
    parser.add_argument(
        "--mode",
        choices=["dev", "prod", "uvicorn-prod"],
        default="dev",
        help="Server mode: dev (development), prod (production with Gunicorn), uvicorn-prod (production with Uvicorn)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["HOST"] = args.host
    os.environ["PORT"] = str(args.port)
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    print("=" * 60)
    print("🎯 AI Job Platform API")
    print("=" * 60)
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🏭 Mode: {args.mode}")
    print("=" * 60)
    
    try:
        if args.mode == "dev":
            start_development_server()
        elif args.mode == "prod":
            start_production_server()
        elif args.mode == "uvicorn-prod":
            start_uvicorn_production()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

