from fastapi import FastAPI
from app.endpoints import oauth

app = FastAPI(title="MobyPark API v2")
app.include_router(oauth.router)

@app.get("/")
async def root():
    return {"message": "Welcome to MobyPark API v2"}