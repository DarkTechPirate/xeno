"""
Phone number validation with country-specific rules
"""
import re
from typing import Dict, Tuple, Optional


class PhoneValidator:
    """Country-specific phone number validator"""
    
    # Country-specific phone patterns
    PHONE_PATTERNS = {
        "IN": {
            "pattern": r"^[6-9]\d{9}$",
            "length": 10,
            "prefix": ["6", "7", "8", "9"],
            "format": "10 digits starting with 6-9",
            "formatted": "+91-{}-{}-{}",
            "country_code": "+91",
        },
        "SG": {
            "pattern": r"^[6-9]\d{7}$",
            "length": 8,
            "prefix": ["6", "8", "9"],
            "format": "8 digits starting with 6, 8, or 9",
            "country_code": "+65",
        },
        "US": {
            "pattern": r"^[2-9]\d{9}$",
            "length": 10,
            "prefix": ["2", "3", "4", "5", "6", "7", "8", "9"],
            "format": "10 digits (NPA-NXX-XXXX)",
            "country_code": "+1",
        },
        "UK": {
            "pattern": r"^0[1-9]\d{8,9}$|^[2-9]\d{9,10}$",
            "length": [10, 11],
            "format": "10-11 digits starting with 0 or 2-9",
            "country_code": "+44",
        },
        "CA": {
            "pattern": r"^[2-9]\d{9}$",
            "length": 10,
            "format": "10 digits (NPA-NXX-XXXX)",
            "country_code": "+1",
        },
        "AU": {
            "pattern": r"^[2-9]\d{8}$",
            "length": 9,
            "format": "9 digits starting with 2-9",
            "country_code": "+61",
        },
        "DE": {
            "pattern": r"^[1-9]\d{2,13}$",
            "length": [4, 15],
            "format": "4-15 digits",
            "country_code": "+49",
        },
        "FR": {
            "pattern": r"^[1-9]\d{8}$",
            "length": 9,
            "format": "9 digits",
            "country_code": "+33",
        },
        "JP": {
            "pattern": r"^[0-9]{10,11}$",
            "length": [10, 11],
            "format": "10-11 digits",
            "country_code": "+81",
        },
        "NZ": {
            "pattern": r"^[2-9]\d{7,8}$",
            "length": [9, 10],
            "format": "9-10 digits",
            "country_code": "+64",
        },
        "DEFAULT": {
            "pattern": r"^\d{7,15}$",
            "length": [7, 15],
            "format": "7-15 digits",
        }
    }
    
    @classmethod
    def validate(cls, phone: str, country_code: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate phone number for given country
        
        Returns: (is_valid, error_message)
        """
        if not phone:
            return False, "Phone number is required"
        
        # Clean phone number
        cleaned = cls._clean_phone(phone)
        
        if not cleaned:
            return False, "Phone number contains no digits"
        
        # Get country pattern
        if country_code and country_code.upper() in cls.PHONE_PATTERNS:
            pattern_config = cls.PHONE_PATTERNS[country_code.upper()]
        else:
            pattern_config = cls.PHONE_PATTERNS["DEFAULT"]
        
        # Validate against pattern
        pattern = pattern_config.get("pattern")
        if pattern and not re.match(pattern, cleaned):
            return False, f"Invalid format for {country_code}. Expected: {pattern_config.get('format')}"
        
        return True, None
    
    @classmethod
    def detect_country(cls, phone: str) -> Optional[str]:
        """Detect country from phone number"""
        cleaned = cls._clean_phone(phone)
        
        # Try to match against known patterns
        for country, config in cls.PHONE_PATTERNS.items():
            if country == "DEFAULT":
                continue
            pattern = config.get("pattern")
            if pattern and re.match(pattern, cleaned):
                return country
        
        return None
    
    @classmethod
    def suggest_correction(cls, phone: str, country_code: Optional[str] = None) -> Tuple[Optional[str], float]:
        """
        Suggest correction for invalid phone number
        
        Returns: (suggested_phone, confidence_score)
        """
        if not phone:
            return None, 0.0
        
        original = phone
        cleaned = cls._clean_phone(phone)
        
        if not cleaned:
            return None, 0.0
        
        # Detect country if not provided
        if not country_code:
            country_code = cls.detect_country(cleaned)
        
        if not country_code:
            country_code = "DEFAULT"
        
        config = cls.PHONE_PATTERNS.get(country_code, cls.PHONE_PATTERNS["DEFAULT"])
        
        # Try different corrections
        corrections = []
        
        # Fix 1: Remove leading zeros if not applicable
        if cleaned.startswith("0"):
            corrected = cleaned[1:]
            is_valid, _ = cls.validate(corrected, country_code)
            if is_valid:
                corrections.append((corrected, 85))  # 85% confidence
        
        # Fix 2: Add leading digit
        if len(cleaned) == config.get("length", 10) - 1:
            for prefix in config.get("prefix", ["1", "6", "7", "8", "9"]):
                corrected = prefix + cleaned
                is_valid, _ = cls.validate(corrected, country_code)
                if is_valid:
                    corrections.append((corrected, 80))
        
        # Fix 3: Remove extra digits
        if isinstance(config.get("length"), int) and len(cleaned) > config["length"]:
            corrected = cleaned[:config["length"]]
            is_valid, _ = cls.validate(corrected, country_code)
            if is_valid:
                corrections.append((corrected, 70))
        
        # Return best suggestion
        if corrections:
            corrections.sort(key=lambda x: x[1], reverse=True)
            return corrections[0]
        
        return None, 0.0
    
    @classmethod
    def format_phone(cls, phone: str, country_code: Optional[str] = None) -> str:
        """Format phone number according to country standard"""
        cleaned = cls._clean_phone(phone)
        
        if not country_code:
            country_code = cls.detect_country(cleaned)
        
        if not country_code:
            return cleaned
        
        config = cls.PHONE_PATTERNS.get(country_code)
        if not config:
            return cleaned
        
        # Format examples: +91-XXXXX-XXXXX, +1-NPA-NXX-XXXX, etc.
        cc = config.get("country_code", "")
        
        if country_code == "IN":
            return f"{cc}-{cleaned[:5]}-{cleaned[5:]}"
        elif country_code == "US" or country_code == "CA":
            return f"{cc}-({cleaned[:3]})-{cleaned[3:6]}-{cleaned[6:]}"
        
        return f"{cc}{cleaned}"
    
    @classmethod
    def _clean_phone(cls, phone: str) -> str:
        """Remove non-digit characters"""
        if not phone:
            return ""
        cleaned = re.sub(r"\D", "", str(phone))
        # Remove leading country code if present
        if cleaned.startswith("1") and len(cleaned) > 10:
            cleaned = cleaned[1:]
        return cleaned
