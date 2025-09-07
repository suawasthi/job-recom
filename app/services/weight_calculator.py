"""
Dynamic Weight Calculation Service
Replaces hardcoded weights with intelligent, data-driven weight calculation
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class IndustryType(Enum):
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    MARKETING = "marketing"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    CONSULTING = "consulting"
    STARTUP = "startup"
    ENTERPRISE = "enterprise"

class CareerStage(Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"

@dataclass
class WeightConfig:
    """Configuration for dynamic weight calculation"""
    skill_weight: float
    experience_weight: float
    location_weight: float
    salary_weight: float
    semantic_weight: float
    market_demand_weight: float
    career_growth_weight: float

class DynamicWeightCalculator:
    """Calculates optimal weights based on context, user profile, and market conditions"""
    
    def __init__(self):
        # Base weights (fallback)
        self.base_weights = WeightConfig(
            skill_weight=0.35,
            experience_weight=0.25,
            location_weight=0.15,
            salary_weight=0.10,
            semantic_weight=0.10,
            market_demand_weight=0.03,
            career_growth_weight=0.02
        )
        
        # Industry-specific weight configurations
        self.industry_weights = {
            IndustryType.TECHNOLOGY: WeightConfig(
                skill_weight=0.45,      # Skills are crucial in tech
                experience_weight=0.20,  # Experience matters but skills more
                location_weight=0.10,    # Remote work common
                salary_weight=0.10,      # Competitive salaries
                semantic_weight=0.10,    # Job description alignment
                market_demand_weight=0.03,
                career_growth_weight=0.02
            ),
            IndustryType.FINANCE: WeightConfig(
                skill_weight=0.25,      # Skills important but not primary
                experience_weight=0.35,  # Experience is crucial
                location_weight=0.20,    # Location matters for finance
                salary_weight=0.15,      # High salary expectations
                semantic_weight=0.03,    # Less emphasis on description
                market_demand_weight=0.01,
                career_growth_weight=0.01
            ),
            IndustryType.HEALTHCARE: WeightConfig(
                skill_weight=0.20,      # Technical skills less important
                experience_weight=0.40,  # Experience and credentials crucial
                location_weight=0.25,    # Location very important
                salary_weight=0.10,      # Stable but not highest
                semantic_weight=0.03,    # Less emphasis on description
                market_demand_weight=0.01,
                career_growth_weight=0.01
            ),
            IndustryType.STARTUP: WeightConfig(
                skill_weight=0.40,      # Versatile skills needed
                experience_weight=0.15,  # Less experience required
                location_weight=0.20,    # Often remote-friendly
                salary_weight=0.15,      # Equity compensation
                semantic_weight=0.08,    # Culture fit important
                market_demand_weight=0.01,
                career_growth_weight=0.01
            ),
            IndustryType.ENTERPRISE: WeightConfig(
                skill_weight=0.30,      # Standard skill requirements
                experience_weight=0.30,  # Experience valued
                location_weight=0.20,    # Office-based often
                salary_weight=0.12,      # Competitive packages
                semantic_weight=0.05,    # Process-oriented
                market_demand_weight=0.02,
                career_growth_weight=0.01
            )
        }
        
        # Career stage adjustments
        self.career_stage_adjustments = {
            CareerStage.ENTRY: {
                'skill_weight': 1.5,      # Skills more important for entry
                'experience_weight': 0.3,  # Experience less important
                'location_weight': 1.2,    # Location flexibility important
                'salary_weight': 0.8,      # Salary less critical
                'semantic_weight': 1.3,    # Job description alignment important
            },
            CareerStage.JUNIOR: {
                'skill_weight': 1.3,
                'experience_weight': 0.5,
                'location_weight': 1.1,
                'salary_weight': 0.9,
                'semantic_weight': 1.2,
            },
            CareerStage.MID: {
                'skill_weight': 1.0,      # Standard weights
                'experience_weight': 1.0,
                'location_weight': 1.0,
                'salary_weight': 1.0,
                'semantic_weight': 1.0,
            },
            CareerStage.SENIOR: {
                'skill_weight': 0.8,      # Skills less critical
                'experience_weight': 1.3,  # Experience more important
                'location_weight': 0.9,    # Location flexibility
                'salary_weight': 1.2,      # Salary more important
                'semantic_weight': 0.9,    # Less emphasis on description
            },
            CareerStage.LEAD: {
                'skill_weight': 0.6,      # Leadership skills more important
                'experience_weight': 1.5,  # Experience crucial
                'location_weight': 0.8,    # Remote leadership common
                'salary_weight': 1.3,      # High salary expectations
                'semantic_weight': 0.8,    # Strategic fit important
            },
            CareerStage.EXECUTIVE: {
                'skill_weight': 0.4,      # Strategic thinking over technical
                'experience_weight': 1.8,  # Extensive experience required
                'location_weight': 0.7,    # Global roles
                'salary_weight': 1.5,      # Executive compensation
                'semantic_weight': 0.7,    # Vision alignment
            }
        }
        
        # Market condition adjustments
        self.market_conditions = {
            'remote_work_trend': 0.7,      # High remote work adoption
            'skill_shortage': 0.6,         # Moderate skill shortage
            'economic_uncertainty': 0.3,   # Low economic uncertainty
            'tech_boom': 0.8,              # High tech growth
        }

    def calculate_optimal_weights(
        self,
        user_profile: Dict[str, Any],
        job_data: Dict[str, Any],
        market_context: Optional[Dict[str, Any]] = None
    ) -> WeightConfig:
        """
        Calculate optimal weights based on user profile, job characteristics, and market conditions
        
        Args:
            user_profile: User's profile information
            job_data: Job posting data
            market_context: Current market conditions
            
        Returns:
            WeightConfig with optimized weights
        """
        try:
            # Start with industry-specific base weights
            industry = self._detect_industry(job_data)
            base_weights = self.industry_weights.get(industry, self.base_weights)
            
            # Apply career stage adjustments
            career_stage = self._detect_career_stage(user_profile, job_data)
            adjusted_weights = self._apply_career_stage_adjustments(base_weights, career_stage)
            
            # Apply user preference adjustments
            user_adjusted_weights = self._apply_user_preferences(adjusted_weights, user_profile)
            
            # Apply market condition adjustments
            market_adjusted_weights = self._apply_market_conditions(
                user_adjusted_weights, 
                market_context or self.market_conditions
            )
            
            # Normalize weights to ensure they sum to 1.0
            normalized_weights = self._normalize_weights(market_adjusted_weights)
            
            logger.info(f"Calculated weights for {industry.value} industry, {career_stage.value} level: {normalized_weights}")
            
            return normalized_weights
            
        except Exception as e:
            logger.error(f"Error calculating optimal weights: {e}")
            return self.base_weights

    def _detect_industry(self, job_data: Dict[str, Any]) -> IndustryType:
        """Detect industry based on job data"""
        title = job_data.get('title', '').lower()
        company = job_data.get('company_name', '').lower()
        description = job_data.get('description', '').lower()
        
        # Technology indicators
        tech_keywords = ['software', 'developer', 'engineer', 'programmer', 'tech', 'it', 'data scientist', 'ai', 'ml']
        if any(keyword in title or keyword in description for keyword in tech_keywords):
            return IndustryType.TECHNOLOGY
        
        # Finance indicators
        finance_keywords = ['finance', 'banking', 'investment', 'trading', 'analyst', 'accountant', 'audit']
        if any(keyword in title or keyword in description for keyword in finance_keywords):
            return IndustryType.FINANCE
        
        # Healthcare indicators
        healthcare_keywords = ['health', 'medical', 'nurse', 'doctor', 'pharmaceutical', 'clinical', 'patient']
        if any(keyword in title or keyword in description for keyword in healthcare_keywords):
            return IndustryType.HEALTHCARE
        
        # Startup indicators
        startup_keywords = ['startup', 'scale', 'growth', 'venture', 'funding', 'series a', 'series b']
        if any(keyword in company or keyword in description for keyword in startup_keywords):
            return IndustryType.STARTUP
        
        # Enterprise indicators
        enterprise_keywords = ['enterprise', 'corporate', 'fortune 500', 'multinational', 'global']
        if any(keyword in company or keyword in description for keyword in enterprise_keywords):
            return IndustryType.ENTERPRISE
        
        # Default to technology for tech-heavy roles
        return IndustryType.TECHNOLOGY

    def _detect_career_stage(self, user_profile: Dict[str, Any], job_data: Dict[str, Any]) -> CareerStage:
        """Detect career stage based on user profile and job requirements"""
        user_experience = user_profile.get('experience_years', 0)
        job_title = job_data.get('title', '').lower()
        job_experience_req = job_data.get('min_experience_years', 0)
        
        # Job title-based detection
        if any(keyword in job_title for keyword in ['senior', 'lead', 'principal', 'staff', 'architect']):
            return CareerStage.SENIOR
        elif any(keyword in job_title for keyword in ['manager', 'director', 'vp', 'head of', 'chief']):
            return CareerStage.LEAD
        elif any(keyword in job_title for keyword in ['ceo', 'cto', 'cfo', 'president', 'executive']):
            return CareerStage.EXECUTIVE
        elif any(keyword in job_title for keyword in ['junior', 'entry', 'associate', 'trainee', 'intern']):
            return CareerStage.ENTRY
        
        # Experience-based detection
        if user_experience < 1:
            return CareerStage.ENTRY
        elif user_experience < 3:
            return CareerStage.JUNIOR
        elif user_experience < 7:
            return CareerStage.MID
        elif user_experience < 12:
            return CareerStage.SENIOR
        else:
            return CareerStage.LEAD

    def _apply_career_stage_adjustments(self, weights: WeightConfig, career_stage: CareerStage) -> WeightConfig:
        """Apply career stage specific adjustments to weights"""
        adjustments = self.career_stage_adjustments.get(career_stage, {})
        
        return WeightConfig(
            skill_weight=weights.skill_weight * adjustments.get('skill_weight', 1.0),
            experience_weight=weights.experience_weight * adjustments.get('experience_weight', 1.0),
            location_weight=weights.location_weight * adjustments.get('location_weight', 1.0),
            salary_weight=weights.salary_weight * adjustments.get('salary_weight', 1.0),
            semantic_weight=weights.semantic_weight * adjustments.get('semantic_weight', 1.0),
            market_demand_weight=weights.market_demand_weight,
            career_growth_weight=weights.career_growth_weight
        )

    def _apply_user_preferences(self, weights: WeightConfig, user_profile: Dict[str, Any]) -> WeightConfig:
        """Apply user-specific preference adjustments"""
        # Remote work preference
        remote_preference = user_profile.get('remote_preference', 0.5)
        if remote_preference > 0.7:
            weights.location_weight *= 0.5  # Reduce location importance
        
        # Salary sensitivity
        salary_sensitivity = user_profile.get('salary_sensitivity', 0.5)
        if salary_sensitivity > 0.7:
            weights.salary_weight *= 1.3  # Increase salary importance
        
        # Career growth focus
        growth_focus = user_profile.get('career_growth_focus', 0.5)
        if growth_focus > 0.7:
            weights.career_growth_weight *= 2.0  # Double career growth importance
        
        return weights

    def _apply_market_conditions(self, weights: WeightConfig, market_context: Dict[str, Any]) -> WeightConfig:
        """Apply market condition adjustments"""
        # Remote work trend
        remote_trend = market_context.get('remote_work_trend', 0.5)
        if remote_trend > 0.6:
            weights.location_weight *= (1.0 - remote_trend * 0.3)  # Reduce location importance
        
        # Skill shortage
        skill_shortage = market_context.get('skill_shortage', 0.5)
        if skill_shortage > 0.6:
            weights.skill_weight *= (1.0 + skill_shortage * 0.2)  # Increase skill importance
        
        # Economic uncertainty
        economic_uncertainty = market_context.get('economic_uncertainty', 0.5)
        if economic_uncertainty > 0.6:
            weights.salary_weight *= 0.8  # Reduce salary importance in uncertain times
        
        return weights

    def _normalize_weights(self, weights: WeightConfig) -> WeightConfig:
        """Normalize weights to ensure they sum to 1.0"""
        total = (weights.skill_weight + weights.experience_weight + 
                weights.location_weight + weights.salary_weight + 
                weights.semantic_weight + weights.market_demand_weight + 
                weights.career_growth_weight)
        
        if total == 0:
            return self.base_weights
        
        return WeightConfig(
            skill_weight=weights.skill_weight / total,
            experience_weight=weights.experience_weight / total,
            location_weight=weights.location_weight / total,
            salary_weight=weights.salary_weight / total,
            semantic_weight=weights.semantic_weight / total,
            market_demand_weight=weights.market_demand_weight / total,
            career_growth_weight=weights.career_growth_weight / total
        )

    def get_weight_explanation(self, weights: WeightConfig, context: Dict[str, Any]) -> str:
        """Generate human-readable explanation of weight choices"""
        industry = context.get('industry', 'general')
        career_stage = context.get('career_stage', 'mid')
        
        explanation = f"Weights optimized for {industry} industry, {career_stage} level:\n"
        explanation += f"• Skills: {weights.skill_weight:.1%} (technical competency)\n"
        explanation += f"• Experience: {weights.experience_weight:.1%} (years of experience)\n"
        explanation += f"• Location: {weights.location_weight:.1%} (geographic fit)\n"
        explanation += f"• Salary: {weights.salary_weight:.1%} (compensation alignment)\n"
        explanation += f"• Job Fit: {weights.semantic_weight:.1%} (description alignment)\n"
        explanation += f"• Market: {weights.market_demand_weight:.1%} (market demand)\n"
        explanation += f"• Growth: {weights.career_growth_weight:.1%} (career advancement)"
        
        return explanation

# Singleton instance
weight_calculator = DynamicWeightCalculator()
