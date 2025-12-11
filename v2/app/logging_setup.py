import logging
import sys
from logging.handlers import RotatingFileHandler
from ecs_logging import StdlibFormatter
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "mobypark_api.log"

def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    if logger.hasHandlers():
        logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StdlibFormatter())
    logger.addHandler(console_handler)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10485760, # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(StdlibFormatter())
    logger.addHandler(file_handler)