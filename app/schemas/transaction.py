from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class Transaction(BaseModel):
    """Схема транзакции"""
    id: UUID
    ticker: str
    buyer_id: UUID
    seller_id: UUID
    amount: int
    price: int
    timestamp: datetime

    class Config:
        from_attributes = True 