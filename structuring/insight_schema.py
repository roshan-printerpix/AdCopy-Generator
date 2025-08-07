"""
Insight Schema Module
Defines expected JSON structure and performs validation.
"""

from typing import Dict, Any, Optional

INSIGHT_SCHEMA = {
    "INSIGHT": str,
    "RESULTS": str,
    "LIMITATIONS_CONTEXT": str,
    "DIFFERENCE_SCORE": int
}

REQUIRED_FIELDS = ["INSIGHT", "RESULTS", "LIMITATIONS_CONTEXT", "DIFFERENCE_SCORE"]

def validate_insight_structure(insight_data):
    """
    Validate that insight data matches expected schema.
    
    Args:
        insight_data (dict): Structured insight data
    
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    
    if not isinstance(insight_data, dict):
        errors.append("Insight data must be a dictionary")
        return False, errors
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in insight_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate field types
    for field, expected_type in INSIGHT_SCHEMA.items():
        if field in insight_data:
            if not isinstance(insight_data[field], expected_type):
                errors.append(f"Field {field} must be of type {expected_type.__name__}")
    
    # Validate difference score range
    if "DIFFERENCE_SCORE" in insight_data:
        score = insight_data["DIFFERENCE_SCORE"]
        if not (0 <= score <= 100):
            errors.append("DIFFERENCE_SCORE must be between 0 and 100")
    
    return len(errors) == 0, errors

def sanitize_insight_data(insight_data):
    """
    Clean and sanitize insight data.
    
    Args:
        insight_data (dict): Raw insight data
    
    Returns:
        dict: Sanitized insight data
    """
    sanitized = {}
    
    for field in REQUIRED_FIELDS:
        if field in insight_data:
            value = insight_data[field]
            
            if field == "DIFFERENCE_SCORE":
                # Ensure score is integer and within range
                try:
                    score = int(value)
                    sanitized[field] = max(0, min(100, score))
                except (ValueError, TypeError):
                    sanitized[field] = 0
            else:
                # Clean string fields
                sanitized[field] = str(value).strip()
    
    return sanitized