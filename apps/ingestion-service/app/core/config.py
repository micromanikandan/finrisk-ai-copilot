"""Configuration settings for the ingestion service."""

from functools import lru_cache
from typing import List

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    APP_NAME: str = "FinRisk Ingestion Service"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://ingestion_user:ingestion_dev_password_2024@localhost:5432/ingestion_service",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379/1", env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(default=10, env="REDIS_POOL_SIZE")
    
    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_PRODUCER_CONFIG: dict = {
        "acks": "all",
        "retries": 3,
        "enable_idempotence": True,
        "max_in_flight_requests_per_connection": 5,
        "compression_type": "snappy",
        "batch_size": 16384,
        "linger_ms": 10,
        "buffer_memory": 33554432,
    }
    
    # Security settings
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="RS256", env="JWT_ALGORITHM")
    JWT_ISSUER: str = Field(default="http://localhost:8080/realms/finrisk", env="JWT_ISSUER")
    JWT_AUDIENCE: str = Field(default="finrisk-copilot", env="JWT_AUDIENCE")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    # File upload settings
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["application/json", "text/csv", "application/xml", "application/octet-stream"],
        env="ALLOWED_FILE_TYPES"
    )
    UPLOAD_PATH: str = Field(default="/tmp/finrisk/uploads", env="UPLOAD_PATH")
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Observability settings
    JAEGER_ENDPOINT: str = Field(default="", env="JAEGER_ENDPOINT")
    PROMETHEUS_METRICS: bool = Field(default=True, env="PROMETHEUS_METRICS")
    
    # Tenant settings
    DEFAULT_TENANT_ID: str = Field(default="default", env="DEFAULT_TENANT_ID")
    DEFAULT_CELL_ID: str = Field(default="default", env="DEFAULT_CELL_ID")
    
    # Ingestion settings
    BATCH_SIZE: int = Field(default=1000, env="BATCH_SIZE")
    BATCH_TIMEOUT: int = Field(default=5, env="BATCH_TIMEOUT")  # seconds
    MAX_CONCURRENT_INGESTS: int = Field(default=10, env="MAX_CONCURRENT_INGESTS")
    
    # Data validation settings
    ENABLE_SCHEMA_VALIDATION: bool = Field(default=True, env="ENABLE_SCHEMA_VALIDATION")
    ENABLE_DATA_ENRICHMENT: bool = Field(default=True, env="ENABLE_DATA_ENRICHMENT")
    ENABLE_PII_DETECTION: bool = Field(default=True, env="ENABLE_PII_DETECTION")
    
    # Kafka topics
    INGESTION_EVENTS_TOPIC: str = Field(default="ingestion-events", env="INGESTION_EVENTS_TOPIC")
    DATA_EVENTS_TOPIC: str = Field(default="data-events", env="DATA_EVENTS_TOPIC")
    ERROR_EVENTS_TOPIC: str = Field(default="error-events", env="ERROR_EVENTS_TOPIC")
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def assemble_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
