"""
Date and time format validation
"""
from datetime import datetime, date
from typing import Tuple, Optional, List
import re


class DateValidator:
    """Date and time format validator"""
    
    # Common date formats
    COMMON_FORMATS = [
        "%Y-%m-%d",           # 2025-01-15
        "%d-%m-%Y",           # 15-01-2025
        "%m-%d-%Y",           # 01-15-2025
        "%Y/%m/%d",           # 2025/01/15
        "%d/%m/%Y",           # 15/01/2025
        "%m/%d/%Y",           # 01/15/2025
        "%Y.%m.%d",           # 2025.01.15
        "%d.%m.%Y",           # 15.01.2025
        "%Y%m%d",             # 20250115
        "%d%m%Y",             # 15012025
        "%B %d, %Y",          # January 15, 2025
        "%b %d, %Y",          # Jan 15, 2025
        "%d %B %Y",           # 15 January 2025
        "%d %b %Y",           # 15 Jan 2025
        "%A, %B %d, %Y",      # Monday, January 15, 2025
        "%a, %b %d, %Y",      # Mon, Jan 15, 2025
    ]
    
    DATETIME_FORMATS = [
        "%Y-%m-%d %H:%M:%S",           # 2025-01-15 14:30:45
        "%Y-%m-%d %H:%M",             # 2025-01-15 14:30
        "%Y-%m-%dT%H:%M:%S",          # 2025-01-15T14:30:45
        "%Y-%m-%dT%H:%M:%SZ",         # 2025-01-15T14:30:45Z
        "%Y-%m-%dT%H:%M:%S.%f",       # 2025-01-15T14:30:45.000000
        "%Y-%m-%dT%H:%M:%S.%fZ",      # 2025-01-15T14:30:45.000000Z
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
    ]
    
    @classmethod
    def validate(cls, date_str: str, date_format: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate date string
        
        Returns: (is_valid, error_message, detected_format)
        """
        if not date_str:
            return False, "Date is required", None
        
        date_str = str(date_str).strip()
        
        # Try specific format if provided
        if date_format:
            try:
                datetime.strptime(date_str, date_format)
                return True, None, date_format
            except ValueError:
                return False, f"Date does not match format {date_format}", None
        
        # Try datetime formats first
        for fmt in cls.DATETIME_FORMATS:
            try:
                parsed = datetime.strptime(date_str, fmt)
                # Check if year is reasonable (1900-2100)
                if 1900 <= parsed.year <= 2100:
                    return True, None, fmt
            except ValueError:
                continue
        
        # Try date formats
        for fmt in cls.COMMON_FORMATS:
            try:
                parsed = datetime.strptime(date_str, fmt)
                # Check if year is reasonable (1900-2100)
                if 1900 <= parsed.year <= 2100:
                    return True, None, fmt
            except ValueError:
                continue
        
        # Check for invalid date patterns
        error = cls._check_invalid_patterns(date_str)
        if error:
            return False, error, None
        
        return False, "Date format not recognized", None
    
    @classmethod
    def suggest_correction(cls, date_str: str) -> Tuple[Optional[str], float]:
        """
        Suggest correction for invalid date
        
        Returns: (suggested_date, confidence_score)
        """
        if not date_str:
            return None, 0.0
        
        date_str = str(date_str).strip()
        
        # Check for common mistakes
        corrections = []
        
        # Fix 1: Swapped day and month (31/12/2025 vs 2025/31/12)
        parts = re.split(r"[-/\s]", date_str)
        if len(parts) >= 3:
            # Try swapping first two parts
            swapped = f"{parts[1]}{cls._get_separator(date_str)}{parts[0]}{cls._get_separator(date_str)}{parts[2]}"
            is_valid, _, _ = cls.validate(swapped)
            if is_valid:
                corrections.append((swapped, 90))
            
            # Try other permutations
            for perm in [[1, 0, 2], [2, 1, 0], [0, 2, 1]]:
                perm_str = f"{parts[perm[0]]}{cls._get_separator(date_str)}{parts[perm[1]]}{cls._get_separator(date_str)}{parts[perm[2]]}"
                is_valid, _, _ = cls.validate(perm_str)
                if is_valid:
                    confidence = 80 if perm == [1, 0, 2] else 70
                    corrections.append((perm_str, confidence))
        
        # Fix 2: Wrong separator
        separators = ["-", "/", "."]
        for sep in separators:
            if sep not in date_str:
                corrected = sep.join(parts[:3]) if len(parts) >= 3 else None
                if corrected:
                    is_valid, _, _ = cls.validate(corrected)
                    if is_valid:
                        corrections.append((corrected, 75))
        
        # Fix 3: 2-digit year
        if len(parts[-1]) == 2:
            year = f"20{parts[-1]}"
            corrected = f"{parts[0]}{cls._get_separator(date_str)}{parts[1]}{cls._get_separator(date_str)}{year}"
            is_valid, _, _ = cls.validate(corrected)
            if is_valid:
                corrections.append((corrected, 85))
        
        # Return best suggestion
        if corrections:
            corrections.sort(key=lambda x: x[1], reverse=True)
            return corrections[0]
        
        return None, 0.0
    
    @classmethod
    def parse_date(cls, date_str: str, date_format: Optional[str] = None) -> Optional[datetime]:
        """Parse date string to datetime object"""
        is_valid, _, fmt = cls.validate(date_str, date_format)
        if is_valid and fmt:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                return None
        return None
    
    @classmethod
    def _check_invalid_patterns(cls, date_str: str) -> Optional[str]:
        """Check for obvious invalid date patterns"""
        parts = re.split(r"[-/\s]", date_str)
        
        if len(parts) < 3:
            return "Date must have at least 3 parts (day, month, year)"
        
        try:
            nums = [int(p) for p in parts[:3]]
        except ValueError:
            return "Date contains non-numeric values"
        
        # Check for invalid day (>31)
        for num in nums[:2]:
            if num > 31:
                return f"Invalid day/month value: {num}"
        
        # Check for invalid month (>12)
        for num in nums[:2]:
            if num > 12 and num < 30:
                return f"Invalid month value: {num}"
        
        return None
    
    @classmethod
    def _get_separator(cls, date_str: str) -> str:
        """Extract date separator from string"""
        for sep in ["-", "/", ".", " "]:
            if sep in date_str:
                return sep
        return "-"
    
    @classmethod
    def normalize_date(cls, date_str: str, target_format: str = "%Y-%m-%d") -> Optional[str]:
        """Normalize date to target format"""
        parsed = cls.parse_date(date_str)
        if parsed:
            return parsed.strftime(target_format)
        return None
