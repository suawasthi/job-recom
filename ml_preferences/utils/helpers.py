import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

class MLHelpers:
    """Helper functions for ML preferences system"""
    
    @staticmethod
    def setup_logging(log_level: str = "INFO", log_file: str = "ml_preferences.log"):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file)
            ]
        )
        
        # Set specific loggers
        logging.getLogger("sklearn").setLevel(logging.WARNING)
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        
        logger.info(f"Logging configured: level={log_level}, file={log_file}")
    
    @staticmethod
    def create_directories():
        """Create necessary directories"""
        directories = [
            "models/artifacts",
            "logs",
            "reports",
            "data/exports"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    @staticmethod
    def save_training_report(user_id: int, report_data: Dict[str, Any], output_dir: str = "reports"):
        """Save training report for a user"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            report_file = os.path.join(output_dir, f"user_{user_id}_training_report.json")
            
            # Add timestamp
            report_data['timestamp'] = datetime.utcnow().isoformat()
            report_data['user_id'] = user_id
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Saved training report for user {user_id} to {report_file}")
            
        except Exception as e:
            logger.error(f"Error saving training report for user {user_id}: {e}")
    
    @staticmethod
    def save_feature_importance_plot(user_id: int, feature_importance: Dict[str, float], 
                                   output_dir: str = "reports", top_n: int = 20):
        """Create and save feature importance plot"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Sort features by importance
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:top_n]
            
            if not sorted_features:
                logger.warning(f"No features to plot for user {user_id}")
                return
            
            # Create plot
            features, importances = zip(*sorted_features)
            
            plt.figure(figsize=(12, 8))
            plt.barh(range(len(features)), importances)
            plt.yticks(range(len(features)), features)
            plt.xlabel('Feature Importance')
            plt.title(f'Top {top_n} Feature Importance - User {user_id}')
            plt.gca().invert_yaxis()
            
            # Save plot
            plot_file = os.path.join(output_dir, f"user_{user_id}_feature_importance.png")
            plt.savefig(plot_file, bbox_inches='tight', dpi=300)
            plt.close()
            
            logger.info(f"Saved feature importance plot for user {user_id} to {plot_file}")
            
        except Exception as e:
            logger.error(f"Error creating feature importance plot for user {user_id}: {e}")
    
    @staticmethod
    def save_training_summary(summary_data: Dict[str, Any], output_dir: str = "reports"):
        """Save overall training summary"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            summary_file = os.path.join(output_dir, f"training_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            # Add timestamp
            summary_data['timestamp'] = datetime.utcnow().isoformat()
            
            with open(summary_file, 'w') as f:
                json.dump(summary_data, f, indent=2, default=str)
            
            logger.info(f"Saved training summary to {summary_file}")
            
        except Exception as e:
            logger.error(f"Error saving training summary: {e}")
    
    @staticmethod
    def validate_training_data(feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate training data quality"""
        try:
            validation_results = {
                'total_samples': len(feedback_data),
                'valid_samples': 0,
                'positive_samples': 0,
                'negative_samples': 0,
                'neutral_samples': 0,
                'missing_job_data': 0,
                'issues': []
            }
            
            for i, feedback in enumerate(feedback_data):
                # Check if job data exists
                if not feedback.get('job'):
                    validation_results['missing_job_data'] += 1
                    validation_results['issues'].append(f"Sample {i}: Missing job data")
                    continue
                
                # Check feedback type
                is_positive = feedback.get('is_bookmarked', False) or feedback.get('is_relevant', False)
                is_negative = feedback.get('is_hidden', False)
                is_neutral = feedback.get('is_maybe_later', False)
                
                if is_positive and not is_negative:
                    validation_results['positive_samples'] += 1
                elif is_negative and not is_positive:
                    validation_results['negative_samples'] += 1
                elif is_neutral:
                    validation_results['neutral_samples'] += 1
                else:
                    validation_results['issues'].append(f"Sample {i}: Ambiguous feedback")
                    continue
                
                validation_results['valid_samples'] += 1
            
            # Check for class imbalance
            total_valid = validation_results['valid_samples']
            if total_valid > 0:
                positive_ratio = validation_results['positive_samples'] / total_valid
                negative_ratio = validation_results['negative_samples'] / total_valid
                
                if positive_ratio > 0.9 or negative_ratio > 0.9:
                    validation_results['issues'].append("Severe class imbalance detected")
                elif positive_ratio > 0.8 or negative_ratio > 0.8:
                    validation_results['issues'].append("Moderate class imbalance detected")
            
            logger.info(f"Data validation completed: {validation_results}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating training data: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def export_user_data(user_id: int, data: Dict[str, Any], output_dir: str = "data/exports"):
        """Export user data for analysis"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            export_file = os.path.join(output_dir, f"user_{user_id}_data.json")
            
            with open(export_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Exported user {user_id} data to {export_file}")
            
        except Exception as e:
            logger.error(f"Error exporting user {user_id} data: {e}")
    
    @staticmethod
    def cleanup_old_files(directory: str, max_age_days: int = 30):
        """Clean up old files in a directory"""
        try:
            import time
            
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            cleaned_count = 0
            
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.info(f"Removed old file: {file_path}")
            
            logger.info(f"Cleaned up {cleaned_count} old files from {directory}")
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information for debugging"""
        try:
            import platform
            import psutil
            
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
            }
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {'error': str(e)}

