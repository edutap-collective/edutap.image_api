# syntax=docker/dockerfile:1
FROM python:3.14

ARG API_HTTP_PORT=${API_HTTP_PORT:-80}
ENV API_HTTP_PORT=${API_HTTP_PORT:-80}

RUN echo "API_HTTP_PORT: $API_HTTP_PORT"

WORKDIR /app

COPY src /app/src
COPY pyproject.toml /app

# mediapipe dlopen()s its GPU bindings at FaceLandmarker construction time, not
# at import, so a missing library here does not fail the build or the import --
# it fails in the lifespan, and the service crash-loops with `exit (3)` while
# looking perfectly healthy in the registry.
#
# Measured on 2026-08-30 against the deployed image, with `ldd` on the mediapipe
# shared objects:
#
#   libEGL.so.1     => not found      (package libegl1)
#   libGLESv2.so.2  => not found      (package libgles2)
#
# BOTH, and that is why they are listed with their sonames: adding only libegl1
# -- the one the traceback named -- would have produced a second crash-loop on
# the next deploy, on the library the traceback had not got round to naming yet.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl-dev \
    libegl1 \
    libgles2 \
    && rm -rf /var/lib/apt/lists/*

# RUN python3 -m venv venv
RUN pip install --no-cache-dir -e /app

CMD ["sh", "-c", "uvicorn edutap.image_api.main:app --proxy-headers --host 0.0.0.0 --port $API_HTTP_PORT --log-level debug --access-log"]
