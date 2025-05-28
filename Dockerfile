# Currents API MCP Server Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/mcpuser/.local

# Copy application code
COPY currents_server.py .

# Set ownership of files to non-root user
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Set environment variables for Python
ENV PYTHONPATH=/home/mcpuser/.local/lib/python3.11/site-packages
ENV PATH=/home/mcpuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default environment variables (can be overridden)
ENV DEFAULT_LANGUAGE=en
ENV API_TIMEOUT=15
ENV MAX_RESULTS=20

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; exit(0 if os.getenv('CURRENTS_API_KEY') else 1)"

# Expose port (if needed for HTTP mode, not used for STDIO)
# EXPOSE 8000

# Default command
CMD ["python", "currents_server.py"]

# Labels for metadata
LABEL maintainer="MCP Workshop"
LABEL description="Currents API MCP Server"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/your-username/currents-mcp"