from fastapi import FastAPI
from app.endpoints import oauth
from app.endpoints import parking_lots

app = FastAPI(title="MobyPark API v2")
app.include_router(oauth.router)
app.include_router(parking_lots.router)

@app.get("/")
async def root():
    return {"message": "Welcome to MobyPark API v2"}