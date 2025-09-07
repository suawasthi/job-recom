# 🚀 AWS Elastic Beanstalk Deployment Guide

This guide will help you deploy the FastAPI backend to AWS Elastic Beanstalk.

## 📋 Prerequisites

- AWS CLI configured with appropriate credentials
- EB CLI installed (`pip install awsebcli`)
- Python 3.11
- AWS account with Elastic Beanstalk permissions

## 🔧 Setup Steps

### 1. Install EB CLI
```bash
pip install awsebcli
```

### 2. Configure AWS Credentials
```bash
aws configure
```

### 3. Navigate to Backend Directory
```bash
cd ai_job_recommendation_backend
```

## 🚀 Quick Deployment

### Option 1: Automated Script
```bash
chmod +x aws-deploy.sh
./aws-deploy.sh
```

### Option 2: Manual Steps

#### Step 1: Initialize EB Application
```bash
eb init -p python-3.11 my-job-recommendation-app --region us-east-1
```

#### Step 2: Create Environment
```bash
eb create production-env --instance-type t3.micro --single-instance
```

#### Step 3: Deploy
```bash
eb deploy
```

## 🌐 Environment Configuration

### Environment Variables
The following environment variables are configured in `.ebextensions/03_environment.config`:

- `SECRET_KEY`: JWT secret key (change this in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiry time
- `DATABASE_URL`: SQLite database path
- `CORS_ORIGINS`: Allowed CORS origins
- `LOG_LEVEL`: Application log level

### Customize Environment Variables
Edit `.ebextensions/03_environment.config` to change values:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    SECRET_KEY: "your-actual-secret-key"
    CORS_ORIGINS: "https://yourdomain.com,https://www.yourdomain.com"
```

## 📊 Monitoring and Management

### View Application Status
```bash
eb status
```

### View Logs
```bash
eb logs
```

### Open Application
```bash
eb open
```

### SSH into Instance
```bash
eb ssh
```

## 🔒 Security Considerations

### 1. Environment Variables
- Change the default `SECRET_KEY`
- Use strong, unique keys
- Don't commit sensitive data to version control

### 2. CORS Configuration
Update CORS origins to match your frontend domain:
```yaml
CORS_ORIGINS: "https://your-frontend-domain.com"
```

### 3. Database Security
For production, consider using:
- Amazon RDS for PostgreSQL/MySQL
- Amazon DynamoDB for NoSQL
- Encrypted storage for sensitive data

## 🛠️ Troubleshooting

### Common Issues

#### 1. EB CLI Installation Issues
```bash
# Reinstall EB CLI
pip uninstall awsebcli
pip install awsebcli

# Or use pip3
pip3 install awsebcli
```

#### 2. Permission Issues
```bash
# Check AWS credentials
aws sts get-caller-identity

# Configure credentials
aws configure
```

#### 3. Deployment Failures
```bash
# Check logs
eb logs

# Check status
eb status

# Restart environment
eb restart
```

#### 4. Health Check Failures
```bash
# SSH into instance
eb ssh

# Check application logs
sudo tail -f /var/log/eb-docker/containers/eb-current-app/*.log
```

### Performance Optimization

#### 1. Instance Type
For better performance, consider:
- `t3.small` for development
- `t3.medium` for production
- `c5.large` for high-traffic applications

#### 2. Auto Scaling
Configure auto scaling in EB console:
- Minimum instances: 1
- Maximum instances: 5
- Scale up CPU: 70%
- Scale down CPU: 30%

## 📈 Production Checklist

- [ ] Environment variables configured
- [ ] SECRET_KEY changed from default
- [ ] CORS origins properly set
- [ ] Database initialized
- [ ] Health checks passing
- [ ] Logs being collected
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] SSL certificate configured (if using custom domain)

## 🔄 Updates and Maintenance

### Deploy Updates
```bash
# Deploy changes
eb deploy

# Deploy to specific environment
eb deploy production-env
```

### Environment Management
```bash
# List environments
eb list

# Terminate environment
eb terminate production-env

# Clone environment
eb clone production-env staging-env
```

### Database Migrations
```bash
# SSH into instance
eb ssh

# Run database initialization
python init_database.py
```

## 🌐 Custom Domain Setup

### 1. Route 53 Configuration
1. Create hosted zone for your domain
2. Create A record pointing to EB environment
3. Configure SSL certificate in EB console

### 2. SSL Certificate
1. Request certificate in AWS Certificate Manager
2. Validate domain ownership
3. Configure in EB environment

## 📝 Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |
| `DATABASE_URL` | Database connection string | `sqlite:///./app.db` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |
| `LOG_LEVEL` | Application log level | `INFO` |
| `ENVIRONMENT` | Environment name | `production` |

## 🔗 Useful Commands

```bash
# Initialize EB application
eb init

# Create environment
eb create

# Deploy application
eb deploy

# Check status
eb status

# View logs
eb logs

# Open application
eb open

# SSH into instance
eb ssh

# List environments
eb list

# Terminate environment
eb terminate

# Clone environment
eb clone
```

## 🆘 Support

If you encounter issues:
1. Check EB logs: `eb logs`
2. Verify environment variables
3. Check AWS credentials
4. Review the troubleshooting section above
5. Check AWS EB documentation
