from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# Создаем движок SQLAlchemy с оптимизированными настройками пула
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Увеличиваем базовый размер пула
    max_overflow=30,  # Увеличиваем максимальное количество дополнительных соединений
    pool_timeout=60,  # Увеличиваем таймаут ожидания соединения
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,  # Пересоздание соединений каждый час
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()

def get_db():
    """Получение сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 