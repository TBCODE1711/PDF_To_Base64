# Use official Python lightweight image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install Poppler directly into the Linux environment
RUN apt-get update && \
    apt-get install -y --no-install-recommends poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install dependencies first (to leverage Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (ignoring test folders and virtual environments via .dockerignore if exists)
COPY main.py .
COPY converter.py .

# Command to run the Uvicorn server, using the PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}

