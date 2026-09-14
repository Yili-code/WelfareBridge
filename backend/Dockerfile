FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/backend

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# data/（raw 檔案、demo seed）由 docker-compose 以 volume 掛在 /app/data；資料庫為 MongoDB（compose 的 mongo 服務）
ENV DATA_DIR=/app/data \
    DEMO_SEED_PATH=/app/data/demo/seed_v2.json

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
