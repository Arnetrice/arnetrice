# syntax=docker/dockerfile:1.7

# ----- Stage 1: build Tailwind CSS -----
FROM node:20-alpine AS css-builder
WORKDIR /build
COPY package.json ./
RUN npm install --no-audit --no-fund
COPY tailwind.config.js ./
COPY static/css ./static/css
COPY templates ./templates
COPY static/js ./static/js
COPY app ./app
RUN mkdir -p ./static/dist && npx @tailwindcss/cli -i ./static/css/input.css -o ./static/dist/output.css --minify

# ----- Stage 2: Python runtime -----
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python deps first for layer caching
COPY requirements.txt ./
RUN pip install -r requirements.txt

# App source
COPY app ./app
COPY templates ./templates
COPY content ./content
COPY static ./static

# Built CSS from stage 1
COPY --from=css-builder /build/static/dist ./static/dist

# Railway-injected build metadata (overridable by env at runtime)
ARG RAILWAY_GIT_COMMIT_SHA=unknown
ARG BUILD_TIMESTAMP=unknown
ENV BUILD_COMMIT_SHA=${RAILWAY_GIT_COMMIT_SHA} \
    BUILD_TIMESTAMP=${BUILD_TIMESTAMP}

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips=*"]
