from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.schemas.user import NewUser, UserRole
from app.core.security import create_api_key
from uuid import UUID

async def create_user(db: Session, user_data: NewUser) -> User:
    """Создание нового пользователя"""
    # Создаем пользователя
    user = User(
        name=user_data.name,
        role=UserRole.USER,
        api_key=create_api_key(user.id)  # api_key будет создан после получения id
    )
    
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        # Обновляем api_key после получения id
        user.api_key = create_api_key(user.id)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при создании пользователя")
    
    return user

async def delete_user(db: Session, user_id: UUID) -> User:
    """Удаление пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при удалении пользователя")
    
    return user

async def get_user(db: Session, user_id: UUID) -> User:
    """Получение пользователя по ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user 