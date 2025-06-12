from sqlalchemy.orm import Session
from typing import List
from app.models.transaction import Transaction as TransactionModel
from app.schemas.transaction import Transaction
from app.services import instrument_service
import logging

async def get_transaction_history(db: Session, ticker: str, limit: int = 10) -> List[Transaction]:
    """Получение истории сделок"""
    logger = logging.getLogger(__name__)
    logger.info(f"Getting transaction history for {ticker}, limit: {limit}")
    
    # Проверяем существование инструмента
    await instrument_service.get_instrument(db, ticker)
    
    transactions = db.query(TransactionModel).filter(
        TransactionModel.ticker == ticker
    ).order_by(TransactionModel.timestamp.desc()).all()  # Убираем limit для правильного расчета баланса
    
    # Конвертируем в схему согласно OpenAPI и добавляем информацию о балансе
    result = []
    for tx in transactions[:limit]:  # Применяем limit только для возвращаемого результата
        transaction = Transaction(
            ticker=tx.ticker,
            amount=tx.amount,
            price=tx.price,
            timestamp=tx.timestamp
        )
        result.append(transaction)
        
        # Логируем каждую транзакцию для отладки
        logger.info(f"[TRANSACTION] Processing transaction: id={tx.id}, "
                   f"buyer={tx.buyer_id}, seller={tx.seller_id}, "
                   f"amount={tx.amount}, price={tx.price}")
    
    return result 