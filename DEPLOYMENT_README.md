# Deployment Guide

This guide explains how to deploy the AI Job Platform API in different environments using the provided WSGI configuration files.

## Files Overview

- `wsgi.py` - WSGI entry point for production deployment
- `gunicorn.conf.py` - Gunicorn configuration with optimized settings
- `start_server.py` - Flexible startup script for different environments
- `requirements.txt` - Updated with Gunicorn for production

## Quick Start

### Development Mode
```bash
# Using the startup script
python start_server.py --mode dev

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode with Gunicorn
```bash
# Using the startup script
python start_server.py --mode prod

# Or directly with gunicorn
gunicorn --config gunicorn.conf.py wsgi:application
```

### Production Mode with Uvicorn
```bash
# Using the startup script
python start_server.py --mode uvicorn-prod

# Or directly with uvicorn
uvicorn wsgi:application --host 0.0.0.0 --port 8000 --workers 4
```

## Deployment Options

### 1. Development Deployment

Best for local development with auto-reload:

```bash
python start_server.py --mode dev --host 127.0.0.1 --port 8000
```

**Features:**
- Auto-reload on code changes
- Detailed error messages
- Single worker process
- Debug mode enabled

### 2. Production Deployment with Gunicorn

Best for production environments with high traffic:

```bash
python start_server.py --mode prod --host 0.0.0.0 --port 8000
```

**Features:**
- Multiple worker processes (CPU cores × 2 + 1)
- Optimized for performance
- Process management and monitoring
- Graceful restarts
- Request limiting and security

### 3. Production Deployment with Uvicorn

Alternative production deployment:

```bash
python start_server.py --mode uvicorn-prod --host 0.0.0.0 --port 8000
```

**Features:**
- ASGI-native server
- Multiple workers
- Good for moderate traffic
- Simpler configuration

## Environment Variables

You can configure the server using environment variables:

```bash
# Server configuration
export HOST="0.0.0.0"
export PORT="8000"
export WORKERS="4"

# Gunicorn specific
export GUNICORN_BIND="0.0.0.0:8000"
export GUNICORN_WORKERS="4"
export GUNICORN_LOG_LEVEL="info"

# Application specific
export ENVIRONMENT="production"
export PYTHONPATH="/app"
```

## Docker Deployment

### Using the existing Dockerfile
```bash
# Build the image
docker build -t ai-job-platform-api .

# Run in development mode
docker run -p 8000:8000 ai-job-platform-api

# Run in production mode
docker run -p 8000:8000 -e ENVIRONMENT=production ai-job-platform-api
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
```

## Cloud Deployment

### Heroku
```bash
# Create Procfile
echo "web: gunicorn --config gunicorn.conf.py wsgi:application" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### AWS Elastic Beanstalk
```bash
# Create Procfile
echo "web: gunicorn --config gunicorn.conf.py wsgi:application" > Procfile

# Deploy using EB CLI
eb init
eb create production
eb deploy
```

### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-job-api
gcloud run deploy --image gcr.io/PROJECT_ID/ai-job-api --platform managed
```

## Performance Tuning

### Gunicorn Configuration
The `gunicorn.conf.py` file includes optimized settings:

- **Workers**: Automatically calculated based on CPU cores
- **Worker Class**: Uses Uvicorn workers for ASGI compatibility
- **Max Requests**: Restarts workers after 1000 requests to prevent memory leaks
- **Timeout**: 30 seconds for request timeout
- **Keepalive**: 2 seconds for connection keepalive

### Customizing Performance
```python
# In gunicorn.conf.py
workers = 4  # Set specific number of workers
worker_connections = 2000  # Increase for high traffic
max_requests = 2000  # Increase for better performance
timeout = 60  # Increase for long-running requests
```

## Monitoring and Logging

### Log Levels
```bash
# Development
export GUNICORN_LOG_LEVEL="debug"

# Production
export GUNICORN_LOG_LEVEL="info"

# Minimal logging
export GUNICORN_LOG_LEVEL="warning"
```

### Health Checks
The API includes built-in health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Root endpoint with status
curl http://localhost:8000/
```

## Security Considerations

### Production Security
1. **HTTPS**: Always use HTTPS in production
2. **CORS**: Configure CORS origins properly
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Authentication**: Ensure proper authentication is in place
5. **Environment Variables**: Use environment variables for sensitive data

### SSL Configuration
```python
# In gunicorn.conf.py (uncomment and configure)
keyfile = "/path/to/ssl/key.pem"
certfile = "/path/to/ssl/cert.pem"
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Permission Denied**
   ```bash
   # Make sure the script is executable
   chmod +x start_server.py
   ```

3. **Import Errors**
   ```bash
   # Make sure PYTHONPATH is set correctly
   export PYTHONPATH="/path/to/your/project"
   ```

4. **Worker Timeout**
   ```bash
   # Increase timeout in gunicorn.conf.py
   timeout = 60
   ```

### Debug Mode
For debugging, you can run in development mode with more verbose logging:

```bash
python start_server.py --mode dev --host 127.0.0.1 --port 8000
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Check network connectivity and firewall settings

