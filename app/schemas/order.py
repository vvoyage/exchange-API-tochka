from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Direction(str, Enum):
    """Направление ордера"""
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    """Статус ордера"""
    NEW = "NEW"
    EXECUTED = "EXECUTED"
    PARTIALLY_EXECUTED = "PARTIALLY_EXECUTED"
    CANCELLED = "CANCELLED"

class LimitOrderBody(BaseModel):
    """Тело запроса для создания лимитного ордера"""
    direction: Direction
    ticker: str
    qty: int = Field(..., gt=0)
    price: int = Field(..., gt=0)

class MarketOrderBody(BaseModel):
    """Тело запроса для создания рыночного ордера"""
    direction: Direction
    ticker: str
    qty: int = Field(..., gt=0)

class CreateOrderResponse(BaseModel):
    """Ответ на создание ордера"""
    success: bool = True
    order_id: str

class OrderBase(BaseModel):
    """Базовая схема ордера"""
    id: str
    status: OrderStatus
    user_id: str
    timestamp: datetime
    filled: int = 0

class LimitOrder(OrderBase):
    """Схема лимитного ордера"""
    body: LimitOrderBody

    class Config:
        from_attributes = True

class MarketOrder(OrderBase):
    """Схема рыночного ордера"""
    body: MarketOrderBody

    class Config:
        from_attributes = True 