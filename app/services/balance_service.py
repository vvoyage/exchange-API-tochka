from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.balance import Balance
from app.services import user_service, instrument_service
from typing import Dict

async def get_user_balances(db: Session, user_id: str) -> Dict[str, int]:
    """Получение балансов пользователя"""
    # Проверяем существование пользователя
    await user_service.get_user(db, user_id)
    
    balances = db.query(Balance).filter(Balance.user_id == user_id).all()
    return {balance.ticker: balance.amount for balance in balances}

async def deposit(db: Session, user_id: str, ticker: str, amount: int):
    """Пополнение баланса"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма должна быть положительной")
    
    # Проверяем существование пользователя и инструмента
    await user_service.get_user(db, user_id)
    await instrument_service.get_instrument(db, ticker)
    
    balance = db.query(Balance).filter(
        Balance.user_id == user_id,
        Balance.ticker == ticker
    ).first()
    
    if balance:
        balance.amount += amount
    else:
        balance = Balance(user_id=user_id, ticker=ticker, amount=amount)
        db.add(balance)
    
    try:
        db.commit()
        db.refresh(balance)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при пополнении баланса")
    
    return {"success": True}

async def withdraw(db: Session, user_id: str, ticker: str, amount: int):
    """Списание с баланса"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма должна быть положительной")
    
    # Проверяем существование пользователя и инструмента
    await user_service.get_user(db, user_id)
    await instrument_service.get_instrument(db, ticker)
    
    balance = db.query(Balance).filter(
        Balance.user_id == user_id,
        Balance.ticker == ticker
    ).first()
    
    if not balance or balance.amount < amount:
        raise HTTPException(status_code=400, detail="Недостаточно средств")
    
    balance.amount -= amount
    
    try:
        db.commit()
        db.refresh(balance)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при списании с баланса")
    
    return {"success": True}

async def check_balance(db: Session, user_id: str, ticker: str, amount: int) -> bool:
    """Проверка достаточности средств"""
    balance = db.query(Balance).filter(
        Balance.user_id == user_id,
        Balance.ticker == ticker
    ).first()
    
    return balance is not None and balance.amount >= amount 