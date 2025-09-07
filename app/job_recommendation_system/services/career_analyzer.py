"""
Career growth analysis service
"""

import logging
from typing import Dict, Any

from config.settings import Config
from models.candidate import CandidateProfile
from models.job import JobPosting

logger = logging.getLogger(__name__)


class CareerAnalyzer:
    """Career growth and progression analysis"""
    
    def __init__(self, config: Config):
        self.config = config
        self.career_paths = self._load_career_paths()
    
    def calculate_growth_potential(
        self,
        candidate_profile: CandidateProfile,
        job_posting: JobPosting
    ) -> float:
        """
        Calculate career growth potential for the candidate in this role
        
        Args:
            candidate_profile: Candidate's profile
            job_posting: Job posting details
            
        Returns:
            Growth potential score between 0.0 and 1.0
        """
        # Check if it's a logical career progression
        progression_score = self._check_career_progression(
            candidate_profile.current_role,
            job_posting.title
        )
        
        # Check experience level appropriateness
        level_score = self._check_level_appropriateness(
            candidate_profile.career_level,
            job_posting
        )
        
        # Check if it's a step up
        advancement_score = self._check_advancement_potential(
            candidate_profile.experience_years,
            job_posting.min_experience_years,
            job_posting.max_experience_years
        )
        
        # Weighted combination
        growth_score = (
            progression_score * 0.4 +
            level_score * 0.3 +
            advancement_score * 0.3
        )
        
        return min(1.0, growth_score)
    
    def _check_career_progression(self, current_role: str, target_role: str) -> float:
        """Check if target role is a logical progression from current role"""
        current_lower = current_role.lower()
        target_lower = target_role.lower()
        
        # Check if current role has defined career paths
        if current_lower in self.career_paths:
            next_roles = [role.lower() for role in self.career_paths[current_lower]]
            if any(target in target_lower for target in next_roles):
                return 0.9  # Excellent progression
        
        # Check for common progression patterns
        progression_patterns = [
            ('junior', 'senior'),
            ('associate', 'senior'),
            ('analyst', 'scientist'),
            ('developer', 'engineer'),
            ('engineer', 'lead'),
            ('lead', 'manager'),
            ('manager', 'director')
        ]
        
        for pattern in progression_patterns:
            if pattern[0] in current_lower and pattern[1] in target_lower:
                return 0.8  # Good progression
        
        # Check for lateral moves
        if current_lower == target_lower:
            return 0.6  # Lateral move
        
        return 0.4  # Unclear progression
    
    def _check_level_appropriateness(self, candidate_level: int, job_posting: JobPosting) -> float:
        """Check if job level is appropriate for candidate's career level"""
        job_level = self._infer_job_level(job_posting.title, job_posting.min_experience_years)
        
        if job_level == candidate_level + 1:
            return 0.9  # Perfect step up
        elif job_level == candidate_level:
            return 0.7  # Lateral move
        elif job_level == candidate_level - 1:
            return 0.5  # Step down
        else:
            return 0.3  # Significant level mismatch
    
    def _check_advancement_potential(
        self,
        candidate_experience: int,
        min_required: int,
        max_required: int
    ) -> float:
        """Check if this role represents advancement for the candidate"""
        if candidate_experience < min_required:
            return 0.9  # Clear advancement opportunity
        elif candidate_experience <= max_required:
            return 0.8  # Good advancement opportunity
        else:
            return 0.6  # May be overqualified
    
    def _infer_job_level(self, job_title: str, min_experience: int) -> int:
        """Infer job level from title and requirements"""
        title_lower = job_title.lower()
        
        # Check for senior/lead keywords
        if any(keyword in title_lower for keyword in self.config.senior_level_keywords):
            return 2
        # Check for junior/entry keywords
        elif any(keyword in title_lower for keyword in self.config.junior_level_keywords):
            return 0
        # Infer from experience requirements
        elif min_experience >= 5:
            return 2
        elif min_experience >= 2:
            return 1
        else:
            return 0
    
    def _load_career_paths(self) -> Dict[str, list]:
        """Load career progression paths"""
        return {
            'data analyst': ['Senior Data Analyst', 'Data Scientist', 'Analytics Manager'],
            'junior developer': ['Senior Developer', 'Tech Lead', 'Engineering Manager'],
            'software engineer': ['Senior Engineer', 'Tech Lead', 'Engineering Manager'],
            'data scientist': ['Senior Data Scientist', 'ML Engineer', 'Data Science Manager'],
            'product manager': ['Senior Product Manager', 'Product Director', 'VP Product'],
            'marketing specialist': ['Marketing Manager', 'Marketing Director', 'VP Marketing']
        }
    
    def get_next_career_steps(self, current_role: str) -> list:
        """Get suggested next career steps for current role"""
        return self.career_paths.get(current_role.lower(), [])
    
    def get_growth_description(self, score: float) -> str:
        """Get human-readable growth potential description"""
        if score >= 0.8:
            return "Excellent career advancement opportunity"
        elif score >= 0.6:
            return "Good growth potential"
        elif score >= 0.4:
            return "Moderate growth opportunity"
        else:
            return "Limited growth opportunity"
