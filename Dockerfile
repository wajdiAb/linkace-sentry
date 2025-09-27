# Build stage
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Create non-root user for security and set up AWS credentials directory
RUN useradd -m appuser && \
    mkdir -p /home/appuser/.aws && \
    chown -R appuser:appuser /app /home/appuser/.aws && \
    chmod 700 /home/appuser/.aws
USER appuser
ENV HOME=/home/appuser

# Set Python path
ENV PYTHONPATH=/app

# Document required environment variables
# LINKACE_BASE_URL
# LINKACE_API_TOKEN
# AWS_SNS_TOPIC_ARN
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# AWS_DEFAULT_REGION

# Expose port if needed (FastAPI default port)
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "src.main"]