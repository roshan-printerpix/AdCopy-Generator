"""
Logging utilities for the Ad-Creative Insight Pipeline.
"""

import logging
import os
from datetime import datetime

def setup_logger(name="pipeline", level=None, log_file=None):
    """
    Set up a logger with console and file handlers.
    
    Args:
        name (str): Logger name
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file (str): Path to log file
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get level from environment or use default
    level = level or os.getenv('LOG_LEVEL', 'INFO')
    log_file = log_file or os.getenv('LOG_FILE', 'pipeline.log')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def log_pipeline_step(logger, step_name, start_time=None, end_time=None, **kwargs):
    """
    Log pipeline step execution with timing and metadata.
    
    Args:
        logger: Logger instance
        step_name (str): Name of the pipeline step
        start_time (datetime): Step start time
        end_time (datetime): Step end time
        **kwargs: Additional metadata to log
    """
    if start_time and end_time:
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Step '{step_name}' completed in {duration:.2f} seconds")
    else:
        logger.info(f"Step '{step_name}' executed")
    
    # Log additional metadata
    for key, value in kwargs.items():
        logger.info(f"  {key}: {value}")