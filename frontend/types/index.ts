/**
 * API Response Types
 */

export type ValidationStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type ErrorSeverity = 'info' | 'warning' | 'error' | 'critical';

export interface Dataset {
  id: string;
  name: string;
  description?: string;
  filename: string;
  status: ValidationStatus;
  metadata: DatasetMetadata;
  health: DatasetHealth;
  chunk_count: number;
  validation_started_at?: string;
  validation_completed_at?: string;
  processing_time_seconds?: number;
  created_at: string;
  updated_at: string;
}

export interface DatasetMetadata {
  total_records: number;
  total_columns: number;
  file_size_bytes: number;
  detected_countries: string[];
  detected_columns: Record<string, string>;
  duplicate_record_count: number;
  missing_values_count: number;
}

export interface DatasetHealth {
  quality_score: number;
  completeness_score: number;
  accuracy_score: number;
  consistency_score: number;
}

export interface ValidationError {
  id: string;
  row_number: number;
  record_id?: string;
  field_name: string;
  error_type: string;
  error_message: string;
  severity: ErrorSeverity;
  current_value?: string;
  detected_country?: string;
  validation_rule?: string;
}

export interface Correction {
  id: string;
  row_number: number;
  field_name: string;
  original_value: string;
  suggested_value: string;
  confidence_score: number;
  correction_type: string;
}

export interface ValidationResult {
  id: string;
  dataset_id: string;
  total_records_validated: number;
  valid_records: number;
  invalid_records: number;
  records_with_warnings: number;
  total_errors: number;
  errors_by_category: Record<string, number>;
  errors_by_severity: Record<string, number>;
  suggested_corrections: number;
  accepted_corrections: number;
  rejected_corrections: number;
  quality_score: number;
  score_after_corrections?: number;
  created_at: string;
}

export interface DemoDataset {
  id: string;
  name: string;
  description: string;
  record_count: number;
  scenarios: string[];
  file_path: string;
}

export interface ChunkInfo {
  id: string;
  chunk_number: number;
  start_row: number;
  end_row: number;
  record_count: number;
  file_size_bytes: number;
  is_processed: boolean;
  error_count: number;
  warning_count: number;
}

export interface Report {
  id: string;
  dataset_id: string;
  report_type: string;
  format: string;
  file_size_bytes: number;
  download_url: string;
  created_at: string;
}

export interface AIInsights {
  root_causes: string[];
  most_frequent_failures: Record<string, number>;
  recommendations: string[];
  business_impact_summary: string;
  estimated_impact_after_corrections: string;
}

/**
 * UI State Types
 */

export interface UploadProgress {
  fileName: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

export interface FilterOptions {
  severity?: ErrorSeverity;
  fieldName?: string;
  errorType?: string;
  searchTerm?: string;
}

export interface PaginationState {
  currentPage: number;
  pageSize: number;
  totalItems: number;
}
