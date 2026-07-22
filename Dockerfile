FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаем директорию для базы данных и даем права
RUN mkdir -p /app/data && chmod 755 /app/data

RUN mkdir -p static/css static/js static/images

EXPOSE 8000

# Используем правильную команду запуска
CMD ["python3", "main.py"]