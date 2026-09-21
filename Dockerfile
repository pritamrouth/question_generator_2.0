# Stage 1: Build stage
FROM python:3.9-slim AS builder

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# setup crawl4ai for Playwright and Chromium
RUN crawl4ai-setup 

# Install Playwright and Chromium
# RUN playwright install
# RUN playwright install chromium

# Stage 2: Runtime stage
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libexpat1 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy Playwright browsers from builder stage
COPY --from=builder /root/.cache /root/.cache

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_GENAI_API_KEY=AIzaSyDPL9heYn808WWJrLdT7FyHXC-4ilrdZ9A

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]