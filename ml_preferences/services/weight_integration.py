import sys
import os
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import logging

# Add the parent directory to the path to import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.database import get_db
from models.ml_models import UserWeightAdjustments
from services.weight_updater import WeightUpdater

logger = logging.getLogger(__name__)

class WeightIntegration:
    """Integration service to connect ML preferences with existing weight calculator"""
    
    def __init__(self):
        self.weight_updater = WeightUpdater()
        logger.info("WeightIntegration initialized")
    
    def get_ml_weight_adjustments(self, user_id: int) -> Dict[str, float]:
        """Get ML-based weight adjustments for a user"""
        try:
            weight_adj = self.weight_updater.get_user_weight_adjustments(user_id)
            
            if not weight_adj:
                logger.debug(f"No ML weight adjustments found for user {user_id}, using defaults")
                return self._get_default_adjustments()
            
            logger.debug(f"Retrieved ML weight adjustments for user {user_id}")
            return weight_adj
            
        except Exception as e:
            logger.error(f"Error getting ML weight adjustments for user {user_id}: {e}")
            return self._get_default_adjustments()
    
    def _get_default_adjustments(self) -> Dict[str, float]:
        """Get default weight adjustments when no ML data is available"""
        return {
            'skill_weight_adjustment': 1.0,
            'location_weight_adjustment': 1.0,
            'salary_weight_adjustment': 1.0,
            'company_weight_adjustment': 1.0,
            'job_type_weight_adjustment': 1.0,
            'remote_preference_boost': 1.0,
            'python_skill_boost': 1.0,
            'startup_company_boost': 1.0,
            'is_new_user': True,
            'feedback_count': 0,
            'learning_rate': 0.3
        }
    
    def apply_ml_adjustments_to_weights(self, base_weights: Dict[str, float], 
                                      user_id: int) -> Dict[str, float]:
        """Apply ML adjustments to base weights"""
        try:
            # Get ML adjustments
            ml_adjustments = self.get_ml_weight_adjustments(user_id)
            
            # Apply adjustments to base weights
            adjusted_weights = base_weights.copy()
            
            # Apply skill weight adjustment
            if 'skill_weight' in adjusted_weights:
                adjusted_weights['skill_weight'] *= ml_adjustments['skill_weight_adjustment']
            
            # Apply location weight adjustment
            if 'location_weight' in adjusted_weights:
                adjusted_weights['location_weight'] *= ml_adjustments['location_weight_adjustment']
            
            # Apply salary weight adjustment
            if 'salary_weight' in adjusted_weights:
                adjusted_weights['salary_weight'] *= ml_adjustments['salary_weight_adjustment']
            
            # Apply company weight adjustment
            if 'company_weight' in adjusted_weights:
                adjusted_weights['company_weight'] *= ml_adjustments['company_weight_adjustment']
            
            # Apply job type weight adjustment
            if 'job_type_weight' in adjusted_weights:
                adjusted_weights['job_type_weight'] *= ml_adjustments['job_type_weight_adjustment']
            
            # Add ML-specific adjustments
            adjusted_weights['remote_preference_boost'] = ml_adjustments['remote_preference_boost']
            adjusted_weights['python_skill_boost'] = ml_adjustments['python_skill_boost']
            adjusted_weights['startup_company_boost'] = ml_adjustments['startup_company_boost']
            
            # Add metadata
            adjusted_weights['ml_adjustments_applied'] = True
            adjusted_weights['is_new_user'] = ml_adjustments['is_new_user']
            adjusted_weights['feedback_count'] = ml_adjustments['feedback_count']
            adjusted_weights['learning_rate'] = ml_adjustments['learning_rate']
            
            logger.debug(f"Applied ML adjustments to weights for user {user_id}")
            return adjusted_weights
            
        except Exception as e:
            logger.error(f"Error applying ML adjustments to weights for user {user_id}: {e}")
            # Return base weights with ML flag set to False
            base_weights['ml_adjustments_applied'] = False
            return base_weights
    
    def get_user_preference_summary(self, user_id: int) -> Dict[str, Any]:
        """Get a summary of user preferences learned by ML"""
        try:
            ml_adjustments = self.get_ml_weight_adjustments(user_id)
            
            # Analyze preferences
            preferences = {
                'user_id': user_id,
                'is_new_user': ml_adjustments['is_new_user'],
                'feedback_count': ml_adjustments['feedback_count'],
                'learning_rate': ml_adjustments['learning_rate'],
                'preferences': {}
            }
            
            # Skill preferences
            if ml_adjustments['skill_weight_adjustment'] > 1.1:
                preferences['preferences']['skills'] = 'High importance'
            elif ml_adjustments['skill_weight_adjustment'] < 0.9:
                preferences['preferences']['skills'] = 'Low importance'
            else:
                preferences['preferences']['skills'] = 'Neutral'
            
            # Location preferences
            if ml_adjustments['location_weight_adjustment'] > 1.1:
                preferences['preferences']['location'] = 'High importance'
            elif ml_adjustments['location_weight_adjustment'] < 0.9:
                preferences['preferences']['location'] = 'Low importance'
            else:
                preferences['preferences']['location'] = 'Neutral'
            
            # Remote work preference
            if ml_adjustments['remote_preference_boost'] > 1.2:
                preferences['preferences']['remote_work'] = 'Strong preference'
            elif ml_adjustments['remote_preference_boost'] > 1.1:
                preferences['preferences']['remote_work'] = 'Moderate preference'
            else:
                preferences['preferences']['remote_work'] = 'No strong preference'
            
            # Python skill preference
            if ml_adjustments['python_skill_boost'] > 1.2:
                preferences['preferences']['python_skills'] = 'Strong preference'
            elif ml_adjustments['python_skill_boost'] > 1.1:
                preferences['preferences']['python_skills'] = 'Moderate preference'
            else:
                preferences['preferences']['python_skills'] = 'No strong preference'
            
            # Startup preference
            if ml_adjustments['startup_company_boost'] > 1.2:
                preferences['preferences']['startup_companies'] = 'Strong preference'
            elif ml_adjustments['startup_company_boost'] > 1.1:
                preferences['preferences']['startup_companies'] = 'Moderate preference'
            else:
                preferences['preferences']['startup_companies'] = 'No strong preference'
            
            logger.debug(f"Generated preference summary for user {user_id}")
            return preferences
            
        except Exception as e:
            logger.error(f"Error generating preference summary for user {user_id}: {e}")
            return {
                'user_id': user_id,
                'error': str(e)
            }
    
    def update_user_feedback(self, user_id: int, job_id: int, feedback_type: str, 
                           feedback_value: bool) -> bool:
        """Update user feedback and trigger weight recalculation if needed"""
        try:
            # This would typically update the user_job_preferences table
            # For now, we'll just log the feedback
            logger.info(f"User {user_id} gave {feedback_type} feedback for job {job_id}: {feedback_value}")
            
            # Check if we should trigger immediate weight update
            # This could be based on feedback count or other criteria
            feedback_stats = self._get_user_feedback_stats(user_id)
            
            if feedback_stats['total_feedback'] % 10 == 0:  # Update every 10 feedback actions
                logger.info(f"Triggering weight update for user {user_id} after {feedback_stats['total_feedback']} feedback actions")
                # In a real implementation, this might trigger an async weight update
                # For now, we'll just log it
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user feedback: {e}")
            return False
    
    def _get_user_feedback_stats(self, user_id: int) -> Dict[str, int]:
        """Get user feedback statistics"""
        try:
            db = next(get_db())
            
            from sqlalchemy import text
            query = text("""
                SELECT 
                    COUNT(*) as total_feedback,
                    SUM(CASE WHEN is_bookmarked = 1 OR is_relevant = 1 THEN 1 ELSE 0 END) as positive_feedback,
                    SUM(CASE WHEN is_hidden = 1 THEN 1 ELSE 0 END) as negative_feedback
                FROM user_job_preferences 
                WHERE user_id = :user_id
                AND (is_bookmarked = 1 OR is_relevant = 1 OR is_hidden = 1 OR is_maybe_later = 1)
            """)
            
            result = db.execute(query, {'user_id': user_id})
            row = result.fetchone()
            
            if row:
                return {
                    'total_feedback': row[0] or 0,
                    'positive_feedback': row[1] or 0,
                    'negative_feedback': row[2] or 0
                }
            else:
                return {
                    'total_feedback': 0,
                    'positive_feedback': 0,
                    'negative_feedback': 0
                }
                
        except Exception as e:
            logger.error(f"Error getting feedback stats for user {user_id}: {e}")
            return {
                'total_feedback': 0,
                'positive_feedback': 0,
                'negative_feedback': 0
            }
        finally:
            db.close()
    
    def get_ml_system_status(self) -> Dict[str, Any]:
        """Get overall ML system status"""
        try:
            db = next(get_db())
            
            # Count users with ML models
            from models.ml_models import UserMLModel, UserWeightAdjustments
            users_with_models = db.query(UserMLModel).count()
            users_with_adjustments = db.query(UserWeightAdjustments).count()
            
            # Get recent training activity
            from sqlalchemy import text
            recent_training_query = text("""
                SELECT COUNT(*) as recent_models
                FROM user_ml_models 
                WHERE trained_at > datetime('now', '-7 days')
            """)
            
            result = db.execute(recent_training_query)
            recent_models = result.fetchone()[0]
            
            return {
                'users_with_models': users_with_models,
                'users_with_adjustments': users_with_adjustments,
                'recent_models_trained': recent_models,
                'system_active': True
            }
            
        except Exception as e:
            logger.error(f"Error getting ML system status: {e}")
            return {
                'error': str(e),
                'system_active': False
            }
        finally:
            db.close()

