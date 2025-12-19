FROM python:3.11-slim

# =========================
# Runtime environment
# =========================
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# =========================
# System dependencies
# =========================
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =========================
# Set project root as WORKDIR
# =========================
WORKDIR /ai-generation-platform

# =========================
# Python dependencies (locked)
# =========================
COPY backend/requirements.lock.txt ./requirements.lock.txt
RUN pip install --no-cache-dir \
    -r requirements.lock.txt

# =========================
# Application source
# =========================
COPY backend ./backend

# =========================
# Network
# =========================
EXPOSE 8000

# =========================
# Entrypoint (aligned with systemd)
# =========================
CMD ["gunicorn", "backend.app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
