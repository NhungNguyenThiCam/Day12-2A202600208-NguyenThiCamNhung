# Production AI Agent — Day 12 Lab Complete

Production-ready AI Agent với đầy đủ features: authentication, rate limiting, cost protection, health checks, và graceful shutdown.

## ✅ Checklist (100 điểm)

### Part 1-5: Exercises (40 điểm)
- ✅ MISSION_ANSWERS.md hoàn chỉnh với tất cả câu trả lời

### Part 6: Final Project (60 điểm)

**Functional Requirements (20 điểm)**
- ✅ Agent trả lời câu hỏi qua REST API
- ✅ Support conversation history (stateless design)
- ✅ Error handling graceful

**Docker & Configuration (15 điểm)**
- ✅ Multi-stage Dockerfile (< 500 MB)
- ✅ docker-compose.yml với agent + redis
- ✅ Config từ environment variables
- ✅ .dockerignore

**Security (20 điểm)**
- ✅ API Key authentication
- ✅ Rate limiting (10 req/min per user)
- ✅ Cost guard ($10/month per user)
- ✅ No hardcoded secrets

**Reliability (15 điểm)**
- ✅ Health check endpoint (`/health`)
- ✅ Readiness check endpoint (`/ready`)
- ✅ Graceful shutdown (SIGTERM handler)
- ✅ Stateless design (ready for Redis)

**Deployment (10 điểm)**
- ✅ Railway config (`railway.toml`)
- ✅ Render config (`render.yaml`)
- ✅ Environment setup

---

## 🚀 Quick Start

### 1. Local Development

```bash
# Clone và setup
cd my-production-agent
cp .env.example .env

# Edit .env với your API key
nano .env

# Install dependencies
pip install -r requirements.txt

# Run locally
python -m app.main
```

Test:
```bash
# Health check
curl http://localhost:8000/health

# Ask endpoint (cần API key)
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: production-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is deployment?"}'
```

### 2. Docker Local

```bash
# Build image
docker build -t production-agent .

# Check image size (should be < 500 MB)
docker images production-agent

# Run container
docker run -p 8000:8000 --env-file .env production-agent
```

### 3. Docker Compose (Full Stack)

```bash
# Start all services (agent + redis)
docker compose up

# Scale agents
docker compose up --scale agent=3

# Stop
docker compose down
```

---

## ☁️ Cloud Deployment

### Deploy to Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables
railway variables set AGENT_API_KEY=your-secret-key
railway variables set ENVIRONMENT=production

# Deploy
railway up

# Get public URL
railway domain
```

### Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. New → Blueprint
4. Connect GitHub repo
5. Render reads `render.yaml` automatically
6. Set secrets in dashboard:
   - `AGENT_API_KEY`
   - `OPENAI_API_KEY` (optional)
7. Deploy!

---

## 📋 API Documentation

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | API information |
| `/ask` | POST | Yes | Ask AI agent |
| `/health` | GET | No | Liveness probe |
| `/ready` | GET | No | Readiness probe |
| `/metrics` | GET | Yes | Application metrics |
| `/docs` | GET | No | Swagger UI (dev only) |

### Authentication

Include API key in header:
```
X-API-Key: your-secret-key
```

### Example Request

```bash
curl -X POST https://your-app.railway.app/ask \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?"
  }'
```

### Example Response

```json
{
  "question": "What is the capital of France?",
  "answer": "The capital of France is Paris.",
  "model": "gpt-4o-mini",
  "timestamp": "2026-04-17T10:30:00Z",
  "tokens_used": {
    "input": 8,
    "output": 7,
    "total": 15
  }
}
```

---

## 🔒 Security Features

### 1. API Key Authentication
- All `/ask` requests require valid API key
- Keys stored in environment variables
- Easy rotation without code changes

### 2. Rate Limiting
- 10 requests per minute per user
- Sliding window algorithm
- Returns 429 with `Retry-After` header

### 3. Cost Guard
- $10 monthly budget per user
- Tracks token usage and costs
- Returns 402 when budget exceeded

### 4. Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- Server header removed

---

## 📊 Monitoring

### Health Check

```bash
curl https://your-app.railway.app/health
```

Response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 3600.5,
  "total_requests": 1234,
  "error_count": 5,
  "timestamp": "2026-04-17T10:30:00Z"
}
```

### Metrics (Protected)

```bash
curl https://your-app.railway.app/metrics \
  -H "X-API-Key: your-secret-key"
```

Response:
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
    "used_usd": 2.3456,
    "remaining_usd": 7.6544,
    "used_percent": 23.46
  }
}
```

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Without API key (should fail)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
# Expected: 401 Unauthorized

# 3. With API key (should work)
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: production-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
# Expected: 200 OK with answer

# 4. Rate limiting (send 15 requests)
for i in {1..15}; do
  curl -X POST http://localhost:8000/ask \
    -H "X-API-Key: production-secret-key-2026" \
    -H "Content-Type: application/json" \
    -d '{"question": "test '$i'"}'
  echo ""
done
# Expected: First 10 succeed, rest return 429
```

### Automated Testing

```bash
# Run production readiness check
python check_production_ready.py
```

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────┐
│  Load Balancer  │  (Railway/Render)
└──────┬──────────┘
       │
       ├─────────┬─────────┐
       ▼         ▼         ▼
   ┌──────┐  ┌──────┐  ┌──────┐
   │Agent1│  │Agent2│  │Agent3│  (Stateless)
   └───┬──┘  └───┬──┘  └───┬──┘
       │         │         │
       └─────────┴─────────┘
                 │
                 ▼
           ┌──────────┐
           │  Redis   │  (Shared state)
           └──────────┘
```

---

## 📝 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |
| `ENVIRONMENT` | No | `development` | Environment name |
| `DEBUG` | No | `false` | Debug mode |
| `AGENT_API_KEY` | **Yes** | - | API key for authentication |
| `OPENAI_API_KEY` | No | - | OpenAI API key (uses mock if not set) |
| `LLM_MODEL` | No | `gpt-4o-mini` | LLM model name |
| `RATE_LIMIT_PER_MINUTE` | No | `10` | Rate limit per user |
| `MONTHLY_BUDGET_USD` | No | `10.0` | Monthly budget per user |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL |
| `LOG_LEVEL` | No | `INFO` | Logging level |

---

## 🐛 Troubleshooting

### Issue: Container fails health check

**Solution:**
```bash
# Check logs
docker logs <container_id>

# Test health endpoint manually
docker exec <container_id> curl http://localhost:8000/health
```

### Issue: Rate limit not working

**Solution:**
- Check if Redis is running: `docker compose ps`
- Verify REDIS_URL in environment
- Check logs for connection errors

### Issue: 401 Unauthorized

**Solution:**
- Verify API key in request header: `X-API-Key: your-key`
- Check AGENT_API_KEY environment variable
- Ensure no typos in key

---

## 📚 Resources

- [12-Factor App](https://12factor.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)

---

## 🎯 Grading Criteria

| Criteria | Points | Status |
|----------|--------|--------|
| **Functionality** | 20 | ✅ |
| **Docker** | 15 | ✅ |
| **Security** | 20 | ✅ |
| **Reliability** | 20 | ✅ |
| **Scalability** | 15 | ✅ |
| **Deployment** | 10 | ✅ |
| **Total** | 100 | ✅ |

---

## 📄 License

MIT License - Free to use for educational purposes.

---

**Built with ❤️ for Day 12 Lab — VinUniversity 2026**
