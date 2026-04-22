# logger_config.py
import logging
import sys

def setup_logging():
    """Configures root logger with a standard formatter and stdout handler."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # Define formatting and handlers here, as detailed in the source
    handler = logging.StreamHandler(sys.stdout)
    # ... handler configuration ...
    if not logger.handlers:
        logger.addHandler(handler)
    # Example: Reduce noise from ASGI server
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)