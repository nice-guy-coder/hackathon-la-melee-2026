import logging
from app.core.logger import setup_logging

# Setup logging for FastAPI
setup_logging()

# Get the FastAPI logger
logger = logging.getLogger("fastapi")
