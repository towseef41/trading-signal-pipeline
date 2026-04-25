FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

EXPOSE 8000

# Default: run the API (override in docker-compose or `docker run` to execute CLI commands)
CMD ["uvicorn", "trading_signal_pipeline.interfaces.api.v1.app:app", "--host", "0.0.0.0", "--port", "8000"]

