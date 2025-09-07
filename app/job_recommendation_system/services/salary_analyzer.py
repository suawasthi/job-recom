"""
Salary analysis service
"""

import logging
from typing import Optional

from config.settings import Config

logger = logging.getLogger(__name__)


class SalaryAnalyzer:
    """Salary matching and analysis service"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def calculate_match(
        self,
        candidate_expectation: float,
        job_min_salary: float,
        job_max_salary: float
    ) -> float:
        """
        Calculate salary match score
        
        Args:
            candidate_expectation: Candidate's salary expectation
            job_min_salary: Job's minimum salary
            job_max_salary: Job's maximum salary
            
        Returns:
            Match score between 0.0 and 1.0
        """
        if not candidate_expectation or (not job_min_salary and not job_max_salary):
            return 1.0  # No salary information available
        
        # Use job_max_salary if min is not available
        if not job_min_salary:
            job_min_salary = job_max_salary * 0.8
        
        # Use job_min_salary if max is not available
        if not job_max_salary:
            job_max_salary = job_min_salary * 1.2
        
        # Perfect match if expectation is within range
        if job_min_salary <= candidate_expectation <= job_max_salary:
            return 1.0
        
        # Candidate expects less than minimum (good for employer)
        elif candidate_expectation < job_min_salary:
            return 1.0
        
        # Candidate expects more than maximum
        else:
            excess_ratio = (candidate_expectation - job_max_salary) / job_max_salary
            penalty = min(0.7, excess_ratio * 1.5)  # Cap penalty at 0.7
            return max(0.3, 1.0 - penalty)
    
    def get_salary_competitiveness(
        self,
        candidate_expectation: float,
        job_min_salary: float,
        job_max_salary: float
    ) -> str:
        """Get salary competitiveness description"""
        if not candidate_expectation or (not job_min_salary and not job_max_salary):
            return "Unknown"
        
        if not job_min_salary:
            job_min_salary = job_max_salary * 0.8
        if not job_max_salary:
            job_max_salary = job_min_salary * 1.2
        
        if candidate_expectation < job_min_salary:
            return "Below market"
        elif candidate_expectation <= job_max_salary:
            return "Competitive"
        else:
            return "Above market"
    
    def calculate_salary_gap(
        self,
        candidate_expectation: float,
        job_min_salary: float,
        job_max_salary: float
    ) -> Optional[float]:
        """Calculate salary gap percentage"""
        if not candidate_expectation or (not job_min_salary and not job_max_salary):
            return None
        
        if not job_min_salary:
            job_min_salary = job_max_salary * 0.8
        if not job_max_salary:
            job_max_salary = job_min_salary * 1.2
        
        if candidate_expectation < job_min_salary:
            return ((job_min_salary - candidate_expectation) / candidate_expectation) * 100
        elif candidate_expectation > job_max_salary:
            return ((candidate_expectation - job_max_salary) / job_max_salary) * 100
        else:
            return 0.0  # Within range
