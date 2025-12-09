import logging
import sys
from fastapi import FastAPI
from ecs_logging import StdlibFormatter

from app.endpoints import oauth, vehicles, parking_lots, reservations, sessions, payments, billing

# Setup logging voor ELK-stack.
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    formatter = StdlibFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
setup_logging()

app = FastAPI(title="MobyPark API v2")
app.include_router(oauth.router)
app.include_router(vehicles.router)
app.include_router(parking_lots.router)
app.include_router(reservations.router)
app.include_router(sessions.router)
app.include_router(payments.router)
app.include_router(billing.router)

@app.get("/")
async def root():
    logging.info("Dummy LOG ASAH")
    return {"message": "Welcome to MobyPark API v2"}
