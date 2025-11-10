from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "GrantGPT"
    APP_VERSION: str = "0.1.0"
    API_VERSION: str = "v1"
    DEBUG: bool = True
    
    # API
    API_URL: str = "http://localhost:8008"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    
    # Qdrant
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "grants"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENROUTER_API_KEY: str = ""
    
    # Security
    JWT_SECRET: str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3008,http://localhost:3000"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # AI Settings
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # File Storage
    STORAGE_PATH: str = "./storage"
    DOCUMENTS_PATH: str = "./storage/documents"
    TEMP_PATH: str = "./storage/temp"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Sentry (Optional)
    SENTRY_DSN: str = ""
    
    # Email (Optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@grantgpt.de"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

