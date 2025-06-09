from sqlalchemy import Column, String, Integer, Enum as SQLEnum, DateTime, ForeignKey
import uuid
from datetime import datetime
from app.schemas.order import OrderStatus, Direction
from app.models.base import Base

class Order(Base):
    """Модель ордера"""
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    ticker = Column(String, ForeignKey("instruments.ticker"), nullable=False)
    direction = Column(SQLEnum(Direction), nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.NEW)
    qty = Column(Integer, nullable=False)
    price = Column(Integer, nullable=True)  # Null для рыночных ордеров
    filled = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow) 