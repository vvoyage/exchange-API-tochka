from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.balance import Balance
from app.services import user_service, instrument_service
from typing import Dict
import logging

async def get_user_balances(db: Session, user_id: str) -> Dict[str, int]:
    """Получение балансов пользователя"""
    # Проверяем существование пользователя
    await user_service.get_user(db, user_id)
    
    balances = db.query(Balance).filter(Balance.user_id == user_id).all()
    return {balance.ticker: balance.amount for balance in balances}

async def deposit(db: Session, user_id: str, ticker: str, amount: int):
    """Пополнение баланса"""
    logger = logging.getLogger(__name__)
    logger.debug(f"Depositing {amount} {ticker} for user {user_id}")

    if amount <= 0:
        logger.error(f"Invalid deposit amount: {amount}")
        raise HTTPException(status_code=400, detail="Сумма должна быть положительной")
    
    # Проверяем существование пользователя и инструмента
    await user_service.get_user(db, user_id)
    await instrument_service.get_instrument(db, ticker)
    
    balance = db.query(Balance).filter(
        Balance.user_id == user_id,
        Balance.ticker == ticker
    ).first()
    
    if balance:
        logger.debug(f"Updating existing balance: {balance.amount} + {amount} = {balance.amount + amount} {ticker}")
        balance.amount += amount
    else:
        logger.debug(f"Creating new balance: {amount} {ticker}")
        balance = Balance(user_id=user_id, ticker=ticker, amount=amount)
        db.add(balance)
    
    try:
        db.commit()
        db.refresh(balance)
        logger.debug(f"Successfully deposited {amount} {ticker}. New balance: {balance.amount}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to deposit: {str(e)}")
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