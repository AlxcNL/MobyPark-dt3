from fastapi import FastAPI
from app.endpoints import oauth, vehicles, parking_lots, reservations, sessions, payments

app = FastAPI(title="MobyPark API v2")
app.include_router(oauth.router)
app.include_router(vehicles.router)
app.include_router(parking_lots.router)
app.include_router(reservations.router)
app.include_router(sessions.router)
app.include_router(payments.router)

@app.get("/")
async def root():
    return {"message": "Welcome to MobyPark API v2"}