import sys
from loguru import logger
import os

def setup_logger():
    """Initialize the Loguru logger."""
    logger.remove()
    if sys.stdout is not None:
        logger.add(
            sys.stdout, 
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
    
    from app.core.paths import get_log_file_path
    log_path = get_log_file_path()
    
    # Add file logger
    logger.add(log_path, rotation="10 MB", retention="1 week", level="DEBUG")
    logger.info("Logger initialized.")
