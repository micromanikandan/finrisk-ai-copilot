"""
FinRisk AI Copilot - Search Service

Advanced search service with OpenSearch integration and hybrid vector search.
Features:
- Hybrid search combining BM25 and vector similarity
- Real-time document indexing and search
- Multi-modal search (text, semantic, fuzzy)
- Entity extraction and relationship mapping
- Search analytics and query optimization
- Real-time search suggestions and autocomplete
"""

from contextlib import asynccontextmanager
from typing import Dict, Any

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import make_asgi_app

from app.api.v1 import search, documents, analytics, suggestions, health, metrics
from app.core.config import get_settings
from app.core.database import get_database
from app.core.opensearch import get_opensearch_client
from app.core.redis_client import get_redis_client
from app.core.kafka_consumer import get_kafka_consumer
from app.services.embedding_service import EmbeddingService
from app.services.search_indexer import SearchIndexer
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
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
        resource = Resource.create({"service.name": "finrisk-search-service"})
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
    logger.info("Starting FinRisk Search Service", version="1.0.0")
    
    # Setup tracing
    setup_tracing()
    
    # Initialize database
    database = get_database()
    await database.connect()
    logger.info("Database connected")
    
    # Initialize OpenSearch
    opensearch_client = get_opensearch_client()
    await opensearch_client.ping()
    logger.info("OpenSearch connected")
    
    # Initialize Redis
    redis_client = get_redis_client()
    await redis_client.ping()
    logger.info("Redis connected")
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    await embedding_service.initialize()
    logger.info("Embedding service initialized")
    
    # Initialize search indexer
    search_indexer = SearchIndexer()
    await search_indexer.initialize()
    logger.info("Search indexer initialized")
    
    # Start Kafka consumer for real-time indexing
    kafka_consumer = get_kafka_consumer()
    await kafka_consumer.start()
    logger.info("Kafka consumer started")
    
    yield
    
    # Cleanup
    await kafka_consumer.stop()
    await redis_client.close()
    await opensearch_client.close()
    await database.disconnect()
    logger.info("FinRisk Search Service stopped")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="FinRisk Search Service",
        description="Advanced search service with OpenSearch integration and hybrid vector search",
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
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
    app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(suggestions.router, prefix="/api/v1/suggestions", tags=["suggestions"])
    
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
    
    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8083,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False,
    )
