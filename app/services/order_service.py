from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Union, Dict
from datetime import datetime
from app.models.order import Order
from app.models.transaction import Transaction
from app.schemas.order import (
    LimitOrderBody, MarketOrderBody, OrderStatus,
    Direction, CreateOrderResponse
)
from app.schemas.instrument import L2OrderBook, Level
from app.services import balance_service, instrument_service

async def create_order(
    db: Session,
    user_id: str,
    order_data: Union[LimitOrderBody, MarketOrderBody]
) -> CreateOrderResponse:
    """Создание ордера"""
    # Проверяем существование инструмента
    await instrument_service.get_instrument(db, order_data.ticker)
    
    # Проверяем баланс для SELL ордеров
    if order_data.direction == Direction.SELL:
        has_balance = await balance_service.check_balance(
            db, user_id, order_data.ticker, order_data.qty
        )
        if not has_balance:
            raise HTTPException(status_code=400, detail="Недостаточно средств")
    
    # Создаем ордер
    order = Order(
        user_id=user_id,
        ticker=order_data.ticker,
        direction=order_data.direction,
        qty=order_data.qty,
        price=getattr(order_data, 'price', None)  # None для рыночных ордеров
    )
    
    db.add(order)
    try:
        db.commit()
        db.refresh(order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при создании ордера")
    
    # Пытаемся исполнить ордер
    await try_execute_order(db, order)
    
    return CreateOrderResponse(order_id=order.id)

async def cancel_order(db: Session, order_id: str, user_id: str):
    """Отмена ордера"""
    order = await get_order(db, order_id, user_id)
    
    if order.status != OrderStatus.NEW:
        raise HTTPException(status_code=400, detail="Ордер нельзя отменить")
    
    order.status = OrderStatus.CANCELLED
    try:
        db.commit()
        db.refresh(order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при отмене ордера")
    
    return {"success": True}

async def get_order(db: Session, order_id: str, user_id: str) -> Order:
    """Получение ордера"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к ордеру")
    
    return order

async def get_user_orders(db: Session, user_id: str) -> List[Order]:
    """Получение списка активных ордеров пользователя"""
    return db.query(Order).filter(
        Order.user_id == user_id,
        Order.status == OrderStatus.NEW
    ).all()

async def get_orderbook(db: Session, ticker: str, limit: int = 10) -> L2OrderBook:
    """Получение стакана заявок"""
    # Проверяем существование инструмента
    await instrument_service.get_instrument(db, ticker)
    
    # Получаем активные ордера
    orders = db.query(Order).filter(
        Order.ticker == ticker,
        Order.status == OrderStatus.NEW
    ).all()
    
    # Группируем ордера по цене
    bids: Dict[int, int] = {}  # price -> total_qty
    asks: Dict[int, int] = {}  # price -> total_qty
    
    for order in orders:
        if not order.price:  # Пропускаем рыночные ордера
            continue
            
        if order.direction == Direction.BUY:
            bids[order.price] = bids.get(order.price, 0) + (order.qty - order.filled)
        else:
            asks[order.price] = asks.get(order.price, 0) + (order.qty - order.filled)
    
    # Сортируем и ограничиваем количество уровней
    bid_levels = [
        Level(price=price, qty=qty)
        for price, qty in sorted(bids.items(), reverse=True)[:limit]
    ]
    
    ask_levels = [
        Level(price=price, qty=qty)
        for price, qty in sorted(asks.items())[:limit]
    ]
    
    return L2OrderBook(bid_levels=bid_levels, ask_levels=ask_levels)

async def get_transaction_history(
    db: Session,
    ticker: str,
    limit: int = 10
) -> List[Transaction]:
    """Получение истории сделок"""
    # Проверяем существование инструмента
    await instrument_service.get_instrument(db, ticker)
    
    return db.query(Transaction).filter(
        Transaction.ticker == ticker
    ).order_by(Transaction.timestamp.desc()).limit(limit).all()

async def try_execute_order(db: Session, order: Order):
    """Попытка исполнения ордера"""
    if order.status != OrderStatus.NEW:
        return
    
    # Находим встречные ордера
    opposite_direction = Direction.SELL if order.direction == Direction.BUY else Direction.BUY
    
    query = db.query(Order).filter(
        Order.ticker == order.ticker,
        Order.direction == opposite_direction,
        Order.status == OrderStatus.NEW
    )
    
    if order.price:  # Для лимитных ордеров
        if order.direction == Direction.BUY:
            query = query.filter(Order.price <= order.price)
        else:
            query = query.filter(Order.price >= order.price)
        
        query = query.order_by(Order.price)
    else:  # Для рыночных ордеров
        if order.direction == Direction.BUY:
            query = query.order_by(Order.price)
        else:
            query = query.order_by(Order.price.desc())
    
    opposite_orders = query.all()
    
    # Исполняем ордер
    remaining_qty = order.qty
    for opposite_order in opposite_orders:
        if remaining_qty == 0:
            break
            
        available_qty = opposite_order.qty - opposite_order.filled
        execute_qty = min(remaining_qty, available_qty)
        execute_price = opposite_order.price or order.price
        
        if not execute_price:
            continue
        
        # Создаем транзакцию
        transaction = Transaction(
            ticker=order.ticker,
            amount=execute_qty,
            price=execute_price,
            buyer_id=order.user_id if order.direction == Direction.BUY else opposite_order.user_id,
            seller_id=opposite_order.user_id if order.direction == Direction.BUY else order.user_id
        )
        
        # Обновляем балансы
        if order.direction == Direction.BUY:
            await balance_service.withdraw(db, order.user_id, "RUB", execute_qty * execute_price)
            await balance_service.deposit(db, order.user_id, order.ticker, execute_qty)
            await balance_service.deposit(db, opposite_order.user_id, "RUB", execute_qty * execute_price)
            await balance_service.withdraw(db, opposite_order.user_id, order.ticker, execute_qty)
        else:
            await balance_service.deposit(db, order.user_id, "RUB", execute_qty * execute_price)
            await balance_service.withdraw(db, order.user_id, order.ticker, execute_qty)
            await balance_service.withdraw(db, opposite_order.user_id, "RUB", execute_qty * execute_price)
            await balance_service.deposit(db, opposite_order.user_id, order.ticker, execute_qty)
        
        # Обновляем ордера
        order.filled += execute_qty
        opposite_order.filled += execute_qty
        
        if opposite_order.filled == opposite_order.qty:
            opposite_order.status = OrderStatus.EXECUTED
        else:
            opposite_order.status = OrderStatus.PARTIALLY_EXECUTED
        
        remaining_qty -= execute_qty
        
        db.add(transaction)
    
    if remaining_qty == 0:
        order.status = OrderStatus.EXECUTED
    elif order.filled > 0:
        order.status = OrderStatus.PARTIALLY_EXECUTED
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при исполнении ордера") 