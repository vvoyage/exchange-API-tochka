from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, Union, List

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from app.models.order import Order as OrderModel
from app.models.user import User
from app.schemas.order import (
    OrderStatus,
    Direction,
    LimitOrder,
    MarketOrder,
    LimitOrderBody,
    MarketOrderBody,
)
from app.services.balance import BalanceService
from app.services.exceptions import (
    OrderNotFoundError,
    InsufficientFundsError,
    OrderCancellationError,
)

def convert_order_to_schema(order: OrderModel) -> Union[LimitOrder, MarketOrder]:
    """Конвертирует модель ордера в схему"""
    base_fields = {
        "id": order.id,
        "status": order.status,
        "user_id": order.user_id,
        "timestamp": order.timestamp.astimezone(timezone.utc).isoformat(),
    }

    if order.price is not None:
        return LimitOrder(
            **base_fields,
            body=LimitOrderBody(
                direction=order.direction,
                ticker=order.ticker,
                qty=order.qty,
                price=order.price,
            ),
            filled=order.filled,
        )
    else:
        return MarketOrder(
            **base_fields,
            body=MarketOrderBody(
                direction=order.direction,
                ticker=order.ticker,
                qty=order.qty,
            ),
        )

# ... остальной код без изменений ... 