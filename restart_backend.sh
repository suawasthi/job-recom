#!/bin/bash

echo "🔄 Restarting backend with updated CORS configuration..."

# Kill any existing Python processes
echo "🛑 Stopping existing backend processes..."
pkill -f "python.*run.py" || true
pkill -f "python.*run_production.py" || true
pkill -f "gunicorn" || true

# Wait a moment
sleep 2

# Set environment variables
export ENVIRONMENT=production
export SECRET_KEY=your-production-secret-key-here-change-this
export ACCESS_TOKEN_EXPIRE_MINUTES=30
export DATABASE_URL=sqlite:///./app.db
export CORS_ORIGINS=*
export LOG_LEVEL=INFO
export MAX_FILE_SIZE_MB=10

echo "🚀 Starting backend with updated CORS..."
python run_production.py
