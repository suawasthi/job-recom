"""
Market analysis service
"""

import logging
from typing import List, Dict, Any

from config.settings import Config

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Market demand and trend analysis"""
    
    def __init__(self, config: Config):
        self.config = config
        self.market_data = self._load_market_data()
    
    def get_market_demand(
        self,
        job_title: str,
        location: str,
        required_skills: List[str]
    ) -> float:
        """
        Get market demand score for a job
        
        Args:
            job_title: Job title
            location: Job location
            required_skills: Required skills for the job
            
        Returns:
            Market demand score between 0.0 and 1.0
        """
        # Get demand for job title
        title_demand = self._get_title_demand(job_title)
        
        # Get demand for location
        location_demand = self._get_location_demand(location)
        
        # Get demand for skills
        skills_demand = self._get_skills_demand(required_skills)
        
        # Calculate weighted average
        demand_score = (
            title_demand * 0.5 +
            location_demand * 0.3 +
            skills_demand * 0.2
        )
        
        return min(1.0, demand_score)
    
    def _get_title_demand(self, job_title: str) -> float:
        """Get demand score for job title"""
        title_lower = job_title.lower()
        
        # High demand roles
        high_demand_titles = [
            'data scientist', 'machine learning engineer', 'software engineer',
            'full stack developer', 'devops engineer', 'product manager',
            'data engineer', 'ml engineer', 'ai engineer'
        ]
        
        # Medium demand roles
        medium_demand_titles = [
            'data analyst', 'business analyst', 'frontend developer',
            'backend developer', 'qa engineer', 'project manager',
            'marketing manager', 'sales manager'
        ]
        
        if any(title in title_lower for title in high_demand_titles):
            return 0.9
        elif any(title in title_lower for title in medium_demand_titles):
            return 0.7
        else:
            return 0.5  # Default medium demand
    
    def _get_location_demand(self, location: str) -> float:
        """Get demand score for location"""
        if not location:
            return 0.5
        
        location_lower = location.lower()
        
        # High demand locations
        high_demand_locations = [
            'san francisco', 'new york', 'seattle', 'austin',
            'boston', 'los angeles', 'chicago', 'denver'
        ]
        
        # Medium demand locations
        medium_demand_locations = [
            'atlanta', 'dallas', 'phoenix', 'miami',
            'philadelphia', 'detroit', 'minneapolis'
        ]
        
        if any(loc in location_lower for loc in high_demand_locations):
            return 0.9
        elif any(loc in location_lower for loc in medium_demand_locations):
            return 0.7
        else:
            return 0.5  # Default medium demand
    
    def _get_skills_demand(self, skills: List[str]) -> float:
        """Get demand score for skills"""
        if not skills:
            return 0.5
        
        # High demand skills
        high_demand_skills = [
            'python', 'machine learning', 'javascript', 'react',
            'aws', 'docker', 'kubernetes', 'sql', 'data science'
        ]
        
        # Medium demand skills
        medium_demand_skills = [
            'java', 'c++', 'angular', 'vue', 'node.js',
            'mongodb', 'postgresql', 'git', 'jenkins'
        ]
        
        high_count = sum(1 for skill in skills if skill.lower() in high_demand_skills)
        medium_count = sum(1 for skill in skills if skill.lower() in medium_demand_skills)
        
        total_skills = len(skills)
        if total_skills == 0:
            return 0.5
        
        # Calculate weighted demand score
        demand_score = (
            (high_count * 0.9 + medium_count * 0.7) / total_skills
        )
        
        return min(1.0, demand_score)
    
    def _load_market_data(self) -> Dict[str, Any]:
        """Load market data (simplified implementation)"""
        return {
            'trending_skills': [
                'machine learning', 'python', 'aws', 'react',
                'data science', 'docker', 'kubernetes'
            ],
            'trending_locations': [
                'san francisco', 'new york', 'seattle', 'austin'
            ],
            'trending_roles': [
                'data scientist', 'machine learning engineer',
                'full stack developer', 'devops engineer'
            ]
        }
    
    def get_market_trends(self, job_title: str, location: str) -> List[str]:
        """Get market trends for job and location"""
        trends = []
        
        title_lower = job_title.lower()
        location_lower = location.lower()
        
        # Check if job is trending
        if any(role in title_lower for role in self.market_data['trending_roles']):
            trends.append("High demand role")
        
        # Check if location is trending
        if any(loc in location_lower for loc in self.market_data['trending_locations']):
            trends.append("High demand location")
        
        # Add general trends
        trends.append("Technology sector growth")
        
        return trends
    
    def get_competition_level(self, job_title: str, location: str) -> str:
        """Get competition level for the job"""
        demand_score = self.get_market_demand(job_title, location, [])
        
        if demand_score >= 0.8:
            return "High"
        elif demand_score >= 0.6:
            return "Medium"
        else:
            return "Low"
