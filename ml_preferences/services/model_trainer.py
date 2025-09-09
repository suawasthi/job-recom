import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Tuple, Optional
import joblib
import os
from datetime import datetime
import logging

from config.settings import settings
from services.feature_engineer import FeatureEngineer
from services.data_collector import DataCollector

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.data_collector = DataCollector()
        self.models_dir = settings.model_artifacts_dir
        self.scaler = StandardScaler()  # For feature scaling
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info(f"ModelTrainer initialized with models directory: {self.models_dir}")
    
    def prepare_training_data(self, user_feedback_data: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare training data from user feedback"""
        try:
            if len(user_feedback_data) < settings.min_feedback_threshold:
                raise ValueError(f"Not enough feedback data. Need at least {settings.min_feedback_threshold} actions, got {len(user_feedback_data)}")
            
            # Extract features and labels
            features_list = []
            labels = []
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for feedback in user_feedback_data:
                job_data = feedback['job']
                features = self.feature_engineer.extract_job_features(job_data)
                features_list.append(features)
                
                # Create label: 1 for positive feedback, 0 for negative
                is_positive = (
                    feedback.get('is_bookmarked', False) or 
                    feedback.get('is_relevant', False)
                )
                is_negative = feedback.get('is_hidden', False)
                is_neutral = feedback.get('is_maybe_later', False)
                
                if is_positive and not is_negative:
                    labels.append(1)  # Positive
                    positive_count += 1
                elif is_negative and not is_positive:
                    labels.append(0)  # Negative
                    negative_count += 1
                elif is_neutral:
                    labels.append(0)  # Treat neutral as negative for now
                    neutral_count += 1
                else:
                    # Skip ambiguous feedback
                    features_list.pop()  # Remove the last added features
                    continue
            
            if len(features_list) != len(labels):
                # Remove last features if labels were skipped
                features_list = features_list[:len(labels)]
            
            if len(features_list) == 0:
                raise ValueError("No valid training data after filtering")
            
            X = pd.DataFrame(features_list)
            y = pd.Series(labels)
            
            logger.info(f"Prepared training data: {len(X)} samples, {positive_count} positive, {negative_count} negative, {neutral_count} neutral")
            
            # Check for class imbalance
            if len(y.unique()) < 2:
                raise ValueError("Only one class present in training data")
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise
    
    def train_user_model(self, user_id: int, user_feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train Random Forest model for a specific user"""
        try:
            logger.info(f"Training model for user {user_id} with {len(user_feedback_data)} feedback items")
            
            # Prepare training data
            X, y = self.prepare_training_data(user_feedback_data)
            
            if len(X) < settings.min_feedback_threshold:
                return {
                    'success': False,
                    'error': f'Not enough training data: {len(X)} samples (need {settings.min_feedback_threshold})'
                }
            
            # Check for class balance
            class_counts = y.value_counts()
            logger.info(f"Class distribution: {dict(class_counts)}")
            
            if len(class_counts) < 2:
                return {
                    'success': False,
                    'error': 'Only one class present in training data'
                }
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            logger.info(f"Data split: {len(X_train)} train, {len(X_test)} test")
            
            # Scale features for Logistic Regression
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Logistic Regression
            model = LogisticRegression(
                random_state=42,
                class_weight=settings.logistic_regression_class_weight,
                max_iter=settings.logistic_regression_max_iter,
                C=settings.logistic_regression_C
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=3, scoring='accuracy')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            # Get feature importance (coefficients for Logistic Regression)
            feature_names = X.columns.tolist()
            # Use absolute values of coefficients as importance
            feature_importance = dict(zip(feature_names, abs(model.coef_[0])))
            
            # Save model and scaler
            model_path = os.path.join(self.models_dir, f"user_{user_id}_model.joblib")
            scaler_path = os.path.join(self.models_dir, f"user_{user_id}_scaler.joblib")
            
            joblib.dump(model, model_path)
            joblib.dump(self.scaler, scaler_path)
            
            # Log detailed results
            logger.info(f"Model training completed for user {user_id}")
            logger.info(f"Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            logger.info(f"CV Score: {cv_mean:.3f} (+/- {cv_std:.3f})")
            
            if settings.debug_mode:
                # Print classification report
                report = classification_report(y_test, y_pred, zero_division=0)
                logger.debug(f"Classification Report for user {user_id}:\n{report}")
                
                # Print top features
                top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
                logger.debug(f"Top 10 features for user {user_id}: {top_features}")
            
            return {
                'success': True,
                'model_path': model_path,
                'scaler_path': scaler_path,
                'feature_importance': feature_importance,
                'feature_coefficients': dict(zip(feature_names, model.coef_[0])),  # Raw coefficients
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'cv_mean': cv_mean,
                'cv_std': cv_std,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'class_distribution': dict(class_counts)
            }
            
        except Exception as e:
            logger.error(f"Error training model for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_feature_importance(self, user_id: int) -> Optional[Dict[str, float]]:
        """Get feature importance for a trained user model"""
        model_path = os.path.join(self.models_dir, f"user_{user_id}_model.joblib")
        
        if not os.path.exists(model_path):
            logger.warning(f"No model found for user {user_id} at {model_path}")
            return None
        
        try:
            model = joblib.load(model_path)
            feature_names = self.feature_engineer.get_feature_names()
            
            if len(model.coef_[0]) != len(feature_names):
                logger.error(f"Feature coefficient length mismatch for user {user_id}")
                return None
            
            # Use absolute values of coefficients as importance
            importance = dict(zip(feature_names, abs(model.coef_[0])))
            logger.debug(f"Retrieved feature importance for user {user_id}")
            return importance
            
        except Exception as e:
            logger.error(f"Error loading model for user {user_id}: {e}")
            return None
    
    def get_users_with_models(self) -> List[int]:
        """Get list of users who have trained models"""
        try:
            user_ids = []
            
            for filename in os.listdir(self.models_dir):
                if filename.startswith("user_") and filename.endswith("_model.joblib"):
                    # Extract user_id from filename
                    try:
                        user_id = int(filename.replace("user_", "").replace("_model.joblib", ""))
                        user_ids.append(user_id)
                    except ValueError:
                        continue
            
            logger.info(f"Found {len(user_ids)} users with trained models")
            return user_ids
            
        except Exception as e:
            logger.error(f"Error getting users with models: {e}")
            return []
    
    def delete_user_model(self, user_id: int) -> bool:
        """Delete a user's trained model"""
        try:
            model_path = os.path.join(self.models_dir, f"user_{user_id}_model.joblib")
            
            if os.path.exists(model_path):
                os.remove(model_path)
                logger.info(f"Deleted model for user {user_id}")
                return True
            else:
                logger.warning(f"No model found to delete for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting model for user {user_id}: {e}")
            return False
    
    def validate_model(self, user_id: int) -> Dict[str, Any]:
        """Validate a trained model"""
        try:
            model_path = os.path.join(self.models_dir, f"user_{user_id}_model.joblib")
            
            if not os.path.exists(model_path):
                return {
                    'valid': False,
                    'error': 'Model file not found'
                }
            
            # Load model
            model = joblib.load(model_path)
            
            # Check if model has required attributes
            if not hasattr(model, 'coef_'):
                return {
                    'valid': False,
                    'error': 'Model missing coef_ (not a Logistic Regression model)'
                }
            
            # Check feature coefficient length
            expected_features = len(self.feature_engineer.get_feature_names())
            actual_features = len(model.coef_[0])
            
            if expected_features != actual_features:
                return {
                    'valid': False,
                    'error': f'Feature count mismatch: expected {expected_features}, got {actual_features}'
                }
            
            return {
                'valid': True,
                'feature_count': actual_features,
                'model_type': type(model).__name__
            }
            
        except Exception as e:
            logger.error(f"Error validating model for user {user_id}: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
