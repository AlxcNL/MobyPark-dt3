from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app import models, schemas
from app.security import check_token ,require_admin
from app.dependencies import get_current_user, page_params, PageParams, generate_payment_hash

from datetime import datetime, timezone

router = APIRouter(prefix="", tags=["payments"])
bearer_scheme = HTTPBearer(auto_error=True)

#post a payment for a session
@router.post("/payments", response_model=schemas.MessageWithId)
async def create_payment(
    payment: schemas.PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    check_token(token.credentials)

    # Ensure the session exists and payment_status is 'pending'
    result = await db.execute(
        select(models.Session).where(models.Session.id == payment.sessions_id)
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    #get vehicle info from sessions.id
    result = await db.execute(
        select(models.Vehicle).where(models.Vehicle.id == session.vehicles_id)
    )
    vehicle = result.scalars().first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    new_payment = models.Payment(
        amount=session.cost,
        sessions_id=payment.sessions_id,
        initiator_users_id=current_user.id,
        created_at=datetime.now(timezone.utc),
        hash=generate_payment_hash(str(session.id), vehicle),
        method=payment.method,
        issuer=payment.issuer,
        bank=payment.bank
    )

    # Commit new_payment and update session.payment_status to 'completed'
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    return {"message": f"Payment created with ID {new_payment.id}", "id": new_payment.id}

#update completed_at payment to now by payment_id
@router.put("/payments/{pid}", response_model=schemas.Message)
async def complete_payment(
    pid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    check_token(token.credentials)

    result = await db.execute(
        select(models.Payment).where(models.Payment.id == pid)
    )
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.initiator_users_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to complete this payment")
    if payment.completed_at is not None:
        raise HTTPException(status_code=400, detail="Payment already completed")
    payment.completed_at = datetime.now(timezone.utc)
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return {"message": f"Payment with ID {payment.id} completed"}

#list payments of current user
@router.get("/payments", response_model=List[schemas.Payment])
async def list_payments(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    params: PageParams = Depends(page_params),
):
    check_token(token.credentials)

    result = await db.execute(
        select(models.Payment)
        .where(models.Payment.initiator_users_id == current_user.id)
        .offset(params.offset)
        .limit(params.limit)
    )
    payments = result.scalars().all()
    return payments

# get payment by user id
@router.get("/payments/{uid}", response_model=schemas.Payment)
async def get_payment_by_user_id(
    uid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    check_token(token.credentials)
    require_admin(current_user)

    result = await db.execute(
        select(models.Payment).where(models.Payment.initiator_users_id == uid)
    )
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment