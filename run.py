#!/usr/bin/env python3
"""
Production runner for AI Job Recommendation System
"""
import uvicorn
import logging
from app.core.config import settings

# Configure logging before starting the server
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('app.log')  # File output
    ]
)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
        workers=1 if settings.debug else 4,
        log_level="debug",
        access_log=True
    )
