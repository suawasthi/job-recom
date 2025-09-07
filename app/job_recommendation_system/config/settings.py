"""
Configuration settings for the Job Recommendation System
"""

from dataclasses import dataclass
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Main configuration class for the job recommendation system"""
    
    # Scoring weights
    skill_weight: float = 0.30
    experience_weight: float = 0.20
    location_weight: float = 0.15
    career_growth_weight: float = 0.10
    salary_weight: float = 0.05
    market_demand_weight: float = 0.10
    culture_weight: float = 0.10
    
    # Thresholds
    min_match_score: float = 0.6
    min_confidence_score: float = 0.7
    max_results: int = 20
    
    # Skill matching
    skill_similarity_threshold: float = 0.8
    transferable_skill_threshold: float = 0.6
    
    # Experience matching
    experience_penalty_per_year: float = 0.15
    over_experience_penalty: float = 0.05
    
    # Location matching
    remote_work_score: float = 1.0
    same_location_score: float = 1.0
    hybrid_work_score: float = 0.8
    relocation_penalty: float = 0.3
    
    # Career growth
    senior_level_keywords: list = None
    junior_level_keywords: list = None
    
    # Market analysis
    market_demand_cache_duration: int = 3600  # 1 hour
    urgency_weight: float = 0.3
    
    # Embeddings
    embedding_dimension: int = 768
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # API settings
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance settings
    enable_caching: bool = True
    enable_semantic_matching: bool = True
    enable_explanations: bool = True
    fast_mode: bool = False  # Skip expensive operations for testing

    # Cache settings
    max_cache_size: int = 1000
    cache_ttl_seconds: int = 3600  # 1 hour

    # Database settings
    sqlite_db_path: str = "job_recommendation.db"
    enable_sqlite_persistence: bool = True

    # FAISS settings
    enable_faiss_ivf: bool = True  # Use IVF index for better performance
    expected_jobs: int = 10000  # Expected number of jobs for FAISS optimization
    expected_resumes: int = 5000  # Expected number of resumes for FAISS optimization
    faiss_index_path: str = "faiss_indices"  # Path to save FAISS indices
    
    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        if self.senior_level_keywords is None:
            self.senior_level_keywords = ['senior', 'lead', 'principal', 'staff', 'architect']
        
        if self.junior_level_keywords is None:
            self.junior_level_keywords = ['junior', 'entry', 'associate', 'trainee', 'intern']
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables"""
        return cls(
            skill_weight=float(os.getenv('SKILL_WEIGHT', 0.30)),
            experience_weight=float(os.getenv('EXPERIENCE_WEIGHT', 0.20)),
            location_weight=float(os.getenv('LOCATION_WEIGHT', 0.15)),
            career_growth_weight=float(os.getenv('CAREER_GROWTH_WEIGHT', 0.10)),
            salary_weight=float(os.getenv('SALARY_WEIGHT', 0.05)),
            market_demand_weight=float(os.getenv('MARKET_DEMAND_WEIGHT', 0.10)),
            min_match_score=float(os.getenv('MIN_MATCH_SCORE', 0.6)),
            min_confidence_score=float(os.getenv('MIN_CONFIDENCE_SCORE', 0.7)),
            max_results=int(os.getenv('MAX_RESULTS', 20)),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'skill_weight': self.skill_weight,
            'experience_weight': self.experience_weight,
            'location_weight': self.location_weight,
            'career_growth_weight': self.career_growth_weight,
            'salary_weight': self.salary_weight,
            'market_demand_weight': self.market_demand_weight,
            'min_match_score': self.min_match_score,
            'min_confidence_score': self.min_confidence_score,
            'max_results': self.max_results
        }
