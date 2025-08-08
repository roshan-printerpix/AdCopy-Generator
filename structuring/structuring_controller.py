"""
Structuring Controller
Connects cleaning module output to structured insight objects.
"""

from . import insight_formatter, insight_schema

def process_cleaned_content(cleaned_content_list):
    """
    Process list of cleaned content into structured insights.
    
    Args:
        cleaned_content_list (list): List of cleaned text content
    
    Returns:
        list: List of validated structured insights
    """
    structured_insights = []
    
    for cleaned_text in cleaned_content_list:
        try:
            insight = structure_single_content(cleaned_text)
            if insight:
                structured_insights.append(insight)
        except Exception as e:
            # Log error and continue processing
            print(f"Error structuring content: {e}")
            continue
    
    return structured_insights

def structure_single_content(cleaned_text):
    """
    Convert single piece of cleaned text into structured insight.
    
    Args:
        cleaned_text (str): Single piece of cleaned text
    
    Returns:
        dict: Validated structured insight or None if invalid
    """
    if not cleaned_text or len(cleaned_text.strip()) < 50:
        return None
    
    # Format using LLM
    raw_insight = insight_formatter.format_insight(cleaned_text)
    
    if not raw_insight:
        return None
    
    # Sanitize data
    sanitized_insight = insight_schema.sanitize_insight_data(raw_insight)
    
    # Validate structure
    is_valid, errors = insight_schema.validate_insight_structure(sanitized_insight)
    
    if not is_valid:
        print(f"Invalid insight structure: {errors}")
        return None
    
    # Add metadata
    sanitized_insight['source_url'] = None  # Will be set if available
    sanitized_insight['source_hash'] = None  # Will be set for deduplication
    sanitized_insight['processing_timestamp'] = None  # Will be set by timestamp utility
    
    return sanitized_insight