from sqlalchemy import Column, String, Integer, ForeignKey
from app.models.base import Base

class Balance(Base):
    """Модель баланса пользователя"""
    __tablename__ = "balances"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    ticker = Column(String, ForeignKey("instruments.ticker"), primary_key=True)
    amount = Column(Integer, nullable=False, default=0) 