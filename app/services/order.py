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
    
    # Проверяем timestamp
    if order.timestamp.tzinfo is None:
        logger.warning(f"Service: Timestamp without timezone detected for order {order.id}. Adding UTC timezone.")
        timestamp = order.timestamp.replace(tzinfo=timezone.utc)
    else:
        timestamp = order.timestamp.astimezone(timezone.utc)
        if order.timestamp.tzinfo != timezone.utc:
            logger.info(f"Service: Converting timestamp to UTC for order {order.id}")

    # Конвертируем в ISO 8601 строку
    timestamp_str = timestamp.isoformat()
    logger.debug(f"Converted timestamp to ISO format: {timestamp_str}")

    base_fields = {
        "id": order.id,
        "status": order.status,
        "user_id": order.user_id,
        "timestamp": timestamp_str,
        "filled": order.filled
    }

    try:
        if order.price is not None:
            result = LimitOrder(
                **base_fields,
                body=LimitOrderBody(
                    direction=order.direction,
                    ticker=order.ticker,
                    qty=order.qty,
                    price=order.price,
                ),
            )
        else:
            result = MarketOrder(
                **base_fields,
                body=MarketOrderBody(
                    direction=order.direction,
                    ticker=order.ticker,
                    qty=order.qty,
                ),
            )
        logger.debug(f"Successfully converted order {order.id} to schema")
        return result
    except Exception as e:
        logger.error(f"Failed to convert order {order.id} to schema: {str(e)}")
        raise

# ... остальной код без изменений ... 