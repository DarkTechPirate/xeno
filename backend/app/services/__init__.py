"""
Dataset processing service
"""
import pandas as pd
import polars as pl
from typing import Dict, List, Any, Optional, Tuple
import uuid
from datetime import datetime
import json
from app.validators.validation_engine import ValidationEngine
from app.engines import ChunkingEngine


class DatasetService:
    """Service for dataset processing, validation, and analysis"""
    
    def __init__(self):
        self.validation_engine = ValidationEngine()
        self.chunking_engine = ChunkingEngine()
    
    def process_csv_file(
        self,
        file_path: str,
        filename: str,
        dataset_name: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process uploaded CSV file
        
        Returns: (dataset_id, metadata)
        """
        dataset_id = str(uuid.uuid4())
        
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Analyze dataset
            analysis = self._analyze_dataset(df)
            analysis["id"] = dataset_id
            analysis["name"] = dataset_name
            analysis["filename"] = filename
            
            # Detect schema
            analysis["detected_columns"] = {col: self._detect_column_type(df[col]) for col in df.columns}
            
            # Detect countries
            analysis["detected_countries"] = self._detect_countries(df)
            
            # Find duplicates
            analysis["duplicate_records"] = len(df) - len(df.drop_duplicates())
            
            # Find missing values
            analysis["missing_values"] = df.isnull().sum().sum()
            
            # Calculate initial quality score
            analysis["quality_score"] = self._calculate_initial_quality_score(analysis, len(df))
            
            # Run validation
            validation_results = self.validation_engine.validate_dataset(df)
            analysis.update(validation_results)
            
            # Split into chunks if needed
            if len(df) > self.chunking_engine.chunk_size:
                chunks = self.chunking_engine.split_dataset(df, dataset_id)
                analysis["chunk_count"] = len(chunks)
                analysis["chunks"] = chunks
            else:
                analysis["chunk_count"] = 1
                analysis["chunks"] = []
            
            return dataset_id, analysis
        
        except Exception as e:
            raise Exception(f"Error processing CSV: {str(e)}")
    
    def _analyze_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataset structure and content"""
        return {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "file_size_bytes": 0,  # Would be calculated from file
            "columns": df.columns.tolist(),
        }
    
    def _detect_column_type(self, series: pd.Series) -> str:
        """Auto-detect column data type"""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return "unknown"
        
        # Check numeric
        try:
            pd.to_numeric(non_null)
            return "numeric"
        except:
            pass
        
        # Check date
        try:
            pd.to_datetime(non_null)
            return "date"
        except:
            pass
        
        # Check boolean
        if non_null.astype(str).str.lower().isin(["true", "false", "yes", "no", "1", "0"]).all():
            return "boolean"
        
        return "string"
    
    def _detect_countries(self, df: pd.DataFrame) -> List[str]:
        """Detect countries in dataset"""
        countries = set()
        
        # Look for country column
        country_cols = [col for col in df.columns if "country" in col.lower()]
        
        if country_cols:
            col = country_cols[0]
            if col in df.columns:
                country_vals = df[col].dropna().unique()
                countries.update([str(v).upper() for v in country_vals])
        
        # Look for phone numbers and detect countries
        phone_cols = [col for col in df.columns if "phone" in col.lower() or "mobile" in col.lower()]
        
        if phone_cols:
            from app.validators.phone_validator import PhoneValidator
            col = phone_cols[0]
            if col in df.columns:
                for phone in df[col].dropna():
                    country = PhoneValidator.detect_country(str(phone))
                    if country:
                        countries.add(country)
        
        return list(countries)
    
    def _calculate_initial_quality_score(self, analysis: Dict[str, Any], total_records: int) -> float:
        """Calculate initial quality score before validation"""
        if total_records == 0:
            return 0.0
        
        # Start with 100 and deduct for issues
        score = 100.0
        
        # Deduct for duplicates
        duplicate_pct = (analysis.get("duplicate_records", 0) / total_records) * 100
        score -= min(20.0, duplicate_pct * 0.2)
        
        # Deduct for missing values
        total_cells = total_records * analysis.get("total_columns", 1)
        missing_pct = (analysis.get("missing_values", 0) / total_cells * 100) if total_cells > 0 else 0
        score -= min(20.0, missing_pct * 0.2)
        
        return max(0.0, min(100.0, score))
    
    def get_dataset_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive statistics for dataset"""
        stats = {
            "basic": {
                "row_count": len(df),
                "column_count": len(df.columns),
                "memory_usage": df.memory_usage(deep=True).sum(),
            },
            "columns": {},
            "missing_data": {
                "total_missing": df.isnull().sum().sum(),
                "by_column": df.isnull().sum().to_dict(),
                "percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
            },
            "duplicates": {
                "total_duplicates": len(df) - len(df.drop_duplicates()),
                "percentage": (len(df) - len(df.drop_duplicates())) / len(df) * 100 if len(df) > 0 else 0
            }
        }
        
        # Column-wise statistics
        for col in df.columns:
            col_stats = {
                "type": str(df[col].dtype),
                "non_null_count": df[col].notna().sum(),
                "unique_count": df[col].nunique(),
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats.update({
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                })
            
            stats["columns"][col] = col_stats
        
        return stats
    
    def apply_corrections(
        self,
        df: pd.DataFrame,
        corrections: Dict[int, Dict[str, Tuple[str, float]]]
    ) -> pd.DataFrame:
        """Apply accepted corrections to dataframe"""
        df_corrected = df.copy()
        
        for row_idx, row_corrections in corrections.items():
            for field_name, (suggested_value, _) in row_corrections.items():
                if row_idx < len(df_corrected) and field_name in df_corrected.columns:
                    df_corrected.at[row_idx, field_name] = suggested_value
        
        return df_corrected
    
    def generate_data_quality_report(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive data quality report"""
        total = validation_results.get("total_records", 0)
        valid = validation_results.get("valid_records", 0)
        
        report = {
            "summary": {
                "total_records": total,
                "valid_records": valid,
                "invalid_records": validation_results.get("invalid_records", 0),
                "quality_score": validation_results.get("quality_score", 0.0),
            },
            "quality_metrics": {
                "completeness": self._calculate_completeness(validation_results),
                "accuracy": self._calculate_accuracy(validation_results),
                "consistency": self._calculate_consistency(validation_results),
                "validity": (valid / total * 100) if total > 0 else 0
            },
            "error_breakdown": validation_results.get("errors_by_category", {}),
            "recommendations": self._generate_recommendations(validation_results),
        }
        
        return report
    
    def _calculate_completeness(self, results: Dict[str, Any]) -> float:
        """Calculate completeness score (% of fields filled)"""
        # This would be based on missing value analysis
        return min(100.0, max(0.0, 100 - (results.get("missing_percentage", 0) * 2)))
    
    def _calculate_accuracy(self, results: Dict[str, Any]) -> float:
        """Calculate accuracy score (% of valid formats)"""
        total = results.get("total_records", 0)
        valid = results.get("valid_records", 0)
        return (valid / total * 100) if total > 0 else 0
    
    def _calculate_consistency(self, results: Dict[str, Any]) -> float:
        """Calculate consistency score"""
        # Based on duplicate and type consistency
        return max(0.0, 100 - (results.get("duplicate_percentage", 0) * 1.5))
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate business-level recommendations"""
        recommendations = []
        
        quality = results.get("quality_score", 0)
        
        if quality < 60:
            recommendations.append("Data quality is below acceptable threshold. Consider data cleansing.")
        elif quality < 85:
            recommendations.append("Apply suggested corrections to improve data quality.")
        else:
            recommendations.append("Data quality is good. Continue regular validation.")
        
        # Error-specific recommendations
        if results.get("errors_by_category", {}).get("phone_format", 0) > 0:
            recommendations.append("Review and correct phone number formats by country.")
        
        if results.get("errors_by_category", {}).get("date_format", 0) > 0:
            recommendations.append("Standardize date formats across the dataset.")
        
        if results.get("duplicate_records", 0) > 0:
            recommendations.append("Investigate and remove duplicate records.")
        
        return recommendations
