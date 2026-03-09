FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.30.0" \
    "sqlalchemy[asyncio]>=2.0.0" \
    "asyncpg>=0.30.0" \
    "alembic>=1.14.0" \
    "pydantic>=2.0.0" \
    "pydantic-settings>=2.0.0" \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" \
    "bcrypt==4.0.1" \
    "python-multipart>=0.0.9" \
    "structlog>=24.0.0" \
    "httpx>=0.27.0" \
    "fhirpy>=2.0.0" \
    "fhir.resources>=8.0.0" \
    "snowflake-connector-python>=3.0.0" \
    "langchain-core>=0.3.0" \
    "langchain-community>=0.3.0" \
    "langchain-aws>=0.2.0" \
    "langgraph>=0.2.0" \
    "openpyxl>=3.1.0" \
    "email-validator>=2.0.0"

COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY scripts/ scripts/
RUN chmod +x scripts/*.sh

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
