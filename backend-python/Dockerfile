FROM python:3.11-slim-bookworm AS builder
WORKDIR /build
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i "s@http://deb.debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list.d/debian.sources && \
        sed -i "s@http://security.debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list.d/debian.sources; \
    else \
        sed -i "s@http://deb.debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list && \
        sed -i "s@http://security.debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list; \
    fi
COPY backend-python/requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev libheif-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install --prefix=/install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

FROM python:3.11-slim-bookworm
WORKDIR /app
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i "s@http://deb.debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list.d/debian.sources && \
        sed -i "s@http://security.debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list.d/debian.sources; \
    else \
        sed -i "s@http://deb.debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list && \
        sed -i "s@http://security.debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list; \
    fi && \
    apt-get update && apt-get install -y --no-install-recommends \
    libpq5 fonts-wqy-zenhei curl libheif1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY --from=builder /install /usr/local
COPY backend-python/ .
COPY VERSION ./VERSION
ENV PYTHONUNBUFFERED=1

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m appuser && \
    mkdir -p /app/logs /app/uploads && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
