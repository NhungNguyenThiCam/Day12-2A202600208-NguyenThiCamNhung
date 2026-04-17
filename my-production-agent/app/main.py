"""
Production AI Agent — Day 12 Lab Complete

Checklist:
  ✅ Config từ environment (12-factor)
  ✅ Structured JSON logging
  ✅ API Key authentication
  ✅ Rate limiting (10 req/min per user)
  ✅ Cost guard ($10/month per user)
  ✅ Input validation (Pydantic)
  ✅ Health check + Readiness probe
  ✅ Graceful shutdown
  ✅ Security headers
  ✅ CORS
  ✅ Error handling
  ✅ Stateless design (ready for Redis)
"""
import os
import sys
import time
import signal
import logging
import json
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from app.config import settings
from app.auth import verify_api_key, get_user_id_from_key
from app.rate_limiter import check_rate_limit, get_rate_limit_status
from app.cost_guard import check_budget, record_cost, estimate_cost, get_budget_status

# Mock LLM (replace with OpenAI when API key available)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.mock_llm import ask as llm_ask

# ─────────────────────────────────────────────────────────
# Logging — Structured JSON
# ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────
# Application State
# ─────────────────────────────────────────────────────────
START_TIME = time.time()
_is_ready = False
_request_count = 0
_error_count = 0

# ─────────────────────────────────────────────────────────
# Lifespan Management
# ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Startup: Initialize connections, load models
    Shutdown: Close connections gracefully
    """
    global _is_ready
    
    # Startup
    logger.info(json.dumps({
        "event": "startup",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "port": settings.port,
    }))
    
    # Simulate initialization (database, Redis, model loading)
    time.sleep(0.1)
    _is_ready = True
    
    logger.info(json.dumps({"event": "ready", "message": "Agent is ready to serve requests"}))
    
    yield  # Application running
    
    # Shutdown
    _is_ready = False
    logger.info(json.dumps({"event": "shutdown", "message": "Shutting down gracefully"}))
    
    # Close connections
    # redis_client.close()
    # db_connection.close()
    
    time.sleep(0.1)  # Allow in-flight requests to complete
    logger.info(json.dumps({"event": "shutdown_complete"}))


# ─────────────────────────────────────────────────────────
# FastAPI Application
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready AI Agent with authentication, rate limiting, and cost protection",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    allow_credentials=True,
)


# ─────────────────────────────────────────────────────────
# Request Middleware
# ─────────────────────────────────────────────────────────
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """
    Middleware for logging and security headers.
    """
    global _request_count, _error_count
    
    start_time = time.time()
    _request_count += 1
    
    try:
        response: Response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # response.headers.pop("server", None)  # Hide server info - commented out due to MutableHeaders issue
        
        # Log request
        duration_ms = round((time.time() - start_time) * 1000, 1)
        logger.info(json.dumps({
            "event": "request",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "client": str(request.client.host) if request.client else "unknown",
        }))
        
        return response
        
    except Exception as e:
        _error_count += 1
        logger.error(json.dumps({
            "event": "request_error",
            "error": str(e),
            "path": request.url.path,
        }))
        raise


# ─────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    """Request model for /ask endpoint"""
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Your question for the AI agent",
        example="What is the capital of France?"
    )


class AskResponse(BaseModel):
    """Response model for /ask endpoint"""
    question: str
    answer: str
    model: str
    timestamp: str
    tokens_used: dict


# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    """
    Root endpoint with API information.
    """
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running",
        "endpoints": {
            "ask": "POST /ask (requires X-API-Key)",
            "health": "GET /health",
            "ready": "GET /ready",
            "docs": "GET /docs (dev only)",
        },
        "authentication": "Include header: X-API-Key: <your-key>",
    }


@app.post("/ask", response_model=AskResponse, tags=["Agent"])
async def ask_agent(
    body: AskRequest,
    request: Request,
    api_key: str = Depends(verify_api_key),
):
    """
    Send a question to the AI agent.
    
    **Authentication:** Include header `X-API-Key: <your-key>`
    
    **Rate Limit:** 10 requests per minute per user
    
    **Cost Limit:** $10 per month per user
    """
    # Get user ID from API key
    user_id = get_user_id_from_key(api_key)
    
    # Rate limiting
    check_rate_limit(user_id)
    
    # Estimate tokens (rough approximation: 1 word ≈ 1.3 tokens)
    input_tokens = int(len(body.question.split()) * 1.3)
    estimated_cost = estimate_cost(input_tokens, 0)
    
    # Budget check
    check_budget(user_id, estimated_cost)
    
    # Log request
    logger.info(json.dumps({
        "event": "agent_call",
        "user_id": user_id,
        "question_length": len(body.question),
        "estimated_tokens": input_tokens,
    }))
    
    # Call LLM
    try:
        answer = llm_ask(body.question)
    except Exception as e:
        logger.error(json.dumps({"event": "llm_error", "error": str(e)}))
        raise HTTPException(
            status_code=500,
            detail="Failed to generate response. Please try again."
        )
    
    # Estimate output tokens
    output_tokens = int(len(answer.split()) * 1.3)
    actual_cost = estimate_cost(input_tokens, output_tokens)
    
    # Record cost
    record_cost(user_id, actual_cost)
    
    # Log response
    logger.info(json.dumps({
        "event": "agent_response",
        "user_id": user_id,
        "answer_length": len(answer),
        "tokens": {"input": input_tokens, "output": output_tokens},
        "cost_usd": round(actual_cost, 6),
    }))
    
    return AskResponse(
        question=body.question,
        answer=answer,
        model=settings.llm_model,
        timestamp=datetime.now(timezone.utc).isoformat(),
        tokens_used={"input": input_tokens, "output": output_tokens, "total": input_tokens + output_tokens},
    )


@app.get("/health", tags=["Operations"])
def health():
    """Liveness probe. Platform restarts container if this endpoint fails."""
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": _request_count,
        "error_count": _error_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready", tags=["Operations"])
def ready():
    """Readiness probe. Load balancer stops routing traffic here if not ready."""
    if not _is_ready:
        raise HTTPException(
            status_code=503,
            detail="Service not ready yet"
        )
    
    # Check dependencies (Redis, database, etc.)
    checks = {
        "app": "ready",
        "llm": "mock" if not settings.openai_api_key else "openai",
    }
    
    return {
        "ready": True,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics", tags=["Operations"])
def metrics(api_key: str = Depends(verify_api_key)):
    """
    Basic metrics endpoint (protected).
    Shows application statistics.
    """
    user_id = get_user_id_from_key(api_key)
    
    return {
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": _request_count,
        "error_count": _error_count,
        "error_rate": round(_error_count / max(_request_count, 1) * 100, 2),
        "rate_limit": get_rate_limit_status(user_id),
        "budget": get_budget_status(user_id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────
# Graceful Shutdown Handler
# ─────────────────────────────────────────────────────────
def handle_shutdown_signal(signum, frame):
    """
    Handle SIGTERM/SIGINT for graceful shutdown.
    Platform sends SIGTERM when stopping container.
    """
    logger.info(json.dumps({
        "event": "signal_received",
        "signal": signum,
        "message": "Initiating graceful shutdown"
    }))
    # uvicorn handles the actual shutdown


signal.signal(signal.SIGTERM, handle_shutdown_signal)
signal.signal(signal.SIGINT, handle_shutdown_signal)


# ─────────────────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"API Key: {settings.agent_api_key[:4]}****")
    logger.info(f"Rate Limit: {settings.rate_limit_per_minute} req/min")
    logger.info(f"Monthly Budget: ${settings.monthly_budget_usd}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        timeout_graceful_shutdown=30,
    )
