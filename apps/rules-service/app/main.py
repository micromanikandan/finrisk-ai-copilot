"""
FinRisk AI Copilot - Rules and Decisions Service

Advanced rules engine with OPA (Open Policy Agent) integration for policy-based decisions.
Features:
- OPA policy engine for complex rule evaluation
- Lightweight ML model scoring for real-time decisions
- Rule versioning and A/B testing
- Decision audit trail and explainability
- Real-time policy updates
- Multi-tenant policy isolation
- Performance-optimized rule execution
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

from app.api.v1 import rules, policies, decisions, evaluation, health, metrics
from app.core.config import get_settings
from app.core.database import get_database
from app.core.redis_client import get_redis_client
from app.core.kafka_producer import get_kafka_producer
from app.services.opa_service import OPAService
from app.services.rules_engine import RulesEngine
from app.services.decision_engine import DecisionEngine
from app.services.model_service import LightweightModelService
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
        resource = Resource.create({"service.name": "finrisk-rules-service"})
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
    logger.info("Starting FinRisk Rules Service", version="1.0.0")
    
    # Setup tracing
    setup_tracing()
    
    # Initialize database
    database = get_database()
    await database.connect()
    logger.info("Database connected")
    
    # Initialize Redis
    redis_client = get_redis_client()
    await redis_client.ping()
    logger.info("Redis connected")
    
    # Initialize Kafka producer
    kafka_producer = get_kafka_producer()
    await kafka_producer.start()
    logger.info("Kafka producer started")
    
    # Initialize OPA service
    opa_service = OPAService()
    await opa_service.initialize()
    logger.info("OPA service initialized")
    
    # Initialize rules engine
    rules_engine = RulesEngine()
    await rules_engine.initialize()
    logger.info("Rules engine initialized")
    
    # Initialize decision engine
    decision_engine = DecisionEngine()
    await decision_engine.initialize()
    logger.info("Decision engine initialized")
    
    # Initialize lightweight model service
    model_service = LightweightModelService()
    await model_service.initialize()
    logger.info("Lightweight model service initialized")
    
    yield
    
    # Cleanup
    await kafka_producer.stop()
    await redis_client.close()
    await database.disconnect()
    logger.info("FinRisk Rules Service stopped")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="FinRisk Rules Service",
        description="Advanced rules engine with OPA integration for policy-based decisions",
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
    app.include_router(rules.router, prefix="/api/v1/rules", tags=["rules"])
    app.include_router(policies.router, prefix="/api/v1/policies", tags=["policies"])
    app.include_router(decisions.router, prefix="/api/v1/decisions", tags=["decisions"])
    app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["evaluation"])
    
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
        port=8085,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False,
    )
