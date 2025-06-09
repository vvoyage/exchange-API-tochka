from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.core.security import verify_admin_key
from app.schemas.user import User
from app.schemas.instrument import Instrument
from app.services import user_service, instrument_service, balance_service

router = APIRouter()

@router.delete("/user/{user_id}", response_model=User)
async def delete_user(
    user_id: str,
    _: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    """Удаление пользователя"""
    return await user_service.delete_user(db, user_id)

@router.post("/instrument")
async def add_instrument(
    instrument: Instrument,
    _: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    """Добавление нового инструмента"""
    return await instrument_service.add_instrument(db, instrument)

@router.delete("/instrument/{ticker}")
async def delete_instrument(
    ticker: str,
    _: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    """Удаление инструмента"""
    return await instrument_service.delete_instrument(db, ticker)

@router.post("/balance/deposit")
async def deposit(
    deposit_data: dict,
    _: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    """Пополнение баланса пользователя"""
    return await balance_service.deposit(
        db,
        user_id=deposit_data["user_id"],
        ticker=deposit_data["ticker"],
        amount=deposit_data["amount"]
    )

@router.post("/balance/withdraw")
async def withdraw(
    withdraw_data: dict,
    _: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    """Списание с баланса пользователя"""
    return await balance_service.withdraw(
        db,
        user_id=withdraw_data["user_id"],
        ticker=withdraw_data["ticker"],
        amount=withdraw_data["amount"]
    ) 