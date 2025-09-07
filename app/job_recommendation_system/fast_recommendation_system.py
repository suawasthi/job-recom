#!/usr/bin/env python3
"""
Fast Job Recommendation System - Vectorized Database Approach
"""

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from config.settings import Config
from models.database import JobVectorDB, JobVector, ResumeVector, MatchResult
from models.match import JobMatch, MatchSummary
from services.vectorizer import VectorizationService
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


class FastJobRecommendationSystem:
    """
    Fast job recommendation system using vectorized database
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the fast recommendation system"""
        self.config = config or Config()
        
        # Initialize database
        self.db = JobVectorDB()
        
        # Initialize services
        self.vectorizer = VectorizationService(self.config)
        self.skill_matcher = SkillMatcher(self.config)
        self.experience_matcher = ExperienceMatcher(self.config)
        self.location_matcher = LocationMatcher(self.config)
        self.career_analyzer = CareerAnalyzer(self.config)
        self.salary_analyzer = SalaryAnalyzer(self.config)
        self.market_analyzer = MarketAnalyzer(self.config)
        self.explanation_generator = ExplanationGenerator(self.config)
        
        logger.info("Fast Job Recommendation System initialized successfully")
    
    def post_job(self, job_data: Dict[str, Any]) -> str:
        """
        Post a new job (vectorize and store)
        
        Args:
            job_data: Job description data
            
        Returns:
            Job ID
        """
        try:
            # Validate job data
            validate_job_data(job_data)
            
            # Vectorize job
            job_vector = self.vectorizer.vectorize_job_description(job_data)
            
            # Store in database
            self.db.store_job(job_vector)
            
            logger.info(f"Job posted successfully: {job_vector.job_id}")
            return job_vector.job_id
            
        except Exception as e:
            logger.error(f"Error posting job: {e}")
            raise
    
    def upload_resume(self, candidate_data: Dict[str, Any]) -> str:
        """
        Upload a resume (vectorize and store)
        
        Args:
            candidate_data: Candidate resume data
            
        Returns:
            Candidate ID
        """
        try:
            # Validate candidate data
            validate_candidate_data(candidate_data)
            
            # Vectorize resume
            resume_vector = self.vectorizer.vectorize_resume(candidate_data)
            
            # Store in database
            self.db.store_resume(resume_vector)
            
            logger.info(f"Resume uploaded successfully: {resume_vector.candidate_id}")
            return resume_vector.candidate_id
            
        except Exception as e:
            logger.error(f"Error uploading resume: {e}")
            raise
    
    def get_job_recommendations(self, candidate_id: str, limit: int = 10) -> List[JobMatch]:
        """
        Get job recommendations for a candidate (FAST - uses vectorized data)
        
        Args:
            candidate_id: Candidate ID
            limit: Maximum number of recommendations
            
        Returns:
            List of JobMatch objects
        """
        start_time = time.time()
        
        try:
            # Get candidate's vectorized resume
            resume_vector = self.db.get_resume(candidate_id)
            if not resume_vector:
                logger.warning(f"Resume not found for candidate: {candidate_id}")
                return []
            
            # Fast FAISS vector similarity search
            similar_job_ids = self.vectorizer.search_similar_jobs_faiss(
                resume_vector.resume_embedding, 
                limit=limit * 2  # Get more for filtering
            )
            
            # Get job vectors from database
            similar_jobs = []
            for job_id, similarity_score in similar_job_ids:
                job_vector = self.db.get_job(job_id)
                if job_vector:
                    similar_jobs.append((job_vector, similarity_score))
            
            # Convert to JobMatch objects with detailed scoring
            matches = []
            for job_vector, similarity_score in similar_jobs:
                # Check cache first
                cached_match = self.db.get_match(candidate_id, job_vector.job_id)
                if cached_match:
                    # Convert cached match to JobMatch
                    job_match = self._create_job_match_from_cache(cached_match, job_vector)
                    matches.append(job_match)
                else:
                    # Calculate detailed match
                    job_match = self._calculate_detailed_match(resume_vector, job_vector, similarity_score)
                    if job_match:
                        matches.append(job_match)
                        
                        # Cache the result
                        self._cache_match_result(candidate_id, job_vector.job_id, job_match)
            
            # Sort by match score and limit results
            matches.sort(key=lambda x: x.match_score, reverse=True)
            final_matches = matches[:limit]
            
            processing_time = time.time() - start_time
            logger.info(f"Generated {len(final_matches)} recommendations in {processing_time:.2f}s")
            
            return final_matches
            
        except Exception as e:
            logger.error(f"Error getting job recommendations: {e}")
            return []
    
    def get_candidate_recommendations(self, job_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get candidate recommendations for a job (reverse search)
        
        Args:
            job_id: Job ID
            limit: Maximum number of recommendations
            
        Returns:
            List of candidate recommendations
        """
        try:
            # Get job's vectorized description
            job_vector = self.db.get_job(job_id)
            if not job_vector:
                logger.warning(f"Job not found: {job_id}")
                return []
            
            # Fast FAISS vector similarity search
            similar_resume_ids = self.vectorizer.search_similar_resumes_faiss(
                job_vector.description_embedding,
                limit=limit
            )
            
            # Get resume vectors from database
            similar_resumes = []
            for candidate_id, similarity_score in similar_resume_ids:
                resume_vector = self.db.get_resume(candidate_id)
                if resume_vector:
                    similar_resumes.append((resume_vector, similarity_score))
            
            # Convert to recommendations
            recommendations = []
            for resume_vector, similarity_score in similar_resumes:
                recommendation = {
                    'candidate_id': resume_vector.candidate_id,
                    'name': resume_vector.name,
                    'email': resume_vector.email,
                    'similarity_score': similarity_score,
                    'current_role': resume_vector.current_role,
                    'experience_years': resume_vector.experience_years,
                    'location': resume_vector.location
                }
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting candidate recommendations: {e}")
            return []
    
    def _calculate_detailed_match(
        self, 
        resume_vector: ResumeVector, 
        job_vector: JobVector, 
        similarity_score: float
    ) -> Optional[JobMatch]:
        """Calculate detailed match between resume and job"""
        try:
            # Calculate component scores
            skill_analysis = self.skill_matcher.calculate_match(
                resume_vector.skills,
                job_vector.required_skills,
                job_vector.preferred_skills,
                ""  # No resume text needed since we have vectorized data
            )
            
            experience_match = self.experience_matcher.calculate_match(
                resume_vector.experience_years,
                job_vector.min_experience_years,
                job_vector.max_experience_years
            )
            
            location_match = self.location_matcher.calculate_match(
                resume_vector.location,
                job_vector.location,
                job_vector.remote_work_allowed,
                resume_vector.remote_preference
            )
            
            career_growth = self.career_analyzer.calculate_growth_potential(
                self._resume_to_profile(resume_vector),
                self._job_to_posting(job_vector)
            )
            
            salary_match = self.salary_analyzer.calculate_match(
                resume_vector.salary_expectation,
                job_vector.min_salary,
                job_vector.max_salary
            )
            
            market_demand = self.market_analyzer.get_market_demand(
                job_vector.title,
                job_vector.location,
                job_vector.required_skills
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
            
            # Create JobMatch
            job_match = JobMatch(
                job_id=job_vector.job_id,
                candidate_id=resume_vector.candidate_id,
                match_score=overall_score,
                confidence_score=similarity_score,
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
            
            return job_match
            
        except Exception as e:
            logger.warning(f"Error calculating detailed match: {e}")
            return None
    
    def _create_job_match_from_cache(self, cached_match: MatchResult, job_vector: JobVector) -> JobMatch:
        """Create JobMatch from cached result"""
        return JobMatch(
            job_id=job_vector.job_id,
            candidate_id=cached_match.candidate_id,
            match_score=cached_match.overall_score,
            confidence_score=0.8,  # High confidence for cached results
            skill_match_score=cached_match.skill_score,
            experience_match_score=cached_match.experience_score,
            location_match_score=cached_match.location_score,
            career_growth_score=cached_match.career_growth_score,
            salary_match_score=cached_match.salary_score
        )
    
    def _cache_match_result(self, candidate_id: str, job_id: str, job_match: JobMatch):
        """Cache match result for future use"""
        cached_match = MatchResult(
            candidate_id=candidate_id,
            job_id=job_id,
            overall_score=job_match.match_score,
            skill_score=job_match.skill_match_score,
            experience_score=job_match.experience_match_score,
            location_score=job_match.location_match_score,
            career_growth_score=job_match.career_growth_score,
            salary_score=job_match.salary_match_score
        )
        self.db.store_match(cached_match)
    
    def _resume_to_profile(self, resume_vector: ResumeVector):
        """Convert ResumeVector to CandidateProfile"""
        from models.candidate import CandidateProfile
        
        return CandidateProfile(
            id=resume_vector.candidate_id,
            name=resume_vector.name,
            email=resume_vector.email,
            skills=resume_vector.skills,
            experience_years=resume_vector.experience_years,
            current_role=resume_vector.current_role,
            location=resume_vector.location,
            salary_expectation=resume_vector.salary_expectation,
            remote_preference=resume_vector.remote_preference,
            resume_text="",  # Not needed for vectorized approach
            career_level=1  # Default
        )
    
    def _job_to_posting(self, job_vector: JobVector):
        """Convert JobVector to JobPosting"""
        from models.job import JobPosting
        
        return JobPosting(
            id=job_vector.job_id,
            title=job_vector.title,
            company=job_vector.company,
            required_skills=job_vector.required_skills,
            preferred_skills=job_vector.preferred_skills,
            min_experience_years=job_vector.min_experience_years,
            max_experience_years=job_vector.max_experience_years,
            location=job_vector.location,
            remote_work_allowed=job_vector.remote_work_allowed,
            min_salary=job_vector.min_salary,
            max_salary=job_vector.max_salary,
            status=job_vector.status
        )
    
    def _calculate_overall_score(
        self,
        skill_score: float,
        experience_score: float,
        location_score: float,
        career_growth_score: float,
        salary_score: float,
        market_demand_score: float
    ) -> float:
        """Calculate overall match score"""
        return (
            skill_score * self.config.skill_weight +
            experience_score * self.config.experience_weight +
            location_score * self.config.location_weight +
            career_growth_score * self.config.career_growth_weight +
            salary_score * self.config.salary_weight +
            market_demand_score * self.config.market_demand_weight
        )
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        db_stats = self.db.get_stats()
        vectorizer_stats = self.vectorizer.get_vectorization_stats()
        
        return {
            'database': db_stats,
            'vectorizer': vectorizer_stats,
            'faiss': {
                'job_index_size': len(self.vectorizer.job_ids),
                'resume_index_size': len(self.vectorizer.resume_ids),
                'job_index_type': type(self.vectorizer.job_index).__name__,
                'resume_index_type': type(self.vectorizer.resume_index).__name__
            },
            'config': {
                'embedding_model': self.config.embedding_model,
                'max_results': self.config.max_results,
                'enable_caching': self.config.enable_caching,
                'enable_faiss_ivf': self.config.enable_faiss_ivf
            }
        }
    
    def clear_all_caches(self):
        """Clear all caches"""
        self.db.matches.clear()
        self.vectorizer.embeddings.clear_cache()
        logger.info("All caches cleared")


def main():
    """Demo the fast recommendation system"""
    print("🚀 Fast Job Recommendation System Demo")
    print("=" * 50)
    
    # Initialize system
    system = FastJobRecommendationSystem()
    
    # Sample job data
    jobs_data = [
        {
            'id': 'job_001',
            'job_title': 'Senior ai ',
            'company': 'TechCorp Inc',
            'required_skills': ['ml', 'Machine Learning', 'Statistics'],
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
    # Sample candidate data
    candidate_data = {
        'id': 'candidate_001',
        'name': 'John Doe',
        'email': 'john@example.com',
        'skills': ['Python', 'Machine Learning', 'SQL', 'Data Science', 'AWS'],
        'experience_years': 4,
        'current_role': 'Data Scientist',
        'location': 'San Francisco, CA',
        'salary_expectation': 140000.0,
        'remote_preference': 0.7,
        'resume_text': 'Experienced data scientist with expertise in Python, machine learning, and cloud computing. Led multiple ML projects and worked with large datasets.'
    }
    
    # Post all jobs
    print("📝 Posting jobs...")
    job_ids = []
    for job_data in jobs_data:
        job_id = system.post_job(job_data)
        job_ids.append(job_id)
        print(f"✅ Job posted with ID: {job_id}")
    print(f"📊 Posted {len(job_ids)} jobs total")
    
    # Upload resume
    print("\n📄 Uploading resume...")
    candidate_id = system.upload_resume(candidate_data)
    print(f"✅ Resume uploaded with ID: {candidate_id}")
    
    # Get recommendations
    print("\n🔍 Getting job recommendations...")
    start_time = time.time()
    recommendations = system.get_job_recommendations(candidate_id, limit=5)
    processing_time = time.time() - start_time
    
    print(f"✅ Found {len(recommendations)} recommendations in {processing_time:.2f}s")
    
    # Display results
    for i, match in enumerate(recommendations, 1):
        print(f"\n{i}. Job: {match.job_id}")
        print(f"   Match Score: {match.match_score:.2f}")
        print(f"   Skill Score: {match.skill_match_score:.2f}")
        print(f"   Experience Score: {match.experience_match_score:.2f}")
    
    # System stats
    print("\n📊 System Statistics:")
    stats = system.get_system_stats()
    print(f"Database: {stats['database']}")
    print(f"Vectorizer: {stats['vectorizer']}")


if __name__ == "__main__":
    main()
