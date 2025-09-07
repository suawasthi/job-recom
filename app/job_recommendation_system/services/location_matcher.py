"""
Location matching service
"""

import logging
from typing import Optional

from config.settings import Config

logger = logging.getLogger(__name__)


class LocationMatcher:
    """Location matching service"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def calculate_match(
        self,
        candidate_location: str,
        job_location: str,
        remote_work_allowed: str,
        candidate_remote_preference: float
    ) -> float:
        """
        Calculate location match score
        
        Args:
            candidate_location: Candidate's current location
            job_location: Job location
            remote_work_allowed: Remote work policy (no, hybrid, yes)
            candidate_remote_preference: Candidate's remote preference (0-1)
            
        Returns:
            Match score between 0.0 and 1.0
        """
        remote_work_allowed = remote_work_allowed.lower()
        
        # Perfect match for remote work
        if remote_work_allowed in ['yes', 'remote', 'fully remote']:
            return self.config.remote_work_score
        
        # Same location
        if self._is_same_location(candidate_location, job_location):
            return self.config.same_location_score
        
        # Hybrid work
        if remote_work_allowed in ['hybrid', 'partial remote']:
            return self.config.hybrid_work_score
        
        # Different locations - calculate proximity penalty
        proximity_score = self._calculate_proximity_score(candidate_location, job_location)
        return max(self.config.relocation_penalty, proximity_score)
    
    def _is_same_location(self, location1: str, location2: str) -> bool:
        """Check if two locations are the same"""
        if not location1 or not location2:
            return False
        
        # Normalize locations
        loc1 = location1.lower().strip()
        loc2 = location2.lower().strip()
        
        # Exact match
        if loc1 == loc2:
            return True
        
        # Check for city matches (e.g., "San Francisco" vs "San Francisco, CA")
        city1 = loc1.split(',')[0].strip()
        city2 = loc2.split(',')[0].strip()
        
        return city1 == city2
    
    def _calculate_proximity_score(self, location1: str, location2: str) -> float:
        """Calculate proximity score between two locations"""
        # This is a simplified implementation
        # In a real system, you would use geocoding and distance calculation
        
        if not location1 or not location2:
            return 0.0
        
        # Check if same state/region
        state1 = self._extract_state(location1)
        state2 = self._extract_state(location2)
        
        if state1 and state2 and state1 == state2:
            return 0.6  # Same state
        
        # Check if same country
        country1 = self._extract_country(location1)
        country2 = self._extract_country(location2)
        
        if country1 and country2 and country1 == country2:
            return 0.4  # Same country
        
        return 0.2  # Different country
    
    def _extract_state(self, location: str) -> Optional[str]:
        """Extract state from location string"""
        parts = location.split(',')
        if len(parts) > 1:
            return parts[1].strip().lower()
        return None
    
    def _extract_country(self, location: str) -> Optional[str]:
        """Extract country from location string"""
        parts = location.split(',')
        if len(parts) > 2:
            return parts[2].strip().lower()
        return None
    
    def is_remote_friendly(self, remote_work_allowed: str) -> bool:
        """Check if job supports remote work"""
        return remote_work_allowed.lower() in ['yes', 'hybrid', 'remote', 'fully remote']
    
    def get_location_compatibility(
        self,
        candidate_location: str,
        job_location: str,
        remote_work_allowed: str
    ) -> str:
        """Get human-readable location compatibility description"""
        if self.is_remote_friendly(remote_work_allowed):
            return "Remote work supported"
        elif self._is_same_location(candidate_location, job_location):
            return "Same location"
        else:
            return "Relocation required"
