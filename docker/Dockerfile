FROM python:3.10-slim-bullseye

LABEL maintainer="you@example.com"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 🔹 수정된 경로 (docker 폴더 안에서 requirements.txt 가져오기)
COPY docker/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY app /app
ENTRYPOINT ["python", "/app/process_image.py"]
