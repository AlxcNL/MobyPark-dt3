from fastapi import APIRouter
from app import models, schemas

router = APIRouter(prefix="", tags=["auth"])  

@router.get("/oauth", response_model=schemas.Message)
async def get_profile():
    return {"message": "This is a placeholder for the user profile endpoint."}