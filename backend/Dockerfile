# =========================
# Backend - Production Image (FINAL · v1.0.3)
# =========================

FROM python:3.11-slim

# ---------- Python runtime ----------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# ---------- System dependencies ----------
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       postgresql-client \
       curl \
    && rm -rf /var/lib/apt/lists/*

# ---------- Python dependencies ----------
COPY requirements.txt requirements.lock.txt* ./

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------- Application code ----------
COPY app ./app
COPY init_aiweb.sql ./init_aiweb.sql

# ---------- Non-root user ----------
RUN useradd -m aiweb \
    && chown -R aiweb:aiweb /app

USER aiweb

# ---------- Runtime ----------
EXPOSE 8000

# ---------- Entry (DB wait + DB init + app start) ----------
CMD sh -c '\
    if [ -n "$DATABASE_URL" ]; then \
        echo "[v1.0.3] Waiting for database to be ready..."; \
        until pg_isready -d "$DATABASE_URL"; do \
            sleep 1; \
        done; \
        echo "[v1.0.3] Database is ready"; \
        echo "[v1.0.3] Running database init (idempotent)"; \
        psql "$DATABASE_URL" -f /app/init_aiweb.sql || true; \
    else \
        echo "[v1.0.3] DATABASE_URL not set, skip db wait & init"; \
    fi; \
    exec gunicorn app.main:app \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --timeout 120 \
'
