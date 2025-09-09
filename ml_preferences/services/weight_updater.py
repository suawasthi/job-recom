import sys
import os
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

# Add the parent directory to the path to import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.database import get_db
from models.ml_models import UserWeightAdjustments, UserFeedbackStats, UserMLModel
from services.model_trainer import ModelTrainer
from services.data_collector import DataCollector
from config.settings import settings

logger = logging.getLogger(__name__)

class WeightUpdater:
    def __init__(self):
        self.model_trainer = ModelTrainer()
        self.data_collector = DataCollector()
        
        logger.info("WeightUpdater initialized")
    
    def update_user_weights(self, user_id: int, feature_importance: Optional[Dict[str, float]] = None) -> bool:
        """Update user weights based on feature importance or fallback strategy"""
        try:
            logger.info(f"Updating weights for user {user_id}")
            
            db = next(get_db())
            
            # Check if user is new
            is_new_user = self.data_collector.is_new_user(user_id)
            feedback_stats = self.data_collector.get_user_feedback_stats(user_id)
            
            logger.info(f"User {user_id}: New user: {is_new_user}, Feedback count: {feedback_stats['total_feedback']}")
            
            # Get or create weight adjustments
            weight_adj = db.query(UserWeightAdjustments).filter(
                UserWeightAdjustments.user_id == user_id
            ).first()
            
            if not weight_adj:
                weight_adj = UserWeightAdjustments(user_id=user_id)
                db.add(weight_adj)
            
            # Update feedback count and new user status
            weight_adj.feedback_count = feedback_stats['total_feedback']
            weight_adj.is_new_user = is_new_user
            
            # Choose strategy based on user status and data availability
            if is_new_user:
                success = self._update_new_user_weights(weight_adj, feedback_stats)
            elif feature_importance:
                success = self._update_ml_weights(weight_adj, feature_importance)
            else:
                success = self._update_fallback_weights(weight_adj, user_id)
            
            if success:
                # Apply smoothing to prevent extreme changes
                self._apply_weight_smoothing(weight_adj)
                
                # Update learning rate based on feedback count
                self._update_learning_rate(weight_adj)
                
                db.commit()
                logger.info(f"Successfully updated weights for user {user_id}")
                return True
            else:
                db.rollback()
                logger.error(f"Failed to update weights for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating weights for user {user_id}: {e}")
            if 'db' in locals():
                db.rollback()
            return False
        finally:
            if 'db' in locals():
                db.close()
    
    def _update_new_user_weights(self, weight_adj: UserWeightAdjustments, feedback_stats: Dict[str, int]) -> bool:
        """Update weights for new users with limited feedback"""
        try:
            logger.info(f"Applying new user strategy for user {weight_adj.user_id}")
            
            # For new users, apply conservative adjustments based on limited feedback
            total_feedback = feedback_stats['total_feedback']
            positive_feedback = feedback_stats['positive_feedback']
            negative_feedback = feedback_stats['negative_feedback']
            
            if total_feedback < settings.new_user_min_feedback:
                # Not enough feedback, use default weights
                logger.info(f"User {weight_adj.user_id}: Not enough feedback for adjustments")
                return True
            
            # Calculate basic preference ratios
            positive_ratio = positive_feedback / total_feedback if total_feedback > 0 else 0.5
            negative_ratio = negative_feedback / total_feedback if total_feedback > 0 else 0.5
            
            # Apply conservative adjustments
            base_boost = settings.new_user_default_boost
            learning_rate = settings.new_user_learning_rate
            
            # Adjust weights based on feedback patterns
            if positive_ratio > 0.6:  # User seems to like most jobs
                weight_adj.skill_weight_adjustment = 1.0 + (base_boost - 1.0) * learning_rate
                weight_adj.location_weight_adjustment = 1.0 + (base_boost - 1.0) * learning_rate
            elif negative_ratio > 0.6:  # User seems to dislike most jobs
                weight_adj.skill_weight_adjustment = 1.0 - (base_boost - 1.0) * learning_rate
                weight_adj.location_weight_adjustment = 1.0 - (base_boost - 1.0) * learning_rate
            else:
                # Mixed feedback, keep neutral
                weight_adj.skill_weight_adjustment = 1.0
                weight_adj.location_weight_adjustment = 1.0
            
            # Apply default boosts for common preferences
            weight_adj.remote_preference_boost = base_boost
            weight_adj.python_skill_boost = base_boost
            weight_adj.startup_company_boost = base_boost
            
            logger.info(f"Applied new user weights for user {weight_adj.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating new user weights: {e}")
            return False
    
    def _update_ml_weights(self, weight_adj: UserWeightAdjustments, feature_importance: Dict[str, float]) -> bool:
        """Update weights using ML model feature importance"""
        try:
            logger.info(f"Applying ML strategy for user {weight_adj.user_id}")
            
            # Update weights based on feature importance
            self._update_skill_weights(weight_adj, feature_importance)
            self._update_location_weights(weight_adj, feature_importance)
            self._update_salary_weights(weight_adj, feature_importance)
            self._update_company_weights(weight_adj, feature_importance)
            self._update_job_type_weights(weight_adj, feature_importance)
            
            logger.info(f"Applied ML weights for user {weight_adj.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating ML weights: {e}")
            return False
    
    def _update_fallback_weights(self, weight_adj: UserWeightAdjustments, user_id: int) -> bool:
        """Update weights using statistical correlation fallback"""
        try:
            logger.info(f"Applying fallback strategy for user {weight_adj.user_id}")
            
            if not settings.use_statistical_correlation:
                logger.info(f"Statistical correlation disabled, using default weights")
                return True
            
            # Calculate feature correlations
            correlations = self.data_collector.calculate_feature_correlations(user_id)
            
            if not correlations:
                logger.info(f"No correlations found for user {user_id}, using default weights")
                return True
            
            # Apply correlations as weight adjustments
            for correlation_type, correlation_value in correlations.items():
                if abs(correlation_value) > settings.correlation_threshold:
                    adjustment = self._calculate_adjustment_from_correlation(correlation_value)
                    
                    if 'skill' in correlation_type:
                        weight_adj.skill_weight_adjustment = adjustment
                    elif 'location' in correlation_type:
                        weight_adj.location_weight_adjustment = adjustment
                    elif 'salary' in correlation_type:
                        weight_adj.salary_weight_adjustment = adjustment
                    elif 'company' in correlation_type:
                        weight_adj.company_weight_adjustment = adjustment
            
            logger.info(f"Applied fallback weights for user {weight_adj.user_id}: {correlations}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating fallback weights: {e}")
            return False
    
    def _update_skill_weights(self, weight_adj: UserWeightAdjustments, feature_importance: Dict[str, float]):
        """Update skill-related weights"""
        # Get average importance of skill features
        skill_features = [f for f in feature_importance.keys() if f.startswith('has_')]
        if skill_features:
            avg_skill_importance = sum(feature_importance[f] for f in skill_features) / len(skill_features)
            weight_adj.skill_weight_adjustment = self._calculate_adjustment(avg_skill_importance)
            
            # Special handling for Python (common skill)
            if 'has_python' in feature_importance:
                weight_adj.python_skill_boost = self._calculate_adjustment(feature_importance['has_python'])
    
    def _update_location_weights(self, weight_adj: UserWeightAdjustments, feature_importance: Dict[str, float]):
        """Update location-related weights"""
        location_features = ['is_remote', 'is_hybrid', 'is_office']
        location_importance = sum(feature_importance.get(f, 0) for f in location_features)
        
        if location_importance > 0:
            weight_adj.location_weight_adjustment = self._calculate_adjustment(location_importance)
            
            # Special handling for remote preference
            if 'is_remote' in feature_importance:
                weight_adj.remote_preference_boost = self._calculate_adjustment(feature_importance['is_remote'])
    
    def _update_salary_weights(self, weight_adj: UserWeightAdjustments, feature_importance: Dict[str, float]):
        """Update salary-related weights"""
        salary_features = ['salary_range_low', 'salary_range_high', 'salary_range_avg']
        salary_importance = sum(feature_importance.get(f, 0) for f in salary_features)
        
        if salary_importance > 0:
            weight_adj.salary_weight_adjustment = self._calculate_adjustment(salary_importance)
    
    def _update_company_weights(self, weight_adj: UserWeightAdjustments, feature_importance: Dict[str, float]):
        """Update company-related weights"""
        company_features = ['is_startup', 'is_enterprise']
        company_importance = sum(feature_importance.get(f, 0) for f in company_features)
        
        if company_importance > 0:
            weight_adj.company_weight_adjustment = self._calculate_adjustment(company_importance)
            
            # Special handling for startup preference
            if 'is_startup' in feature_importance:
                weight_adj.startup_company_boost = self._calculate_adjustment(feature_importance['is_startup'])
    
    def _update_job_type_weights(self, weight_adj: UserWeightAdjustments, feature_importance: Dict[str, float]):
        """Update job type-related weights"""
        job_type_features = [f for f in feature_importance.keys() if f.startswith('is_') and f in ['is_full_time', 'is_part_time', 'is_contract', 'is_freelance']]
        job_type_importance = sum(feature_importance.get(f, 0) for f in job_type_features)
        
        if job_type_importance > 0:
            weight_adj.job_type_weight_adjustment = self._calculate_adjustment(job_type_importance)
    
    def _calculate_adjustment(self, importance: float) -> float:
        """Calculate weight adjustment from feature importance"""
        # Convert importance (0-1) to adjustment factor (0.1-2.0)
        # Higher importance = higher adjustment
        adjustment = 1.0 + (importance * (settings.max_weight_adjustment - 1.0))
        
        # Clamp to limits
        adjustment = max(settings.min_weight_adjustment, min(settings.max_weight_adjustment, adjustment))
        
        return adjustment
    
    def _calculate_adjustment_from_correlation(self, correlation: float) -> float:
        """Calculate weight adjustment from correlation coefficient"""
        # Convert correlation (-1 to 1) to adjustment factor
        # Positive correlation = boost, negative correlation = reduce
        if correlation > 0:
            adjustment = 1.0 + (correlation * (settings.max_weight_adjustment - 1.0))
        else:
            adjustment = 1.0 + (correlation * (1.0 - settings.min_weight_adjustment))
        
        # Clamp to limits
        adjustment = max(settings.min_weight_adjustment, min(settings.max_weight_adjustment, adjustment))
        
        return adjustment
    
    def _apply_weight_smoothing(self, weight_adj: UserWeightAdjustments):
        """Apply smoothing to prevent extreme weight changes"""
        smoothing_factor = settings.weight_smoothing_factor
        
        # Smooth all adjustments
        weight_adj.skill_weight_adjustment = self._smooth_value(weight_adj.skill_weight_adjustment, smoothing_factor)
        weight_adj.location_weight_adjustment = self._smooth_value(weight_adj.location_weight_adjustment, smoothing_factor)
        weight_adj.salary_weight_adjustment = self._smooth_value(weight_adj.salary_weight_adjustment, smoothing_factor)
        weight_adj.company_weight_adjustment = self._smooth_value(weight_adj.company_weight_adjustment, smoothing_factor)
        weight_adj.job_type_weight_adjustment = self._smooth_value(weight_adj.job_type_weight_adjustment, smoothing_factor)
        weight_adj.remote_preference_boost = self._smooth_value(weight_adj.remote_preference_boost, smoothing_factor)
        weight_adj.python_skill_boost = self._smooth_value(weight_adj.python_skill_boost, smoothing_factor)
        weight_adj.startup_company_boost = self._smooth_value(weight_adj.startup_company_boost, smoothing_factor)
    
    def _smooth_value(self, current_value: float, smoothing_factor: float) -> float:
        """Apply exponential smoothing to a value"""
        # Smooth towards 1.0 (neutral adjustment)
        return current_value * (1 - smoothing_factor) + 1.0 * smoothing_factor
    
    def _update_learning_rate(self, weight_adj: UserWeightAdjustments):
        """Update learning rate based on feedback count"""
        # Decrease learning rate as user provides more feedback
        feedback_count = weight_adj.feedback_count
        
        if feedback_count < 10:
            weight_adj.learning_rate = 0.5  # High learning rate for new users
        elif feedback_count < 50:
            weight_adj.learning_rate = 0.3  # Medium learning rate
        else:
            weight_adj.learning_rate = 0.1  # Low learning rate for experienced users
    
    def get_user_weight_adjustments(self, user_id: int) -> Optional[Dict[str, float]]:
        """Get current weight adjustments for a user"""
        try:
            db = next(get_db())
            
            weight_adj = db.query(UserWeightAdjustments).filter(
                UserWeightAdjustments.user_id == user_id
            ).first()
            
            if not weight_adj:
                return None
            
            return {
                'skill_weight_adjustment': weight_adj.skill_weight_adjustment,
                'location_weight_adjustment': weight_adj.location_weight_adjustment,
                'salary_weight_adjustment': weight_adj.salary_weight_adjustment,
                'company_weight_adjustment': weight_adj.company_weight_adjustment,
                'job_type_weight_adjustment': weight_adj.job_type_weight_adjustment,
                'remote_preference_boost': weight_adj.remote_preference_boost,
                'python_skill_boost': weight_adj.python_skill_boost,
                'startup_company_boost': weight_adj.startup_company_boost,
                'is_new_user': weight_adj.is_new_user,
                'feedback_count': weight_adj.feedback_count,
                'learning_rate': weight_adj.learning_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting weight adjustments for user {user_id}: {e}")
            return None
        finally:
            db.close()
    
    def reset_user_weights(self, user_id: int) -> bool:
        """Reset user weights to default values"""
        try:
            db = next(get_db())
            
            weight_adj = db.query(UserWeightAdjustments).filter(
                UserWeightAdjustments.user_id == user_id
            ).first()
            
            if weight_adj:
                # Reset to default values
                weight_adj.skill_weight_adjustment = 1.0
                weight_adj.location_weight_adjustment = 1.0
                weight_adj.salary_weight_adjustment = 1.0
                weight_adj.company_weight_adjustment = 1.0
                weight_adj.job_type_weight_adjustment = 1.0
                weight_adj.remote_preference_boost = 1.0
                weight_adj.python_skill_boost = 1.0
                weight_adj.startup_company_boost = 1.0
                weight_adj.learning_rate = 0.3
                
                db.commit()
                logger.info(f"Reset weights for user {user_id}")
                return True
            else:
                logger.warning(f"No weight adjustments found for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error resetting weights for user {user_id}: {e}")
            return False
        finally:
            db.close()
