from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.instrument import Instrument
from app.schemas.instrument import Instrument as InstrumentSchema
from typing import List

async def add_instrument(db: Session, instrument_data: InstrumentSchema):
    """Добавление нового инструмента"""
    instrument = Instrument(
        name=instrument_data.name,
        ticker=instrument_data.ticker
    )
    
    db.add(instrument)
    try:
        db.commit()
        db.refresh(instrument)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при добавлении инструмента")
    
    return {"success": True}

async def delete_instrument(db: Session, ticker: str):
    """Удаление инструмента"""
    instrument = db.query(Instrument).filter(Instrument.ticker == ticker).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    
    # Используем мягкое удаление
    instrument.is_active = False
    try:
        db.commit()
        db.refresh(instrument)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при удалении инструмента")
    
    return {"success": True}

async def get_instruments(db: Session) -> List[Instrument]:
    """Получение списка активных инструментов"""
    return db.query(Instrument).filter(Instrument.is_active == True).all()

async def get_instrument(db: Session, ticker: str) -> Instrument:
    """Получение инструмента по тикеру"""
    instrument = db.query(Instrument).filter(
        Instrument.ticker == ticker,
        Instrument.is_active == True
    ).first()
    
    if not instrument:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    
    return instrument