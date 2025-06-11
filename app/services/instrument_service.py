from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.instrument import Instrument
from app.schemas.instrument import Instrument as InstrumentSchema
from typing import List
import logging

async def add_instrument(db: Session, instrument_data: InstrumentSchema):
    """Добавление нового инструмента"""
    logger = logging.getLogger(__name__)
    logger.debug(f"Adding instrument: name={instrument_data.name}, ticker={instrument_data.ticker}")
    
    try:
        # Проверяем существование инструмента (активного или неактивного)
        existing_instrument = db.query(Instrument).filter(
            Instrument.ticker == instrument_data.ticker
        ).first()
        
        if existing_instrument:
            if existing_instrument.is_active:
                logger.error(f"Instrument {instrument_data.ticker} already exists and is active")
                raise HTTPException(
                    status_code=400,
                    detail="Инструмент уже существует"
                )
            else:
                # Реактивируем существующий инструмент
                logger.info(f"Reactivating existing instrument {instrument_data.ticker}")
                existing_instrument.is_active = True
                existing_instrument.name = instrument_data.name  # Обновляем имя
                db.commit()
                db.refresh(existing_instrument)
                return {"success": True}
        
        # Создаем новый инструмент если не существует
        instrument = Instrument(
            name=instrument_data.name,
            ticker=instrument_data.ticker,
            is_active=True
        )
        db.add(instrument)
        db.commit()
        db.refresh(instrument)
        logger.debug(f"Successfully added new instrument {instrument_data.ticker}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add instrument: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при добавлении инструмента: {str(e)}"
        )
    
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