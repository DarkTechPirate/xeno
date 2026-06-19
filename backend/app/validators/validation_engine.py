"""
Main validation engine
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import re
from app.validators.phone_validator import PhoneValidator
from app.validators.date_validator import DateValidator


@dataclass
class ValidationError:
    """Validation error record"""
    row_number: int
    field_name: str
    error_type: str
    error_message: str
    severity: str  # "info", "warning", "error", "critical"
    current_value: Any
    detected_country: Optional[str] = None
    validation_rule: Optional[str] = None


class ValidationEngine:
    """Main validation orchestration engine"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.corrections: Dict[int, Dict[str, Tuple[str, float]]] = {}
    
    def validate_dataset(
        self,
        df: pd.DataFrame,
        validation_rules: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Validate entire dataset
        
        Returns validation results with errors and suggestions
        """
        self.errors = []
        self.corrections = {}
        
        results = {
            "total_records": len(df),
            "valid_records": 0,
            "invalid_records": 0,
            "warnings": 0,
            "errors": [],
            "corrections": {},
            "quality_score": 0.0,
            "detected_countries": set(),
            "detected_columns": {},
        }
        
        # Analyze columns
        for col in df.columns:
            results["detected_columns"][col] = self._detect_column_type(df[col])
        
        # Validate each row
        invalid_count = 0
        for idx, row in df.iterrows():
            row_errors = self._validate_row(idx, row, validation_rules or {})
            if row_errors:
                invalid_count += 1
                results["errors"].extend(row_errors)
                self.errors.extend(row_errors)
        
        results["valid_records"] = len(df) - invalid_count
        results["invalid_records"] = invalid_count
        
        # Generate corrections
        self._generate_corrections(df)
        results["corrections"] = self.corrections
        
        # Calculate quality score
        results["quality_score"] = self._calculate_quality_score(results)
        results["detected_countries"] = list(results["detected_countries"])
        
        return results
    
    def _validate_row(
        self,
        row_number: int,
        row: pd.Series,
        validation_rules: Dict[str, Dict[str, Any]]
    ) -> List[ValidationError]:
        """Validate single row"""
        errors = []
        
        for field_name, value in row.items():
            # Check for required fields
            if pd.isna(value) or str(value).strip() == "":
                errors.append(ValidationError(
                    row_number=row_number,
                    field_name=field_name,
                    error_type="required_field",
                    error_message=f"Required field '{field_name}' is empty",
                    severity="error",
                    current_value=value
                ))
                continue
            
            value_str = str(value).strip()
            
            # Phone validation
            if field_name.lower() in ["phone", "phone_number", "mobile", "contact"]:
                country = row.get("country", None)
                errors.extend(self._validate_phone(row_number, field_name, value_str, country))
            
            # Date validation
            elif field_name.lower() in ["date", "order_date", "transaction_date", "timestamp", "created_at", "updated_at"]:
                errors.extend(self._validate_date(row_number, field_name, value_str))
            
            # Email validation
            elif field_name.lower() in ["email", "email_address", "contact_email"]:
                errors.extend(self._validate_email(row_number, field_name, value_str))
            
            # Order ID validation
            elif field_name.lower() in ["order_id", "order_number", "transaction_id", "ref_id"]:
                errors.extend(self._validate_order_id(row_number, field_name, value_str))
            
            # Payment mode validation
            elif field_name.lower() in ["payment_mode", "payment_method", "payment_type"]:
                errors.extend(self._validate_payment_mode(row_number, field_name, value_str))
            
            # Amount validation
            elif field_name.lower() in ["amount", "total_amount", "price", "value"]:
                errors.extend(self._validate_amount(row_number, field_name, value_str))
            
            # Country validation
            elif field_name.lower() in ["country", "country_code", "country_name"]:
                errors.extend(self._validate_country(row_number, field_name, value_str))
            
            # Apply custom rules
            if field_name in validation_rules:
                rule = validation_rules[field_name]
                errors.extend(self._apply_custom_rule(row_number, field_name, value_str, rule))
        
        return errors
    
    def _validate_phone(self, row_number: int, field_name: str, phone: str, country: Optional[str] = None) -> List[ValidationError]:
        """Validate phone number"""
        errors = []
        
        is_valid, error_msg = PhoneValidator.validate(phone, country)
        if not is_valid:
            detected_country = PhoneValidator.detect_country(phone)
            errors.append(ValidationError(
                row_number=row_number,
                field_name=field_name,
                error_type="phone_format",
                error_message=error_msg or "Invalid phone format",
                severity="error",
                current_value=phone,
                detected_country=detected_country
            ))
        
        return errors
    
    def _validate_date(self, row_number: int, field_name: str, date_str: str) -> List[ValidationError]:
        """Validate date"""
        errors = []
        
        is_valid, error_msg, detected_format = DateValidator.validate(date_str)
        if not is_valid:
            errors.append(ValidationError(
                row_number=row_number,
                field_name=field_name,
                error_type="date_format",
                error_message=error_msg or "Invalid date format",
                severity="error",
                current_value=date_str
            ))
        
        return errors
    
    def _validate_email(self, row_number: int, field_name: str, email: str) -> List[ValidationError]:
        """Validate email"""
        errors = []
        
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            errors.append(ValidationError(
                row_number=row_number,
                field_name=field_name,
                error_type="email_format",
                error_message="Invalid email format",
                severity="error",
                current_value=email
            ))
        
        return errors
    
    def _validate_order_id(self, row_number: int, field_name: str, order_id: str) -> List[ValidationError]:
        """Validate order ID"""
        errors = []
        
        # Order ID should be alphanumeric, possibly with hyphens/underscores
        if not re.match(r"^[a-zA-Z0-9_-]{3,}$", order_id):
            errors.append(ValidationError(
                row_number=row_number,
                field_name=field_name,
                error_type="order_id_format",
                error_message="Order ID must be alphanumeric (at least 3 characters)",
                severity="warning",
                current_value=order_id
            ))
        
        return errors
    
    def _validate_payment_mode(self, row_number: int, field_name: str, mode: str) -> List[ValidationError]:
        """Validate payment mode"""
        errors = []
        
        valid_modes = ["credit_card", "debit_card", "upi", "net_banking", "cash", "check", "bank_transfer", "wallet", "cryptocurrency"]
        mode_lower = mode.lower().strip()
        
        if mode_lower not in valid_modes:
            errors.append(ValidationError(
                row_number=row_number,
                field_name=field_name,
                error_type="payment_mode",
                error_message=f"Payment mode must be one of: {', '.join(valid_modes)}",
                severity="error",
                current_value=mode
            ))
        
        return errors
    
    def _validate_amount(self, row_number: int, field_name: str, amount_str: str) -> List[ValidationError]:
        """Validate amount"""
        errors = []
        
        try:
            amount = float(amount_str)
            if amount < 0:
                errors.append(ValidationError(
                    row_number=row_number,
                    field_name=field_name,
                    error_type="amount_negative",
                    error_message="Amount cannot be negative",
                    severity="error",
                    current_value=amount_str
                ))
            elif amount == 0:
                errors.append(ValidationError(
                    row_number=row_number,
                    field_name=field_name,
                    error_type="amount_zero",
                    error_message="Amount cannot be zero",
                    severity="warning",
                    current_value=amount_str
                ))
        except ValueError:
            errors.append(ValidationError(
                row_number=row_number,
                field_name=field_name,
                error_type="amount_format",
                error_message="Amount must be a valid number",
                severity="error",
                current_value=amount_str
            ))
        
        return errors
    
    def _validate_country(self, row_number: int, field_name: str, country: str) -> List[ValidationError]:
        """Validate country code/name"""
        errors = []
        
        valid_countries = {
            "IN": "India", "SG": "Singapore", "US": "USA", "UK": "United Kingdom",
            "CA": "Canada", "AU": "Australia", "DE": "Germany", "FR": "France",
            "JP": "Japan", "NZ": "New Zealand", "ID": "Indonesia", "MY": "Malaysia"
        }
        
        country_upper = country.upper().strip()
        
        if country_upper not in valid_countries and country not in valid_countries.values():
            errors.append(ValidationError(
                row_number=row_number,
                field_name=field_name,
                error_type="country_invalid",
                error_message="Country code or name not recognized",
                severity="warning",
                current_value=country
            ))
        
        return errors
    
    def _apply_custom_rule(self, row_number: int, field_name: str, value: str, rule: Dict[str, Any]) -> List[ValidationError]:
        """Apply custom validation rule"""
        errors = []
        
        if rule.get("type") == "regex":
            pattern = rule.get("pattern")
            if pattern and not re.match(pattern, value):
                errors.append(ValidationError(
                    row_number=row_number,
                    field_name=field_name,
                    error_type="regex_mismatch",
                    error_message=rule.get("message", f"Value does not match pattern {pattern}"),
                    severity=rule.get("severity", "error"),
                    current_value=value,
                    validation_rule=rule.get("name")
                ))
        
        elif rule.get("type") == "enum":
            allowed_values = rule.get("values", [])
            if value.lower() not in [v.lower() for v in allowed_values]:
                errors.append(ValidationError(
                    row_number=row_number,
                    field_name=field_name,
                    error_type="enum_mismatch",
                    error_message=f"Value must be one of: {', '.join(allowed_values)}",
                    severity=rule.get("severity", "error"),
                    current_value=value,
                    validation_rule=rule.get("name")
                ))
        
        elif rule.get("type") == "length":
            min_len = rule.get("min", 0)
            max_len = rule.get("max", float('inf'))
            if not (min_len <= len(value) <= max_len):
                errors.append(ValidationError(
                    row_number=row_number,
                    field_name=field_name,
                    error_type="length_mismatch",
                    error_message=f"Length must be between {min_len} and {max_len}",
                    severity=rule.get("severity", "error"),
                    current_value=value,
                    validation_rule=rule.get("name")
                ))
        
        return errors
    
    def _detect_column_type(self, series: pd.Series) -> str:
        """Auto-detect column data type"""
        # Remove null values
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return "unknown"
        
        # Check if numeric
        try:
            pd.to_numeric(non_null)
            return "numeric"
        except (ValueError, TypeError):
            pass
        
        # Check if date
        try:
            pd.to_datetime(non_null)
            return "date"
        except (ValueError, TypeError):
            pass
        
        # Check if boolean
        if non_null.astype(str).str.lower().isin(["true", "false", "yes", "no", "1", "0"]).all():
            return "boolean"
        
        return "string"
    
    def _calculate_quality_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall data quality score"""
        if results["total_records"] == 0:
            return 0.0
        
        # Valid records contribute to score
        valid_percentage = (results["valid_records"] / results["total_records"]) * 100
        
        # Completeness
        completeness = 100 - (results.get("missing_count", 0) / (results["total_records"] * len(results["detected_columns"])) * 100)
        
        # Quality score
        quality = (valid_percentage * 0.6) + (completeness * 0.4)
        
        return min(100.0, max(0.0, quality))
    
    def _generate_corrections(self, df: pd.DataFrame):
        """Generate correction suggestions"""
        for idx, row in df.iterrows():
            corrections_for_row = {}
            
            for field_name, value in row.items():
                if pd.isna(value) or str(value).strip() == "":
                    continue
                
                value_str = str(value).strip()
                
                # Phone corrections
                if field_name.lower() in ["phone", "phone_number", "mobile"]:
                    country = row.get("country", None)
                    suggested, confidence = PhoneValidator.suggest_correction(value_str, country)
                    if suggested and confidence > 0:
                        corrections_for_row[field_name] = (suggested, confidence)
                
                # Date corrections
                elif field_name.lower() in ["date", "order_date", "transaction_date"]:
                    suggested, confidence = DateValidator.suggest_correction(value_str)
                    if suggested and confidence > 0:
                        corrections_for_row[field_name] = (suggested, confidence)
            
            if corrections_for_row:
                self.corrections[idx] = corrections_for_row
