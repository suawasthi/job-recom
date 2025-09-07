"""
WORKING FastAPI Main Application
This file actually registers all routers and endpoints
Replace your main.py with this content
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
import os
import logging
from datetime import timedelta
from typing import List, Optional
from app.api import resume
from app.api.jobs import router as jobs_router  # Your real router!
from app.api.auth import router as auth_router
from app.api.resume import router as resume_router
from app.api.analytics import router as analytics_router

# Import all models to ensure they are registered with Base
from app.models.user import User
from app.models.job import Job, JobApplication
from app.models.resume import Resume
from app.models.user_preferences import UserJobPreferences, JobComparison, JobComparisonItem

from app.core.config import settings
from datetime import datetime

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('app.log')  # File output
    ]
)

# Set specific loggers to appropriate levels
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("app").setLevel(logging.WARNING)  # Only warnings and errors

# =============================================================================
# MAIN APPLICATION
# =============================================================================

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="AI-Powered Job Recommendation Platform API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =============================================================================
# CORS MIDDLEWARE
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# ROUTERS
# =============================================================================

# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(jobs_router)
app.include_router(resume_router)
app.include_router(analytics_router)

# =============================================================================
# ROOT ENDPOINT
# =============================================================================

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to AI Job Recommendation Platform API",
        "version": settings.version,
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "active"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.version
    }

# =============================================================================
# STARTUP AND SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting AI Job Recommendation Platform API...")
    logger.info(f"📊 API Version: {settings.version}")
    logger.info(f"🌐 CORS Origins: {len(settings.allowed_origins)} configured")
    logger.info("✅ API is ready to serve requests!")
    print("🚀 Starting AI Job Recommendation Platform API...")
    print(f"📊 API Version: {settings.version}")
    print(f"🌐 CORS Origins: {len(settings.allowed_origins)} configured")
    print("✅ API is ready to serve requests!")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    print("🛑 Shutting down AI Job Recommendation Platform API...")
    print("✅ API shutdown complete!")

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Endpoint not found: {request.url.path}",
            "available_endpoints": [
                "/docs", "/", "/health",
                "/api/v1/auth/register", "/api/v1/auth/token", "/api/v1/auth/me",
                "/api/v1/resumes/", "/api/v1/resumes/upload", "/api/v1/resumes/{id}",
                "/api/v1/jobs/", "/api/v1/jobs/recommendations", "/api/v1/jobs/search", 
                "/api/v1/jobs/{id}/apply", "/api/v1/jobs/{id}",
                "/api/v1/analytics/trends", "/api/v1/analytics/platform"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,  
        reload=True,
        log_level="info"
    )
