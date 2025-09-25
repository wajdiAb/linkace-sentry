# Build stage
FROM python:3.12-slim as builder

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

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Set Python path
ENV PYTHONPATH=/app

# Default environment variables (can be overridden at runtime)
ENV LINKACE_BASE_URL="http://localhost:8080"
ENV LINKACE_API_TOKEN=""
ENV AWS_SNS_TOPIC_ARN=""
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_DEFAULT_REGION="us-east-1"

# Expose port if needed (FastAPI default port)
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "src.main"]