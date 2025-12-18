# =========================
# Backend - Production Image (FINAL)
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
       curl \
    && rm -rf /var/lib/apt/lists/*

# ---------- Python dependencies ----------
COPY requirements.txt requirements.lock.txt* ./

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------- Application code ----------
COPY app ./app
COPY init_aiweb.sql ./init_aiweb.sql

# ---------- Non-root user (recommended) ----------
RUN useradd -m aiweb \
    && chown -R aiweb:aiweb /app

USER aiweb

# ---------- Runtime ----------
EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "120"]
