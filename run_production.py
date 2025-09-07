#!/usr/bin/env python3
"""
Production run script for the FastAPI application.
This script sets up environment variables and starts the application.
"""

import os
import sys
from pathlib import Path

# Set production environment variables
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('SECRET_KEY', 'your-production-secret-key-here-change-this')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '30')
os.environ.setdefault('DATABASE_URL', 'sqlite:///./app.db')
os.environ.setdefault('CORS_ORIGINS', '*')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('MAX_FILE_SIZE_MB', '10')

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    try:
        # Import and run the application
        from app.main import app
        import uvicorn
        
        print("🚀 Starting production server...")
        print(f"📁 Working directory: {current_dir}")
        print(f"🔧 Environment: {os.environ.get('ENVIRONMENT', 'production')}")
        
        # Run the application
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

