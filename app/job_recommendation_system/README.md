# Job Recommendation System

A clean, modular, and intelligent job recommendation system built with Python.

## 🚀 Features

- **Multi-dimensional matching**: Skills, experience, location, career growth, salary
- **Semantic understanding**: Advanced skill matching with embeddings
- **Market intelligence**: Real-time market demand and trends
- **Personalized recommendations**: User-specific preferences and behavior
- **Explainable AI**: Clear reasoning for each recommendation
- **Bias detection**: Fair and unbiased recommendations

## 📁 Project Structure

```
job_recommendation_system/
├── main.py                 # Main entry point
├── config/                 # Configuration settings
├── models/                 # Data models and schemas
├── services/               # Core business logic
├── data/                   # Data sources and embeddings
├── utils/                  # Utility functions
└── requirements.txt        # Dependencies
```

## 🛠️ Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## 🎯 Usage

```python
from main import JobRecommendationSystem

# Initialize system
system = JobRecommendationSystem()

# Get recommendations
recommendations = system.recommend_jobs(candidate_data, jobs_data)
```

## 📊 Architecture

- **Modular Design**: Each component is independent and testable
- **Clean Code**: Well-documented and maintainable
- **Scalable**: Easy to extend and modify
- **Production Ready**: Error handling and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License
