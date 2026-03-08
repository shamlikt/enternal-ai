FROM python:3.11-slim AS base
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim AS runner
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY scripts/ scripts/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
