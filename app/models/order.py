from sqlalchemy import Column, String, Integer, Enum as SQLEnum, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from app.schemas.order import OrderStatus, Direction
from app.models.base import Base
import logging

logger = logging.getLogger(__name__)

class Order(Base):
    """Модель ордера"""
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ticker = Column(String, ForeignKey("instruments.ticker"), nullable=False)
    direction = Column(SQLEnum(Direction), nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.NEW)
    qty = Column(Integer, nullable=False)
    price = Column(Integer, nullable=True)  # Null для рыночных ордеров
    filled = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime(timezone=True), nullable=False, 
                      default=datetime.now(timezone.utc),
                      server_default=func.now())

    def __init__(self, **kwargs):
        # Обработка timestamp
        if 'timestamp' not in kwargs or kwargs['timestamp'] is None:
            kwargs['timestamp'] = datetime.now(timezone.utc)
        elif isinstance(kwargs['timestamp'], datetime):
            if kwargs['timestamp'].tzinfo is None:
                logger.warning(f"DB: Timestamp without timezone detected for order creation. Adding UTC timezone.")
                kwargs['timestamp'] = kwargs['timestamp'].replace(tzinfo=timezone.utc)
            elif kwargs['timestamp'].tzinfo != timezone.utc:
                logger.info(f"DB: Converting timestamp to UTC for order creation")
                kwargs['timestamp'] = kwargs['timestamp'].astimezone(timezone.utc)
        
        super().__init__(**kwargs)
        logger.info(f"Created order: id={self.id}, direction={self.direction}, "
                   f"ticker={self.ticker}, qty={self.qty}, price={self.price}, "
                   f"timestamp={self.timestamp}") 