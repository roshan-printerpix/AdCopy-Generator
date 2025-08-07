"""
Cleaning Controller
Takes raw input and returns cleaned text ready for structuring.
"""

from . import cleaner

def process_raw_content(raw_content_list):
    """
    Process a list of raw content through the cleaning pipeline.
    
    Args:
        raw_content_list (list): List of raw text content
    
    Returns:
        list: List of cleaned text ready for structuring
    """
    cleaned_content = []
    
    for raw_text in raw_content_list:
        cleaned_text = clean_single_text(raw_text)
        if cleaned_text:  # Only add non-empty cleaned text
            cleaned_content.append(cleaned_text)
    
    return cleaned_content

def clean_single_text(raw_text):
    """
    Clean a single piece of raw text through all cleaning steps.
    
    Args:
        raw_text (str): Single piece of raw text
    
    Returns:
        str: Cleaned text ready for structuring
    """
    if not raw_text or not isinstance(raw_text, str):
        return None
    
    # Apply all cleaning steps
    text = cleaner.remove_html_tags(raw_text)
    text = cleaner.remove_usernames_and_mentions(text)
    text = cleaner.remove_urls(text)
    text = cleaner.remove_emojis_and_symbols(text)
    text = cleaner.truncate_to_paragraphs(text)
    text = cleaner.normalize_whitespace(text)
    
    # Return None if text is too short after cleaning
    if len(text.strip()) < 50:
        return None
    
    return text.strip()