#!/usr/bin/env python3
"""
Train Models Script

This script trains ML models for all users with sufficient feedback data.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import train_all_models
from utils.helpers import MLHelpers

if __name__ == "__main__":
    # Setup logging
    MLHelpers.setup_logging("INFO", "logs/train_models.log")
    
    # Create directories
    MLHelpers.create_directories()
    
    print("Starting model training...")
    result = train_all_models()
    
    if result.get('success', True):
        print(f"Training completed successfully!")
        print(f"Models trained: {result.get('trained_count', 0)}")
        print(f"Failed: {result.get('failed_count', 0)}")
    else:
        print(f"Training failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

