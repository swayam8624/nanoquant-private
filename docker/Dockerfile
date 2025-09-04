# Multi-stage build for NanoQuant Enterprise

# Build stage
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Generate self-signed SSL certificates for development
RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy the application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Make startup script executable
RUN chmod +x startup.sh

# Expose ports for API, admin dashboard, and HTTPS
EXPOSE 80 443 8001 8502

# Create a non-root user
RUN useradd --create-home --shell /bin/bash nanoquant
USER nanoquant

# Set environment variables
ENV HOME=/home/nanoquant
ENV PATH=/home/nanoquant/.local/bin:$PATH
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Default command
CMD ["./startup.sh"]