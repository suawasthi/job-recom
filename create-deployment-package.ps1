# PowerShell script to create deployment package for AWS Elastic Beanstalk

Write-Host "🚀 Creating AWS Elastic Beanstalk Deployment Package" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Error: requirements.txt not found. Please run this script from the backend directory." -ForegroundColor Red
    exit 1
}

# Remove existing ZIP if it exists
if (Test-Path "app.zip") {
    Write-Host "🗑️ Removing existing app.zip..." -ForegroundColor Yellow
    Remove-Item "app.zip" -Force
}

Write-Host "📦 Creating deployment package..." -ForegroundColor Cyan

# Create ZIP file excluding unnecessary files
$excludePatterns = @(
    "*.pyc",
    "__pycache__/*",
    ".git/*",
    "*.db",
    "uploads/*",
    "node_modules/*",
    ".env",
    ".env.local",
    "*.log",
    "*.tmp",
    ".DS_Store",
    "Thumbs.db"
)

# Build the exclude string
$excludeString = $excludePatterns | ForEach-Object { "--exclude=$_" }

# Create ZIP using PowerShell
try {
    # Get all files and directories
    $files = Get-ChildItem -Path . -Recurse | Where-Object {
        $exclude = $false
        foreach ($pattern in $excludePatterns) {
            if ($pattern -like "*/*") {
                $dirPattern = $pattern.Replace("/*", "")
                if ($_.FullName -like "*\$dirPattern*") {
                    $exclude = $true
                    break
                }
            } else {
                if ($_.Name -like $pattern) {
                    $exclude = $true
                    break
                }
            }
        }
        -not $exclude
    }

    # Create ZIP
    Compress-Archive -Path $files.FullName -DestinationPath "app.zip" -Force
    
    Write-Host "✅ Deployment package created successfully!" -ForegroundColor Green
    Write-Host "📁 Package: app.zip" -ForegroundColor Cyan
    
    # Show package size
    $size = (Get-Item "app.zip").Length
    $sizeMB = [math]::Round($size / 1MB, 2)
    Write-Host "📊 Package size: $sizeMB MB" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error creating deployment package: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to AWS Elastic Beanstalk Console: https://console.aws.amazon.com/elasticbeanstalk/" -ForegroundColor White
Write-Host "2. Create a new application named 'my-job-recommendation-app'" -ForegroundColor White
Write-Host "3. Create a new environment with Python 3.11 platform" -ForegroundColor White
Write-Host "4. Upload app.zip and deploy" -ForegroundColor White
Write-Host "5. Configure environment variables in the EB console" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Required environment variables:" -ForegroundColor Yellow
Write-Host "   - SECRET_KEY: your-production-secret-key" -ForegroundColor White
Write-Host "   - ACCESS_TOKEN_EXPIRE_MINUTES: 30" -ForegroundColor White
Write-Host "   - DATABASE_URL: sqlite:///./app.db" -ForegroundColor White
Write-Host "   - CORS_ORIGINS: *" -ForegroundColor White
Write-Host "   - LOG_LEVEL: INFO" -ForegroundColor White
Write-Host "   - MAX_FILE_SIZE_MB: 10" -ForegroundColor White
Write-Host "   - ENVIRONMENT: production" -ForegroundColor White

