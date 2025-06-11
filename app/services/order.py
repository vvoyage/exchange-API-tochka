from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, Union, List
import logging

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
    logger = logging.getLogger(__name__)
    
    # Ensure timestamp is timezone-aware and in UTC
    if order.timestamp.tzinfo is None:
        logger.warning(f"Service: Timestamp without timezone detected for order {order.id}. Adding UTC timezone.")
        timestamp = order.timestamp.replace(tzinfo=timezone.utc)
    else:
        timestamp = order.timestamp.astimezone(timezone.utc)

    # Convert to ISO 8601 format with timezone info
    timestamp_str = timestamp.isoformat()
    if not timestamp_str.endswith('Z') and '+' not in timestamp_str and '-' not in timestamp_str[10:]:
        timestamp_str += 'Z'

    base_fields = {
        "id": order.id,
        "status": order.status,
        "user_id": order.user_id,
        "timestamp": timestamp_str,
        "filled": order.filled or 0
    }

    if order.price is not None:  # Limit order
        return LimitOrder(
            **base_fields,
            body=LimitOrderBody(
                direction=order.direction,
                ticker=order.ticker,
                qty=order.qty,
                price=order.price,
            ),
        )
    else:  # Market order
        return MarketOrder(
            **base_fields,
            body=MarketOrderBody(
                direction=order.direction,
                ticker=order.ticker,
                qty=order.qty,
            ),
        )

# ... остальной код без изменений ... 