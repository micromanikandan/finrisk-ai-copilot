"""Database models for the ingestion service."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class IngestionStatus(str, Enum):
    """Ingestion status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class DataFormat(str, Enum):
    """Data format enumeration."""
    JSON = "JSON"
    CSV = "CSV"
    XML = "XML"
    PARQUET = "PARQUET"
    AVRO = "AVRO"
    EXCEL = "EXCEL"


class IngestionJob(Base):
    """Ingestion job model."""
    
    __tablename__ = "ingestion_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Source information
    source_type = Column(String(50), nullable=False)  # FILE, API, STREAM, DATABASE
    source_path = Column(String(500))
    data_format = Column(String(20), nullable=False)
    
    # Status and timing
    status = Column(String(20), nullable=False, default=IngestionStatus.PENDING.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Progress tracking
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    
    # Configuration
    config = Column(JSONB, default={})
    validation_rules = Column(JSONB, default={})
    transformation_rules = Column(JSONB, default={})
    
    # User and tenant information
    created_by = Column(UUID(as_uuid=True), nullable=False)
    tenant_id = Column(String(50), nullable=False)
    cell_id = Column(String(50), nullable=False)
    
    # Error information
    error_message = Column(Text)
    error_details = Column(JSONB)
    
    # Metadata
    metadata = Column(JSONB, default={})
    tags = Column(JSONB, default=[])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "job_name": self.job_name,
            "description": self.description,
            "source_type": self.source_type,
            "source_path": self.source_path,
            "data_format": self.data_format,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_records": self.total_records,
            "processed_records": self.processed_records,
            "failed_records": self.failed_records,
            "config": self.config,
            "created_by": str(self.created_by),
            "tenant_id": self.tenant_id,
            "cell_id": self.cell_id,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "tags": self.tags,
        }


class OutboxEvent(Base):
    """Outbox pattern implementation for reliable event publishing."""
    
    __tablename__ = "outbox_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event information
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSONB, nullable=False)
    aggregate_id = Column(String(100), nullable=False)
    aggregate_type = Column(String(50), nullable=False)
    
    # Processing status
    processed = Column(Boolean, default=False, nullable=False)
    processed_at = Column(DateTime(timezone=True))
    retry_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tenant_id = Column(String(50), nullable=False)
    cell_id = Column(String(50), nullable=False)
    
    # Kafka publishing info
    topic = Column(String(100))
    partition_key = Column(String(100))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "event_type": self.event_type,
            "event_data": self.event_data,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "processed": self.processed,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tenant_id": self.tenant_id,
            "cell_id": self.cell_id,
            "topic": self.topic,
            "partition_key": self.partition_key,
        }


class DataRecord(Base):
    """Individual data record processed during ingestion."""
    
    __tablename__ = "data_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingestion_job_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Record data
    original_data = Column(JSONB, nullable=False)
    processed_data = Column(JSONB)
    record_hash = Column(String(64))  # SHA-256 hash for deduplication
    
    # Processing status
    status = Column(String(20), nullable=False, default="PENDING")
    processed_at = Column(DateTime(timezone=True))
    
    # Validation results
    validation_passed = Column(Boolean)
    validation_errors = Column(JSONB, default=[])
    
    # Enrichment results
    enriched_fields = Column(JSONB, default={})
    
    # Error information
    error_message = Column(Text)
    
    # Metadata
    source_line_number = Column(Integer)
    metadata = Column(JSONB, default={})
    
    # Tenant information
    tenant_id = Column(String(50), nullable=False)
    cell_id = Column(String(50), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "ingestion_job_id": str(self.ingestion_job_id),
            "original_data": self.original_data,
            "processed_data": self.processed_data,
            "record_hash": self.record_hash,
            "status": self.status,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "validation_passed": self.validation_passed,
            "validation_errors": self.validation_errors,
            "enriched_fields": self.enriched_fields,
            "error_message": self.error_message,
            "source_line_number": self.source_line_number,
            "metadata": self.metadata,
            "tenant_id": self.tenant_id,
            "cell_id": self.cell_id,
        }


class IngestionMetrics(Base):
    """Metrics for ingestion performance monitoring."""
    
    __tablename__ = "ingestion_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingestion_job_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Performance metrics
    records_per_second = Column(Integer)
    memory_usage_mb = Column(Integer)
    cpu_usage_percent = Column(Integer)
    
    # Data quality metrics
    duplicate_records = Column(Integer, default=0)
    malformed_records = Column(Integer, default=0)
    validation_failures = Column(Integer, default=0)
    
    # Processing metrics
    transformation_time_ms = Column(Integer)
    validation_time_ms = Column(Integer)
    enrichment_time_ms = Column(Integer)
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Tenant information
    tenant_id = Column(String(50), nullable=False)
    cell_id = Column(String(50), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "ingestion_job_id": str(self.ingestion_job_id),
            "records_per_second": self.records_per_second,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "duplicate_records": self.duplicate_records,
            "malformed_records": self.malformed_records,
            "validation_failures": self.validation_failures,
            "transformation_time_ms": self.transformation_time_ms,
            "validation_time_ms": self.validation_time_ms,
            "enrichment_time_ms": self.enrichment_time_ms,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "tenant_id": self.tenant_id,
            "cell_id": self.cell_id,
        }
