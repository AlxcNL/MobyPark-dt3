import logging
import os
from datetime import date

LOG_DIR = "/v2/app/logs"

def setup_logging(log_level):
    os.makedirs(LOG_DIR, exist_ok=True)

    today = date.today().isoformat()
    logfile = f"{LOG_DIR}/mobipark_api_{today}.log"

    logging.basicConfig(
        level=log_level,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "endpoint=%(endpoint)s "
            "httpcode=%(httpcode)s "
            "%(message)s"
        ),
        filename=logfile
    )