from pydantic import BaseModel, Field
from uuid import UUID
from typing import Dict

class BalanceResponse(BaseModel):
    """Схема ответа на запрос баланса"""
    __root__: Dict[str, int]

    class Config:
        json_schema_extra = {
            "example": {
                "MEMCOIN": 0,
                "DODGE": 100500
            }
        }

class Body_deposit_api_v1_admin_balance_deposit_post(BaseModel):
    """Схема запроса на пополнение баланса"""
    user_id: UUID
    ticker: str
    amount: int = Field(gt=0)

class Body_withdraw_api_v1_admin_balance_withdraw_post(BaseModel):
    """Схема запроса на списание с баланса"""
    user_id: UUID
    ticker: str
    amount: int = Field(gt=0) 