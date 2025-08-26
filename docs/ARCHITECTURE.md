# FinRisk AI Copilot - Architecture Documentation

## 🏗️ System Architecture Overview

FinRisk AI Copilot is a production-grade, enterprise-ready financial crime investigation platform built with modern microservices architecture, event-driven design, and AI-first principles.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FinRisk AI Copilot                                   │
│                    Financial Crime Investigation Platform                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gateway BFF   │    │  Case Service   │    │ Ingestion Svc   │    │ ML Scoring Svc  │
│  (Next.js/GQL)  │    │ (Java/Spring)   │    │   (FastAPI)     │    │   (FastAPI)     │
│     :3000       │    │     :8080       │    │     :8081       │    │     :8082       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │                      │
          └──────────────────────┼──────────────────────┼──────────────────────┘
                                 │                      │
                    ┌─────────────▼──────────────────────▼─────────────┐
                    │                 Kafka                            │
                    │           (Event Streaming)                      │
                    └─────────────┬──────────────────────┬─────────────┘
                                  │                      │
         ┌────────────────────────┼──────────────────────┼────────────────────────┐
         │                       │                      │                        │
┌────────▼────────┐    ┌─────────▼─────────┐    ┌──────▼──────┐    ┌─────────▼─────────┐
│   Search Svc    │    │   Copilot Orch    │    │ Rules Svc   │    │   Entity Svc      │
│   (FastAPI)     │    │   (LangGraph)     │    │ (OPA/FastAPI│    │ (Neo4j/FastAPI)   │
│     :8083       │    │     :8084         │    │     :8085   │    │     :8086         │
└─────────────────┘    └───────────────────┘    └─────────────┘    └───────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Data Layer                                        │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   PostgreSQL    │      Redis      │   OpenSearch    │       ClickHouse        │
│     (OLTP)      │   (Cache/Sess)  │  (Search/Logs)  │     (Analytics)         │
│     :5432       │     :6379       │     :9200       │       :8123             │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│     Neo4j       │    Weaviate     │     Kafka       │                         │
│    (Graph)      │   (Vectors)     │  (Streaming)    │                         │
│     :7474       │     :8080       │     :9092       │                         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## 🎯 Core Principles

### 1. **Event-Driven Architecture**
- **Kafka** as the central nervous system for event streaming
- **Transactional Outbox Pattern** for reliable event publishing
- **Event Sourcing** for complete audit trails
- **CQRS** separation for read/write optimization

### 2. **Microservices Design**
- **Domain-Driven Design** with bounded contexts
- **API-First** development with OpenAPI specifications
- **Polyglot Persistence** - right database for each use case
- **Independent Deployability** with Docker/Kubernetes

### 3. **AI-First Approach**
- **LangGraph** for deterministic AI agent workflows
- **MCP (Model Context Protocol)** for structured AI tool interactions
- **Hybrid Search** combining BM25 and vector similarity
- **Explainable AI** with SHAP for model transparency

### 4. **Production-Grade Quality**
- **Multi-Tenant** architecture with cell-based isolation
- **Security-First** with OAuth2, field-level encryption
- **Observability** with OpenTelemetry, Prometheus, Grafana
- **High Availability** with auto-scaling and health checks

## 🏛️ Service Architecture

### Core Services

#### 1. **Gateway BFF** (Port 3000)
- **Technology**: Next.js 14, React 18, GraphQL, Apollo
- **Purpose**: Frontend aggregation and user interface
- **Features**:
  - Unified GraphQL API for all backend services
  - Server-side rendering for performance
  - Real-time updates with WebSockets
  - Modern UI with Tailwind CSS and Radix UI

#### 2. **Case Service** (Port 8080)
- **Technology**: Java 21, Spring Boot 3, WebFlux, R2DBC
- **Purpose**: Core case management for investigations
- **Features**:
  - Reactive, non-blocking I/O
  - Complete case lifecycle management
  - Event-driven updates via Kafka
  - Comprehensive audit trails

#### 3. **Ingestion Service** (Port 8081)
- **Technology**: Python 3.11, FastAPI, AsyncIO
- **Purpose**: High-performance data ingestion and validation
- **Features**:
  - Multi-format support (CSV, JSON, XML, Parquet)
  - Real-time validation and enrichment
  - Transactional outbox for reliability
  - Background processing with Celery

#### 4. **ML Scoring Service** (Port 8082)
- **Technology**: Python 3.11, FastAPI, scikit-learn, SHAP
- **Purpose**: ML model serving with explainability
- **Features**:
  - Real-time and batch scoring
  - ONNX runtime for performance
  - SHAP-based explainability
  - Model versioning and A/B testing

#### 5. **Search Service** (Port 8083)
- **Technology**: Python 3.11, FastAPI, OpenSearch
- **Purpose**: Advanced search with hybrid vector capabilities
- **Features**:
  - Hybrid search (BM25 + vector similarity)
  - Real-time indexing via Kafka
  - Multi-modal search capabilities
  - Search analytics and optimization

#### 6. **Copilot Orchestrator** (Port 8084)
- **Technology**: Python 3.11, LangGraph, LangChain
- **Purpose**: AI agent orchestration and conversation management
- **Features**:
  - LangGraph state machines for complex workflows
  - MCP tool integration
  - Multi-modal AI interactions
  - Conversation memory and context

#### 7. **Rules Service** (Port 8085)
- **Technology**: Python 3.11, FastAPI, OPA (Open Policy Agent)
- **Purpose**: Policy engine for compliance and decision making
- **Features**:
  - OPA integration for complex policies
  - Real-time rule evaluation
  - Lightweight ML model scoring
  - Rule versioning and testing

#### 8. **Entity Service** (Port 8086)
- **Technology**: Python 3.11, FastAPI, Neo4j
- **Purpose**: Entity resolution and relationship mapping
- **Features**:
  - Advanced entity resolution algorithms
  - Graph-based relationship discovery
  - Network analysis and pattern detection
  - Real-time entity updates

## 🗄️ Data Architecture

### Polyglot Persistence Strategy

#### **PostgreSQL** - OLTP (Transactional Data)
- **Use Cases**: Core business data, user management, configurations
- **Services**: Case Service, Ingestion Service metadata
- **Features**: ACID compliance, complex queries, referential integrity
- **Scaling**: Read replicas, connection pooling

#### **Redis** - Caching & Session Store
- **Use Cases**: Session management, caching, rate limiting
- **Services**: All services for caching
- **Features**: Sub-millisecond latency, pub/sub, persistence
- **Scaling**: Redis Cluster, multiple read replicas

#### **OpenSearch** - Search & Analytics
- **Use Cases**: Full-text search, log analysis, real-time analytics
- **Services**: Search Service, logging aggregation
- **Features**: Near real-time indexing, complex queries, aggregations
- **Scaling**: Multi-node cluster, index lifecycle management

#### **ClickHouse** - OLAP Analytics
- **Use Cases**: Time-series analytics, reporting, data warehousing
- **Services**: Analytics queries, historical data analysis
- **Features**: Columnar storage, real-time analytics, compression
- **Scaling**: Distributed tables, sharding

#### **Neo4j** - Graph Database
- **Use Cases**: Entity relationships, network analysis, fraud detection
- **Services**: Entity Service, relationship mapping
- **Features**: Graph algorithms, pattern matching, traversals
- **Scaling**: Cluster mode, read replicas

#### **Weaviate** - Vector Database
- **Use Cases**: Semantic search, recommendation engines, similarity
- **Services**: Search Service, ML Scoring Service
- **Features**: Vector similarity, hybrid search, ML integration
- **Scaling**: Horizontal scaling, vector indexing

### Event Streaming (Kafka)

#### **Topics Architecture**
```
case-events          # Case lifecycle events
data-events          # Data ingestion events  
search-events        # Search and indexing events
ml-events           # ML scoring and model events
audit-events        # Security and compliance events
user-events         # User activity events
system-events       # System health and metrics
```

#### **Event Schema Registry**
- **Avro Schemas** for event serialization
- **Schema Evolution** with backward compatibility
- **Dead Letter Queues** for error handling
- **Event Replay** capabilities for recovery

## 🔒 Security Architecture

### Multi-Layered Security

#### **Authentication & Authorization**
- **OAuth2/OIDC** with Auth0 or AWS Cognito
- **JWT Tokens** with RS256 signing
- **Role-Based Access Control (RBAC)**
- **Attribute-Based Access Control (ABAC)**

#### **Data Protection**
- **Field-Level Encryption** for sensitive data
- **Encryption at Rest** (AES-256)
- **Encryption in Transit** (TLS 1.3)
- **Key Management** with AWS KMS/Azure Key Vault

#### **Network Security**
- **VPC** with private subnets
- **Security Groups** and NACLs
- **WAF** for web application protection
- **DDoS Protection** with CloudFlare/AWS Shield

#### **Compliance & Auditing**
- **Immutable Audit Logs** with blockchain-style verification
- **GDPR/CCPA** compliance features
- **SOC 2 Type II** readiness
- **Real-time Security Monitoring**

## 🎛️ Operational Architecture

### Monitoring & Observability

#### **Metrics (Prometheus + Grafana)**
```
Application Metrics:
- Request rate, latency, error rate
- Business KPIs (cases processed, alerts generated)
- Custom domain metrics

Infrastructure Metrics:
- CPU, memory, disk, network utilization
- Database performance metrics
- Kafka lag and throughput

Service Mesh Metrics:
- Inter-service communication
- Circuit breaker status
- Load balancing metrics
```

#### **Logging (Structured Logging)**
```
Log Levels:
- ERROR: System errors and exceptions
- WARN: Performance degradation, retries
- INFO: Business events, key operations
- DEBUG: Detailed troubleshooting info

Log Structure (JSON):
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "case-service",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": "user_789",
  "tenant_id": "tenant_1",
  "event": "case_created",
  "case_id": "case_12345",
  "message": "Case created successfully"
}
```

#### **Tracing (OpenTelemetry + Jaeger)**
- **Distributed Tracing** across all services
- **Request Flow Visualization**
- **Performance Bottleneck Identification**
- **Error Root Cause Analysis**

### Deployment Architecture

#### **Kubernetes (Production)**
```
Namespace: finrisk-prod
├── Services (8 microservices)
├── Ingress Controllers (NGINX)
├── Service Mesh (Istio - optional)
├── Databases (Operators for PostgreSQL, Redis, etc.)
├── Monitoring Stack (Prometheus, Grafana, Jaeger)
└── Security (RBAC, Network Policies, Pod Security)
```

#### **Auto-Scaling Configuration**
```yaml
HPA (Horizontal Pod Autoscaler):
- CPU: 70% utilization
- Memory: 80% utilization
- Custom: Queue depth, request rate

VPA (Vertical Pod Autoscaler):
- Automatic resource recommendations
- Resource limit adjustments

Cluster Autoscaler:
- Node scaling based on pod requirements
- Cost optimization with spot instances
```

## 🌐 Cloud Architecture

### AWS Deployment

#### **Compute Layer**
- **EKS** (Elastic Kubernetes Service) for container orchestration
- **EC2** instances with mixed instance types (on-demand + spot)
- **Lambda** functions for serverless processing
- **Fargate** for serverless containers

#### **Data Layer**
- **RDS Aurora PostgreSQL** (Multi-AZ, read replicas)
- **ElastiCache Redis** (Cluster mode, automatic failover)
- **OpenSearch Service** (Multi-AZ deployment)
- **MSK** (Managed Streaming for Apache Kafka)
- **S3** for object storage and data lake

#### **Network Layer**
- **VPC** with public/private subnets
- **Application Load Balancer** (ALB)
- **CloudFront** CDN for global distribution
- **Route 53** for DNS management

#### **Security Layer**
- **IAM** roles and policies
- **KMS** for encryption key management
- **Secrets Manager** for secret storage
- **GuardDuty** for threat detection
- **Config** for compliance monitoring

## 📊 Performance Characteristics

### Scalability Targets

| Metric | Target | Current |
|--------|---------|---------|
| Concurrent Users | 10,000+ | 1,000 |
| API Requests/sec | 50,000+ | 5,000 |
| Data Ingestion | 1M records/min | 100K/min |
| Search Latency | <100ms p95 | <50ms p95 |
| ML Scoring Latency | <200ms p95 | <100ms p95 |
| Case Processing | 100K cases/day | 10K/day |

### Resource Requirements

#### **Development Environment**
- **CPU**: 8 cores minimum
- **Memory**: 16GB minimum
- **Storage**: 100GB SSD
- **Network**: 1Gbps

#### **Production Environment (Per Service)**
- **Small**: 2 vCPU, 4GB RAM
- **Medium**: 4 vCPU, 8GB RAM  
- **Large**: 8 vCPU, 16GB RAM
- **XLarge**: 16 vCPU, 32GB RAM (ML workloads)

## 🔄 Data Flow Architecture

### Investigation Workflow
```
1. Data Ingestion → Validation → Enrichment → Storage
2. Real-time ML Scoring → Risk Assessment → Alert Generation
3. Case Creation → Investigation → Evidence Collection
4. AI Copilot Assistance → Pattern Analysis → Recommendations
5. Decision Making → Reporting → Audit Trail
```

### Event Flow
```
Service A → Outbox Table → Kafka Producer → Kafka Topic
   ↓                                           ↓
Database Transaction                   Service B Consumer
   ↓                                           ↓
Business Logic                         Event Processing
   ↓                                           ↓
Response to Client                     State Update
```

This architecture ensures **high availability**, **scalability**, **security**, and **maintainability** while providing a seamless experience for financial crime investigators and compliance teams.

---

**Next**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.
