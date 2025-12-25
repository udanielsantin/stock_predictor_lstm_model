# Lightweight CPU image for FastAPI service
FROM python:3.11-slim

WORKDIR /app

# Install system deps (including matplotlib for dashboard)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY api /app/api
COPY src /app/src
COPY models /app/models

# Create logs directory
RUN mkdir -p /app/logs

ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
