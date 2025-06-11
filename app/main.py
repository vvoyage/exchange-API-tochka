from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.v1 import public, user, admin
from app.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO
)

app = FastAPI(
    title="Toy Exchange",
    version="0.1.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на список разрешенных доменов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(public.router, prefix="/api/v1/public", tags=["public"])
app.include_router(user.router, prefix="/api/v1", tags=["user"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"]) 