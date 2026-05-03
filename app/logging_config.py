import logging
import sys

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
logger.propagate = True

if not logger.handlers:
    log_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("app.log")

    stream_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    stream_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)