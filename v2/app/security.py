import hashlib
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, status

def hash_password(password: str):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

TOKEN_TTL = timedelta(minutes=5)
active_tokens: dict[str, tuple[int, datetime]] = {}

def create_token(user_id: int):
    #Generate a token and store it with user_id + issue time.
    token = uuid.uuid4().hex
    active_tokens[token] = (user_id, datetime.now())
    return token

def remove_token(token: str):
    active_tokens.pop(token, None)

def remove_all_tokens_for_user(user_id: int):
    to_delete = [t for t, (uid, _) in active_tokens.items() if uid == user_id]
    for t in to_delete:
        active_tokens.pop(t, None)

def check_token(token: str):
    #Raises HTTPException if invalid/expired.
    record = active_tokens.get(token)
    if not record:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    #Validate token, check expiry.
    user_id, issued_at = record
    if datetime.now() - issued_at > TOKEN_TTL:
        remove_token(token)
        raise HTTPException(status_code=401, detail="Token expired")
    
    #Returns user_id if valid.
    return user_id

def require_admin(user: str):
    if not user or getattr(user, "role", None) != "admin":
        raise HTTPException(status_code=403,detail="Admin privileges required")
    return True