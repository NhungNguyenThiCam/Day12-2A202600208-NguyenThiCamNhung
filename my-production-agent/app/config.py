"""
Production Config — 12-Factor App Principles
All configuration from environment variables
"""
import os
import logging
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")

    # Application Info
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Production AI Agent"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))

    # LLM Configuration
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("MAX_TOKENS", "500")))

    # Security
    agent_api_key: str = field(default_factory=lambda: os.getenv("AGENT_API_KEY", "dev-key-change-me"))
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", "dev-jwt-secret"))
    allowed_origins: list = field(
        default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "*").split(",")
    )

    # Rate Limiting
    rate_limit_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    )

    # Cost Guard
    monthly_budget_usd: float = field(
        default_factory=lambda: float(os.getenv("MONTHLY_BUDGET_USD", "10.0"))
    )
    daily_budget_usd: float = field(
        default_factory=lambda: float(os.getenv("DAILY_BUDGET_USD", "1.0"))
    )

    # Storage
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    def validate(self):
        """Validate configuration and fail fast if critical settings are missing"""
        logger = logging.getLogger(__name__)
        
        # Production checks
        if self.environment == "production":
            if self.agent_api_key == "dev-key-change-me":
                raise ValueError("❌ AGENT_API_KEY must be set in production!")
            if self.jwt_secret == "dev-jwt-secret":
                raise ValueError("❌ JWT_SECRET must be set in production!")
            if self.debug:
                logger.warning("⚠️  DEBUG mode is enabled in production!")
        
        # Warnings
        if not self.openai_api_key:
            logger.warning("⚠️  OPENAI_API_KEY not set — using mock LLM")
        
        if self.rate_limit_per_minute < 1:
            raise ValueError("❌ RATE_LIMIT_PER_MINUTE must be at least 1")
        
        if self.monthly_budget_usd <= 0:
            raise ValueError("❌ MONTHLY_BUDGET_USD must be positive")
        
        logger.info(f"✅ Configuration validated for environment: {self.environment}")
        return self


# Singleton instance
settings = Settings().validate()
