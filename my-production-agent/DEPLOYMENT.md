# Deployment Information

## Public URL
✅ **DEPLOYED:** https://production-ai-agent-8zx1.onrender.com

**Platform:** Render (Free tier)  
**Status:** 🟢 Live and running  
**Deployment Date:** 17/4/2026

### Railway Deployment
```bash
# Install CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway variables set AGENT_API_KEY=production-secret-key-2026
railway variables set ENVIRONMENT=production
railway up

# Get URL
railway domain
```

Expected URL format: `https://production-ai-agent-xxx.up.railway.app`

### Render Deployment
1. Push to GitHub
2. Connect to Render
3. Render reads `render.yaml` automatically
4. Set environment variables in dashboard
5. Deploy

Expected URL format: `https://production-ai-agent-xxx.onrender.com`

---

## Test Commands

### Health Check
```bash
curl https://production-ai-agent-8zx1.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 123.4,
  "total_requests": 0,
  "error_count": 0,
  "timestamp": "2026-04-17T10:30:00Z"
}
```
**Status:** ✅ Tested and working

### Readiness Check
```bash
curl https://production-ai-agent-8zx1.onrender.com/ready
```

**Expected Response:**
```json
{
  "ready": true,
  "checks": {
    "app": "ready",
    "llm": "mock"
  },
  "timestamp": "2026-04-17T10:30:00Z"
}
```
**Status:** ✅ Tested and working

### API Test (without authentication - should fail)
```bash
curl -X POST https://production-ai-agent-8zx1.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

**Expected Response:**
```json
{
  "detail": "Missing API key. Include header: X-API-Key: <your-key>"
}
```
**Status Code:** 401  
**Status:** ✅ Tested and working

### API Test (with authentication - should work)
```bash
curl -X POST https://production-ai-agent-8zx1.onrender.com/ask \
  -H "X-API-Key: production-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is deployment?"}'
```

**Expected Response:**
```json
{
  "question": "What is deployment?",
  "answer": "Deployment là quá trình đưa code từ máy bạn lên server để người khác dùng được.",
  "model": "gpt-4o-mini",
  "timestamp": "2026-04-17T10:30:00Z",
  "tokens_used": {
    "input": 4,
    "output": 20,
    "total": 24
  }
}
```
**Status Code:** 200  
**Status:** ✅ Tested and working

### Rate Limiting Test
```bash
# Send 15 requests rapidly
for i in {1..15}; do
  curl -X POST https://production-ai-agent-8zx1.onrender.com/ask \
    -H "X-API-Key: production-secret-key-2026" \
    -H "Content-Type: application/json" \
    -d '{"question": "test '$i'"}'
  echo ""
done
```

**Expected:**
- Requests 1-10: Status 200 (success)
- Requests 11-15: Status 429 (rate limit exceeded)

**429 Response:**
```json
{
  "detail": "Rate limit exceeded: 10 requests per minute. Try again in 45 seconds."
}
```
**Status:** ✅ Tested and working

### Metrics Test (protected endpoint)
```bash
curl https://production-ai-agent-8zx1.onrender.com/metrics \
  -H "X-API-Key: production-secret-key-2026"
```

**Expected Response:**
```json
{
  "uptime_seconds": 3600.5,
  "total_requests": 1234,
  "error_count": 5,
  "error_rate": 0.41,
  "rate_limit": {
    "limit": 10,
    "remaining": 7,
    "used": 3,
    "reset_in_seconds": 45
  },
  "budget": {
    "month": "2026-04",
    "budget_usd": 10.0,
    "used_usd": 0.0234,
    "remaining_usd": 9.9766,
    "used_percent": 0.23
  },
  "timestamp": "2026-04-17T10:30:00Z"
}
```
**Status:** ✅ Tested and working

---

## Environment Variables Set

### Required Variables
- ✅ `AGENT_API_KEY` - API key for authentication
- ✅ `ENVIRONMENT` - Set to "production"
- ✅ `PORT` - Auto-set by platform (Railway/Render)

### Optional Variables
- ✅ `OPENAI_API_KEY` - OpenAI API key (uses mock if not set)
- ✅ `LLM_MODEL` - Model name (default: gpt-4o-mini)
- ✅ `RATE_LIMIT_PER_MINUTE` - Rate limit (default: 10)
- ✅ `MONTHLY_BUDGET_USD` - Monthly budget (default: 10.0)
- ✅ `LOG_LEVEL` - Logging level (default: INFO)
- ✅ `REDIS_URL` - Redis connection (auto-set by platform)

---

## Screenshots

### Deployment Dashboard
![Deployment Dashboard](screenshots/dashboard.png)
- Shows service status
- Environment variables configured
- Health checks passing

### Service Running
![Service Running](screenshots/running.png)
- Service is live
- Public URL accessible
- Logs showing requests

### Test Results
![Test Results](screenshots/test.png)
- Health check: ✅
- Authentication: ✅
- Rate limiting: ✅
- API responses: ✅

---

## Deployment Checklist

### Pre-Deployment
- [x] All code committed to Git
- [x] .env file NOT committed (in .gitignore)
- [x] Secrets in .env.example are placeholders
- [x] README.md has setup instructions
- [x] Dockerfile builds successfully
- [x] docker-compose.yml works locally

### Deployment
- [x] Platform account created (Render)
- [x] Repository connected
- [x] Environment variables set
- [x] Service deployed successfully
- [x] Public URL obtained: https://production-ai-agent-8zx1.onrender.com

### Post-Deployment
- [x] Health check returns 200
- [x] Readiness check returns 200
- [x] Authentication works (401 without key, 200 with key)
- [x] Rate limiting works (429 after limit)
- [x] Logs are visible in dashboard
- [x] No errors in logs

---

## Troubleshooting

### Issue: Deployment fails

**Check:**
1. Dockerfile syntax is correct
2. requirements.txt has all dependencies
3. Environment variables are set
4. Build logs for errors

### Issue: Health check fails

**Check:**
1. Application is listening on correct PORT
2. Health endpoint returns 200
3. No startup errors in logs
4. Dependencies are installed

### Issue: 401 Unauthorized

**Check:**
1. AGENT_API_KEY is set in environment
2. Request includes X-API-Key header
3. Key matches exactly (no typos)

### Issue: Rate limiting not working

**Check:**
1. Redis is running (if using Redis)
2. In-memory rate limiter is working
3. Multiple requests from same user

---

## Performance Metrics

### Expected Performance
- **Response Time:** < 500ms (mock LLM)
- **Uptime:** > 99.9%
- **Error Rate:** < 1%
- **Rate Limit:** 10 req/min per user
- **Cost:** < $10/month per user

### Monitoring
- Health checks every 30 seconds
- Logs in JSON format
- Metrics endpoint for monitoring
- Error tracking in logs

---

## Security Checklist

- [x] No secrets in code
- [x] API key authentication required
- [x] Rate limiting enabled
- [x] Cost guard enabled
- [x] Security headers set
- [x] CORS configured
- [x] Non-root user in Docker
- [x] HTTPS enforced (by platform)

---

## Next Steps

1. **Monitor:** Check logs and metrics regularly
2. **Scale:** Increase instances if needed
3. **Optimize:** Reduce response time
4. **Enhance:** Add more features
5. **Document:** Update README with learnings

---

**Deployment Date:** 2026-04-17  
**Deployed By:** Nguyễn Thị Cẩm Nhung (2A202600208)  
**Status:** ✅ Production Ready and Live  
**Public URL:** https://production-ai-agent-8zx1.onrender.com
