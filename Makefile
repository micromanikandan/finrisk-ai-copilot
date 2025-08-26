# FinRisk AI Copilot - Development Makefile
# Simplifies common development tasks

.PHONY: help setup start stop clean test build deploy docs

# Default target
help:
	@echo "FinRisk AI Copilot - Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup          Set up development environment"
	@echo "  validate       Validate system prerequisites"
	@echo "  install-deps   Install all service dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  start          Start all services in development mode"
	@echo "  stop           Stop all services"
	@echo "  restart        Restart all services"
	@echo "  logs           Show logs from all services"
	@echo ""
	@echo "Database Commands:"
	@echo "  db-setup       Initialize databases and run migrations"
	@echo "  db-migrate     Run database migrations"
	@echo "  db-reset       Reset all databases"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo ""
	@echo "Build Commands:"
	@echo "  build          Build all Docker images"
	@echo "  build-case     Build Case Service image"
	@echo "  build-ingestion Build Ingestion Service image"
	@echo "  build-ml       Build ML Scoring Service image"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean          Clean up containers and volumes"
	@echo "  format         Format code with linters"
	@echo "  lint           Run code linters"
	@echo "  docs           Generate API documentation"

# Validate system prerequisites
validate:
	@echo "Validating system prerequisites..."
	@./scripts/validate-setup.sh

# Setup development environment
setup:
	@echo "Setting up FinRisk AI Copilot development environment..."
	@./scripts/validate-setup.sh
	@cp infra/docker-compose/env.example infra/docker-compose/.env
	@echo "✅ Environment file created"
	@make install-deps
	@make db-setup
	@echo "🎉 Setup complete! Run 'make start' to begin."

# Install dependencies for all services
install-deps:
	@echo "Installing dependencies..."
	
	# Check prerequisites
	@command -v java >/dev/null 2>&1 || { echo "❌ Java is required but not installed. Please install Java 21."; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python is required but not installed. Please install Python 3.11+."; exit 1; }
	@command -v poetry >/dev/null 2>&1 || { echo "❌ Poetry is required but not installed. Installing Poetry..."; curl -sSL https://install.python-poetry.org | python3 -; }
	
	# Java dependencies (Case Service)
	@echo "Installing Java dependencies..."
	@cd apps/case-service && ./mvnw dependency:resolve
	@echo "✅ Java dependencies installed"
	
	# Python dependencies (Ingestion Service)
	@echo "Installing Python dependencies for Ingestion Service..."
	@cd apps/ingestion-service && poetry env use python3.12 && poetry install --only=main --no-root
	@echo "✅ Ingestion service dependencies installed"
	
	# Python dependencies (ML Scoring Service)
	@echo "Installing Python dependencies for ML Scoring Service..."
	@cd apps/ml-scoring && poetry env use python3.12 && poetry install --only=main --no-root
	@echo "✅ ML scoring service dependencies installed"
	
	# Python dependencies (Search Service)
	@echo "Installing Python dependencies for Search Service..."
	@cd apps/search-service && poetry env use python3.12 && poetry install --only=main --no-root
	@echo "✅ Search service dependencies installed"
	
	# Python dependencies (Copilot Orchestrator)
	@echo "Installing Python dependencies for Copilot Orchestrator..."
	@cd apps/copilot-orchestrator && poetry env use python3.12 && poetry install --only=main --no-root
	@echo "✅ Copilot orchestrator dependencies installed"
	
	# Python dependencies (Rules Service)
	@echo "Installing Python dependencies for Rules Service..."
	@cd apps/rules-service && poetry env use python3.12 && poetry install --only=main --no-root
	@echo "✅ Rules service dependencies installed"
	
	# Python dependencies (Entity Service)
	@echo "Installing Python dependencies for Entity Service..."
	@cd apps/entity-service && poetry env use python3.12 && poetry install --only=main --no-root
	@echo "✅ Entity service dependencies installed"
	
	# Node.js dependencies (Gateway BFF)
	@echo "Installing Node.js dependencies for Gateway BFF..."
	@command -v node >/dev/null 2>&1 || { echo "⚠️  Node.js not found. Skipping frontend dependencies. Install Node.js 20+ to build the frontend."; }
	@command -v node >/dev/null 2>&1 && cd apps/gateway-bff && npm install || true
	@echo "✅ All dependencies installed successfully!"

# Start all services
start:
	@echo "Starting FinRisk AI Copilot services..."
	@cd infra/docker-compose && docker compose up -d
	@echo "🚀 Infrastructure started"
	@echo ""
	@echo "Services will be available at:"
	@echo "  - Postgres: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - Kafka: localhost:9092"
	@echo "  - Kafdrop (Kafka UI): http://localhost:19000"
	@echo "  - OpenSearch: localhost:9200"
	@echo "  - OpenSearch Dashboards: http://localhost:5601"
	@echo "  - ClickHouse: localhost:8123"
	@echo "  - Neo4j: http://localhost:7474"
	@echo "  - Weaviate: localhost:8080"
	@echo ""
	@echo "To start application services:"
	@echo "  - Case Service: cd apps/case-service && ./mvnw spring-boot:run"
	@echo "  - Ingestion Service: cd apps/ingestion-service && poetry run uvicorn app.main:app --reload --port 8081"
	@echo "  - ML Scoring Service: cd apps/ml-scoring && poetry run uvicorn app.main:app --reload --port 8082"

# Stop all services
stop:
	@echo "Stopping FinRisk AI Copilot services..."
	@cd infra/docker-compose && docker compose down
	@echo "🛑 All services stopped"

# Restart all services
restart: stop start

# Show logs
logs:
	@cd infra/docker-compose && docker compose logs -f

# Database setup
db-setup:
	@echo "Setting up databases..."
	@cd infra/docker-compose && docker compose up -d postgres redis
	@sleep 10
	@echo "✅ Databases initialized"

# Run database migrations
db-migrate:
	@echo "Running database migrations..."
	@cd apps/case-service && ./mvnw flyway:migrate
	@cd apps/ingestion-service && poetry run alembic upgrade head
	@cd apps/ml-scoring && poetry run alembic upgrade head
	@echo "✅ Migrations completed"

# Reset databases
db-reset:
	@echo "Resetting databases..."
	@cd infra/docker-compose && docker compose down -v postgres redis
	@cd infra/docker-compose && docker compose up -d postgres redis
	@sleep 10
	@make db-migrate
	@echo "✅ Databases reset"

# Run all tests
test:
	@echo "Running all tests..."
	@cd apps/case-service && ./mvnw test
	@cd apps/ingestion-service && poetry run pytest
	@cd apps/ml-scoring && poetry run pytest
	@echo "✅ All tests completed"

# Run unit tests only
test-unit:
	@echo "Running unit tests..."
	@cd apps/case-service && ./mvnw test -Dtest="**/*UnitTest"
	@cd apps/ingestion-service && poetry run pytest -m "unit"
	@cd apps/ml-scoring && poetry run pytest -m "unit"

# Run integration tests only
test-integration:
	@echo "Running integration tests..."
	@cd apps/case-service && ./mvnw test -Dtest="**/*IntegrationTest"
	@cd apps/ingestion-service && poetry run pytest -m "integration"
	@cd apps/ml-scoring && poetry run pytest -m "integration"

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	@cd apps/ingestion-service && poetry run pytest --cov=app --cov-report=html
	@cd apps/ml-scoring && poetry run pytest --cov=app --cov-report=html
	@echo "✅ Coverage reports generated"

# Build all Docker images
build:
	@echo "Building all Docker images..."
	@make build-case
	@make build-ingestion
	@make build-ml
	@echo "✅ All images built"

# Build Case Service image
build-case:
	@echo "Building Case Service image..."
	@cd apps/case-service && docker build -t finrisk/case-service:latest .

# Build Ingestion Service image
build-ingestion:
	@echo "Building Ingestion Service image..."
	@cd apps/ingestion-service && docker build -t finrisk/ingestion-service:latest .

# Build ML Scoring Service image
build-ml:
	@echo "Building ML Scoring Service image..."
	@cd apps/ml-scoring && docker build -t finrisk/ml-scoring:latest .

# Clean up
clean:
	@echo "Cleaning up..."
	@cd infra/docker-compose && docker compose down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Cleanup completed"

# Format code
format:
	@echo "Formatting code..."
	@cd apps/ingestion-service && poetry run black . && poetry run isort .
	@cd apps/ml-scoring && poetry run black . && poetry run isort .
	@echo "✅ Code formatted"

# Run linters
lint:
	@echo "Running linters..."
	@cd apps/ingestion-service && poetry run flake8 . && poetry run mypy .
	@cd apps/ml-scoring && poetry run flake8 . && poetry run mypy .
	@echo "✅ Linting completed"

# Generate documentation
docs:
	@echo "Generating API documentation..."
	@echo "Documentation will be available at:"
	@echo "  - Case Service: http://localhost:8080/swagger-ui.html"
	@echo "  - Ingestion Service: http://localhost:8081/docs"
	@echo "  - ML Scoring Service: http://localhost:8082/docs"

# Development helpers
dev-case:
	@echo "Starting Case Service in development mode..."
	@cd apps/case-service && ./mvnw spring-boot:run -Dspring-boot.run.profiles=dev

dev-ingestion:
	@echo "Starting Ingestion Service in development mode..."
	@cd apps/ingestion-service && poetry run uvicorn app.main:app --reload --port 8081

dev-ml:
	@echo "Starting ML Scoring Service in development mode..."
	@cd apps/ml-scoring && poetry run uvicorn app.main:app --reload --port 8082

dev-search:
	@echo "Starting Search Service in development mode..."
	@cd apps/search-service && poetry run uvicorn app.main:app --reload --port 8083

dev-copilot:
	@echo "Starting Copilot Orchestrator in development mode..."
	@cd apps/copilot-orchestrator && poetry run uvicorn app.main:app --reload --port 8084

dev-rules:
	@echo "Starting Rules Service in development mode..."
	@cd apps/rules-service && poetry run uvicorn app.main:app --reload --port 8085

dev-entity:
	@echo "Starting Entity Service in development mode..."
	@cd apps/entity-service && poetry run uvicorn app.main:app --reload --port 8086

dev-frontend:
	@echo "Starting Frontend Gateway BFF in development mode..."
	@cd apps/gateway-bff && npm run dev

# Show service status
status:
	@echo "Service Status:"
	@echo "==============="
	@cd infra/docker-compose && docker compose ps

# Open services in browser
open-services:
	@echo "Opening services in browser..."
	@open http://localhost:19000  # Kafdrop
	@open http://localhost:5601   # OpenSearch Dashboards
	@open http://localhost:7474   # Neo4j Browser
