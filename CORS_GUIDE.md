# CORS Configuration Guide

This guide explains the CORS (Cross-Origin Resource Sharing) configuration for the AI Job Platform API and how to troubleshoot CORS issues.

## Current Configuration

The API uses environment-aware CORS configuration that automatically adjusts based on the environment:

### Development Environment
- Allows all localhost URLs (3000, 4200, 8080)
- Allows ngrok URLs for testing
- More permissive for development

### Production Environment
- Only allows specific production domains
- More restrictive for security
- No wildcard origins

## CORS Settings

### Allowed Origins
```python
# Development
[
    "http://localhost:3000",      # React default
    "http://localhost:4200",      # Angular default
    "http://localhost:8080",      # Vue default
    "http://127.0.0.1:4200",      # Angular alternative
    "http://127.0.0.1:3000",      # React alternative
    "https://5705d9dc3a2f.ngrok-free.app",  # Your ngrok URL
    "https://*.ngrok-free.app",   # All ngrok URLs
]

# Production
[
    "https://your-production-domain.com",
    "https://www.your-production-domain.com",
]
```

### Allowed Methods
- GET, POST, PUT, DELETE, PATCH, OPTIONS

### Allowed Headers
- All headers (`*`)

### Credentials
- Enabled (`allow_credentials=True`)

## Testing CORS Configuration

### 1. Check CORS Info Endpoint
```bash
curl https://5705d9dc3a2f.ngrok-free.app/cors-info
```

This will return:
```json
{
    "allowed_origins": ["http://localhost:4200", "https://5705d9dc3a2f.ngrok-free.app", ...],
    "environment": "development",
    "debug": true,
    "cors_enabled": true
}
```

### 2. Test Preflight Request
```bash
curl -X OPTIONS \
  -H "Origin: http://localhost:4200" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  https://5705d9dc3a2f.ngrok-free.app/health
```

### 3. Test Actual Request
```bash
curl -X GET \
  -H "Origin: http://localhost:4200" \
  https://5705d9dc3a2f.ngrok-free.app/health
```

## Common CORS Issues and Solutions

### 1. "No 'Access-Control-Allow-Origin' header"

**Problem**: The frontend origin is not in the allowed origins list.

**Solution**: 
- Check the `/cors-info` endpoint to see current allowed origins
- Add your frontend URL to the CORS configuration
- Update the `cors_origins` list in `app/core/config.py`

### 2. "Method not allowed"

**Problem**: The HTTP method is not in the allowed methods list.

**Solution**: 
- Check that your request method is in the allowed methods
- Current allowed methods: GET, POST, PUT, DELETE, PATCH, OPTIONS

### 3. "Credentials not supported"

**Problem**: Frontend is sending credentials but CORS is not configured for it.

**Solution**: 
- Ensure `allow_credentials=True` in CORS configuration
- Frontend must set `withCredentials: true` in requests

### 4. "Request header not allowed"

**Problem**: Custom headers are being sent but not allowed.

**Solution**: 
- Add specific headers to `allow_headers` list
- Or use `allow_headers=["*"]` for all headers

## Frontend Configuration

### Angular HTTP Client
```typescript
// In your Angular service
import { HttpClient, HttpHeaders } from '@angular/common/http';

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  }),
  withCredentials: true  // If sending cookies/credentials
};

this.http.get(`${this.configService.getApiUrl()}/health`, httpOptions)
```

### JavaScript Fetch API
```javascript
fetch('https://5705d9dc3a2f.ngrok-free.app/health', {
  method: 'GET',
  credentials: 'include',  // If sending cookies
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  }
})
```

## Environment Variables

You can control CORS behavior using environment variables:

```bash
# Set environment
export ENVIRONMENT=development

# Custom origins (comma-separated)
export CORS_ORIGINS="http://localhost:4200,https://myapp.com"
```

## Debugging CORS Issues

### 1. Browser Developer Tools
- Open Developer Tools (F12)
- Go to Network tab
- Look for failed requests (red)
- Check the CORS error details

### 2. Server Logs
- Check your FastAPI server logs
- Look for CORS-related errors
- Verify the request is reaching the server

### 3. Test with curl
```bash
# Test preflight
curl -X OPTIONS -H "Origin: http://localhost:4200" \
  -H "Access-Control-Request-Method: POST" \
  https://5705d9dc3a2f.ngrok-free.app/health

# Test actual request
curl -X GET -H "Origin: http://localhost:4200" \
  https://5705d9dc3a2f.ngrok-free.app/health
```

## Production Considerations

### 1. Security
- Never use `allow_origins=["*"]` in production
- Specify exact domains
- Use HTTPS only

### 2. Performance
- Set appropriate `max_age` for preflight caching
- Minimize allowed headers and methods

### 3. Monitoring
- Monitor CORS errors in production
- Set up alerts for CORS failures
- Log CORS-related issues

## Quick Fixes

### For Development
If you're having CORS issues in development, you can temporarily allow all origins:

```python
# In app/core/config.py, temporarily change:
cors_origins: List[str] = ["*"]
```

### For Production
For production, ensure you have the correct domains:

```python
# In app/core/config.py
if env == "production":
    return [
        "https://your-actual-domain.com",
        "https://www.your-actual-domain.com",
    ]
```

## Testing Checklist

- [ ] Frontend origin is in allowed origins list
- [ ] HTTP method is allowed
- [ ] Headers are allowed
- [ ] Credentials are properly configured
- [ ] HTTPS is used in production
- [ ] No wildcard origins in production

## Support

If you're still having CORS issues:

1. Check the `/cors-info` endpoint
2. Verify your frontend URL is in the allowed origins
3. Test with curl to isolate the issue
4. Check browser developer tools for detailed error messages
5. Review server logs for any backend errors
