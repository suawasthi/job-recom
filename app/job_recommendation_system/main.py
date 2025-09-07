#!/usr/bin/env python3
"""
Job Recommendation System - Main Entry Point
Clean, modular implementation of AI-powered job matching
"""

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from config.settings import Config
from models.candidate import CandidateProfile, CandidateData
from models.job import JobPosting, JobData
from models.match import JobMatch, MatchSummary
from services.skill_matcher import SkillMatcher
from services.experience_matcher import ExperienceMatcher
from services.location_matcher import LocationMatcher
from services.career_analyzer import CareerAnalyzer
from services.salary_analyzer import SalaryAnalyzer
from services.market_analyzer import MarketAnalyzer
from services.explanation_generator import ExplanationGenerator
from utils.validators import validate_candidate_data, validate_job_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobRecommendationSystem:
    """
    Clean, modular job recommendation system
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the recommendation system"""
        self.config = config or Config()
        
        # Initialize service components
        self.skill_matcher = SkillMatcher(self.config)
        self.experience_matcher = ExperienceMatcher(self.config)
        self.location_matcher = LocationMatcher(self.config)
        self.career_analyzer = CareerAnalyzer(self.config)
        self.salary_analyzer = SalaryAnalyzer(self.config)
        self.market_analyzer = MarketAnalyzer(self.config)
        self.explanation_generator = ExplanationGenerator(self.config)
        
        logger.info("Job Recommendation System initialized successfully")
    
    def recommend_jobs(
        self, 
        candidate_data: Dict[str, Any], 
        jobs_data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[JobMatch]:
        """
        Main method to get job recommendations for a candidate
        
        Args:
            candidate_data: Dictionary containing candidate information
            jobs_data: List of job posting dictionaries
            context: Optional additional context (preferences, market conditions, etc.)
            
        Returns:
            List of JobMatch objects ranked by match score
        """
        start_time = time.time()
        context = context or {}
        
        try:
            # Validate inputs
            validate_candidate_data(candidate_data)
            for job in jobs_data:
                validate_job_data(job)
            
            # Create enhanced candidate profile
            candidate_profile = self._create_candidate_profile(candidate_data)
            logger.info(f"Created profile for candidate: {candidate_profile.id}")
            
            # Generate matches
            matches = self._generate_matches(candidate_profile, jobs_data, context)
            logger.info(f"Generated {len(matches)} initial matches")
            
            # Apply enhancements and filtering
            enhanced_matches = self._apply_enhancements(matches, candidate_profile, context)
            logger.info(f"Enhanced to {len(enhanced_matches)} matches")
            
            # Generate explanations
            self._generate_explanations(enhanced_matches, candidate_profile)
            
            # Sort and limit results
            final_matches = self._sort_and_limit_matches(enhanced_matches)
            
            # Log summary
            processing_time = time.time() - start_time
            summary = self._create_summary(jobs_data, final_matches, processing_time)
            logger.info(f"Recommendation complete: {summary.to_dict()}")
            
            return final_matches
            
        except Exception as e:
            logger.error(f"Error in job recommendation: {str(e)}")
            raise
    
    def _create_candidate_profile(self, candidate_data: Dict[str, Any]) -> CandidateProfile:
        """Create enhanced candidate profile"""
        return CandidateProfile(
            id=candidate_data.get('id', 'unknown'),
            name=candidate_data.get('name', ''),
            email=candidate_data.get('email', ''),
            skills=candidate_data.get('skills', []),
            experience_years=candidate_data.get('experience_years', 0),
            current_role=candidate_data.get('current_role', ''),
            location=candidate_data.get('location', ''),
            salary_expectation=candidate_data.get('salary_expectation', 0.0),
            remote_preference=candidate_data.get('remote_preference', 0.5),
            resume_text=candidate_data.get('resume_text', ''),
            career_level=self._infer_career_level(candidate_data)
        )
    
    def _generate_matches(
        self, 
        candidate_profile: CandidateProfile, 
        jobs_data: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[JobMatch]:
        """Generate initial job matches"""
        matches = []
        
        for job_data in jobs_data:
            # Skip inactive jobs
            if not self._is_job_active(job_data):
                continue
            
            # Create job posting object
            job_posting = self._create_job_posting(job_data)
            
            # Calculate comprehensive match
            match = self._calculate_comprehensive_match(candidate_profile, job_posting, context)
            
            # Add to matches if meets minimum threshold
            if match and match.match_score >= self.config.min_match_score:
                matches.append(match)
        
        return matches
    
    def _calculate_comprehensive_match(
        self, 
        candidate_profile: CandidateProfile, 
        job_posting: JobPosting, 
        context: Dict[str, Any]
    ) -> Optional[JobMatch]:
        """Calculate comprehensive match between candidate and job"""
        
        # Calculate component scores
        skill_analysis = self.skill_matcher.calculate_match(
            candidate_profile.skills,
            job_posting.required_skills,
            job_posting.preferred_skills,
            candidate_profile.resume_text
        )
        
        experience_match = self.experience_matcher.calculate_match(
            candidate_profile.experience_years,
            job_posting.min_experience_years,
            job_posting.max_experience_years
        )
        
        location_match = self.location_matcher.calculate_match(
            candidate_profile.location,
            job_posting.location,
            job_posting.remote_work_allowed,
            candidate_profile.remote_preference
        )
        
        career_growth = self.career_analyzer.calculate_growth_potential(
            candidate_profile, job_posting
        )
        
        salary_match = self.salary_analyzer.calculate_match(
            candidate_profile.salary_expectation,
            job_posting.min_salary,
            job_posting.max_salary
        )
        
        # Get market intelligence
        market_demand = self.market_analyzer.get_market_demand(
            job_posting.title,
            job_posting.location,
            job_posting.required_skills
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            skill_analysis['score'],
            experience_match,
            location_match,
            career_growth,
            salary_match,
            market_demand
        )
        
        # Calculate confidence
        confidence_score = self._calculate_confidence_score(
            skill_analysis,
            experience_match,
            location_match,
            market_demand
        )
        
        # Create match object
        match = JobMatch(
            job_id=job_posting.id,
            candidate_id=candidate_profile.id,
            match_score=overall_score,
            confidence_score=confidence_score,
            skill_match_score=skill_analysis['score'],
            experience_match_score=experience_match,
            location_match_score=location_match,
            career_growth_score=career_growth,
            salary_match_score=salary_match,
            skill_matches=skill_analysis.get('exact_matches', []),
            missing_skills=skill_analysis.get('missing_skills', []),
            transferable_skills=list(skill_analysis.get('transferable_matches', {}).keys()),
            market_demand_score=market_demand
        )
        
        return match
    
    def _calculate_overall_score(
        self,
        skill_score: float,
        experience_score: float,
        location_score: float,
        career_growth_score: float,
        salary_score: float,
        market_demand_score: float
    ) -> float:
        """Calculate overall match score using weighted components"""
        return (
            skill_score * self.config.skill_weight +
            experience_score * self.config.experience_weight +
            location_score * self.config.location_weight +
            career_growth_score * self.config.career_growth_weight +
            salary_score * self.config.salary_weight +
            market_demand_score * self.config.market_demand_weight
        )
    
    def _calculate_confidence_score(
        self,
        skill_analysis: Dict[str, Any],
        experience_score: float,
        location_score: float,
        market_demand_score: float
    ) -> float:
        """Calculate confidence in the match"""
        confidence_factors = [
            len(skill_analysis.get('exact_matches', [])) / max(1, len(skill_analysis.get('required_skills', []))),
            1.0 if experience_score > 0.7 else 0.5,
            location_score,
            1.0 if market_demand_score > 0.7 else 0.7
        ]
        return sum(confidence_factors) / len(confidence_factors)
    
    def _apply_enhancements(
        self, 
        matches: List[JobMatch], 
        candidate_profile: CandidateProfile, 
        context: Dict[str, Any]
    ) -> List[JobMatch]:
        """Apply enhancements and filtering to matches"""
        # Sort by match score
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        # Apply confidence filtering
        filtered_matches = [
            m for m in matches 
            if m.confidence_score >= self.config.min_confidence_score
        ]
        
        return filtered_matches
    
    def _generate_explanations(
        self, 
        matches: List[JobMatch], 
        candidate_profile: CandidateProfile
    ):
        """Generate explanations for matches"""
        for match in matches:
            reasons, concerns = self.explanation_generator.generate_explanations(match, candidate_profile)
            match.match_reasons = reasons
            match.potential_concerns = concerns
    
    def _sort_and_limit_matches(self, matches: List[JobMatch]) -> List[JobMatch]:
        """Sort matches and limit to maximum results"""
        # Sort by match score (descending)
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        # Limit to maximum results
        return matches[:self.config.max_results]
    
    def _create_summary(
        self, 
        jobs_data: List[Dict[str, Any]], 
        matches: List[JobMatch], 
        processing_time: float
    ) -> MatchSummary:
        """Create summary of matching results"""
        total_jobs = len(jobs_data)
        total_matches = len(matches)
        high_quality = len([m for m in matches if m.is_high_match()])
        good_matches = len([m for m in matches if m.is_good_match()])
        
        avg_score = sum(m.match_score for m in matches) / len(matches) if matches else 0.0
        best_score = max(m.match_score for m in matches) if matches else 0.0
        
        return MatchSummary(
            total_jobs_analyzed=total_jobs,
            total_matches_found=total_matches,
            high_quality_matches=high_quality,
            good_matches=good_matches,
            average_match_score=avg_score,
            best_match_score=best_score,
            processing_time_seconds=processing_time
        )
    
    def _is_job_active(self, job_data: Dict[str, Any]) -> bool:
        """Check if job is active"""
        status = job_data.get('status', '').lower()
        return status == 'active'
    
    def _create_job_posting(self, job_data: Dict[str, Any]) -> JobPosting:
        """Create JobPosting object from dictionary"""
        return JobPosting(
            id=job_data.get('id', 'unknown'),
            title=job_data.get('job_title', ''),
            company=job_data.get('company', ''),
            required_skills=job_data.get('required_skills', []),
            preferred_skills=job_data.get('preferred_skills', []),
            min_experience_years=job_data.get('min_experience_years', 0),
            max_experience_years=job_data.get('max_experience_years', 10),
            location=job_data.get('location', ''),
            remote_work_allowed=job_data.get('remote_work_allowed', 'no'),
            min_salary=job_data.get('min_salary', 0.0),
            max_salary=job_data.get('max_salary', 0.0),
            status=job_data.get('status', 'active')
        )
    
    def clear_caches(self):
        """Clear all caches to free memory"""
        self._candidate_cache.clear()
        self._market_cache.clear()
        self.skill_matcher.skill_embeddings.clear_cache()
        logger.info("All caches cleared")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        embedding_stats = self.skill_matcher.skill_embeddings.get_cache_stats()
        
        return {
            'candidate_cache_size': len(self._candidate_cache),
            'market_cache_size': len(self._market_cache),
            'embedding_cache': embedding_stats
        }
    
    def _infer_career_level(self, candidate_data: Dict[str, Any]) -> int:
        """Infer career level from candidate data"""
        experience_years = candidate_data.get('experience_years', 0)
        current_role = candidate_data.get('current_role', '').lower()
        
        if any(keyword in current_role for keyword in self.config.senior_level_keywords):
            return 2
        elif any(keyword in current_role for keyword in self.config.junior_level_keywords):
            return 0
        elif experience_years < 2:
            return 0
        else:
            return 1


def main():
    """Main function for testing the system"""
    # Initialize system
    system = JobRecommendationSystem()
    
    # Sample candidate data
    candidate_data = {
        'id': 'candidate_123',
        'name': 'John Doe',
        'email': 'john.doe@email.com',
        'skills': ['Python', 'Machine Learning', 'SQL', 'Data Science', 'AWS'],
        'experience_years': 4,
        'current_role': 'Data Scientist',
        'location': 'San Francisco, CA',
        'salary_expectation': 95000,
        'remote_preference': 0.7
    }
    
    # Sample job data
    jobs_data = [
        {
            'id': 'job_001',
            'job_title': 'Senior Data Scientist',
            'company': 'TechCorp Inc',
            'required_skills': ['Python', 'Machine Learning', 'Statistics'],
            'preferred_skills': ['AWS', 'Docker'],
            'min_experience_years': 3,
            'max_experience_years': 6,
            'location': 'San Francisco, CA',
            'remote_work_allowed': 'hybrid',
            'min_salary': 90000,
            'max_salary': 130000,
            'status': 'active'
        }, 
        {
            'id': 'job_002',
            'job_title': 'Machine Learning Engineer',
            'company': 'AI Startup',
            'required_skills': ['Python', 'Machine Learning', 'TensorFlow'],
            'preferred_skills': ['AWS', 'Docker', 'Kubernetes'],
            'min_experience_years': 2,
            'max_experience_years': 5,
            'location': 'Remote',
            'remote_work_allowed': 'yes',
            'min_salary': 80000,
            'max_salary': 120000,
            'status': 'active'
        },
        {
            'id': 'job_003',
            'job_title': 'Data Analyst',
            'company': 'DataCorp',
            'required_skills': ['SQL', 'Tableau', 'Excel'],
            'preferred_skills': ['AWS', 'Docker'],
            'min_experience_years': 1,
            'max_experience_years': 4,
            'location': 'Remote',
            'remote_work_allowed': 'yes',
            'min_salary': 70000,
            'max_salary': 110000,
            'status': 'active'
        },
        {
            'id': 'job_004',
            'job_title': 'Software Engineer',
            'company': 'CodeCraft',
            'required_skills': ['Python', 'JavaScript', 'React'],
            'preferred_skills': ['AWS', 'Docker', 'Kubernetes'],
            'min_experience_years': 1,
            'max_experience_years': 4,
            'location': 'Remote',
            'remote_work_allowed': 'yes',
            'min_salary': 70000,
            'max_salary': 110000,
            'status': 'active'
        }
    ]
    
    # Get recommendations
    print("🚀 Getting job recommendations...")
    recommendations = system.recommend_jobs(candidate_data, jobs_data)
    
    # Display results
    print(f"\n✅ Found {len(recommendations)} recommendations:")
    for i, match in enumerate(recommendations, 1):
        print(f"\n#{i} - {match.job_id}")
        print(f"   Match Score: {match.match_score:.3f}")
        print(f"   Confidence: {match.confidence_score:.3f}")
        print(f"   Quality: {match.get_match_quality()}")
        print(f"   Skills: {len(match.skill_matches)}/{len(match.skill_matches) + len(match.missing_skills)} matched")
        if match.match_reasons:
            print(f"   Reason: {match.match_reasons[0]}")


if __name__ == "__main__":
    main()
