import logging
import os
from .generator import LokiDataGenerator

# Constants
supported_log_levels = ["INFO", "ERROR", "DEBUG"]
logger = logging.getLogger(__name__)


# Functions 
def main():
    # Configure logging with timestamp, level, function name, and message
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Override log level if LDG_LOG_LEVEL environment variable is set
    if "LDG_LOG_LEVEL" in os.environ:
        if os.environ["LDG_LOG_LEVEL"].upper() in supported_log_levels:
            logger.setLevel(os.environ["LDG_LOG_LEVEL"].upper())

    logger.info("Starting Loki Data Generator")

    loki_data_generator = LokiDataGenerator()
    loki_data_generator.run()

    loki_data_generator.stop()

# Entry point
if __name__ == "__main__":
    main()
