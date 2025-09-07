"""
Experience matching service
"""

import logging
from typing import Optional

from config.settings import Config

logger = logging.getLogger(__name__)


class ExperienceMatcher:
    """Experience level matching service"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def calculate_match(
        self,
        candidate_experience: int,
        min_required_experience: int,
        max_required_experience: int
    ) -> float:
        """
        Calculate experience match score
        
        Args:
            candidate_experience: Candidate's years of experience
            min_required_experience: Minimum required experience
            max_required_experience: Maximum required experience
            
        Returns:
            Match score between 0.0 and 1.0
        """
        if min_required_experience <= candidate_experience <= max_required_experience:
            return 1.0  # Perfect match
        
        elif candidate_experience < min_required_experience:
            # Under-qualified: calculate penalty
            gap = min_required_experience - candidate_experience
            penalty = gap * self.config.experience_penalty_per_year
            return max(0.0, 1.0 - penalty)
        
        else:
            # Over-qualified: calculate penalty
            excess = candidate_experience - max_required_experience
            penalty = excess * self.config.over_experience_penalty
            return max(0.7, 1.0 - penalty)  # Minimum 0.7 for over-qualified
    
    def get_experience_level(self, years: int) -> str:
        """Get experience level description"""
        if years < 2:
            return "Junior"
        elif years < 5:
            return "Mid-level"
        elif years < 8:
            return "Senior"
        else:
            return "Lead/Principal"
    
    def is_experience_appropriate(
        self,
        candidate_experience: int,
        min_required: int,
        max_required: int
    ) -> bool:
        """Check if experience level is appropriate for the role"""
        return min_required <= candidate_experience <= max_required
