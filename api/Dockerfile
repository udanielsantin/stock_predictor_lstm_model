# Lightweight CPU image for FastAPI service
FROM python:3.11-slim

WORKDIR /app

# Install system deps (including matplotlib for dashboard)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY api /app/api
COPY src /app/src
COPY models /app/models

# S3-based logging - no local logs directory needed
# All logs are stored directly in S3 (vapor-stock-predictor-logs)
# 
# Required environment variables (set in docker-compose.yml or EC2):
# - S3_BUCKET_NAME: vapor-stock-predictor-logs
# - AWS_ACCESS_KEY_ID: your-aws-access-key
# - AWS_SECRET_ACCESS_KEY: your-aws-secret-key
# - AWS_REGION: us-east-1 (optional, defaults to us-east-1)
# - S3_LOG_PREFIX: logs/ (optional, defaults to logs/)

ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
