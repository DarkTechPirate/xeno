"""
Pydantic schemas for TransactIQ API
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ValidationStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorSeverityEnum(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============ Dataset Schemas ============

class DatasetCreate(BaseModel):
    """Schema for dataset upload"""
    name: str
    description: Optional[str] = None


class DatasetMetadata(BaseModel):
    """Dataset metadata response"""
    total_records: int
    total_columns: int
    file_size_bytes: int
    detected_countries: List[str]
    detected_columns: Dict[str, str]
    duplicate_record_count: int
    missing_values_count: int


class DatasetHealth(BaseModel):
    """Dataset health scores"""
    quality_score: float = Field(ge=0, le=100)
    completeness_score: float = Field(ge=0, le=100)
    accuracy_score: float = Field(ge=0, le=100)
    consistency_score: float = Field(ge=0, le=100)


class DatasetResponse(BaseModel):
    """Complete dataset response"""
    id: str
    name: str
    description: Optional[str]
    filename: str
    status: ValidationStatusEnum
    metadata: DatasetMetadata
    health: DatasetHealth
    chunk_count: int
    validation_started_at: Optional[datetime]
    validation_completed_at: Optional[datetime]
    processing_time_seconds: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Validation Error Schemas ============

class ValidationErrorResponse(BaseModel):
    """Individual validation error"""
    id: str
    row_number: int
    record_id: Optional[str]
    field_name: str
    error_type: str
    error_message: str
    severity: ErrorSeverityEnum
    current_value: Optional[str]
    detected_country: Optional[str]
    validation_rule: Optional[str]

    class Config:
        from_attributes = True


class ErrorsFilterRequest(BaseModel):
    """Request to filter errors"""
    field_name: Optional[str] = None
    error_type: Optional[str] = None
    severity: Optional[ErrorSeverityEnum] = None
    search_term: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=500)


class ErrorsResponse(BaseModel):
    """Paginated errors response"""
    total: int
    items: List[ValidationErrorResponse]
    skip: int
    limit: int


# ============ Correction Schemas ============

class CorrectionSuggestion(BaseModel):
    """Auto-correction suggestion"""
    id: str
    row_number: int
    field_name: str
    original_value: str
    suggested_value: str
    confidence_score: float = Field(ge=0, le=100)
    correction_type: str

    class Config:
        from_attributes = True


class CorrectionAction(BaseModel):
    """Accept/reject correction"""
    correction_id: str
    is_accepted: bool


class CorrectionsResponse(BaseModel):
    """Paginated corrections response"""
    total: int
    accepted: int
    rejected: int
    pending: int
    items: List[CorrectionSuggestion]
    skip: int
    limit: int


# ============ Validation Result Schemas ============

class ValidationResultResponse(BaseModel):
    """Overall validation result"""
    id: str
    dataset_id: str
    total_records_validated: int
    valid_records: int
    invalid_records: int
    records_with_warnings: int
    total_errors: int
    errors_by_category: Dict[str, int]
    errors_by_severity: Dict[str, int]
    suggested_corrections: int
    accepted_corrections: int
    rejected_corrections: int
    quality_score: float
    score_after_corrections: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Chunk Schemas ============

class ChunkInfo(BaseModel):
    """Dataset chunk information"""
    id: str
    chunk_number: int
    start_row: int
    end_row: int
    record_count: int
    file_size_bytes: int
    is_processed: bool
    error_count: int
    warning_count: int

    class Config:
        from_attributes = True


class ChunksResponse(BaseModel):
    """Chunks information"""
    total_chunks: int
    chunk_size: int
    total_records: int
    chunks: List[ChunkInfo]


# ============ Report Schemas ============

class ReportRequest(BaseModel):
    """Request to generate report"""
    report_type: str = Field(default="summary")  # "summary", "detailed", "executive"
    format: str = Field(default="pdf")  # "pdf", "csv", "json"


class ReportResponse(BaseModel):
    """Generated report"""
    id: str
    dataset_id: str
    report_type: str
    format: str
    file_size_bytes: int
    download_url: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Health Analyzer Schemas ============

class ColumnAnalysis(BaseModel):
    """Analysis of a single column"""
    column_name: str
    data_type: str
    non_null_count: int
    null_count: int
    unique_count: int
    stats: Optional[Dict[str, Any]]


class CountryStats(BaseModel):
    """Statistics for a detected country"""
    country_code: str
    country_name: str
    record_count: int
    percentage: float


class HealthAnalyzerResponse(BaseModel):
    """Dataset health analysis"""
    dataset_id: str
    total_records: int
    total_columns: int
    columns: List[ColumnAnalysis]
    countries: List[CountryStats]
    duplicate_records: int
    duplicate_percentage: float
    missing_values_total: int
    quality_score: float
    insights: List[str]  # Business-level insights


# ============ Validation Rule Schemas ============

class ValidationRuleCreate(BaseModel):
    """Create validation rule"""
    name: str
    description: Optional[str]
    rule_type: str
    pattern: Optional[str]
    country_codes: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None


class ValidationRuleResponse(BaseModel):
    """Validation rule"""
    id: str
    name: str
    description: Optional[str]
    rule_type: str
    pattern: Optional[str]
    country_codes: List[str]
    config: Dict[str, Any]
    is_active: bool
    priority: int

    class Config:
        from_attributes = True


# ============ Demo Dataset Schemas ============

class DemoDataset(BaseModel):
    """Demo dataset metadata"""
    id: str
    name: str
    description: str
    record_count: int
    scenarios: List[str]
    file_path: str


class DemoDatasetsResponse(BaseModel):
    """Available demo datasets"""
    datasets: List[DemoDataset]


# ============ AI Insights Schemas ============

class AIInsights(BaseModel):
    """AI-powered insights"""
    root_causes: List[str]
    most_frequent_failures: Dict[str, int]
    recommendations: List[str]
    business_impact_summary: str
    estimated_impact_after_corrections: str


# ============ Upload Response ============

class UploadResponse(BaseModel):
    """Response after file upload"""
    dataset_id: str
    filename: str
    total_records: int
    status: ValidationStatusEnum
    message: str


# ============ Pagination ============

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    total: int
    items: List[Any]
    skip: int
    limit: int
