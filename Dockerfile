# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Moscow

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директорию для статики и базы данных
RUN mkdir -p static/css static/js static/images

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["python", "-m", "hypercorn", "app:app", "--bind", "0.0.0.0:8000"]