import sys
from loguru import logger
import os

def setup_logger():
    """Initialize the Loguru logger."""
    logger.remove()
    logger.add(
        sys.stdout, 
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Add file logger
    logger.add("logs/neuralradar.log", rotation="10 MB", retention="1 week", level="DEBUG")
    logger.info("Logger initialized.")
