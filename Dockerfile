# syntax=docker/dockerfile:1
FROM python:3.12

ARG API_HTTP_PORT=${API_HTTP_PORT:-80}
ENV API_HTTP_PORT=${API_HTTP_PORT:-80}

RUN echo "API_HTTP_PORT: $API_HTTP_PORT"

WORKDIR /app

COPY src /app/src
COPY pyproject.toml /app

# RUN python3 -m venv venv
RUN pip install --no-cache-dir -e /app

CMD ["sh", "-c", "uvicorn edutap.image_api.main:app --proxy-headers --host 0.0.0.0 --port $API_HTTP_PORT --log-level debug --access-log"]
