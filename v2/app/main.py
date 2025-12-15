import logging

from fastapi import FastAPI
from app.logging_setup import setup_logging 
from app.endpoints import oauth, vehicles, parking_lots, reservations, sessions, payments, billing, businesses

setup_logging()
app = FastAPI(title="MobyPark API v2")
app.include_router(oauth.router)
app.include_router(vehicles.router)
app.include_router(parking_lots.router)
app.include_router(reservations.router)
app.include_router(sessions.router)
app.include_router(payments.router)
app.include_router(billing.router)
app.include_router(businesses.router)

@app.get("/")
async def root():
    logging.info("Root endpoint accessed")
    return {"message": "Welcome to MobyPark API v2"}