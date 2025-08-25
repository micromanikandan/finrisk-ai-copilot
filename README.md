<div align="center">

<img src="assets/logo.png" alt="FinRisk AI Labs" width="140" url="https://www.linkedin.com/in/manikandanbala/"/>

# **FinRisk Investigation Copilot**

**Open‑source AI for Fraud, Risk & Compliance Investigations**
*Production‑grade reference architecture — designed to scale to millions in enterprise fintech.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## ✨ Overview

**FinRisk Investigation Copilot** is a reference implementation of a **microservices + streaming + GenAI** system for banks/fintechs.

* **Event‑driven**: Kafka → Flink/Streams → materialized views (Search/OLAP/Vector/Graph)
* **Microservices**: Case, Ingestion, Rules/Decisions, Search, ML Scoring, Copilot
* **AI Copilot**: LangGraph + MCP tools, hybrid RAG (BM25 + Vector), guardrails
* **Explainability‑first**: SHAP/Captum artifacts persisted for audits
* **Security & Residency**: OIDC/OAuth2, field‑level encryption, audit ledger

> ⚠️ This repo is **portfolio‑grade** and **production‑minded**: it demonstrates patterns **designed** to scale to millions of users in real deployments. It does **not** claim current production traffic.

---

## 🗺️ Architecture (High‑Level)

* **Cell‑based** (per region/tenant) with independent data planes
* **Hot path**: Edge → BFF → Services → OLTP/Search; heavy ops async via Kafka
* **Polyglot storage**: Postgres (OLTP), OpenSearch (search), ClickHouse (OLAP), pgvector/Weaviate (vector), Neo4j (graph)

> See the **Architecture canvas** in this repo: `/docs/architecture/high-level-architecture.png` (or open the code/canvas in ChatGPT if you’re viewing there).

---

## 📦 Repo Structure (proposed)

```
finrisk/
├─ apps/
│  ├─ gateway-bff/               # Next.js/Node BFF or GraphQL (optional)
│  ├─ case-service/              # Java 21 / Spring Boot WebFlux (R2DBC)
│  ├─ ingestion-service/         # FastAPI or Java for intake + outbox → Kafka
│  ├─ rules-decisions/           # OPA + lightweight model scoring (Triton/ONNX)
│  ├─ search-service/            # OpenSearch + hybrid vector endpoints
│  ├─ ml-scoring/                # FastAPI + SHAP; talks to Feast/Redis
│  ├─ copilot-orchestrator/      # Python: LangGraph + MCP tool servers
│  └─ entity-service/            # (P1) Neo4j entity resolution & links
│
├─ infra/
│  ├─ docker-compose/            # Local dev stack (Kafka, Postgres, Redis, etc.)
│  ├─ k8s/                        # Helm charts/manifests
│  └─ terraform/                 # IaC (EKS, MSK, RDS/Aurora, etc.)
│
├─ docs/
│  ├─ architecture/              # PNG/PDF diagrams, ADRs
│  └─ api/                       # OpenAPI/GraphQL schemas
│
├─ .github/                      # Actions, issue templates
└─ README.md
```

---

## 🚀 Quickstart (Local Dev)

### 1) Prereqs

* macOS with **Docker Desktop** (or Colima), **Git**, **Homebrew**
* **Java 21**, **Python 3.11+**, **Node 20+** (if using BFF)

### 2) Spin up core infra

Create `.env` from sample, then:

```bash
cd infra/docker-compose
cp .env.example .env
# Bring up Kafka + Postgres + Redis + Kafdrop + OpenSearch (optional) + ClickHouse (optional)
docker compose up -d
```

Services exposed (defaults):

* Postgres → `localhost:5432` (`finrisk/finrisk`)
* Redis → `localhost:6379`
* Kafka → `localhost:9092` (KRaft) + Kafdrop UI → `localhost:19000`
* OpenSearch → `localhost:9200`
* ClickHouse → `localhost:8123`

### 3) Run services (dev mode)

**Case Service (WebFlux)**

```bash
cd apps/case-service
./mvnw spring-boot:run
```

**ML Scoring (FastAPI)**

```bash
cd apps/ml-scoring
poetry install
poetry run uvicorn app.main:app --reload --port 8081
```

**Copilot Orchestrator (LangGraph)**

```bash
cd apps/copilot-orchestrator
poetry install
poetry run python -m app.main
```

> Tip: Use **Cursor AI IDE** repo prompt (in `.cursor/rules`) to auto‑scaffold modules following the structure above.

---

## 🔧 Configuration

* **Environment**: `.env` files per service + `infra/docker-compose/.env`
* **Secrets**: Development secrets only; production should use **AWS SSM/Vault**
* **Auth**: OIDC provider (Keycloak/Auth0/Cognito) — dev profile uses mock/JWT

---

## 🧠 AI & RAG Layer

* **LangGraph** for deterministic agent graphs
* **MCP Tools**: CaseStore, Search, PolicyStore, GraphQuery, AuditLogger
* **Retrieval**: Hybrid (BM25 + Vector) with rerankers; citations enforced
* **Guardrails**: JSON‑schema tool calls, PII redaction, cost budgets per tenant

---

## 🧪 Testing

* Java: JUnit 5, Testcontainers (Postgres/Kafka)
* Python: pytest, httpx, pydantic v2
* Contract tests: Pact (BFF ↔ services)
* Load: k6/Locust profiles in `/tests/load/`

---

## 🛡️ Security & Compliance (starter checklist)

* [ ] OIDC login + RBAC/ABAC (OPA policies)
* [ ] Field‑level encryption + tokenization (AES‑GCM, KMS in prod)
* [ ] Immutable audit log (append‑only + S3 object lock)
* [ ] Data residency per region/cell

---

## 🤝 Contributing

PRs welcome! Please open an issue with context (service, topic, tenant/cell). See `/docs/adr/` for decisions.

---

## 📣 Credits & Contact

Built by **Manikandan (“Mani”) — Founder & AI Architect, FinRisk AI Labs**.

* LinkedIn: \<your‑profile‑url>
* Company Page: FinRisk AI Labs
* GitHub: \<repo‑url>

---

## 📜 License

MIT — see [LICENSE](LICENSE).
