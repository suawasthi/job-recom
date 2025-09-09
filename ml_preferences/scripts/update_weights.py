#!/usr/bin/env python3
"""
Update Weights Script

This script updates weights for users with existing trained models.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import update_weights_only
from utils.helpers import MLHelpers

if __name__ == "__main__":
    # Setup logging
    MLHelpers.setup_logging("INFO", "logs/update_weights.log")
    
    # Create directories
    MLHelpers.create_directories()
    
    print("Starting weight updates...")
    result = update_weights_only()
    
    if result.get('success', True):
        print(f"Weight updates completed successfully!")
        print(f"Weights updated: {result.get('updated_count', 0)}")
    else:
        print(f"Weight updates failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

