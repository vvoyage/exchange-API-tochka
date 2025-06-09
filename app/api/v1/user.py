from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Union
from app.models.base import get_db
from app.core.security import verify_api_key
from app.schemas.order import LimitOrderBody, MarketOrderBody, CreateOrderResponse, LimitOrder, MarketOrder
from app.services import order_service, balance_service

router = APIRouter()

@router.get("/balance", response_model=Dict[str, int])
async def get_balances(
    user_id: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получение балансов пользователя"""
    return await balance_service.get_user_balances(db, user_id)

@router.post("/order", response_model=CreateOrderResponse)
async def create_order(
    order: Union[LimitOrderBody, MarketOrderBody],
    user_id: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Создание ордера"""
    return await order_service.create_order(db, user_id, order)

@router.get("/order", response_model=List[Union[LimitOrder, MarketOrder]])
async def list_orders(
    user_id: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получение списка активных ордеров пользователя"""
    return await order_service.get_user_orders(db, user_id)

@router.get("/order/{order_id}", response_model=Union[LimitOrder, MarketOrder])
async def get_order(
    order_id: str,
    user_id: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получение информации об ордере"""
    return await order_service.get_order(db, order_id, user_id)

@router.delete("/order/{order_id}")
async def cancel_order(
    order_id: str,
    user_id: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Отмена ордера"""
    return await order_service.cancel_order(db, order_id, user_id)