import os
import sys
from pathlib import Path
from loguru import logger

# Add the app directory to Python path to enable absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loki_data_generator.generator import LokiDataGenerator
from loki_data_generator.setup import VERSION

# Constants
supported_log_levels = ["INFO", "ERROR", "DEBUG", "WARNING", "CRITICAL"]

def configure_logging():
    """Configure loguru logging with proper format and level."""
    # Remove default handler
    logger.remove()
    
    # Get log level from environment or default to INFO
    log_level = os.environ.get("LDG_LOG_LEVEL", "INFO").upper()
    if log_level not in supported_log_levels:
        log_level = "INFO"
    
    # Add console handler with custom format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Add file handler for persistent logs
    logger.add(
        "logs/loki-data-generator.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )

# Functions 
def main():
    # Configure logging
    configure_logging()
    
    logger.info(f"Loki Data Generator version: {VERSION}")
    logger.info("Starting Loki Data Generator")
    logger.info(f"Log level: {os.environ.get('LDG_LOG_LEVEL', 'INFO')}")

    loki_data_generator = LokiDataGenerator()
    loki_data_generator.run()

    loki_data_generator.stop()

# Entry point
if __name__ == "__main__":
    main()
