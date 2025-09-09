# ML Preferences System

A machine learning system that learns user preferences from job feedback and adjusts recommendation weights accordingly.

## Features

- **Random Forest Models**: Train user-specific models to learn preference patterns
- **Feature Engineering**: Extract meaningful features from job data
- **Weight Updates**: Adjust recommendation weights based on learned preferences
- **Fallback Strategy**: Use statistical correlation for users with limited data
- **New User Handling**: Intelligent defaults and gradual learning
- **Independent Operation**: Runs separately from main API but uses same database

## Architecture

```
User Feedback → Feature Engineering → ML Model → Weight Updates → Recommendation System
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Train Models**:
   ```bash
   python scripts/train_models.py
   ```

3. **Update Weights**:
   ```bash
   python scripts/update_weights.py
   ```

4. **Run Daily Training**:
   ```bash
   python main.py --mode daily
   ```

## Configuration

- **Database**: Uses same SQLite database as main API
- **Models**: Random Forest with feature importance extraction
- **Training**: Daily batch training for all users
- **Features**: Skills, location, salary, company, job type, etc.

## API Integration

The system updates weights in the main recommendation system by:
1. Training ML models on user feedback
2. Extracting feature importance scores
3. Updating user-specific weight adjustments
4. Main API uses updated weights for recommendations

## Debugging

- Comprehensive logging at all levels
- Model performance metrics
- Feature importance visualization
- Training data validation
- Error handling with detailed messages

