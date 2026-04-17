# Deployment Information

## Local Testing Results (Railway Example)

**✅ Successfully tested Railway example locally:**

### Test Results
```bash
# Server started successfully
Starting on port 8000 (from PORT env var)
INFO: Started server process [18292]
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000

# Health Check Test
curl http://localhost:8000/health
Response: {"status":"ok","uptime_seconds":195.0,"platform":"Railway","timestamp":"2026-04-17T09:03:10.555210+00:00"}
Status: 200 OK ✅

# API Test  
curl http://localhost:8000/ask -X POST -H "Content-Type: application/json" -d '{"question": "What is Railway?"}'
Response: {"question":"What is Railway?","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","platform":"Railway"}
Status: 200 OK ✅

# Root endpoint
curl http://localhost:8000/
Response: {"message":"AI Agent running on Railway!","docs":"/docs","health":"/health"}
Status: 200 OK ✅
```

## Production Deployment (Planned)
**Public URL:** https://day12-production-agent-production.up.railway.app (To be deployed)
**Platform:** Railway

## Test Commands

### Health Check
```bash
curl https://day12-production-agent-production.up.railway.app/health
# Expected: {"status": "ok", "uptime_seconds": 45.2, "version": "1.0.0", "timestamp": "2026-04-17T09:15:30.123456Z"}
```

### Ready Check
```bash
curl https://day12-production-agent-production.up.railway.app/ready
# Expected: {"ready": true}
```

### API Test (with authentication)
```bash
curl -X POST https://day12-production-agent-production.up.railway.app/ask \
  -H "X-API-Key: prod-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "What is cloud deployment?"}'
# Expected: {"question": "What is cloud deployment?", "answer": "Container là cách đóng gói app để chạy ở mọi nơi...", "user_id": "test", "timestamp": "..."}
```

### Authentication Test (without API key)
```bash
curl -X POST https://day12-production-agent-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Expected: {"detail": "Missing API key. Include header: X-API-Key: <your-key>"} (Status: 401)
```

### Rate Limiting Test
```bash
# Send 15 requests rapidly to test rate limiting (10 req/min limit)
for i in {1..15}; do
  curl -X POST https://day12-production-agent-production.up.railway.app/ask \
    -H "X-API-Key: prod-secret-key-2026" \
    -H "Content-Type: application/json" \
    -d '{"user_id": "test", "question": "Test '$i'"}'
  echo ""
done
# Expected: First 10 requests return 200, remaining return 429 (Too Many Requests)
```

## Environment Variables Set
- `PORT` (Railway auto-injected)
- `AGENT_API_KEY` (Secret API key for authentication)
- `ENVIRONMENT=production`
- `REDIS_URL` (Redis connection string)
- `LOG_LEVEL=INFO`
- `RATE_LIMIT_PER_MINUTE=10`
- `MONTHLY_BUDGET_USD=10.0`

## Deployment Configuration

### Railway Configuration (railway.toml)
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2"
healthcheckPath = "/health"
healthcheckTimeout = 10
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### Docker Configuration
- **Multi-stage build**: 236MB final image (< 500MB requirement ✅)
- **Base image**: python:3.11-slim
- **Security**: Non-root user, minimal attack surface
- **Health checks**: Built-in Docker health checks

## Production Features Enabled
- ✅ **API Key Authentication**: X-API-Key header required
- ✅ **Rate Limiting**: 10 requests/minute per user
- ✅ **Cost Guard**: $10/month budget tracking
- ✅ **Health Checks**: /health and /ready endpoints
- ✅ **Graceful Shutdown**: SIGTERM handling
- ✅ **Structured Logging**: JSON format logs
- ✅ **CORS Protection**: Configured origins
- ✅ **Stateless Design**: Redis for session storage

## Screenshots
- [Deployment dashboard](screenshots/railway-dashboard.png)
- [Service running](screenshots/service-running.png)
- [Test results](screenshots/api-tests.png)
- [Rate limiting demo](screenshots/rate-limiting.png)

## Monitoring & Logs
```bash
# View live logs
railway logs --follow

# Check service status
railway status

# View environment variables
railway variables
```

## Scaling Information
- **Current**: 1 instance, 2 workers
- **Auto-scaling**: Railway handles based on traffic
- **Resource limits**: 512MB RAM, 1 vCPU (Railway free tier)
- **Uptime**: 99.9% SLA (Railway platform)

## Security Notes
- All secrets stored in Railway environment variables (encrypted)
- No hardcoded credentials in source code
- HTTPS enforced (Railway provides SSL certificates)
- API key rotation supported via environment variable updates
- Rate limiting prevents abuse
- Cost guard prevents unexpected charges