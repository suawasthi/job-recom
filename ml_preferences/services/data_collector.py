import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

# Add the parent directory to the path to import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.database import get_db
from config.settings import settings

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.min_feedback_threshold = settings.min_feedback_threshold
        self.max_feedback_threshold = settings.max_feedback_threshold
        
        logger.info("DataCollector initialized")
    
    def get_users_with_feedback(self) -> List[int]:
        """Get all users who have given feedback"""
        try:
            db = next(get_db())
            
            # Query to get users with feedback
            query = text("""
                SELECT DISTINCT user_id 
                FROM user_job_preferences 
                WHERE (is_bookmarked = 1 OR is_relevant = 1 OR is_hidden = 1 OR is_maybe_later = 1)
                ORDER BY user_id
            """)
            
            result = db.execute(query)
            user_ids = [row[0] for row in result.fetchall()]
            
            logger.info(f"Found {len(user_ids)} users with feedback")
            return user_ids
            
        except Exception as e:
            logger.error(f"Error getting users with feedback: {e}")
            return []
        finally:
            db.close()
    
    def get_user_feedback_data(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all feedback data for a specific user"""
        try:
            db = next(get_db())
            
            # Query to get user feedback with job data
            query = text("""
                SELECT 
                    ujp.id as preference_id,
                    ujp.user_id,
                    ujp.job_id,
                    ujp.is_relevant,
                    ujp.is_maybe_later,
                    ujp.is_bookmarked,
                    ujp.is_hidden,
                    ujp.created_at as feedback_date,
                    j.id as job_id,
                    j.title,
                    j.description,
                    j.company_name,
                    j.location,
                    j.job_type,
                    j.required_skills,
                    j.preferred_skills,
                    j.min_experience_years,
                    j.max_experience_years,
                    j.min_salary,
                    j.max_salary,
                    j.remote_work_allowed,
                    j.benefits,
                    j.status
                FROM user_job_preferences ujp
                JOIN jobs j ON ujp.job_id = j.id
                WHERE ujp.user_id = :user_id
                AND (ujp.is_bookmarked = 1 OR ujp.is_relevant = 1 OR ujp.is_hidden = 1 OR ujp.is_maybe_later = 1)
                ORDER BY ujp.created_at DESC
                LIMIT :max_feedback
            """)
            
            result = db.execute(query, {
                'user_id': user_id,
                'max_feedback': self.max_feedback_threshold
            })
            
            feedback_data = []
            for row in result.fetchall():
                feedback_item = {
                    'preference_id': row[0],
                    'user_id': row[1],
                    'job_id': row[2],
                    'is_relevant': bool(row[3]),
                    'is_maybe_later': bool(row[4]),
                    'is_bookmarked': bool(row[5]),
                    'is_hidden': bool(row[6]),
                    'feedback_date': row[7],
                    'job': {
                        'id': row[8],
                        'title': row[9],
                        'description': row[10],
                        'company_name': row[11],
                        'location': row[12],
                        'job_type': row[13],
                        'required_skills': row[14],
                        'preferred_skills': row[15],
                        'min_experience_years': row[16],
                        'max_experience_years': row[17],
                        'min_salary': row[18],
                        'max_salary': row[19],
                        'remote_work_allowed': row[20],
                        'benefits': row[21],
                        'status': row[22]
                    }
                }
                feedback_data.append(feedback_item)
            
            logger.info(f"Retrieved {len(feedback_data)} feedback items for user {user_id}")
            return feedback_data
            
        except Exception as e:
            logger.error(f"Error getting feedback data for user {user_id}: {e}")
            return []
        finally:
            db.close()
    
    def get_user_feedback_stats(self, user_id: int) -> Dict[str, int]:
        """Get feedback statistics for a user"""
        try:
            db = next(get_db())
            
            query = text("""
                SELECT 
                    COUNT(*) as total_feedback,
                    SUM(CASE WHEN is_bookmarked = 1 OR is_relevant = 1 THEN 1 ELSE 0 END) as positive_feedback,
                    SUM(CASE WHEN is_hidden = 1 THEN 1 ELSE 0 END) as negative_feedback,
                    SUM(CASE WHEN is_maybe_later = 1 THEN 1 ELSE 0 END) as neutral_feedback
                FROM user_job_preferences 
                WHERE user_id = :user_id
                AND (is_bookmarked = 1 OR is_relevant = 1 OR is_hidden = 1 OR is_maybe_later = 1)
            """)
            
            result = db.execute(query, {'user_id': user_id})
            row = result.fetchone()
            
            if row:
                stats = {
                    'total_feedback': row[0] or 0,
                    'positive_feedback': row[1] or 0,
                    'negative_feedback': row[2] or 0,
                    'neutral_feedback': row[3] or 0
                }
            else:
                stats = {
                    'total_feedback': 0,
                    'positive_feedback': 0,
                    'negative_feedback': 0,
                    'neutral_feedback': 0
                }
            
            logger.debug(f"User {user_id} feedback stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting feedback stats for user {user_id}: {e}")
            return {
                'total_feedback': 0,
                'positive_feedback': 0,
                'negative_feedback': 0,
                'neutral_feedback': 0
            }
        finally:
            db.close()
    
    def calculate_feature_correlations(self, user_id: int) -> Dict[str, float]:
        """Calculate feature correlations for fallback strategy"""
        try:
            feedback_data = self.get_user_feedback_data(user_id)
            
            if len(feedback_data) < 5:  # Need minimum data for correlation
                return {}
            
            # Import here to avoid circular imports
            from services.feature_engineer import FeatureEngineer
            feature_engineer = FeatureEngineer()
            
            # Prepare data for correlation
            features_list = []
            labels = []
            
            for feedback in feedback_data:
                job_data = feedback['job']
                features = feature_engineer.extract_job_features(job_data)
                features_list.append(features)
                
                # Create label: 1 for positive, 0 for negative
                is_positive = feedback.get('is_bookmarked', False) or feedback.get('is_relevant', False)
                is_negative = feedback.get('is_hidden', False)
                
                if is_positive and not is_negative:
                    labels.append(1)
                elif is_negative and not is_positive:
                    labels.append(0)
                else:
                    labels.append(0.5)  # Neutral
            
            if len(features_list) != len(labels):
                features_list = features_list[:len(labels)]
            
            # Calculate correlations
            correlations = {}
            
            # Group features by category
            feature_categories = {
                'skill': [f for f in features_list[0].keys() if f.startswith('has_')],
                'location': ['is_remote', 'is_hybrid', 'is_office'],
                'salary': ['salary_range_low', 'salary_range_high', 'salary_range_avg'],
                'company': ['is_startup', 'is_enterprise']
            }
            
            for category, feature_names in feature_categories.items():
                category_correlation = 0.0
                valid_features = 0
                
                for feature_name in feature_names:
                    if feature_name in features_list[0]:
                        feature_values = [f[feature_name] for f in features_list]
                        
                        # Calculate correlation between feature and labels
                        correlation = self._calculate_correlation(feature_values, labels)
                        if abs(correlation) > 0.1:  # Only consider meaningful correlations
                            category_correlation += abs(correlation)
                            valid_features += 1
                
                if valid_features > 0:
                    correlations[f'{category}_correlation'] = category_correlation / valid_features
                else:
                    correlations[f'{category}_correlation'] = 0.0
            
            logger.info(f"Calculated correlations for user {user_id}: {correlations}")
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating correlations for user {user_id}: {e}")
            return {}
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient between two lists"""
        try:
            import numpy as np
            
            if len(x) != len(y) or len(x) < 2:
                return 0.0
            
            x_array = np.array(x)
            y_array = np.array(y)
            
            correlation = np.corrcoef(x_array, y_array)[0, 1]
            
            # Handle NaN values
            if np.isnan(correlation):
                return 0.0
            
            return float(correlation)
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    def is_new_user(self, user_id: int) -> bool:
        """Check if user is new (has limited feedback)"""
        stats = self.get_user_feedback_stats(user_id)
        return stats['total_feedback'] < settings.new_user_min_feedback
    
    def has_sufficient_data(self, user_id: int) -> bool:
        """Check if user has sufficient data for ML training"""
        stats = self.get_user_feedback_stats(user_id)
        return stats['total_feedback'] >= self.min_feedback_threshold

