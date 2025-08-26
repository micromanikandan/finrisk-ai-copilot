"""
FinRisk AI Copilot - Orchestrator Service

Advanced AI copilot orchestrator using LangGraph for deterministic agent workflows.
Features:
- LangGraph state machines for complex agent flows
- MCP (Model Context Protocol) tool integration
- Multi-modal AI interactions (text, voice, vision)
- Conversation memory and context management
- Guardrails and safety measures
- Real-time streaming responses
- Audit trail for AI interactions
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

from app.api.v1 import chat, agents, tools, conversations, health, metrics
from app.core.config import get_settings
from app.core.database import get_database
from app.core.redis_client import get_redis_client
from app.core.kafka_producer import get_kafka_producer
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.tool_registry import ToolRegistry
from app.services.conversation_manager import ConversationManager
from app.services.guardrails import GuardrailsService
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.tenant import TenantMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware

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
        resource = Resource.create({"service.name": "finrisk-copilot-orchestrator"})
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
    logger.info("Starting FinRisk Copilot Orchestrator", version="1.0.0")
    
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
    
    # Initialize tool registry
    tool_registry = ToolRegistry()
    await tool_registry.initialize()
    logger.info("Tool registry initialized")
    
    # Initialize conversation manager
    conversation_manager = ConversationManager()
    await conversation_manager.initialize()
    logger.info("Conversation manager initialized")
    
    # Initialize guardrails service
    guardrails = GuardrailsService()
    await guardrails.initialize()
    logger.info("Guardrails service initialized")
    
    # Initialize agent orchestrator
    agent_orchestrator = AgentOrchestrator()
    await agent_orchestrator.initialize()
    logger.info("Agent orchestrator initialized")
    
    yield
    
    # Cleanup
    await kafka_producer.stop()
    await redis_client.close()
    await database.disconnect()
    logger.info("FinRisk Copilot Orchestrator stopped")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="FinRisk Copilot Orchestrator",
        description="Advanced AI copilot orchestrator using LangGraph for deterministic agent workflows",
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
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(tools.router, prefix="/api/v1/tools", tags=["tools"])
    app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["conversations"])
    
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
        port=8084,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False,
    )
