-- FinRisk AI Copilot - Database Initialization Script
-- This script sets up the initial database schemas for all services

-- Create databases for different services
CREATE DATABASE IF NOT EXISTS case_service;
CREATE DATABASE IF NOT EXISTS ingestion_service;
CREATE DATABASE IF NOT EXISTS search_service;
CREATE DATABASE IF NOT EXISTS ml_scoring;
CREATE DATABASE IF NOT EXISTS audit_service;

-- Create dedicated users for each service (following least privilege principle)
CREATE USER IF NOT EXISTS case_user WITH PASSWORD 'case_dev_password_2024';
CREATE USER IF NOT EXISTS ingestion_user WITH PASSWORD 'ingestion_dev_password_2024';
CREATE USER IF NOT EXISTS search_user WITH PASSWORD 'search_dev_password_2024';
CREATE USER IF NOT EXISTS ml_user WITH PASSWORD 'ml_dev_password_2024';
CREATE USER IF NOT EXISTS audit_user WITH PASSWORD 'audit_dev_password_2024';

-- Grant appropriate permissions
GRANT ALL PRIVILEGES ON DATABASE case_service TO case_user;
GRANT ALL PRIVILEGES ON DATABASE ingestion_service TO ingestion_user;
GRANT ALL PRIVILEGES ON DATABASE search_service TO search_user;
GRANT ALL PRIVILEGES ON DATABASE ml_scoring TO ml_user;
GRANT ALL PRIVILEGES ON DATABASE audit_service TO audit_user;

-- Connect to case_service database to create initial tables
\c case_service;

-- Cases table - Core investigation cases
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    case_type VARCHAR(50) NOT NULL, -- 'FRAUD', 'AML', 'SANCTIONS', 'KYC'
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN', -- 'OPEN', 'IN_PROGRESS', 'CLOSED', 'ESCALATED'
    assigned_to UUID,
    created_by UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    
    -- Audit fields
    version INTEGER DEFAULT 1,
    tenant_id VARCHAR(50) NOT NULL,
    cell_id VARCHAR(50) NOT NULL
);

-- Case events - Audit trail for case activities
CREATE TABLE IF NOT EXISTS case_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id),
    event_type VARCHAR(50) NOT NULL, -- 'CREATED', 'UPDATED', 'ASSIGNED', 'CLOSED', etc.
    event_data JSONB NOT NULL,
    created_by UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(50) NOT NULL,
    cell_id VARCHAR(50) NOT NULL
);

-- Evidence table - Documents, transactions, communications
CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id),
    evidence_type VARCHAR(50) NOT NULL, -- 'DOCUMENT', 'TRANSACTION', 'COMMUNICATION', 'SCREENSHOT'
    source VARCHAR(100) NOT NULL,
    content_hash VARCHAR(64) NOT NULL, -- SHA-256 hash for integrity
    storage_path VARCHAR(500), -- S3/MinIO path
    metadata JSONB DEFAULT '{}',
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    collected_by UUID NOT NULL,
    
    -- Encryption and security
    encrypted BOOLEAN DEFAULT false,
    classification VARCHAR(20) DEFAULT 'INTERNAL', -- 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'
    
    tenant_id VARCHAR(50) NOT NULL,
    cell_id VARCHAR(50) NOT NULL
);

-- Entities table - People, organizations, accounts involved in cases
CREATE TABLE IF NOT EXISTS entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL, -- 'PERSON', 'ORGANIZATION', 'ACCOUNT', 'TRANSACTION'
    external_id VARCHAR(100), -- Reference to external system
    name VARCHAR(255) NOT NULL,
    attributes JSONB DEFAULT '{}',
    risk_score DECIMAL(5,2), -- 0.00 to 100.00
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    tenant_id VARCHAR(50) NOT NULL,
    cell_id VARCHAR(50) NOT NULL,
    
    UNIQUE(external_id, tenant_id, cell_id)
);

-- Case entity relationships
CREATE TABLE IF NOT EXISTS case_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id),
    entity_id UUID NOT NULL REFERENCES entities(id),
    relationship_type VARCHAR(50) NOT NULL, -- 'SUBJECT', 'WITNESS', 'RELATED_ACCOUNT', etc.
    confidence_score DECIMAL(5,2), -- 0.00 to 100.00
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(50) NOT NULL,
    cell_id VARCHAR(50) NOT NULL,
    
    UNIQUE(case_id, entity_id, relationship_type)
);

-- Create indexes for performance
CREATE INDEX idx_cases_case_number ON cases(case_number);
CREATE INDEX idx_cases_status_priority ON cases(status, priority);
CREATE INDEX idx_cases_created_at ON cases(created_at);
CREATE INDEX idx_cases_tenant_cell ON cases(tenant_id, cell_id);

CREATE INDEX idx_case_events_case_id ON case_events(case_id);
CREATE INDEX idx_case_events_created_at ON case_events(created_at);
CREATE INDEX idx_case_events_tenant_cell ON case_events(tenant_id, cell_id);

CREATE INDEX idx_evidence_case_id ON evidence(case_id);
CREATE INDEX idx_evidence_content_hash ON evidence(content_hash);
CREATE INDEX idx_evidence_tenant_cell ON evidence(tenant_id, cell_id);

CREATE INDEX idx_entities_external_id ON entities(external_id);
CREATE INDEX idx_entities_entity_type ON entities(entity_type);
CREATE INDEX idx_entities_tenant_cell ON entities(tenant_id, cell_id);

CREATE INDEX idx_case_entities_case_id ON case_entities(case_id);
CREATE INDEX idx_case_entities_entity_id ON case_entities(entity_id);
CREATE INDEX idx_case_entities_tenant_cell ON case_entities(tenant_id, cell_id);

-- Connect to audit_service database
\c audit_service;

-- Audit log table - Immutable audit trail
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    service_name VARCHAR(50) NOT NULL,
    user_id UUID,
    session_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    
    -- Security and compliance
    tenant_id VARCHAR(50) NOT NULL,
    cell_id VARCHAR(50) NOT NULL,
    classification VARCHAR(20) DEFAULT 'INTERNAL',
    
    -- Integrity
    checksum VARCHAR(64) NOT NULL -- SHA-256 of critical fields
);

-- Audit log is append-only, no updates allowed
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_service ON audit_log(service_name);
CREATE INDEX idx_audit_log_tenant_cell ON audit_log(tenant_id, cell_id);

-- Performance monitoring table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    service_name VARCHAR(50) NOT NULL,
    endpoint VARCHAR(200),
    method VARCHAR(10),
    response_time_ms INTEGER,
    status_code INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    error_message TEXT,
    
    tenant_id VARCHAR(50) NOT NULL,
    cell_id VARCHAR(50) NOT NULL
);

CREATE INDEX idx_performance_timestamp ON performance_metrics(timestamp);
CREATE INDEX idx_performance_service ON performance_metrics(service_name);
CREATE INDEX idx_performance_tenant_cell ON performance_metrics(tenant_id, cell_id);
