from pydantic import BaseModel
from datetime import datetime

class Transaction(BaseModel):
    """Схема транзакции"""
    ticker: str
    amount: int
    price: int
    timestamp: datetime

    class Config:
        from_attributes = True 