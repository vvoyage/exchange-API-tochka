from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
import uuid
from datetime import datetime
from app.models.base import Base

class Transaction(Base):
    """Модель транзакции (исполненной сделки)"""
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String, ForeignKey("instruments.ticker"), nullable=False)
    buyer_id = Column(String, ForeignKey("users.id"), nullable=False)
    seller_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow) 