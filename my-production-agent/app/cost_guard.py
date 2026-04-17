"""
Cost Guard Module
Tracks and limits API costs per user
"""
import time
from collections import defaultdict
from fastapi import HTTPException
from app.config import settings


# In-memory cost tracking
# Format: {user_id: {"month": "2026-04", "cost": 5.23}}
_user_costs: dict[str, dict] = defaultdict(lambda: {"month": "", "cost": 0.0})


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Estimate cost based on token usage.
    Using GPT-4o-mini pricing as reference:
    - Input: $0.150 per 1M tokens
    - Output: $0.600 per 1M tokens
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        float: Estimated cost in USD
    """
    input_cost = (input_tokens / 1_000_000) * 0.150
    output_cost = (output_tokens / 1_000_000) * 0.600
    return input_cost + output_cost


def check_budget(user_id: str, estimated_cost: float) -> None:
    """
    Check if user has budget remaining for this request.
    
    Args:
        user_id: User identifier
        estimated_cost: Estimated cost of the request
        
    Raises:
        HTTPException: 402 if budget exceeded
    """
    current_month = time.strftime("%Y-%m")
    user_data = _user_costs[user_id]
    
    # Reset if new month
    if user_data["month"] != current_month:
        user_data["month"] = current_month
        user_data["cost"] = 0.0
    
    # Check if adding this cost would exceed budget
    new_total = user_data["cost"] + estimated_cost
    
    if new_total > settings.monthly_budget_usd:
        raise HTTPException(
            status_code=402,
            detail=f"Monthly budget of ${settings.monthly_budget_usd} exceeded. Current: ${user_data['cost']:.4f}",
        )


def record_cost(user_id: str, actual_cost: float) -> None:
    """
    Record actual cost after request completion.
    
    Args:
        user_id: User identifier
        actual_cost: Actual cost of the request
    """
    current_month = time.strftime("%Y-%m")
    user_data = _user_costs[user_id]
    
    # Reset if new month
    if user_data["month"] != current_month:
        user_data["month"] = current_month
        user_data["cost"] = 0.0
    
    user_data["cost"] += actual_cost


def get_budget_status(user_id: str) -> dict:
    """
    Get current budget status for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        dict: Budget status information
    """
    current_month = time.strftime("%Y-%m")
    user_data = _user_costs[user_id]
    
    # Reset if new month
    if user_data["month"] != current_month:
        user_data["month"] = current_month
        user_data["cost"] = 0.0
    
    remaining = max(0, settings.monthly_budget_usd - user_data["cost"])
    used_percent = (user_data["cost"] / settings.monthly_budget_usd) * 100
    
    return {
        "month": current_month,
        "budget_usd": settings.monthly_budget_usd,
        "used_usd": round(user_data["cost"], 4),
        "remaining_usd": round(remaining, 4),
        "used_percent": round(used_percent, 2),
    }
