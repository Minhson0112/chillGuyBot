# Base image Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Set biến môi trường (tuỳ chọn)
ENV PYTHONUNBUFFERED=1

# Command để chạy bot (giả sử file chính là bot.py)
CMD ["python", "-m", "bot.main"]
