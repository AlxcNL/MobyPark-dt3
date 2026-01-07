import json
import logging
from os import makedirs
from datetime import date, datetime, timezone

LOG_DIR = "app/logs"

class DefaultContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "endpoint"):
            record.endpoint = None
        if not hasattr(record, "httpcode"):
            record.httpcode = None
        return True

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(timespec="milliseconds"),
            "log_level": record.levelname,
            "endpoint": record.endpoint,
            "httpcode": record.httpcode,
            "message": record.getMessage(),
        }
        return json.dumps(data, ensure_ascii=False)

def setup_logging(log_level):
    makedirs(LOG_DIR, exist_ok=True)

    today = date.today().isoformat()
    logfile = f"{LOG_DIR}/mobipark_api_{today}.log"

    handler = logging.FileHandler(logfile)
    handler.setLevel(log_level)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers = [handler]  # simpel: alleen file logging
    root.addFilter(DefaultContextFilter())

logger = logging.getLogger("mobypark")

def log_event(level, endpoint: str, httpcode: int, msg: str):
    logger.log(level, msg, extra={"endpoint": endpoint, "httpcode": httpcode})
