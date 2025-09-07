"""
WSGI entry point for production deployment
This file allows the FastAPI application to be served by WSGI servers like Gunicorn
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app from the main module
from app.main import app

# For WSGI servers that expect a callable named 'application'
application = app

# Alternative: If you need to use the ASGI app directly with WSGI
# from fastapi.middleware.wsgi import WSGIMiddleware
# from starlette.applications import Starlette
# 
# # Create a WSGI wrapper for the FastAPI app
# wsgi_app = WSGIMiddleware(app)
# application = wsgi_app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting AI Job Platform API on {host}:{port}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "wsgi:application",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        workers=1      # For WSGI compatibility
    )
