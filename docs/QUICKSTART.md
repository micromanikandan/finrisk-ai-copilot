# FinRisk AI Copilot - Quick Start Guide

Get up and running with the FinRisk AI Copilot in under 10 minutes!

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required
- **Docker Desktop** (or Colima) with at least 8GB RAM allocated
- **Git** for version control
- **Make** for running development commands

### For Development
- **Java 21** (for Case Service development)
- **Python 3.11+** (for Python services)
- **Node.js 20+** (for frontend development)
- **Poetry** (Python dependency management)

### Quick Installation (macOS)
```bash
# Install prerequisites with Homebrew
brew install git make docker colima
brew install openjdk@21 python@3.11 node@20
brew install poetry

# Start Docker alternative (if not using Docker Desktop)
colima start --cpu 4 --memory 8
```

## 🚀 Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/micromanikandan/finrisk-ai-copilot.git
cd finrisk-ai-copilot
```

### 2. One-Command Setup
```bash
make setup
```

This command will:
- Create environment configuration
- Install all service dependencies
- Initialize databases
- Set up the development environment

### 3. Start Infrastructure Services
```bash
make start
```

This starts all the backend infrastructure:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Kafka with KRaft (port 9092)
- OpenSearch (port 9200)
- ClickHouse (port 8123)
- Neo4j (port 7474)
- Weaviate (port 8080)

### 4. Start Application Services

Open three separate terminal windows and run:

**Terminal 1 - Case Service:**
```bash
make dev-case
# or manually:
cd apps/case-service
./mvnw spring-boot:run
```

**Terminal 2 - Ingestion Service:**
```bash
make dev-ingestion
# or manually:
cd apps/ingestion-service
poetry run uvicorn app.main:app --reload --port 8081
```

**Terminal 3 - ML Scoring Service:**
```bash
make dev-ml
# or manually:
cd apps/ml-scoring
poetry run uvicorn app.main:app --reload --port 8082
```

## 🌐 Access the Services

Once everything is running, you can access:

### Application APIs
- **Case Service API**: http://localhost:8080/swagger-ui.html
- **Ingestion Service API**: http://localhost:8081/docs
- **ML Scoring Service API**: http://localhost:8082/docs

### Infrastructure UIs
- **Kafdrop (Kafka UI)**: http://localhost:19000
- **OpenSearch Dashboards**: http://localhost:5601
- **Neo4j Browser**: http://localhost:7474 (neo4j/finrisk123)
- **ClickHouse**: http://localhost:8123/play

### Health Checks
- Case Service: http://localhost:8080/actuator/health
- Ingestion Service: http://localhost:8081/health
- ML Scoring Service: http://localhost:8082/health

## 🧪 Test the System

### 1. Create a Fraud Investigation Case

```bash
curl -X POST "http://localhost:8080/api/v1/cases" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Suspicious Transaction Pattern",
    "description": "Multiple small transactions just below reporting threshold",
    "caseType": "FRAUD",
    "priority": "HIGH",
    "metadata": {
      "customer_id": "CUST-12345",
      "transaction_count": 15,
      "total_amount": 49500.00
    },
    "tags": ["structuring", "money-laundering", "high-risk"]
  }'
```

### 2. Ingest Transaction Data

```bash
curl -X POST "http://localhost:8081/api/v1/ingestion/jobs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "job_name": "Daily Transaction Ingestion",
    "description": "Import daily transaction data for fraud monitoring",
    "source_type": "FILE",
    "data_format": "CSV",
    "config": {
      "delimiter": ",",
      "header_row": true,
      "chunk_size": 1000
    }
  }'
```

### 3. Score a Transaction for Fraud Risk

```bash
curl -X POST "http://localhost:8082/api/v1/scoring/predict" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "model_name": "fraud_detection_v1",
    "features": {
      "transaction_amount": 9500.00,
      "account_age_days": 45,
      "daily_transaction_count": 12,
      "avg_transaction_amount": 1200.00,
      "merchant_category": "cash_advance",
      "time_of_day": 23,
      "is_weekend": true
    },
    "explain": true
  }'
```

## 📊 Monitoring and Observability

### View Metrics
- **Prometheus Metrics**: 
  - Case Service: http://localhost:8080/actuator/prometheus
  - Ingestion Service: http://localhost:8081/prometheus
  - ML Scoring Service: http://localhost:8082/prometheus

### View Logs
```bash
# All services
make logs

# Specific service
docker logs finrisk-postgres
docker logs finrisk-kafka
```

### Database Access
```bash
# PostgreSQL
docker exec -it finrisk-postgres psql -U finrisk -d finrisk

# Redis
docker exec -it finrisk-redis redis-cli

# ClickHouse
docker exec -it finrisk-clickhouse clickhouse-client
```

## 🛠 Development Commands

```bash
# Setup and start
make setup          # One-time setup
make start          # Start infrastructure
make status         # Check service status

# Development
make dev-case       # Start Case Service in dev mode
make dev-ingestion  # Start Ingestion Service in dev mode
make dev-ml         # Start ML Scoring Service in dev mode

# Testing
make test           # Run all tests
make test-unit      # Unit tests only
make test-coverage  # Tests with coverage

# Database
make db-migrate     # Run migrations
make db-reset       # Reset databases

# Cleanup
make stop           # Stop all services
make clean          # Clean up containers and volumes
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `infra/docker-compose/env.example`):

```bash
# Database
POSTGRES_PASSWORD=your_secure_password

# AI APIs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Security
JWT_SECRET=your_jwt_secret_32_chars_minimum
ENCRYPTION_KEY=your_encryption_key_32_chars

# Feature Flags
ENABLE_AUDIT_LOGGING=true
ENABLE_PII_REDACTION=true
ENABLE_FIELD_ENCRYPTION=true
```

### Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Case Service | 8080 | REST API |
| Ingestion Service | 8081 | REST API |
| ML Scoring Service | 8082 | REST API |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
| Kafka | 9092 | Message Broker |
| Kafdrop | 19000 | Kafka UI |
| OpenSearch | 9200 | Search Engine |
| OpenSearch Dashboards | 5601 | Search UI |
| ClickHouse | 8123 | Analytics DB |
| Neo4j | 7474 | Graph DB |
| Weaviate | 8080 | Vector DB |

## 🚨 Troubleshooting

### Common Issues

**1. Port Conflicts**
```bash
# Check what's using a port
lsof -i :8080

# Kill process using port
kill -9 $(lsof -t -i:8080)
```

**2. Docker Issues**
```bash
# Restart Docker
docker restart

# Clean up everything
make clean
docker system prune -a
```

**3. Database Connection Issues**
```bash
# Reset databases
make db-reset

# Check database logs
docker logs finrisk-postgres
```

**4. Memory Issues**
```bash
# Increase Docker memory to 8GB+ in Docker Desktop settings
# Or for Colima:
colima stop
colima start --cpu 4 --memory 8
```

### Getting Help

- **Documentation**: Check `/docs` folder for detailed guides
- **Issues**: Create an issue on GitHub
- **Logs**: Always check service logs first: `make logs`

## 🎯 Next Steps

1. **Explore the APIs**: Use the Swagger/OpenAPI documentation
2. **Run the Test Suite**: `make test` to verify everything works
3. **Load Sample Data**: Use the ingestion service to load test datasets
4. **Configure Authentication**: Set up OIDC/OAuth2 for production use
5. **Deploy to Cloud**: Use the Kubernetes manifests in `/infra/k8s`

## 📚 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Case Service  │    │ Ingestion Svc   │    │ ML Scoring Svc  │
│   (Java/Spring) │    │   (FastAPI)     │    │   (FastAPI)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │         Kafka               │
                    │    (Event Streaming)        │
                    └─────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                       │                        │
   ┌─────▼─────┐      ┌─────────▼──────────┐    ┌─────────▼─────────┐
   │PostgreSQL │      │    OpenSearch      │    │   ClickHouse      │
   │  (OLTP)   │      │   (Search/Logs)    │    │   (Analytics)     │
   └───────────┘      └────────────────────┘    └───────────────────┘
```

**Core Features:**
- 🔍 **Real-time Fraud Detection** with ML scoring
- 📊 **Case Management** for investigations
- 🚰 **Data Ingestion** with validation and enrichment
- 🤖 **AI Copilot** with LangGraph and MCP tools
- 🔐 **Multi-tenant Security** with field-level encryption
- 📈 **Explainable AI** with SHAP and audit trails

---

**Happy investigating! 🕵️‍♂️💰**
