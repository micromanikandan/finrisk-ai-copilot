"""
FinRisk AI Copilot - Ingestion Service

High-performance data ingestion service for financial crime data.
Features:
- FastAPI with async/await for high concurrency
- Transactional Outbox Pattern for reliable event streaming
- Multi-format data ingestion (JSON, CSV, XML, Parquet)
- Real-time validation and enrichment
- Kafka integration for event streaming
- PostgreSQL with async SQLAlchemy
- Redis for caching and rate limiting
- OpenTelemetry for observability
"""

from contextlib import asynccontextmanager
from typing import Any, Dict

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import make_asgi_app

from app.api.v1 import ingestion, health, metrics
from app.core.config import get_settings
from app.core.database import get_database
from app.core.kafka_producer import get_kafka_producer
from app.core.redis_client import get_redis_client
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.middleware.tenant import TenantMiddleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(30),  # INFO level
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


def setup_tracing() -> None:
    """Setup OpenTelemetry tracing."""
    settings = get_settings()
    
    if settings.JAEGER_ENDPOINT:
        resource = Resource.create({"service.name": "finrisk-ingestion-service"})
        provider = TracerProvider(resource=resource)
        
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        provider.add_span_processor(span_processor)
        trace.set_tracer_provider(provider)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings = get_settings()
    logger.info("Starting FinRisk Ingestion Service", version="1.0.0")
    
    # Setup tracing
    setup_tracing()
    
    # Initialize database
    database = get_database()
    await database.connect()
    logger.info("Database connected")
    
    # Initialize Kafka producer
    kafka_producer = get_kafka_producer()
    await kafka_producer.start()
    logger.info("Kafka producer started")
    
    # Initialize Redis client
    redis_client = get_redis_client()
    await redis_client.ping()
    logger.info("Redis client connected")
    
    yield
    
    # Cleanup
    await kafka_producer.stop()
    await database.disconnect()
    await redis_client.close()
    logger.info("FinRisk Ingestion Service stopped")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="FinRisk Ingestion Service",
        description="High-performance data ingestion service for financial crime data",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TenantMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
    app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["ingestion"])
    
    # Prometheus metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/prometheus", metrics_app)
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception",
            exc_info=exc,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "message": str(exc)},
        )
    
    # Instrument with OpenTelemetry
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    
    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8081,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False,
    )
