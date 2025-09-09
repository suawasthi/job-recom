#!/usr/bin/env python3
"""
ML Preferences System - Main Entry Point

This script trains machine learning models to learn user preferences from job feedback
and adjusts recommendation weights accordingly.

Usage:
    python main.py --mode train          # Train all models
    python main.py --mode update         # Update weights only
    python main.py --mode daily          # Full daily process
    python main.py --mode debug          # Debug mode with detailed logging
"""

import argparse
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from config.settings import settings
from services.data_collector import DataCollector
from services.model_trainer import ModelTrainer
from services.weight_updater import WeightUpdater
from utils.helpers import MLHelpers

# Configure logging
logger = logging.getLogger(__name__)

def train_all_models() -> Dict[str, Any]:
    """Train models for all users with sufficient feedback data"""
    logger.info("=" * 60)
    logger.info("STARTING MODEL TRAINING FOR ALL USERS")
    logger.info("=" * 60)
    
    data_collector = DataCollector()
    model_trainer = ModelTrainer()
    weight_updater = WeightUpdater()
    
    # Get all users with feedback data
    users_with_feedback = data_collector.get_users_with_feedback()
    
    if not users_with_feedback:
        logger.warning("No users with feedback data found")
        return {
            'success': False,
            'error': 'No users with feedback data found',
            'trained_count': 0,
            'failed_count': 0
        }
    
    logger.info(f"Found {len(users_with_feedback)} users with feedback data")
    
    trained_count = 0
    failed_count = 0
    training_results = []
    
    for i, user_id in enumerate(users_with_feedback, 1):
        try:
            logger.info(f"[{i}/{len(users_with_feedback)}] Processing user {user_id}")
            
            # Get user feedback data
            feedback_data = data_collector.get_user_feedback_data(user_id)
            
            if len(feedback_data) < settings.min_feedback_threshold:
                logger.info(f"User {user_id}: Not enough feedback data ({len(feedback_data)} actions, need {settings.min_feedback_threshold})")
                continue
            
            # Validate training data
            validation_results = MLHelpers.validate_training_data(feedback_data)
            if validation_results.get('issues'):
                logger.warning(f"User {user_id}: Data validation issues: {validation_results['issues']}")
            
            # Train model
            result = model_trainer.train_user_model(user_id, feedback_data)
            
            if result['success']:
                # Update weights using ML model
                feature_importance = result['feature_importance']
                weight_success = weight_updater.update_user_weights(user_id, feature_importance)
                
                if weight_success:
                    logger.info(f"User {user_id}: Model trained successfully (accuracy: {result['accuracy']:.3f}, F1: {result['f1_score']:.3f})")
                    trained_count += 1
                    
                    # Save training report
                    if settings.save_model_artifacts:
                        MLHelpers.save_training_report(user_id, result)
                        MLHelpers.save_feature_importance_plot(user_id, feature_importance)
                    
                    training_results.append({
                        'user_id': user_id,
                        'success': True,
                        'accuracy': result['accuracy'],
                        'f1_score': result['f1_score'],
                        'training_samples': result['training_samples']
                    })
                else:
                    logger.error(f"User {user_id}: Model trained but weight update failed")
                    failed_count += 1
            else:
                logger.error(f"User {user_id}: Model training failed - {result['error']}")
                failed_count += 1
                training_results.append({
                    'user_id': user_id,
                    'success': False,
                    'error': result['error']
                })
                
        except Exception as e:
            logger.error(f"User {user_id}: Unexpected error during training - {e}")
            failed_count += 1
            training_results.append({
                'user_id': user_id,
                'success': False,
                'error': str(e)
            })
    
    # Save training summary
    summary = {
        'total_users': len(users_with_feedback),
        'trained_count': trained_count,
        'failed_count': failed_count,
        'success_rate': trained_count / len(users_with_feedback) if users_with_feedback else 0,
        'training_results': training_results
    }
    
    if settings.save_model_artifacts:
        MLHelpers.save_training_summary(summary)
    
    logger.info("=" * 60)
    logger.info(f"TRAINING COMPLETED: {trained_count} successful, {failed_count} failed")
    logger.info(f"Success rate: {summary['success_rate']:.2%}")
    logger.info("=" * 60)
    
    return summary

def update_weights_only() -> Dict[str, Any]:
    """Update weights for users with existing models"""
    logger.info("=" * 60)
    logger.info("STARTING WEIGHT UPDATES FOR EXISTING MODELS")
    logger.info("=" * 60)
    
    model_trainer = ModelTrainer()
    weight_updater = WeightUpdater()
    
    # Get all users with trained models
    users_with_models = model_trainer.get_users_with_models()
    
    if not users_with_models:
        logger.warning("No users with trained models found")
        return {
            'success': False,
            'error': 'No users with trained models found',
            'updated_count': 0
        }
    
    logger.info(f"Found {len(users_with_models)} users with trained models")
    
    updated_count = 0
    update_results = []
    
    for i, user_id in enumerate(users_with_models, 1):
        try:
            logger.info(f"[{i}/{len(users_with_models)}] Updating weights for user {user_id}")
            
            # Validate model
            validation_result = model_trainer.validate_model(user_id)
            if not validation_result['valid']:
                logger.error(f"User {user_id}: Model validation failed - {validation_result['error']}")
                continue
            
            # Get feature importance
            feature_importance = model_trainer.get_feature_importance(user_id)
            
            if feature_importance:
                # Update weights
                success = weight_updater.update_user_weights(user_id, feature_importance)
                
                if success:
                    logger.info(f"User {user_id}: Weights updated successfully")
                    updated_count += 1
                    update_results.append({
                        'user_id': user_id,
                        'success': True
                    })
                else:
                    logger.error(f"User {user_id}: Weight update failed")
                    update_results.append({
                        'user_id': user_id,
                        'success': False,
                        'error': 'Weight update failed'
                    })
            else:
                logger.warning(f"User {user_id}: No feature importance found")
                update_results.append({
                    'user_id': user_id,
                    'success': False,
                    'error': 'No feature importance found'
                })
                
        except Exception as e:
            logger.error(f"User {user_id}: Error updating weights - {e}")
            update_results.append({
                'user_id': user_id,
                'success': False,
                'error': str(e)
            })
    
    logger.info("=" * 60)
    logger.info(f"WEIGHT UPDATES COMPLETED: {updated_count} users updated")
    logger.info("=" * 60)
    
    return {
        'total_users': len(users_with_models),
        'updated_count': updated_count,
        'update_results': update_results
    }

def process_new_users() -> Dict[str, Any]:
    """Process new users with limited feedback data"""
    logger.info("=" * 60)
    logger.info("PROCESSING NEW USERS")
    logger.info("=" * 60)
    
    data_collector = DataCollector()
    weight_updater = WeightUpdater()
    
    # Get all users with feedback data
    users_with_feedback = data_collector.get_users_with_feedback()
    
    new_user_count = 0
    processed_count = 0
    
    for user_id in users_with_feedback:
        try:
            # Check if user is new
            if data_collector.is_new_user(user_id):
                logger.info(f"Processing new user {user_id}")
                
                # Update weights using new user strategy
                success = weight_updater.update_user_weights(user_id)
                
                if success:
                    processed_count += 1
                    logger.info(f"New user {user_id}: Weights updated successfully")
                else:
                    logger.error(f"New user {user_id}: Weight update failed")
                
                new_user_count += 1
                
        except Exception as e:
            logger.error(f"Error processing new user {user_id}: {e}")
    
    logger.info("=" * 60)
    logger.info(f"NEW USER PROCESSING COMPLETED: {processed_count}/{new_user_count} processed")
    logger.info("=" * 60)
    
    return {
        'new_user_count': new_user_count,
        'processed_count': processed_count
    }

def daily_process() -> Dict[str, Any]:
    """Full daily process: train new models, update weights, process new users"""
    logger.info("=" * 60)
    logger.info("STARTING DAILY ML PREFERENCES PROCESS")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    # Step 1: Train models for users with sufficient data
    training_results = train_all_models()
    
    # Step 2: Update weights for existing models
    weight_update_results = update_weights_only()
    
    # Step 3: Process new users
    new_user_results = process_new_users()
    
    # Calculate total time
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    # Create summary
    summary = {
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'total_time_seconds': total_time,
        'training_results': training_results,
        'weight_update_results': weight_update_results,
        'new_user_results': new_user_results
    }
    
    # Save daily summary
    if settings.save_model_artifacts:
        MLHelpers.save_training_summary(summary, "reports/daily")
    
    logger.info("=" * 60)
    logger.info("DAILY PROCESS COMPLETED")
    logger.info(f"Total time: {total_time:.2f} seconds")
    logger.info(f"Models trained: {training_results.get('trained_count', 0)}")
    logger.info(f"Weights updated: {weight_update_results.get('updated_count', 0)}")
    logger.info(f"New users processed: {new_user_results.get('processed_count', 0)}")
    logger.info("=" * 60)
    
    return summary

def debug_mode() -> Dict[str, Any]:
    """Debug mode with detailed logging and system info"""
    logger.info("=" * 60)
    logger.info("STARTING DEBUG MODE")
    logger.info("=" * 60)
    
    # Get system info
    system_info = MLHelpers.get_system_info()
    logger.info(f"System info: {system_info}")
    
    # Test data collection
    data_collector = DataCollector()
    users_with_feedback = data_collector.get_users_with_feedback()
    logger.info(f"Users with feedback: {len(users_with_feedback)}")
    
    # Test feature engineering
    from services.feature_engineer import FeatureEngineer
    feature_engineer = FeatureEngineer()
    feature_names = feature_engineer.get_feature_names()
    logger.info(f"Feature names: {len(feature_names)} features")
    
    # Test model trainer
    model_trainer = ModelTrainer()
    users_with_models = model_trainer.get_users_with_models()
    logger.info(f"Users with models: {len(users_with_models)}")
    
    # Test weight updater
    weight_updater = WeightUpdater()
    
    # Run a small training test if possible
    if users_with_feedback:
        test_user = users_with_feedback[0]
        feedback_data = data_collector.get_user_feedback_data(test_user)
        logger.info(f"Test user {test_user} feedback data: {len(feedback_data)} items")
        
        if len(feedback_data) >= settings.min_feedback_threshold:
            logger.info(f"Running test training for user {test_user}")
            result = model_trainer.train_user_model(test_user, feedback_data)
            logger.info(f"Test training result: {result}")
    
    logger.info("=" * 60)
    logger.info("DEBUG MODE COMPLETED")
    logger.info("=" * 60)
    
    return {
        'system_info': system_info,
        'users_with_feedback': len(users_with_feedback),
        'feature_count': len(feature_names),
        'users_with_models': len(users_with_models)
    }

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ML Preferences System')
    parser.add_argument('--mode', choices=['train', 'update', 'daily', 'debug'], default='daily',
                       help='Operation mode: train (train all models), update (update weights only), daily (full daily process), debug (debug mode)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO',
                       help='Logging level')
    parser.add_argument('--log-file', default='ml_preferences.log',
                       help='Log file path')
    
    args = parser.parse_args()
    
    # Setup logging
    MLHelpers.setup_logging(args.log_level, args.log_file)
    
    # Create directories
    MLHelpers.create_directories()
    
    logger.info(f"Starting ML Preferences System in {args.mode} mode")
    logger.info(f"Settings: {settings.dict()}")
    
    try:
        if args.mode == 'train':
            result = train_all_models()
        elif args.mode == 'update':
            result = update_weights_only()
        elif args.mode == 'daily':
            result = daily_process()
        elif args.mode == 'debug':
            result = debug_mode()
        else:
            raise ValueError(f"Unknown mode: {args.mode}")
        
        logger.info(f"ML Preferences System completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"ML Preferences System failed: {e}")
        raise

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

