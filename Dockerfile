# Инструкции для образа

FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для SQLite и часовых поясов
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ=Europe/Moscow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD test -f data/health.txt || exit 1