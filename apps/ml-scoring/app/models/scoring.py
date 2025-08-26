"""Database models for ML scoring service."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List

from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ModelType(str, Enum):
    """Model type enumeration."""
    FRAUD_DETECTION = "FRAUD_DETECTION"
    AML_SCREENING = "AML_SCREENING"
    SANCTIONS_SCREENING = "SANCTIONS_SCREENING"
    KYC_RISK_ASSESSMENT = "KYC_RISK_ASSESSMENT"
    TRANSACTION_MONITORING = "TRANSACTION_MONITORING"
    CUSTOMER_RISK_SCORING = "CUSTOMER_RISK_SCORING"
    BEHAVIORAL_ANALYTICS = "BEHAVIORAL_ANALYTICS"


class ModelStatus(str, Enum):
    """Model status enumeration."""
    TRAINING = "TRAINING"
    VALIDATING = "VALIDATING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class ScoringStatus(str, Enum):
    """Scoring request status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ModelRegistry(Base):
    """Model registry for tracking ML models."""
    
    __tablename__ = "model_registry"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)
    model_status = Column(String(20), nullable=False, default=ModelStatus.TRAINING.value)
    
    # Model metadata
    description = Column(Text)
    algorithm = Column(String(100))
    framework = Column(String(50))  # sklearn, xgboost, lightgbm, etc.
    
    # Model artifacts
    model_path = Column(String(500))  # S3/MinIO path to model file
    onnx_path = Column(String(500))   # ONNX model for inference
    preprocessing_path = Column(String(500))  # Preprocessing pipeline
    
    # Model performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)
    auc_pr = Column(Float)
    
    # Feature information
    feature_names = Column(ARRAY(String))
    feature_importance = Column(JSONB)
    
    # Training metadata
    training_data_hash = Column(String(64))
    training_config = Column(JSONB)
    hyperparameters = Column(JSONB)
    
    # Timestamps
    trained_at = Column(DateTime(timezone=True))
    validated_at = Column(DateTime(timezone=True))
    deployed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # User and tenant information
    created_by = Column(UUID(as_uuid=True), nullable=False)
    tenant_id = Column(String(50), nullable=False)
    cell_id = Column(String(50), nullable=False)
    
    # Additional metadata
    metadata = Column(JSONB, default={})
    tags = Column(ARRAY(String), default=[])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_type": self.model_type,
            "model_status": self.model_status,
            "description": self.description,
            "algorithm": self.algorithm,
            "framework": self.framework,
            "model_path": self.model_path,
            "onnx_path": self.onnx_path,
            "preprocessing_path": self.preprocessing_path,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "auc_roc": self.auc_roc,
            "auc_pr": self.auc_pr,
            "feature_names": self.feature_names,
            "feature_importance": self.feature_importance,
            "training_data_hash": self.training_data_hash,
            "training_config": self.training_config,
            "hyperparameters": self.hyperparameters,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "deployed_at": self.deployed_at.isoformat() if self.deployed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": str(self.created_by),
            "tenant_id": self.tenant_id,
            "cell_id": self.cell_id,
            "metadata": self.metadata,
            "tags": self.tags,
        }


class ScoringRequest(Base):
    """Scoring request for tracking ML inference requests."""
    
    __tablename__ = "scoring_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(100), unique=True, nullable=False)
    
    # Model information
    model_id = Column(UUID(as_uuid=True), nullable=False)
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(50), nullable=False)
    
    # Request data
    input_data = Column(JSONB, nullable=False)
    feature_names = Column(ARRAY(String))
    
    # Scoring results
    predictions = Column(JSONB)
    probabilities = Column(JSONB)
    risk_score = Column(Float)
    risk_level = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Explainability results
    shap_values = Column(JSONB)
    feature_contributions = Column(JSONB)
    explanation_summary = Column(Text)
    
    # Status and timing
    status = Column(String(20), nullable=False, default=ScoringStatus.PENDING.value)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    processing_time_ms = Column(Integer)
    
    # User and context
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    context = Column(JSONB, default={})  # Additional context data
    
    # Error information
    error_message = Column(Text)
    error_details = Column(JSONB)
    
    # Tenant information
    tenant_id = Column(String(50), nullable=False)
    cell_id = Column(String(50), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "request_id": self.request_id,
            "model_id": str(self.model_id),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "input_data": self.input_data,
            "feature_names": self.feature_names,
            "predictions": self.predictions,
            "probabilities": self.probabilities,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "shap_values": self.shap_values,
            "feature_contributions": self.feature_contributions,
            "explanation_summary": self.explanation_summary,
            "status": self.status,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "processing_time_ms": self.processing_time_ms,
            "requested_by": str(self.requested_by),
            "context": self.context,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "tenant_id": self.tenant_id,
            "cell_id": self.cell_id,
        }


class BatchScoringJob(Base):
    """Batch scoring job for processing large datasets."""
    
    __tablename__ = "batch_scoring_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Model information
    model_id = Column(UUID(as_uuid=True), nullable=False)
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(50), nullable=False)
    
    # Input/Output data
    input_path = Column(String(500), nullable=False)
    output_path = Column(String(500))
    data_format = Column(String(20), default="CSV")  # CSV, JSON, PARQUET
    
    # Job configuration
    batch_size = Column(Integer, default=1000)
    enable_explainability = Column(Boolean, default=True)
    
    # Job status and progress
    status = Column(String(20), nullable=False, default=ScoringStatus.PENDING.value)
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    estimated_completion_at = Column(DateTime(timezone=True))
    
    # Error information
    error_message = Column(Text)
    error_details = Column(JSONB)
    
    # User and tenant information
    created_by = Column(UUID(as_uuid=True), nullable=False)
    tenant_id = Column(String(50), nullable=False)
    cell_id = Column(String(50), nullable=False)
    
    # Additional metadata
    metadata = Column(JSONB, default={})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "job_name": self.job_name,
            "description": self.description,
            "model_id": str(self.model_id),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "data_format": self.data_format,
            "batch_size": self.batch_size,
            "enable_explainability": self.enable_explainability,
            "status": self.status,
            "total_records": self.total_records,
            "processed_records": self.processed_records,
            "failed_records": self.failed_records,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_completion_at": self.estimated_completion_at.isoformat() if self.estimated_completion_at else None,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "created_by": str(self.created_by),
            "tenant_id": self.tenant_id,
            "cell_id": self.cell_id,
            "metadata": self.metadata,
        }


class ModelMetrics(Base):
    """Model performance metrics tracking."""
    
    __tablename__ = "model_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Metrics
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50))  # ACCURACY, PRECISION, RECALL, etc.
    
    # Context
    dataset_name = Column(String(255))
    evaluation_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    # Tenant information
    tenant_id = Column(String(50), nullable=False)
    cell_id = Column(String(50), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "model_id": str(self.model_id),
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_type": self.metric_type,
            "dataset_name": self.dataset_name,
            "evaluation_date": self.evaluation_date.isoformat() if self.evaluation_date else None,
            "metadata": self.metadata,
            "tenant_id": self.tenant_id,
            "cell_id": self.cell_id,
        }
