"""
FastAPI routes for TransactIQ API
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import schemas, Dataset, ValidationResult, ValidationError, Correction
from app.services import DatasetService
import pandas as pd
import tempfile
import os

router = APIRouter(prefix="/api/v1", tags=["datasets"])

dataset_service = DatasetService()


@router.post("/datasets/upload", response_model=schemas.UploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Upload and process CSV dataset"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            # Process dataset
            dataset_id, analysis = dataset_service.process_csv_file(
                tmp_path,
                file.filename,
                name or file.filename
            )
            
            # Save to database
            dataset = Dataset(
                id=dataset_id,
                name=analysis.get("name"),
                filename=analysis.get("filename"),
                total_records=analysis.get("total_records", 0),
                total_columns=analysis.get("total_columns", 0),
                detected_countries=analysis.get("detected_countries", []),
                detected_columns=analysis.get("detected_columns", {}),
                duplicate_record_count=analysis.get("duplicate_records", 0),
                missing_values_count=analysis.get("missing_values", 0),
                quality_score=analysis.get("quality_score", 0.0),
                chunk_count=analysis.get("chunk_count", 1)
            )
            db.add(dataset)
            db.commit()
            
            return schemas.UploadResponse(
                dataset_id=dataset_id,
                filename=file.filename,
                total_records=analysis.get("total_records", 0),
                status="completed",
                message="Dataset processed successfully"
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_id}", response_model=schemas.DatasetResponse)
async def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get dataset details"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return schemas.DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        filename=dataset.filename,
        status=dataset.status,
        metadata=schemas.DatasetMetadata(
            total_records=dataset.total_records,
            total_columns=dataset.total_columns,
            file_size_bytes=dataset.file_size_bytes,
            detected_countries=dataset.detected_countries or [],
            detected_columns=dataset.detected_columns or {},
            duplicate_record_count=dataset.duplicate_record_count,
            missing_values_count=dataset.missing_values_count
        ),
        health=schemas.DatasetHealth(
            quality_score=dataset.quality_score,
            completeness_score=dataset.completeness_score,
            accuracy_score=dataset.accuracy_score,
            consistency_score=dataset.consistency_score
        ),
        chunk_count=dataset.chunk_count,
        validation_started_at=dataset.validation_started_at,
        validation_completed_at=dataset.validation_completed_at,
        processing_time_seconds=dataset.processing_time_seconds,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at
    )


@router.get("/datasets/{dataset_id}/results", response_model=schemas.ValidationResultResponse)
async def get_validation_results(dataset_id: str, db: Session = Depends(get_db)):
    """Get validation results for dataset"""
    result = db.query(ValidationResult).filter(ValidationResult.dataset_id == dataset_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Validation results not found")
    
    return schemas.ValidationResultResponse.model_validate(result)


@router.get("/datasets/{dataset_id}/errors", response_model=schemas.ErrorsResponse)
async def get_errors(
    dataset_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    severity: Optional[str] = None,
    field_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get validation errors for dataset"""
    query = db.query(ValidationError).filter(ValidationError.dataset_id == dataset_id)
    
    if severity:
        query = query.filter(ValidationError.severity == severity)
    
    if field_name:
        query = query.filter(ValidationError.field_name == field_name)
    
    total = query.count()
    errors = query.offset(skip).limit(limit).all()
    
    return schemas.ErrorsResponse(
        total=total,
        items=[schemas.ValidationErrorResponse.model_validate(e) for e in errors],
        skip=skip,
        limit=limit
    )


@router.get("/datasets/{dataset_id}/corrections", response_model=schemas.CorrectionsResponse)
async def get_corrections(
    dataset_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get correction suggestions for dataset"""
    query = db.query(Correction).filter(Correction.dataset_id == dataset_id)
    
    total = query.count()
    accepted = query.filter(Correction.is_accepted == True).count()
    rejected = query.filter(Correction.is_accepted == False).count()
    pending = query.filter(Correction.is_accepted == None).count()
    
    corrections = query.offset(skip).limit(limit).all()
    
    return schemas.CorrectionsResponse(
        total=total,
        accepted=accepted,
        rejected=rejected,
        pending=pending,
        items=[schemas.CorrectionSuggestion.model_validate(c) for c in corrections],
        skip=skip,
        limit=limit
    )


@router.post("/datasets/{dataset_id}/corrections/{correction_id}/action")
async def action_correction(
    dataset_id: str,
    correction_id: str,
    action: schemas.CorrectionAction,
    db: Session = Depends(get_db)
):
    """Accept or reject correction suggestion"""
    correction = db.query(Correction).filter(
        Correction.id == correction_id,
        Correction.dataset_id == dataset_id
    ).first()
    
    if not correction:
        raise HTTPException(status_code=404, detail="Correction not found")
    
    from datetime import datetime
    correction.is_accepted = action.is_accepted
    correction.accepted_at = datetime.utcnow()
    db.commit()
    
    return {"status": "success", "correction_id": correction_id}


@router.get("/datasets/{dataset_id}/chunks", response_model=schemas.ChunksResponse)
async def get_chunks(dataset_id: str, db: Session = Depends(get_db)):
    """Get chunk information for dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    chunks = db.query(ChunkInfo).filter(ChunkInfo.dataset_id == dataset_id).all()
    
    return schemas.ChunksResponse(
        total_chunks=dataset.chunk_count,
        chunk_size=dataset.chunk_size,
        total_records=dataset.total_records,
        chunks=[schemas.ChunkInfo.model_validate(c) for c in chunks]
    )


@router.get("/datasets/{dataset_id}/report/{report_type}")
async def download_report(
    dataset_id: str,
    report_type: str = "pdf",
    db: Session = Depends(get_db)
):
    """Download validation report"""
    # Implementation would generate PDF/CSV report
    raise HTTPException(status_code=501, detail="Report generation coming soon")


@router.get("/demo-datasets", response_model=schemas.DemoDatasetsResponse)
async def get_demo_datasets():
    """Get available demo datasets"""
    demo_datasets = [
        schemas.DemoDataset(
            id="demo_001",
            name="Perfect Dataset",
            description="100% valid records - demonstrates successful validation",
            record_count=1000,
            scenarios=["successful_validation", "perfect_data"],
            file_path="/demo/perfect_dataset.csv"
        ),
        schemas.DemoDataset(
            id="demo_002",
            name="Phone Validation Dataset",
            description="Invalid country-specific phone numbers for validation testing",
            record_count=500,
            scenarios=["phone_format_errors", "country_detection"],
            file_path="/demo/phone_dataset.csv"
        ),
        schemas.DemoDataset(
            id="demo_003",
            name="Date Validation Dataset",
            description="Invalid timestamps and date formats for testing",
            record_count=500,
            scenarios=["date_format_errors", "timestamp_validation"],
            file_path="/demo/date_dataset.csv"
        ),
        schemas.DemoDataset(
            id="demo_004",
            name="Mixed Country Dataset",
            description="Multi-country transactions (India, Singapore, USA, UK)",
            record_count=2000,
            scenarios=["multi_country", "country_detection", "phone_formats"],
            file_path="/demo/mixed_country_dataset.csv"
        ),
        schemas.DemoDataset(
            id="demo_005",
            name="Duplicate Orders Dataset",
            description="Demonstrates duplicate detection and handling",
            record_count=800,
            scenarios=["duplicate_detection", "data_integrity"],
            file_path="/demo/duplicates_dataset.csv"
        ),
        schemas.DemoDataset(
            id="demo_006",
            name="Payment Integrity Dataset",
            description="Invalid payment modes and missing transaction references",
            record_count=600,
            scenarios=["payment_validation", "required_fields"],
            file_path="/demo/payment_dataset.csv"
        ),
        schemas.DemoDataset(
            id="demo_007",
            name="Large Scale Dataset",
            description="100,000+ rows to demonstrate chunking capability",
            record_count=100000,
            scenarios=["chunking", "large_files", "performance"],
            file_path="/demo/large_dataset.csv"
        ),
        schemas.DemoDataset(
            id="demo_008",
            name="Real World Dirty Dataset",
            description="Mixed realistic issues - duplicates, missing values, invalid formats",
            record_count=3000,
            scenarios=["mixed_errors", "real_world_data", "comprehensive_validation"],
            file_path="/demo/dirty_dataset.csv"
        ),
    ]
    
    return schemas.DemoDatasetsResponse(datasets=demo_datasets)


@router.post("/demo-datasets/{demo_id}/load")
async def load_demo_dataset(demo_id: str, db: Session = Depends(get_db)):
    """Load and process demo dataset"""
    # Implementation would load demo CSV and process it
    raise HTTPException(status_code=501, detail="Demo dataset loading coming soon")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
