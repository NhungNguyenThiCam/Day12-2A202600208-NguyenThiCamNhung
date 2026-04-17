"""
Configuration Management
Using Pydantic Settings for 12-factor app compliance
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server Configuration
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"
    
    # Security
    AGENT_API_KEY: str = "demo-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    RATE_LIMIT_ADMIN_PER_MINUTE: int = 100
    
    # Cost Guard
    DAILY_BUDGET_USD: float = 1.0
    GLOBAL_DAILY_BUDGET_USD: float = 10.0
    MONTHLY_BUDGET_USD: float = 10.0
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    # Application
    APP_NAME: str = "Production AI Agent"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()