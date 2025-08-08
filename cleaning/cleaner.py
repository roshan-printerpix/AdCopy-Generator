"""
Text Cleaner Module
Contains logic to sanitize and normalize raw text content.
"""

import re
from utils.config import Config

def remove_html_tags(text):
    """
    Remove HTML tags from text.
    
    Args:
        text (str): Raw text with HTML tags
    
    Returns:
        str: Clean text without HTML tags
    """
    if not text:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    # Remove HTML entities
    clean_text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', clean_text)
    
    return clean_text

def remove_usernames_and_mentions(text):
    """
    Remove usernames, mentions, and handles from text.
    
    Args:
        text (str): Text containing usernames/mentions
    
    Returns:
        str: Text without usernames/mentions
    """
    if not text:
        return ""
    
    # Remove Reddit usernames (u/username)
    text = re.sub(r'\bu/[A-Za-z0-9_-]+\b', '', text)
    # Remove subreddit mentions (r/subreddit)
    text = re.sub(r'\br/[A-Za-z0-9_-]+\b', '', text)
    # Remove Twitter-style mentions (@username)
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)
    
    return text

def remove_urls(text):
    """
    Remove URLs from text.
    
    Args:
        text (str): Text containing URLs
    
    Returns:
        str: Text without URLs
    """
    if not text:
        return ""
    
    # Remove HTTP/HTTPS URLs
    text = re.sub(r'https?://[^\s]+', '', text)
    # Remove www URLs
    text = re.sub(r'www\.[^\s]+', '', text)
    # Remove Reddit-style URLs
    text = re.sub(r'reddit\.com[^\s]*', '', text)
    
    return text

def remove_emojis_and_symbols(text):
    """
    Remove emojis and unwanted symbols from text.
    
    Args:
        text (str): Text containing emojis/symbols
    
    Returns:
        str: Clean text without emojis/symbols
    """
    if not text:
        return ""
    
    # Remove emojis (basic pattern)
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    text = re.sub(r'[.]{3,}', '...', text)
    
    return text

def truncate_to_paragraphs(text, max_paragraphs=4):
    """
    Truncate text to specified number of paragraphs.
    
    Args:
        text (str): Full text content
        max_paragraphs (int): Maximum number of paragraphs to keep
    
    Returns:
        str: Truncated text
    """
    if not text:
        return ""
    
    # Split by double newlines (paragraph breaks)
    paragraphs = re.split(r'\n\s*\n', text.strip())
    
    # Keep only the first max_paragraphs
    if len(paragraphs) > max_paragraphs:
        paragraphs = paragraphs[:max_paragraphs]
    
    return '\n\n'.join(paragraphs)

def normalize_whitespace(text):
    """
    Normalize whitespace and line breaks.
    
    Args:
        text (str): Text with irregular whitespace
    
    Returns:
        str: Text with normalized whitespace
    """
    if not text:
        return ""
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()

def clean_reddit_specific(text):
    """
    Clean Reddit-specific formatting and content.
    
    Args:
        text (str): Reddit post text
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove "Edit:" lines
    text = re.sub(r'^Edit:.*$', '', text, flags=re.MULTILINE)
    # Remove "Update:" lines
    text = re.sub(r'^Update:.*$', '', text, flags=re.MULTILINE)
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
    # Remove quote markers
    text = re.sub(r'^>', '', text, flags=re.MULTILINE)
    
    return text