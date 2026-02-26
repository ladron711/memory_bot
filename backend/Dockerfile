FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Копируем requirements отдельно (для кеша)
COPY requirements.txt .

# Обновляем pip и ставим зависимости
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем код
COPY . .

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]