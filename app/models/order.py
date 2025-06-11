from sqlalchemy import Column, String, Integer, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from app.schemas.order import OrderStatus, Direction
from app.models.base import Base

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
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)) 