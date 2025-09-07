# AI-Powered Job Recommendation System

A production-ready Python backend system that provides AI-powered job recommendations for both job seekers and recruiters. Built with FastAPI, spaCy NLP, and modern software engineering practices.

## 🚀 Features

### For Job Seekers
- **Resume Upload & Parsing**: Upload PDF/DOCX resumes with intelligent field extraction using NLP
- **ATS-Friendly Scoring**: Get comprehensive resume scores with detailed feedback
- **Smart Job Recommendations**: AI-powered job matching based on skills, experience, and preferences  
- **Resume Improvement**: Get actionable suggestions to improve your resume
- **Application Tracking**: Track your job applications and their status

### For Recruiters
- **Job Posting Management**: Create, update, and manage job postings
- **Candidate Matching**: Get AI-ranked candidates based on job requirements
- **Application Management**: View and manage applications for your job postings
- **Analytics Dashboard**: Get insights on job performance and hiring trends

### Analytics & Insights
- **Trending Skills**: See which skills are in high demand
- **Job Market Trends**: Analyze job title and industry trends
- **Salary Insights**: Get salary benchmarks by location and experience
- **Performance Analytics**: Track user engagement and success metrics

## 🏗️ Architecture

The system follows clean architecture principles with clear separation of concerns:

```
app/
├── api/           # REST API endpoints
├── core/          # Configuration, database, security
├── models/        # SQLAlchemy database models  
├── schemas/       # Pydantic request/response models
├── services/      # Business logic and AI services
└── utils/         # Utility functions and helpers
```

### Key Components

- **Resume Parser**: Advanced NLP-based parsing using spaCy for extracting structured data from resumes
- **Resume Scorer**: Multi-factor scoring algorithm for ATS-friendliness and completeness
- **Job Matcher**: ML-powered recommendation engine using TF-IDF and cosine similarity
- **Authentication**: JWT-based secure authentication with role-based access control

## 🛠️ Technology Stack

- **Framework**: FastAPI (high-performance async web framework)
- **NLP**: spaCy for natural language processing and entity extraction
- **ML**: scikit-learn for recommendation algorithms and text analysis
- **Database**: SQLAlchemy ORM with SQLite (easily configurable for PostgreSQL)
- **Security**: JWT tokens, password hashing with bcrypt
- **Testing**: pytest with comprehensive test coverage
- **Validation**: Pydantic for request/response validation

## 📋 Prerequisites

- Python 3.11+ (works with Python 3.13 as requested)
- Windows, macOS, or Linux
- 4GB+ RAM recommended
- 1GB+ free disk space

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Extract the zip file
unzip ai_job_recommendation_backend.zip
cd ai_job_recommendation_backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm
```

### 3. Environment Configuration

```bash
# Copy and configure environment variables
copy .env.example .env  # On Windows
# cp .env.example .env   # On macOS/Linux

# Edit .env file with your settings
```

### 4. Run the Application

```bash
# Option 1: Using the run script
python run.py

# Option 2: Using uvicorn directly  
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using Python module
python -m app.main
```

The API will be available at: `http://localhost:8000`

### 5. API Documentation

Once running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/test_auth.py          # Authentication tests
pytest tests/test_resume.py        # Resume processing tests  
pytest tests/test_integration.py   # End-to-end integration tests

# Run with verbose output
pytest -v
```

## 📚 API Usage Examples

### Authentication

```bash
# Register as job seeker
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jobseeker@example.com",
    "name": "John Doe", 
    "password": "securepassword123",
    "role": "job_seeker",
    "location": "San Francisco, CA"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jobseeker@example.com",
    "password": "securepassword123"
  }'
```

### Resume Operations

```bash
# Upload resume (replace TOKEN with actual JWT token)
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@path/to/resume.pdf"

# Get job recommendations
curl -X GET "http://localhost:8000/api/v1/jobs/recommendations" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Job Management

```bash
# Create job posting (recruiter role required)
curl -X POST "http://localhost:8000/api/v1/jobs/" \
  -H "Authorization: Bearer YOUR_RECRUITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "Looking for an experienced Python developer...",
    "company_name": "TechCorp Inc.",
    "location": "New York, NY",
    "job_type": "full_time",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "min_salary": 90000,
    "max_salary": 130000
  }'
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=sqlite:///./app.db

# Security  
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=uploads

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=AI Job Recommendation System
DEBUG=True
```

### Production Deployment

For production deployment:

1. **Set DEBUG=False** in environment variables
2. **Use PostgreSQL** instead of SQLite:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost/jobmatch_db
   ```
3. **Configure proper CORS** origins in `main.py`
4. **Use environment-specific secrets** for JWT keys
5. **Set up proper logging** and monitoring
6. **Use a process manager** like supervisord or systemd

## 🧠 AI/ML Features

### Resume Parsing Algorithm

The system uses advanced NLP techniques:

- **Named Entity Recognition (NER)** for extracting personal information
- **Custom skill extraction** with comprehensive skill databases
- **Experience calculation** using pattern matching and NLP
- **Education parsing** with institution and degree recognition
- **Fallback mechanisms** for manual input when automation fails

### Job Matching Algorithm

The recommendation engine employs:

- **TF-IDF Vectorization** for semantic text analysis
- **Cosine Similarity** for measuring job-candidate compatibility  
- **Multi-factor scoring** including skills, experience, location, and salary
- **Weighted ranking** with configurable importance factors
- **Real-time learning** from user feedback and application outcomes

### Resume Scoring System

Comprehensive scoring based on:

- **ATS Compatibility** (25%): Keyword density, formatting, structure
- **Completeness** (35%): Critical fields, information completeness  
- **Content Quality** (25%): Action verbs, quantifiable achievements
- **Formatting** (15%): Professional appearance, readability

## 🔐 Security Features

- **JWT Authentication** with configurable expiration
- **Password Hashing** using bcrypt with salt
- **Role-Based Access Control** (RBAC) for job seekers vs recruiters
- **Input Validation** using Pydantic schemas
- **File Upload Security** with type and size validation
- **SQL Injection Protection** via SQLAlchemy ORM
- **CORS Configuration** for cross-origin requests

## 📈 Performance & Scalability

- **Async/Await** support for high concurrency
- **Connection Pooling** for database efficiency
- **Caching-Ready** architecture for Redis integration
- **Horizontal Scaling** support with stateless design
- **Background Tasks** ready for Celery integration
- **Database Indexing** for optimized queries

## 🛡️ Error Handling

Comprehensive error handling with:

- **Global exception handler** for unhandled errors
- **Custom HTTP exceptions** with meaningful messages
- **Validation errors** with detailed field-level feedback
- **Logging integration** for debugging and monitoring
- **Graceful degradation** for service failures

## 📊 Monitoring & Analytics

Built-in analytics endpoints provide:

- **Trending Skills Analysis** based on job requirements
- **Job Market Insights** with growth trends
- **Salary Benchmarking** by location and experience
- **User Engagement Metrics** for platform optimization
- **Performance Analytics** for job posting effectiveness

## 🔄 Future Enhancements

Potential improvements and features:

- **Machine Learning Pipeline** for continuous model improvement
- **Real-time Notifications** using WebSockets
- **Advanced Resume Templates** with AI-generated suggestions
- **Integration APIs** for job boards and HR systems
- **Mobile API Support** for native mobile apps
- **Multi-language Support** for international markets
- **Video Interview Scheduling** integration
- **Skills Assessment** with coding challenges

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- **Documentation**: Check the API docs at `/docs` when running
- **Issues**: Create an issue on the repository
- **Email**: Contact the development team

## 🙏 Acknowledgments

- **spaCy** for excellent NLP capabilities
- **FastAPI** for the high-performance web framework
- **SQLAlchemy** for robust ORM functionality
- **scikit-learn** for machine learning algorithms
- **Pydantic** for data validation and settings management

---

**Happy coding! 🚀**

*Built with ❤️ for the modern job market*
