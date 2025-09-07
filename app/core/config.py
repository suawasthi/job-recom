from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Database settings
    database_url: str = "sqlite:///./app.db"
    
    # JWT settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",      # React default
        "http://localhost:4200",      # Angular default
        "http://localhost:8080",      # Vue default
        "http://127.0.0.1:4200",      # Angular alternative
        "http://127.0.0.1:3000",      # React alternative
        "http://localhost:4200",      # Angular development server (explicit)
        "https://5705d9dc3a2f.ngrok-free.app",  # Your ngrok URL
        "https://*.ngrok-free.app",   # All ngrok URLs
        "http://job-recomedation-ai.s3-website.eu-north-1.amazonaws.com",  # Your AWS S3 frontend
        "https://job-recomedation-ai.s3-website.eu-north-1.amazonaws.com",  # HTTPS version
        "http://*.s3-website.eu-north-1.amazonaws.com",  # All AWS S3 websites in this region
        "https://*.s3-website.eu-north-1.amazonaws.com",  # HTTPS version
        "http://15.206.120.107:4200",  # Your EC2 Angular server
        "https://15.206.120.107:4200",  # HTTPS version
    ]
    
    # Environment-specific CORS origins
    @property
    def allowed_origins(self) -> List[str]:
        """Get allowed origins based on environment"""
        env = os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            # In production, only allow specific domains
            return [
                "https://your-production-domain.com",
                "https://www.your-production-domain.com",
                "http://job-recomedation-ai.s3-website.eu-north-1.amazonaws.com",
                "https://job-recomedation-ai.s3-website.eu-north-1.amazonaws.com",
                "http://localhost:4200",  # Angular development server
                "http://127.0.0.1:4200",  # Angular alternative
                "http://15.206.120.107:4200",  # Your EC2 Angular server
                "https://15.206.120.107:4200",  # HTTPS version
                "http://localhost:4200", 
                self.cors_origins
            ]
        elif env == "staging":
            # In staging, allow staging domains
            return [
                "https://staging.your-domain.com",
                "https://*.ngrok-free.app", 
                self.cors_origins # For testing
            ]
        else:
            # In development, allow all localhost and ngrok URLs
            return self.cors_origins
    
    # File upload settings
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["pdf", "doc", "docx", "txt"]
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "AI Job Platform API"
    version: str = "1.0.0"
    
    # Security settings
    debug: bool = True
    
    # Legacy field mappings (for backward compatibility)
    max_file_size_mb: Optional[int] = 10  # 10MB default
    api_v1_str: Optional[str] = None
    log_level: Optional[str] = None
    allowed_origins_legacy: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from environment variables
        env_file_encoding = 'utf-8'
        case_sensitive = False

settings = Settings()

