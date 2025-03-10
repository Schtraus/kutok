FROM python:3.11-slim

# Установим рабочую директорию
WORKDIR /app

# Установим зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Установим необходимые зависимости для работы с PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Копируем все файлы проекта в контейнер
COPY . /app/

# Копируем .env файл
COPY .env /app/.env

# Создаем директорию для статики
RUN mkdir -p /app/staticfiles

# Команда для запуска приложения через Daphne (на порту, а не через сокет)
CMD ["daphne", "0.0.0.0:8000", "kutok.asgi:application"]
