import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from config.settings import settings
import re
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self):
        self.skill_features = settings.skill_features
        self.location_features = settings.location_features
        self.job_type_features = settings.job_type_features
        
        logger.info(f"FeatureEngineer initialized with {len(self.skill_features)} skill features")
    
    def extract_job_features(self, job_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from job data"""
        try:
            features = {}
            
            # Skill features (binary)
            required_skills = job_data.get('required_skills', []) or []
            preferred_skills = job_data.get('preferred_skills', []) or []
            all_skills = required_skills + preferred_skills
            
            # Normalize skills to lowercase for matching
            all_skills_lower = [str(skill).lower().strip() for skill in all_skills]
            
            for skill in self.skill_features:
                skill_lower = skill.lower()
                # Check if skill appears in any of the job skills
                has_skill = any(skill_lower in job_skill for job_skill in all_skills_lower)
                features[f'has_{skill_lower}'] = 1.0 if has_skill else 0.0
            
            # Location features
            location = str(job_data.get('location', '')).lower()
            remote_work = str(job_data.get('remote_work_allowed', '')).lower()
            
            features['is_remote'] = 1.0 if ('remote' in location or remote_work in ['yes', 'true', '1']) else 0.0
            features['is_hybrid'] = 1.0 if ('hybrid' in location or remote_work == 'hybrid') else 0.0
            features['is_office'] = 1.0 if (features['is_remote'] == 0.0 and features['is_hybrid'] == 0.0) else 0.0
            
            # Job type features
            job_type = str(job_data.get('job_type', '')).lower()
            for jt in self.job_type_features:
                features[f'is_{jt}'] = 1.0 if jt in job_type else 0.0
            
            # Salary features
            min_salary = float(job_data.get('min_salary', 0) or 0)
            max_salary = float(job_data.get('max_salary', 0) or 0)
            avg_salary = (min_salary + max_salary) / 2 if min_salary > 0 and max_salary > 0 else 0
            
            # Normalize salary to 100k scale
            features['salary_range_low'] = min_salary / 100000.0
            features['salary_range_high'] = max_salary / 100000.0
            features['salary_range_avg'] = avg_salary / 100000.0
            
            # Company features
            company_name = str(job_data.get('company_name', '')).lower()
            features['is_startup'] = 1.0 if any(word in company_name for word in ['startup', 'inc', 'llc', 'corp', 'ltd']) else 0.0
            features['is_enterprise'] = 1.0 if any(word in company_name for word in ['enterprise', 'corporation', 'group', 'systems']) else 0.0
            
            # Experience features
            min_exp = float(job_data.get('min_experience_years', 0) or 0)
            max_exp = float(job_data.get('max_experience_years', 0) or 0)
            features['min_experience'] = min_exp / 10.0  # Normalize to 10 years
            features['max_experience'] = max_exp / 10.0
            
            # Job level features
            if min_exp <= 2:
                features['is_junior'] = 1.0
                features['is_mid'] = 0.0
                features['is_senior'] = 0.0
            elif min_exp <= 5:
                features['is_junior'] = 0.0
                features['is_mid'] = 1.0
                features['is_senior'] = 0.0
            else:
                features['is_junior'] = 0.0
                features['is_mid'] = 0.0
                features['is_senior'] = 1.0
            
            # Additional features
            features['has_benefits'] = 1.0 if job_data.get('benefits') else 0.0
            features['is_active'] = 1.0 if job_data.get('status') == 'active' else 0.0
            
            logger.debug(f"Extracted {len(features)} features for job {job_data.get('id', 'unknown')}")
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features from job data: {e}")
            # Return default features
            return self._get_default_features()
    
    def _get_default_features(self) -> Dict[str, float]:
        """Get default feature values when extraction fails"""
        features = {}
        
        # Skill features
        for skill in self.skill_features:
            features[f'has_{skill.lower()}'] = 0.0
        
        # Location features
        features.update({
            'is_remote': 0.0,
            'is_hybrid': 0.0,
            'is_office': 1.0
        })
        
        # Job type features
        for jt in self.job_type_features:
            features[f'is_{jt}'] = 0.0
        features['is_full_time'] = 1.0  # Default to full-time
        
        # Salary features
        features.update({
            'salary_range_low': 0.0,
            'salary_range_high': 0.0,
            'salary_range_avg': 0.0
        })
        
        # Company features
        features.update({
            'is_startup': 0.0,
            'is_enterprise': 0.0
        })
        
        # Experience features
        features.update({
            'min_experience': 0.0,
            'max_experience': 0.0,
            'is_junior': 1.0,
            'is_mid': 0.0,
            'is_senior': 0.0
        })
        
        # Additional features
        features.update({
            'has_benefits': 0.0,
            'is_active': 1.0
        })
        
        return features
    
    def create_feature_matrix(self, jobs_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create feature matrix from list of jobs"""
        try:
            features_list = []
            for i, job in enumerate(jobs_data):
                features = self.extract_job_features(job)
                features_list.append(features)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1} jobs for feature extraction")
            
            df = pd.DataFrame(features_list)
            logger.info(f"Created feature matrix with shape {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error creating feature matrix: {e}")
            return pd.DataFrame()
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        features = []
        
        # Skill features
        for skill in self.skill_features:
            features.append(f'has_{skill.lower()}')
        
        # Location features
        features.extend(['is_remote', 'is_hybrid', 'is_office'])
        
        # Job type features
        for jt in self.job_type_features:
            features.append(f'is_{jt}')
        
        # Salary features
        features.extend(['salary_range_low', 'salary_range_high', 'salary_range_avg'])
        
        # Company features
        features.extend(['is_startup', 'is_enterprise'])
        
        # Experience features
        features.extend(['min_experience', 'max_experience'])
        
        # Job level features
        features.extend(['is_junior', 'is_mid', 'is_senior'])
        
        # Additional features
        features.extend(['has_benefits', 'is_active'])
        
        return features
    
    def validate_features(self, features: Dict[str, float]) -> bool:
        """Validate that all required features are present"""
        required_features = self.get_feature_names()
        
        for feature in required_features:
            if feature not in features:
                logger.warning(f"Missing feature: {feature}")
                return False
        
        return True

