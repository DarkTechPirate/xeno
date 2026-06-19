"""
Database models for TransactIQ platform
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, JSON, Enum, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from app.database import Base


class ValidationStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Dataset(Base):
    """Main dataset model"""
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    
    # Metadata
    total_records = Column(Integer, default=0)
    total_columns = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    
    # Detection
    detected_countries = Column(JSON, default=list)  # List of detected country codes
    detected_columns = Column(JSON, default=dict)    # {column_name: data_type}
    duplicate_record_count = Column(Integer, default=0)
    missing_values_count = Column(Integer, default=0)
    
    # Health
    quality_score = Column(Float, default=0.0)  # 0-100
    completeness_score = Column(Float, default=0.0)
    accuracy_score = Column(Float, default=0.0)
    consistency_score = Column(Float, default=0.0)
    
    # Processing
    status = Column(Enum(ValidationStatus), default=ValidationStatus.PENDING)
    validation_started_at = Column(DateTime, nullable=True)
    validation_completed_at = Column(DateTime, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Chunks
    chunk_count = Column(Integer, default=0)
    chunk_size = Column(Integer, default=10000)
    
    # Audit
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    validation_results = relationship("ValidationResult", back_populates="dataset", cascade="all, delete-orphan")
    errors = relationship("ValidationError", back_populates="dataset", cascade="all, delete-orphan")
    corrections = relationship("Correction", back_populates="dataset", cascade="all, delete-orphan")
    chunks = relationship("DatasetChunk", back_populates="dataset", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="dataset", cascade="all, delete-orphan")


class ValidationResult(Base):
    """Overall validation result for dataset"""
    __tablename__ = "validation_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    
    # Counts
    total_records_validated = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    invalid_records = Column(Integer, default=0)
    records_with_warnings = Column(Integer, default=0)
    
    # Errors
    total_errors = Column(Integer, default=0)
    errors_by_category = Column(JSON, default=dict)  # {category: count}
    errors_by_severity = Column(JSON, default=dict)  # {severity: count}
    
    # Corrections
    suggested_corrections = Column(Integer, default=0)
    accepted_corrections = Column(Integer, default=0)
    rejected_corrections = Column(Integer, default=0)
    
    # Quality
    quality_score = Column(Float, default=0.0)
    score_after_corrections = Column(Float, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    dataset = relationship("Dataset", back_populates="validation_results")


class ValidationError(Base):
    """Individual validation errors"""
    __tablename__ = "validation_errors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    
    # Record info
    row_number = Column(Integer, nullable=False)
    record_id = Column(String(255), nullable=True)
    
    # Error details
    field_name = Column(String(255), nullable=False)
    error_type = Column(String(100), nullable=False)  # e.g., "phone_format", "date_format", "required_field"
    error_message = Column(Text)
    severity = Column(Enum(ErrorSeverity), default=ErrorSeverity.ERROR)
    
    # Context
    current_value = Column(Text, nullable=True)
    detected_country = Column(String(50), nullable=True)
    validation_rule = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    dataset = relationship("Dataset", back_populates="errors")
    correction = relationship("Correction", back_populates="error", uselist=False)


class Correction(Base):
    """Auto-correction suggestions"""
    __tablename__ = "corrections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    error_id = Column(String(36), ForeignKey("validation_errors.id"), nullable=True)
    
    # Record info
    row_number = Column(Integer, nullable=False)
    field_name = Column(String(255), nullable=False)
    
    # Correction details
    original_value = Column(Text)
    suggested_value = Column(Text)
    confidence_score = Column(Float)  # 0-100
    correction_type = Column(String(100))  # e.g., "phone_format", "date_normalize", "trim"
    
    # Status
    is_accepted = Column(Boolean, default=None, nullable=True)  # None = not reviewed
    accepted_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    dataset = relationship("Dataset", back_populates="corrections")
    error = relationship("ValidationError", back_populates="correction")


class DatasetChunk(Base):
    """Chunk information for large datasets"""
    __tablename__ = "dataset_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    
    # Chunk details
    chunk_number = Column(Integer, nullable=False)
    start_row = Column(Integer, nullable=False)
    end_row = Column(Integer, nullable=False)
    record_count = Column(Integer, nullable=False)
    
    # File info
    file_path = Column(String(512), nullable=True)
    file_size_bytes = Column(Integer, default=0)
    
    # Processing
    is_processed = Column(Boolean, default=False)
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    dataset = relationship("Dataset", back_populates="chunks")


class Report(Base):
    """Generated reports"""
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    
    # Report info
    report_type = Column(String(50))  # "summary", "detailed", "executive"
    format = Column(String(10))  # "pdf", "csv", "json"
    
    # File storage
    file_path = Column(String(512), nullable=True)
    file_size_bytes = Column(Integer, default=0)
    
    # Content
    summary = Column(JSON)  # Report summary statistics
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    dataset = relationship("Dataset", back_populates="reports")


class ValidationRule(Base):
    """Enterprise validation rules"""
    __tablename__ = "validation_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Rule definition
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    rule_type = Column(String(100))  # "phone", "date", "email", "custom", "regex"
    
    # Configuration
    pattern = Column(String(512), nullable=True)  # Regex pattern
    country_codes = Column(JSON, default=list)  # Applicable countries
    config = Column(JSON)  # Additional configuration
    
    # Status
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Action info
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100))  # "dataset", "correction", "report"
    entity_id = Column(String(36))
    
    # Details
    details = Column(JSON)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
