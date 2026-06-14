FROM python:3.12-slim

WORKDIR /app

# Установка зависимостей через pip (а не poetry)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем сервер
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


#git config --global user.name 'Vadim20240808'