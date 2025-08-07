"""
General helper utilities for the pipeline.
"""

import time
import uuid
from datetime import datetime, timezone
from functools import wraps

def generate_uuid():
    """
    Generate a UUID string.
    
    Returns:
        str: UUID string
    """
    return str(uuid.uuid4())

def get_current_timestamp():
    """
    Get current UTC timestamp.
    
    Returns:
        datetime: Current UTC timestamp
    """
    return datetime.now(timezone.utc)

def get_current_timestamp_iso():
    """
    Get current UTC timestamp as ISO string.
    
    Returns:
        str: Current UTC timestamp in ISO format
    """
    return get_current_timestamp().isoformat()

def retry_on_failure(max_retries=3, delay=1.0, backoff=2.0):
    """
    Decorator to retry function calls on failure.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        delay (float): Initial delay between retries in seconds
        backoff (float): Backoff multiplier for delay
    
    Returns:
        function: Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay} seconds...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print(f"All {max_retries + 1} attempts failed.")
            
            raise last_exception
        
        return wrapper
    return decorator

def chunk_list(lst, chunk_size):
    """
    Split a list into chunks of specified size.
    
    Args:
        lst (list): List to chunk
        chunk_size (int): Size of each chunk
    
    Yields:
        list: Chunks of the original list
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def safe_get(dictionary, key, default=None):
    """
    Safely get a value from a dictionary.
    
    Args:
        dictionary (dict): Dictionary to get value from
        key: Key to look up
        default: Default value if key not found
    
    Returns:
        Value from dictionary or default
    """
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default

def truncate_text(text, max_length=100, suffix="..."):
    """
    Truncate text to specified length with suffix.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length of text
        suffix (str): Suffix to add if truncated
    
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def measure_execution_time(func):
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to measure
    
    Returns:
        function: Decorated function that prints execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result
    
    return wrapper