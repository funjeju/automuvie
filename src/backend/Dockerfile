FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app

ENV PORT=8080
EXPOSE 8080

# Cloud Run은 $PORT 환경변수(기본 8080)를 주입한다. 로컬 docker run도 default 8080.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
