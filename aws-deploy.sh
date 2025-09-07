#!/bin/bash

set -e

echo "🚀 Deploying to AWS Elastic Beanstalk..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    print_error "EB CLI is not installed. Please install it first:"
    echo "pip install awsebcli"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the backend directory."
    exit 1
fi

# Initialize EB application if not already done
if [ ! -f ".elasticbeanstalk/config.yml" ]; then
    print_status "Initializing Elastic Beanstalk application..."
    eb init -p python-3.11 my-job-recommendation-app --region us-east-1
fi

# Create environment if it doesn't exist
if ! eb status &> /dev/null; then
    print_status "Creating Elastic Beanstalk environment..."
    eb create production-env --instance-type t3.micro --single-instance
else
    print_status "Environment already exists. Deploying updates..."
fi

# Deploy the application
print_status "Deploying application..."
eb deploy

# Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 30

# Get the application URL
APP_URL=$(eb status | grep CNAME | awk '{print $2}')
if [ -n "$APP_URL" ]; then
    print_status "Deployment completed successfully!"
    echo "🌐 Application URL: http://$APP_URL"
    echo "🔍 Health Check: http://$APP_URL/health"
else
    print_warning "Could not retrieve application URL. Check EB console."
fi

print_status "Deployment script completed!"
