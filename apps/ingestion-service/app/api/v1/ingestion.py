"""Ingestion API endpoints."""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.ingestion import IngestionJob, IngestionStatus, DataFormat
from app.services.ingestion_service import IngestionService
from app.services.file_processor import FileProcessor
from app.services.outbox_service import OutboxService

logger = structlog.get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


class CreateIngestionJobRequest(BaseModel):
    """Request model for creating an ingestion job."""
    job_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    source_type: str = Field(..., pattern="^(FILE|API|STREAM|DATABASE)$")
    data_format: DataFormat
    config: Dict[str, Any] = Field(default_factory=dict)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    transformation_rules: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class IngestionJobResponse(BaseModel):
    """Response model for ingestion job."""
    id: str
    job_name: str
    description: Optional[str]
    source_type: str
    source_path: Optional[str]
    data_format: str
    status: str
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    total_records: int
    processed_records: int
    failed_records: int
    config: Dict[str, Any]
    created_by: str
    tenant_id: str
    cell_id: str
    error_message: Optional[str]
    metadata: Dict[str, Any]
    tags: List[str]


class IngestionStatsResponse(BaseModel):
    """Response model for ingestion statistics."""
    total_jobs: int
    pending_jobs: int
    processing_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_records_processed: int
    avg_processing_time_seconds: Optional[float]


@router.post("/jobs", response_model=IngestionJobResponse)
async def create_ingestion_job(
    request: CreateIngestionJobRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IngestionJobResponse:
    """Create a new ingestion job."""
    logger.info("Creating ingestion job", job_name=request.job_name, user=current_user["sub"])
    
    try:
        # Create ingestion service
        ingestion_service = IngestionService(db)
        
        # Create the job
        job = await ingestion_service.create_job(
            job_name=request.job_name,
            description=request.description,
            source_type=request.source_type,
            data_format=request.data_format,
            config=request.config,
            validation_rules=request.validation_rules,
            transformation_rules=request.transformation_rules,
            created_by=uuid.UUID(current_user["sub"]),
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"],
            metadata=request.metadata,
            tags=request.tags,
        )
        
        logger.info("Ingestion job created", job_id=str(job.id), job_name=job.job_name)
        
        return IngestionJobResponse(**job.to_dict())
        
    except Exception as e:
        logger.error("Failed to create ingestion job", error=str(e), job_name=request.job_name)
        raise HTTPException(status_code=500, detail=f"Failed to create ingestion job: {str(e)}")


@router.post("/jobs/{job_id}/upload", response_model=IngestionJobResponse)
async def upload_file_for_ingestion(
    job_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    start_processing: bool = Form(default=True),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IngestionJobResponse:
    """Upload a file for an existing ingestion job."""
    logger.info("Uploading file for ingestion", job_id=job_id, filename=file.filename)
    
    try:
        # Validate file
        if file.size > 100 * 1024 * 1024:  # 100MB limit
            raise HTTPException(status_code=413, detail="File too large")
        
        # Get ingestion service and file processor
        ingestion_service = IngestionService(db)
        file_processor = FileProcessor()
        
        # Get the job
        job = await ingestion_service.get_job_by_id(
            job_id=uuid.UUID(job_id),
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        if not job:
            raise HTTPException(status_code=404, detail="Ingestion job not found")
        
        if job.status != IngestionStatus.PENDING:
            raise HTTPException(status_code=400, detail="Job is not in pending status")
        
        # Save the uploaded file
        file_path = await file_processor.save_uploaded_file(file, job_id)
        
        # Update job with file path
        await ingestion_service.update_job_source_path(job.id, file_path)
        
        logger.info("File uploaded successfully", job_id=job_id, file_path=file_path)
        
        # Start processing if requested
        if start_processing:
            background_tasks.add_task(
                process_ingestion_job_async,
                job_id=job.id,
                tenant_id=current_user["tenant_id"],
                cell_id=current_user["cell_id"]
            )
        
        # Return updated job
        updated_job = await ingestion_service.get_job_by_id(
            job_id=job.id,
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        return IngestionJobResponse(**updated_job.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to upload file", error=str(e), job_id=job_id)
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/jobs/{job_id}/start", response_model=IngestionJobResponse)
async def start_ingestion_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IngestionJobResponse:
    """Start processing an ingestion job."""
    logger.info("Starting ingestion job", job_id=job_id)
    
    try:
        ingestion_service = IngestionService(db)
        
        # Get the job
        job = await ingestion_service.get_job_by_id(
            job_id=uuid.UUID(job_id),
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        if not job:
            raise HTTPException(status_code=404, detail="Ingestion job not found")
        
        if job.status != IngestionStatus.PENDING:
            raise HTTPException(status_code=400, detail="Job is not in pending status")
        
        # Start processing in background
        background_tasks.add_task(
            process_ingestion_job_async,
            job_id=job.id,
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        # Update job status to processing
        await ingestion_service.update_job_status(job.id, IngestionStatus.PROCESSING)
        
        # Return updated job
        updated_job = await ingestion_service.get_job_by_id(
            job_id=job.id,
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        logger.info("Ingestion job started", job_id=job_id)
        return IngestionJobResponse(**updated_job.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start ingestion job", error=str(e), job_id=job_id)
        raise HTTPException(status_code=500, detail=f"Failed to start ingestion job: {str(e)}")


@router.get("/jobs/{job_id}", response_model=IngestionJobResponse)
async def get_ingestion_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IngestionJobResponse:
    """Get an ingestion job by ID."""
    try:
        ingestion_service = IngestionService(db)
        
        job = await ingestion_service.get_job_by_id(
            job_id=uuid.UUID(job_id),
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        if not job:
            raise HTTPException(status_code=404, detail="Ingestion job not found")
        
        return IngestionJobResponse(**job.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get ingestion job", error=str(e), job_id=job_id)
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion job: {str(e)}")


@router.get("/jobs", response_model=List[IngestionJobResponse])
async def list_ingestion_jobs(
    skip: int = 0,
    limit: int = 20,
    status: Optional[IngestionStatus] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[IngestionJobResponse]:
    """List ingestion jobs with pagination and filtering."""
    try:
        ingestion_service = IngestionService(db)
        
        jobs = await ingestion_service.list_jobs(
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"],
            status=status,
            skip=skip,
            limit=limit
        )
        
        return [IngestionJobResponse(**job.to_dict()) for job in jobs]
        
    except Exception as e:
        logger.error("Failed to list ingestion jobs", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list ingestion jobs: {str(e)}")


@router.delete("/jobs/{job_id}")
async def cancel_ingestion_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Cancel an ingestion job."""
    logger.info("Cancelling ingestion job", job_id=job_id)
    
    try:
        ingestion_service = IngestionService(db)
        
        # Get the job
        job = await ingestion_service.get_job_by_id(
            job_id=uuid.UUID(job_id),
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        if not job:
            raise HTTPException(status_code=404, detail="Ingestion job not found")
        
        if job.status in [IngestionStatus.COMPLETED, IngestionStatus.FAILED, IngestionStatus.CANCELLED]:
            raise HTTPException(status_code=400, detail="Job cannot be cancelled in current status")
        
        # Cancel the job
        await ingestion_service.update_job_status(job.id, IngestionStatus.CANCELLED)
        
        logger.info("Ingestion job cancelled", job_id=job_id)
        return {"message": "Ingestion job cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel ingestion job", error=str(e), job_id=job_id)
        raise HTTPException(status_code=500, detail=f"Failed to cancel ingestion job: {str(e)}")


@router.get("/stats", response_model=IngestionStatsResponse)
async def get_ingestion_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IngestionStatsResponse:
    """Get ingestion statistics for the tenant."""
    try:
        ingestion_service = IngestionService(db)
        
        stats = await ingestion_service.get_statistics(
            tenant_id=current_user["tenant_id"],
            cell_id=current_user["cell_id"]
        )
        
        return IngestionStatsResponse(**stats)
        
    except Exception as e:
        logger.error("Failed to get ingestion statistics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion statistics: {str(e)}")


async def process_ingestion_job_async(
    job_id: uuid.UUID,
    tenant_id: str,
    cell_id: str
) -> None:
    """Process an ingestion job asynchronously."""
    from app.core.database import get_database
    
    logger.info("Starting async processing", job_id=str(job_id))
    
    database = get_database()
    async with database.session() as db:
        try:
            ingestion_service = IngestionService(db)
            file_processor = FileProcessor()
            outbox_service = OutboxService(db)
            
            # Get the job
            job = await ingestion_service.get_job_by_id(job_id, tenant_id, cell_id)
            if not job:
                logger.error("Job not found for processing", job_id=str(job_id))
                return
            
            # Update status to processing
            await ingestion_service.update_job_status(job.id, IngestionStatus.PROCESSING)
            await ingestion_service.update_job_started_at(job.id, datetime.utcnow())
            
            # Process the file
            await file_processor.process_file(job, ingestion_service, outbox_service)
            
            # Update status to completed
            await ingestion_service.update_job_status(job.id, IngestionStatus.COMPLETED)
            await ingestion_service.update_job_completed_at(job.id, datetime.utcnow())
            
            # Publish completion event
            await outbox_service.publish_ingestion_completed_event(job)
            
            logger.info("Ingestion job completed", job_id=str(job_id))
            
        except Exception as e:
            logger.error("Ingestion job failed", job_id=str(job_id), error=str(e))
            
            # Update status to failed
            await ingestion_service.update_job_status(job.id, IngestionStatus.FAILED)
            await ingestion_service.update_job_error(job.id, str(e))
            
            # Publish failure event
            await outbox_service.publish_ingestion_failed_event(job, str(e))
