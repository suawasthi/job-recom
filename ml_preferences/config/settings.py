from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class MLPreferencesSettings(BaseSettings):
    # Database settings (same as main API)
    database_url: str = "sqlite:///./app.db"
    
    # ML Model settings
    min_feedback_threshold: int = 10  # Minimum feedback actions to train model
    max_feedback_threshold: int = 1000  # Maximum feedback actions to use
    model_retrain_frequency: str = "daily"  # daily, weekly, monthly
    model_type: str = "logistic_regression"  # Model type
    
    # Feature settings
    skill_features: List[str] = [
        "python", "react", "aws", "docker", "kubernetes", "javascript",
        "typescript", "nodejs", "django", "flask", "fastapi", "postgresql",
        "mongodb", "redis", "git", "linux", "agile", "scrum", "java",
        "spring", "angular", "vue", "sql", "mysql", "elasticsearch"
    ]
    
    location_features: List[str] = ["remote", "hybrid", "office"]
    job_type_features: List[str] = ["full_time", "part_time", "contract", "freelance"]
    
    # Model settings (Logistic Regression)
    logistic_regression_C: float = 1.0  # Regularization strength
    logistic_regression_max_iter: int = 1000  # Maximum iterations
    logistic_regression_class_weight: str = 'balanced'  # Handle class imbalance
    
    # Weight adjustment settings
    max_weight_adjustment: float = 2.0  # Maximum weight multiplier
    min_weight_adjustment: float = 0.1  # Minimum weight multiplier
    weight_smoothing_factor: float = 0.1  # Smoothing for weight updates
    
    # New user handling
    new_user_default_boost: float = 1.2  # Default boost for new users
    new_user_learning_rate: float = 0.3  # How quickly new users learn
    new_user_min_feedback: int = 3  # Minimum feedback before any adjustments
    
    # Fallback strategy
    use_statistical_correlation: bool = True  # Use correlation for limited data
    correlation_threshold: float = 0.3  # Minimum correlation to apply
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "ml_preferences.log"
    
    # Debug settings
    debug_mode: bool = True
    save_model_artifacts: bool = True
    model_artifacts_dir: str = "models/artifacts"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = MLPreferencesSettings()
