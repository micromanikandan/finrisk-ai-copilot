"""
FinRisk AI Copilot - Entity Service

Advanced entity resolution and relationship mapping using Neo4j graph database.
Features:
- Entity resolution and deduplication
- Relationship discovery and mapping
- Graph-based risk scoring
- Real-time entity updates
- Complex network analysis
- Suspicious pattern detection
- Multi-tenant entity isolation
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

from app.api.v1 import entities, relationships, resolution, networks, health, metrics
from app.core.config import get_settings
from app.core.database import get_database
from app.core.neo4j_client import get_neo4j_client
from app.core.redis_client import get_redis_client
from app.core.kafka_consumer import get_kafka_consumer
from app.services.entity_resolution import EntityResolutionService
from app.services.relationship_mapper import RelationshipMapper
from app.services.graph_analyzer import GraphAnalyzer
from app.services.risk_scorer import RiskScorer
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
        resource = Resource.create({"service.name": "finrisk-entity-service"})
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
    logger.info("Starting FinRisk Entity Service", version="1.0.0")
    
    # Setup tracing
    setup_tracing()
    
    # Initialize database
    database = get_database()
    await database.connect()
    logger.info("Database connected")
    
    # Initialize Neo4j
    neo4j_client = get_neo4j_client()
    await neo4j_client.verify_connectivity()
    logger.info("Neo4j connected")
    
    # Initialize Redis
    redis_client = get_redis_client()
    await redis_client.ping()
    logger.info("Redis connected")
    
    # Initialize Kafka consumer
    kafka_consumer = get_kafka_consumer()
    await kafka_consumer.start()
    logger.info("Kafka consumer started")
    
    # Initialize entity resolution service
    entity_resolution = EntityResolutionService()
    await entity_resolution.initialize()
    logger.info("Entity resolution service initialized")
    
    # Initialize relationship mapper
    relationship_mapper = RelationshipMapper()
    await relationship_mapper.initialize()
    logger.info("Relationship mapper initialized")
    
    # Initialize graph analyzer
    graph_analyzer = GraphAnalyzer()
    await graph_analyzer.initialize()
    logger.info("Graph analyzer initialized")
    
    # Initialize risk scorer
    risk_scorer = RiskScorer()
    await risk_scorer.initialize()
    logger.info("Risk scorer initialized")
    
    yield
    
    # Cleanup
    await kafka_consumer.stop()
    await redis_client.close()
    await neo4j_client.close()
    await database.disconnect()
    logger.info("FinRisk Entity Service stopped")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="FinRisk Entity Service",
        description="Advanced entity resolution and relationship mapping using Neo4j graph database",
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
    app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
    app.include_router(relationships.router, prefix="/api/v1/relationships", tags=["relationships"])
    app.include_router(resolution.router, prefix="/api/v1/resolution", tags=["resolution"])
    app.include_router(networks.router, prefix="/api/v1/networks", tags=["networks"])
    
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
        port=8086,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False,
    )
