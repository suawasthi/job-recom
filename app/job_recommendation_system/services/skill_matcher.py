"""
Skill matching service with semantic analysis
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from config.settings import Config
from data.skill_graph import SkillGraph
from data.embeddings import SkillEmbeddings

logger = logging.getLogger(__name__)


class SkillMatcher:
    """Advanced skill matching with semantic analysis"""
    
    def __init__(self, config: Config):
        self.config = config
        self.skill_graph = SkillGraph()
        self.skill_embeddings = SkillEmbeddings(config)
        
    def calculate_match(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str] = None,
        resume_text: str = ""
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive skill match between candidate and job requirements
        
        Args:
            candidate_skills: List of candidate's skills
            required_skills: List of required skills for the job
            preferred_skills: List of preferred skills (optional)
            resume_text: Resume text for semantic analysis (optional)
            
        Returns:
            Dictionary with detailed skill analysis
        """
        if not candidate_skills or not required_skills:
            return self._empty_skill_analysis(required_skills)
        
        preferred_skills = preferred_skills or []
        
        # Normalize skills
        candidate_normalized = self._normalize_skills(candidate_skills)
        required_normalized = self._normalize_skills(required_skills)
        preferred_normalized = self._normalize_skills(preferred_skills)
        
        # Calculate different types of matches
        exact_matches = self._find_exact_matches(candidate_normalized, required_normalized)
        semantic_matches = self._find_semantic_matches(candidate_normalized, required_normalized, resume_text)
        transferable_matches = self._find_transferable_matches(candidate_normalized, required_normalized)
        preferred_matches = self._find_preferred_matches(candidate_normalized, preferred_normalized)
        
        # Calculate scores
        exact_score = self._calculate_exact_score(exact_matches, required_normalized)
        semantic_score = self._calculate_semantic_score(semantic_matches, required_normalized)
        transferable_score = self._calculate_transferable_score(transferable_matches, required_normalized)
        preferred_bonus = self._calculate_preferred_bonus(preferred_matches, preferred_normalized)
        
        # Calculate final score
        final_score = self._calculate_final_score(
            exact_score, semantic_score, transferable_score, preferred_bonus
        )
        
        # Identify missing skills
        all_matches = set(exact_matches) | set(semantic_matches) | set(transferable_matches.keys())
        missing_skills = [skill for skill in required_normalized if skill not in all_matches]
        
        # Calculate skill gaps
        skill_gaps = self._calculate_skill_gaps(missing_skills)
        
        return {
            'score': final_score,
            'exact_matches': exact_matches,
            'semantic_matches': semantic_matches,
            'transferable_matches': transferable_matches,
            'preferred_matches': preferred_matches,
            'missing_skills': missing_skills,
            'skill_gaps': skill_gaps,
            'required_skills': required_normalized,
            'component_scores': {
                'exact': exact_score,
                'semantic': semantic_score,
                'transferable': transferable_score,
                'preferred_bonus': preferred_bonus
            }
        }
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize skill names for comparison"""
        normalized = []
        for skill in skills:
            if skill:
                # Convert to lowercase and strip whitespace
                normalized_skill = skill.lower().strip()
                # Remove common variations
                normalized_skill = self._standardize_skill_name(normalized_skill)
                if normalized_skill:
                    normalized.append(normalized_skill)
        return list(set(normalized))  # Remove duplicates
    
    def _standardize_skill_name(self, skill: str) -> str:
        """Standardize skill names to handle variations"""
        skill_mappings = {
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'js': 'javascript',
            'react.js': 'react',
            'reactjs': 'react',
            'node.js': 'nodejs',
            'nodejs': 'node.js',
            'aws cloud': 'aws',
            'amazon web services': 'aws',
            'google cloud': 'gcp',
            'google cloud platform': 'gcp',
            'microsoft azure': 'azure',
            'data sci': 'data science',
            'deep learning': 'machine learning',
            'statistical analysis': 'statistics',
            'statistical modeling': 'statistics'
        }
        
        return skill_mappings.get(skill, skill)
    
    def _find_exact_matches(self, candidate_skills: List[str], required_skills: List[str]) -> List[str]:
        """Find exact skill matches"""
        return list(set(candidate_skills) & set(required_skills))
    
    def _find_semantic_matches(
        self, 
        candidate_skills: List[str], 
        required_skills: List[str],
        resume_text: str = ""
    ) -> List[str]:
        """Find semantic skill matches using embeddings with batch processing"""
        if not resume_text:
            return []
        
        semantic_matches = []
        
        try:
            # Get resume embedding once (cached)
            resume_embedding = self.skill_embeddings.get_text_embedding(resume_text)
            
            # Use batch processing for better performance
            skill_similarities = self.skill_embeddings.calculate_skill_similarity_batch(
                resume_embedding, required_skills
            )
            
            # Filter matches above threshold
            for skill, similarity in skill_similarities.items():
                if similarity > self.config.skill_similarity_threshold:
                    semantic_matches.append(skill)
        
        except Exception as e:
            logger.warning(f"Error in semantic matching: {e}")
        
        return semantic_matches
    
    def _find_transferable_matches(self, candidate_skills: List[str], required_skills: List[str]) -> Dict[str, float]:
        """Find transferable skill matches using skill graph"""
        transferable_matches = {}
        
        for required_skill in required_skills:
            for candidate_skill in candidate_skills:
                transferability = self.skill_graph.get_transferability(candidate_skill, required_skill)
                if transferability > self.config.transferable_skill_threshold:
                    transferable_matches[required_skill] = transferability
                    break
        
        return transferable_matches
    
    def _find_preferred_matches(self, candidate_skills: List[str], preferred_skills: List[str]) -> List[str]:
        """Find matches with preferred skills"""
        return list(set(candidate_skills) & set(preferred_skills))
    
    def _calculate_exact_score(self, exact_matches: List[str], required_skills: List[str]) -> float:
        """Calculate score for exact matches"""
        if not required_skills:
            return 0.0
        return len(exact_matches) / len(required_skills)
    
    def _calculate_semantic_score(self, semantic_matches: List[str], required_skills: List[str]) -> float:
        """Calculate score for semantic matches"""
        if not required_skills:
            return 0.0
        return len(semantic_matches) / len(required_skills)
    
    def _calculate_transferable_score(self, transferable_matches: Dict[str, float], required_skills: List[str]) -> float:
        """Calculate score for transferable matches"""
        if not required_skills:
            return 0.0
        return sum(transferable_matches.values()) / len(required_skills)
    
    def _calculate_preferred_bonus(self, preferred_matches: List[str], preferred_skills: List[str]) -> float:
        """Calculate bonus for preferred skill matches"""
        if not preferred_skills:
            return 0.0
        return len(preferred_matches) / len(preferred_skills) * 0.1  # 10% bonus
    
    def _calculate_final_score(
        self,
        exact_score: float,
        semantic_score: float,
        transferable_score: float,
        preferred_bonus: float
    ) -> float:
        """Calculate final skill match score"""
        # Weighted combination of different match types
        final_score = (
            exact_score * 0.6 +      # Exact matches are most important
            semantic_score * 0.3 +   # Semantic matches are valuable
            transferable_score * 0.1 + # Transferable skills are least important
            preferred_bonus          # Small bonus for preferred skills
        )
        
        return min(1.0, final_score)  # Cap at 1.0
    
    def _calculate_skill_gaps(self, missing_skills: List[str]) -> Dict[str, float]:
        """Calculate skill gaps for missing skills"""
        skill_gaps = {}
        for skill in missing_skills:
            # Assign gap severity based on skill importance
            # This could be enhanced with skill importance data
            skill_gaps[skill] = 0.8  # Default high gap severity
        return skill_gaps
    
    def _empty_skill_analysis(self, required_skills: List[str]) -> Dict[str, Any]:
        """Return empty skill analysis when no skills provided"""
        return {
            'score': 0.0,
            'exact_matches': [],
            'semantic_matches': [],
            'transferable_matches': {},
            'preferred_matches': [],
            'missing_skills': required_skills,
            'skill_gaps': {skill: 1.0 for skill in required_skills},
            'required_skills': required_skills,
            'component_scores': {
                'exact': 0.0,
                'semantic': 0.0,
                'transferable': 0.0,
                'preferred_bonus': 0.0
            }
        }
