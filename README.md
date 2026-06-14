# Meeting Room Booking

Сервис бронирования переговорных комнат для коворкинга на FastAPI + JWT.

## Возможности

- Просмотр списка комнат и их временных слотов
- Проверка доступности комнат на конкретную дату
- Бронирование свободного слота
- Отмена своего бронирования
- Администратор может отменить любое бронирование
- Аутентификация через JWT-токен

## Запуск

### Локально (SQLite)

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

При первом запуске автоматически создадутся таблицы и тестовые пользователи.

### Docker (SQLite, одна команда)

```bash
docker build -t meeting-booking .
docker run -p 8000:8000 meeting-booking
```

### Docker Compose (PostgreSQL)

```bash
docker compose up --build
```

## Учётные данные для тестирования

| Роль          | Логин  | Пароль      |
|---------------|--------|-------------|
| Администратор | admin  | adminpass   |
| Сотрудник     | user   | userpass    |

## API

Документация доступна после запуска: http://localhost:8000/docs

### Эндпоинты

| Метод   | URL                          | Доступ        | Описание                          |
|---------|------------------------------|---------------|-----------------------------------|
| POST    | `/auth/login`                | Все           | Получить JWT-токен                |
| GET     | `/rooms`                     | Авторизован   | Список комнат со слотами          |
| GET     | `/rooms/{id}/availability?date=YYYY-MM-DD` | Авторизован | Доступность слотов на дату |
| POST    | `/bookings`                  | Авторизован   | Забронировать слот                |
| GET     | `/bookings`                  | Авторизован   | Мои бронирования                  |
| DELETE  | `/bookings/{id}`             | Авторизован   | Отменить бронирование             |

## Примеры использования (curl)

### 1. Логин

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"userpass"}'
```

Ответ:
```json
{"access_token":"eyJ...","token_type":"bearer"}
```

### 2. Список комнат

```bash
TOKEN="полученный_токен"
curl http://localhost:8000/rooms \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Доступность комнаты на дату

```bash
curl "http://localhost:8000/rooms/1/availability?date=2026-06-11" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Забронировать слот

```bash
curl -X POST http://localhost:8000/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"room_id":1,"slot_id":1,"date":"2026-06-11"}'
```

### 5. Мои бронирования

```bash
curl http://localhost:8000/bookings \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Отменить бронирование

```bash
curl -X DELETE http://localhost:8000/bookings/1 \
  -H "Authorization: Bearer $TOKEN"
```

## Запуск тестов

```bash
pip install -r requirements.txt
python -m pytest -v
```

## Стек

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async)
- JWT (python-jose)
- Pydantic v2
- SQLite / PostgreSQL
- Docker

## Демонстрация в Google Colab
Нажмите на кнопку, чтобы запустить интерактивный ноутбук с работающим сервисом прямо в браузере.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/gist/Vadim20240808/666a6ee329c09232056923a1dbbd87af)
