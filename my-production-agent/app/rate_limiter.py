"""
Rate Limiting Module
Implements sliding window rate limiting using in-memory storage
For production, use Redis-based implementation
"""
import time
from collections import defaultdict, deque
from fastapi import HTTPException
from app.config import settings


# In-memory storage for rate limiting
# Format: {user_id: deque([timestamp1, timestamp2, ...])}
_rate_windows: dict[str, deque] = defaultdict(deque)


def check_rate_limit(user_id: str) -> None:
    """
    Check if user has exceeded rate limit using sliding window algorithm.
    
    Args:
        user_id: User identifier for rate limiting
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    now = time.time()
    window = _rate_windows[user_id]
    
    # Remove timestamps older than 60 seconds (sliding window)
    while window and window[0] < now - 60:
        window.popleft()
    
    # Check if limit exceeded
    if len(window) >= settings.rate_limit_per_minute:
        retry_after = int(60 - (now - window[0]))
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} requests per minute. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )
    
    # Add current request timestamp
    window.append(now)


def get_rate_limit_status(user_id: str) -> dict:
    """
    Get current rate limit status for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        dict: Rate limit status information
    """
    now = time.time()
    window = _rate_windows.get(user_id, deque())
    
    # Clean old timestamps
    while window and window[0] < now - 60:
        window.popleft()
    
    remaining = max(0, settings.rate_limit_per_minute - len(window))
    
    return {
        "limit": settings.rate_limit_per_minute,
        "remaining": remaining,
        "used": len(window),
        "reset_in_seconds": 60 if window else 0,
    }
