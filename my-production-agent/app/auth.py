"""
Authentication Module
Supports API Key authentication
"""
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.config import settings

# API Key Header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: 401 if key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include header: X-API-Key: <your-key>",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )
    
    return api_key


def get_user_id_from_key(api_key: str) -> str:
    """
    Extract user ID from API key for rate limiting and cost tracking.
    In production, this would lookup from database.
    
    Args:
        api_key: Validated API key
        
    Returns:
        str: User identifier
    """
    # Simple hash for demo - in production, lookup from database
    return f"user_{hash(api_key) % 10000}"
