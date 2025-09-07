"""
Explanation generator service
"""

import logging
from typing import List, Tuple

from config.settings import Config
from models.candidate import CandidateProfile
from models.match import JobMatch

logger = logging.getLogger(__name__)


class ExplanationGenerator:
    """Generate human-readable explanations for job matches"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def generate_explanations(
        self,
        match: JobMatch,
        candidate_profile: CandidateProfile
    ) -> Tuple[List[str], List[str]]:
        """
        Generate explanations for a job match
        
        Args:
            match: Job match object
            candidate_profile: Candidate profile
            
        Returns:
            Tuple of (reasons, concerns)
        """
        reasons = []
        concerns = []
        
        # Generate skill-based reasons
        reasons.extend(self._generate_skill_reasons(match))
        
        # Generate experience-based reasons
        reasons.extend(self._generate_experience_reasons(match))
        
        # Generate location-based reasons
        reasons.extend(self._generate_location_reasons(match))
        
        # Generate career growth reasons
        reasons.extend(self._generate_career_reasons(match))
        
        # Generate market-based reasons
        reasons.extend(self._generate_market_reasons(match))
        
        # Generate concerns
        concerns.extend(self._generate_concerns(match, candidate_profile))
        
        return reasons, concerns
    
    def _generate_skill_reasons(self, match: JobMatch) -> List[str]:
        """Generate skill-based reasons"""
        reasons = []
        
        if match.skill_match_score >= 0.8:
            reasons.append(f"Excellent skills match ({len(match.skill_matches)} matching skills)")
        elif match.skill_match_score >= 0.6:
            reasons.append(f"Good skills alignment ({len(match.skill_matches)} matching skills)")
        elif match.skill_match_score >= 0.4:
            reasons.append(f"Moderate skills match ({len(match.skill_matches)} matching skills)")
        
        # Add specific skill mentions
        if match.skill_matches:
            top_skills = match.skill_matches[:3]  # Top 3 skills
            reasons.append(f"Strong in: {', '.join(top_skills)}")
        
        # Add transferable skills
        if match.transferable_skills:
            reasons.append(f"Has transferable skills: {', '.join(match.transferable_skills[:2])}")
        
        return reasons
    
    def _generate_experience_reasons(self, match: JobMatch) -> List[str]:
        """Generate experience-based reasons"""
        reasons = []
        
        if match.experience_match_score >= 0.8:
            reasons.append("Experience level is ideal for this role")
        elif match.experience_match_score >= 0.6:
            reasons.append("Good experience level match")
        elif match.experience_match_score >= 0.4:
            reasons.append("Experience level is acceptable")
        
        return reasons
    
    def _generate_location_reasons(self, match: JobMatch) -> List[str]:
        """Generate location-based reasons"""
        reasons = []
        
        if match.location_match_score >= 0.9:
            reasons.append("Perfect location match")
        elif match.location_match_score >= 0.7:
            reasons.append("Good location compatibility")
        elif match.location_match_score >= 0.5:
            reasons.append("Location is manageable")
        
        return reasons
    
    def _generate_career_reasons(self, match: JobMatch) -> List[str]:
        """Generate career growth reasons"""
        reasons = []
        
        if match.career_growth_score >= 0.7:
            reasons.append("Strong career advancement opportunity")
        elif match.career_growth_score >= 0.5:
            reasons.append("Good growth potential")
        elif match.career_growth_score >= 0.3:
            reasons.append("Moderate career growth opportunity")
        
        return reasons
    
    def _generate_market_reasons(self, match: JobMatch) -> List[str]:
        """Generate market-based reasons"""
        reasons = []
        
        if match.market_demand_score >= 0.8:
            reasons.append("High demand role in current market")
        elif match.market_demand_score >= 0.6:
            reasons.append("Good market demand for this role")
        elif match.market_demand_score >= 0.4:
            reasons.append("Stable market demand")
        
        return reasons
    
    def _generate_concerns(self, match: JobMatch, candidate_profile: CandidateProfile) -> List[str]:
        """Generate potential concerns"""
        concerns = []
        
        # Skill gaps
        if match.missing_skills:
            high_priority_missing = [
                skill for skill, gap in match.skill_gaps.items() 
                if gap > 0.7
            ]
            if high_priority_missing:
                concerns.append(f"May need to develop: {', '.join(high_priority_missing[:2])}")
        
        # Experience concerns
        if match.experience_match_score < 0.6:
            if match.experience_match_score < 0.4:
                concerns.append("Experience level may be insufficient")
            else:
                concerns.append("Experience level may not be ideal")
        
        # Location concerns
        if match.location_match_score < 0.5:
            concerns.append("Location requires significant adjustment")
        
        # Salary concerns
        if match.salary_match_score < 0.5:
            concerns.append("Salary expectations may not align")
        
        # Market concerns
        if match.market_demand_score < 0.4:
            concerns.append("Low market demand for this role")
        
        return concerns
    
    def generate_learning_recommendations(self, missing_skills: List[str]) -> List[str]:
        """Generate learning recommendations for missing skills"""
        recommendations = []
        
        for skill in missing_skills[:3]:  # Top 3 missing skills
            recommendations.append(f"Learn {skill}")
        
        return recommendations
    
    def generate_career_advice(self, match: JobMatch) -> List[str]:
        """Generate career advice based on match"""
        advice = []
        
        if match.career_growth_score >= 0.7:
            advice.append("This role offers excellent career advancement")
        
        if match.market_demand_score >= 0.8:
            advice.append("High demand role - good timing for application")
        
        if match.skill_match_score < 0.6:
            advice.append("Consider developing missing skills before applying")
        
        return advice
