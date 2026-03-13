# Base image Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Set biến môi trường
ENV PYTHONUNBUFFERED=1

# Run bot
CMD ["python", "-m", "bot.main"]