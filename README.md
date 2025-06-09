# Toy Exchange API

Биржевое API для торговли различными инструментами.

## Требования

- Python 3.11+
- PostgreSQL 15+
- Docker

### Публичное API

- `POST /api/v1/public/register` - Регистрация нового пользователя
- `GET /api/v1/public/instrument` - Список доступных инструментов
- `GET /api/v1/public/orderbook/{ticker}` - Стакан заявок
- `GET /api/v1/public/transactions/{ticker}` - История сделок

### API Пользователя

- `GET /api/v1/balance` - Получение балансов
- `POST /api/v1/order` - Создание заявки
- `GET /api/v1/order` - Список активных заявок
- `GET /api/v1/order/{order_id}` - Информация о заявке
- `DELETE /api/v1/order/{order_id}` - Отмена заявки

### Административное API

- `DELETE /api/v1/admin/user/{user_id}` - Удаление пользователя
- `POST /api/v1/admin/instrument` - Добавление инструмента
- `DELETE /api/v1/admin/instrument/{ticker}` - Удаление инструмента
- `POST /api/v1/admin/balance/deposit` - Пополнение баланса
- `POST /api/v1/admin/balance/withdraw` - Списание с баланса

## Аутентификация

Все запросы (кроме публичных) требуют передачи токена в заголовке:
```
Authorization: TOKEN <api_key>
```

API ключ выдается при регистрации пользователя. 