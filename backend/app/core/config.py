from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/coin87"
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash-lite"

    # VAPID keys for Web Push (read from backend/.env)
    VAPID_PUBLIC_KEY: Optional[str] = None
    VAPID_PRIVATE_KEY: Optional[str] = None
    VAPID_SUBJECT: Optional[str] = None
    
    # CORS - Production should override this in .env
    ALLOWED_ORIGINS: str = "http://localhost:9010,http://127.0.0.1:9010,http://localhost:9011,http://127.0.0.1:9011"
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 9010
    WORKERS: int = 1  # Override in production
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Feature Flags
    ENABLE_PAYWALL: bool = False  # Set to True to enable content locking

    class Config:
        env_file = ".env"
        
    @property
    def cors_origins(self) -> list[str]:
        """Parse ALLOWED_ORIGINS into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
