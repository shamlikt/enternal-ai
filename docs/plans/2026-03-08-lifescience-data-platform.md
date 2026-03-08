# LifeScience Data Platform Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a B2B PaaS/SaaS healthcare data platform that ingests FHIR and athenahealth DataView data, transforms it to PCORnet CDM v7.0, and provides SQL editor, agentic AI search, and dashboard analytics.

**Architecture:** Modular monolith with Query Adapter pattern. FastAPI backend + Next.js frontend + PostgreSQL, deployed via Docker Compose. LangChain/LangGraph for agentic AI with AWS Bedrock LLM.

**Tech Stack:** FastAPI, SQLAlchemy 2.x (async), Pydantic v2, fhirpy, fhir.resources, LangChain + LangGraph, langchain-aws, Next.js 15, shadcn/ui, Tailwind CSS, Monaco Editor, Tremor, react-grid-layout, AG Grid, Playwright, pytest, Vitest

**Team:** backend, frontend, data-engineer, qa, devops

---

## Task Assignment Map

| Task Range | Agent | Description |
|------------|-------|-------------|
| #1–#8 | backend | Backend scaffolding, core infrastructure, auth, query, agent, dashboard APIs |
| #9–#16 | frontend | Frontend scaffolding, layout, pages, components |
| #17–#22 | data-engineer | FHIR ingestion, Snowflake ingestion, CDM transformation engine |
| #23–#28 | qa | Backend tests, frontend tests, CDM mapping tests, E2E tests |
| #29–#32 | devops | Docker Compose, CI/CD, environment setup, deployment guide |

---

### Task 1: Backend Project Scaffolding
**Assigned to:** backend
**Blocked by:** none

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/dependencies.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/database.py`
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/logging.py`
- Create: `backend/app/core/exceptions.py`

**Step 1: Create pyproject.toml with all dependencies**
```toml
[project]
name = "enternal-backend"
version = "0.1.0"
description = "LifeScience Data Platform Backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.9",
    "structlog>=24.0.0",
    "httpx>=0.27.0",
    "fhirpy>=2.0.0",
    "fhir.resources>=8.0.0",
    "snowflake-connector-python>=3.0.0",
    "langchain-core>=0.3.0",
    "langchain-community>=0.3.0",
    "langchain-aws>=0.2.0",
    "langgraph>=0.2.0",
    "openpyxl>=3.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "testcontainers[postgres]>=4.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]
```

**Step 2: Create config.py with pydantic-settings**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/enternal"
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Step 3: Create core/database.py with async SQLAlchemy**
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

**Step 4: Create core/security.py with JWT + bcrypt**
```python
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
```

**Step 5: Create core/logging.py with structlog + PHI sanitizer**
```python
import structlog
import re

PHI_PATTERNS = [
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN_REDACTED]'),
    (re.compile(r'\b\d{9}\b'), '[SSN_REDACTED]'),
    (re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b'), '[DATE_REDACTED]'),
]

def phi_sanitizer(logger, method_name, event_dict):
    for key, value in event_dict.items():
        if isinstance(value, str):
            for pattern, replacement in PHI_PATTERNS:
                value = pattern.sub(replacement, value)
            event_dict[key] = value
    return event_dict

def configure_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            phi_sanitizer,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

**Step 6: Create core/exceptions.py**
```python
from fastapi import Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
```

**Step 7: Create main.py FastAPI app entrypoint**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import configure_logging
from app.core.exceptions import AppException, app_exception_handler

configure_logging()

app = FastAPI(
    title="Enternal Health API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}
```

**Step 8: Create __init__.py files for all module directories**
Create empty `__init__.py` in: `app/`, `app/core/`, `app/modules/`, and each module subdirectory (`auth/`, `ingestion/`, `transformation/`, `cdm/`, `query/`, `agent/`, `dashboard/`, `export/`, `health/`, `audit/`).

**Step 9: Commit**
```bash
git add backend/pyproject.toml backend/app/
git commit -m "feat: backend project scaffolding with FastAPI, SQLAlchemy, JWT auth core"
```

---

### Task 2: PCORnet CDM v7.0 SQLAlchemy Models
**Assigned to:** backend
**Blocked by:** #1

**Files:**
- Create: `backend/app/modules/cdm/__init__.py`
- Create: `backend/app/modules/cdm/models.py`
- Create: `backend/app/modules/cdm/schemas.py`

**Step 1: Create SQLAlchemy models for all 22 PCORnet CDM v7.0 tables**
Each table must follow the PCORnet CDM v7.0 specification. Key tables:
- DEMOGRAPHIC (PATID PK, BIRTH_DATE, SEX, SEXUAL_ORIENTATION, GENDER_IDENTITY, HISPANIC, RACE, BIOBANK_FLAG, PAT_PREF_LANGUAGE_SPOKEN)
- ENCOUNTER (ENCOUNTERID PK, PATID FK, ADMIT_DATE, DISCHARGE_DATE, ENC_TYPE, FACILITY_LOCATION, PROVIDERID)
- DIAGNOSIS (DIAGNOSISID PK, PATID FK, ENCOUNTERID FK, ENC_TYPE, DX, DX_TYPE, DX_SOURCE, DX_ORIGIN, PDX, ADMIT_DATE)
- PROCEDURES (PROCEDURESID PK, PATID FK, ENCOUNTERID FK, PX, PX_TYPE, PX_SOURCE, PX_DATE, PROVIDERID)
- VITAL (VITALID PK, PATID FK, ENCOUNTERID FK, MEASURE_DATE, HT, WT, DIASTOLIC, SYSTOLIC, ORIGINAL_BMI, BP_POSITION)
- LAB_RESULT_CM (LAB_RESULT_CM_ID PK, PATID FK, ENCOUNTERID FK, LAB_LOINC, LAB_RESULT_SOURCE, RESULT_NUM, RESULT_UNIT, RESULT_QUAL, SPECIMEN_DATE)
- PRESCRIBING (PRESCRIBINGID PK, PATID FK, ENCOUNTERID FK, RX_ORDER_DATE, RXNORM_CUI, RX_QUANTITY, RX_DAYS_SUPPLY, RX_REFILLS)
- DISPENSING (DISPENSINGID PK, PATID FK, DISPENSE_DATE, NDC, DISPENSE_QUANTITY, DISPENSE_DAYS_SUPPLY)
- CONDITION (CONDITIONID PK, PATID FK, ENCOUNTERID FK, CONDITION, CONDITION_TYPE, CONDITION_STATUS, CONDITION_SOURCE, ONSET_DATE, RESOLVE_DATE)
- DEATH (PATID PK, DEATH_DATE, DEATH_DATE_IMPUTE, DEATH_SOURCE, DEATH_MATCH_CONFIDENCE)
- DEATH_CAUSE (PATID FK, DEATH_CAUSE, DEATH_CAUSE_CODE, DEATH_CAUSE_TYPE, DEATH_CAUSE_SOURCE)
- ENROLLMENT (PATID FK, ENR_START_DATE, ENR_END_DATE, CHART, ENR_BASIS)
- HARVEST (NETWORKID PK, NETWORK_NAME, DATAMARTID, REFRESH_DEMOGRAPHIC_DATE, etc.)
- LDS_ADDRESS_HISTORY (ADDRESSID PK, PATID FK, ADDRESS_ZIP5, ADDRESS_ZIP9, ADDRESS_STATE, ADDRESS_COUNTY)
- MED_ADMIN (MEDADMINID PK, PATID FK, ENCOUNTERID FK, MEDADMIN_TYPE, MEDADMIN_CODE, MEDADMIN_START_DATE)
- OBS_CLIN (OBSCLINID PK, PATID FK, ENCOUNTERID FK, OBSCLIN_TYPE, OBSCLIN_CODE, OBSCLIN_RESULT_TEXT, OBSCLIN_RESULT_NUM)
- OBS_GEN (OBSGENID PK, PATID FK, ENCOUNTERID FK, OBSGEN_TYPE, OBSGEN_CODE, OBSGEN_RESULT_TEXT, OBSGEN_RESULT_NUM)
- PCORNET_TRIAL (PATID FK, TRIALID, TRIAL_SITEID, TRIAL_ENROLL_DATE, TRIAL_END_DATE)
- PRO_CM (PRO_CM_ID PK, PATID FK, ENCOUNTERID FK, PRO_ITEM_LOINC, PRO_RESPONSE_NUM)
- PROVIDER (PROVIDERID PK, PROVIDER_SEX, PROVIDER_SPECIALTY_PRIMARY, PROVIDER_NPI)
- IMMUNIZATION (IMMUNIZATIONID PK, PATID FK, ENCOUNTERID FK, PROCEDURE_DATE, VX_CODE, VX_CODE_TYPE, VX_STATUS, VX_SOURCE)
- HASH_TOKEN (PATID FK, TOKEN_ENCRYPTION_KEY)

Use `mapped_column`, proper types (String, Date, DateTime, Float, Integer), and set nullable correctly per spec.

**Step 2: Create Pydantic schemas for validation**
Create Pydantic v2 models in `schemas.py` for input validation of each CDM table (used during ingestion transformation).

**Step 3: Commit**
```bash
git add backend/app/modules/cdm/
git commit -m "feat: PCORnet CDM v7.0 SQLAlchemy models and Pydantic schemas for all 22 tables"
```

---

### Task 3: Auth Module — Backend
**Assigned to:** backend
**Blocked by:** #1

**Files:**
- Create: `backend/app/modules/auth/__init__.py`
- Create: `backend/app/modules/auth/models.py`
- Create: `backend/app/modules/auth/schemas.py`
- Create: `backend/app/modules/auth/service.py`
- Create: `backend/app/modules/auth/router.py`
- Create: `backend/app/modules/auth/dependencies.py`
- Modify: `backend/app/main.py` (register auth router)

**Step 1: Create User model**
```python
# models.py
import enum
from sqlalchemy import String, Boolean, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Role(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.VIEWER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

**Step 2: Create auth schemas (LoginRequest, TokenResponse, UserCreate, UserResponse, UserUpdate)**

**Step 3: Create auth service (authenticate_user, create_user, get_users, update_user, deactivate_user)**

**Step 4: Create auth router**
- POST `/api/v1/auth/login` — Login, returns JWT
- POST `/api/v1/auth/logout` — Logout
- POST `/api/v1/auth/refresh` — Refresh token
- GET `/api/v1/auth/me` — Current user

**Step 5: Create auth dependencies**
```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    # decode token, fetch user from DB
    ...

def require_role(*roles: Role):
    async def role_checker(current_user = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker
```

**Step 6: Create User Management router (Admin only)**
- GET `/api/v1/users/` — List users
- POST `/api/v1/users/` — Create user
- PATCH `/api/v1/users/{id}` — Update user
- DELETE `/api/v1/users/{id}` — Deactivate user

**Step 7: Register routers in main.py**

**Step 8: Commit**
```bash
git add backend/app/modules/auth/ backend/app/main.py
git commit -m "feat: JWT auth module with RBAC (Admin/Analyst/Viewer), login, user management"
```

---

### Task 4: Query Adapter + SQL Query Module
**Assigned to:** backend
**Blocked by:** #1, #2

**Files:**
- Create: `backend/app/modules/query/__init__.py`
- Create: `backend/app/modules/query/adapter.py`
- Create: `backend/app/modules/query/postgres_adapter.py`
- Create: `backend/app/modules/query/models.py`
- Create: `backend/app/modules/query/schemas.py`
- Create: `backend/app/modules/query/service.py`
- Create: `backend/app/modules/query/router.py`
- Modify: `backend/app/main.py` (register query router)

**Step 1: Create Query Adapter interface (ABC)**
```python
# adapter.py
from abc import ABC, abstractmethod
from typing import Any

class QueryAdapter(ABC):
    @abstractmethod
    async def execute_query(self, sql: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def get_tables(self) -> list[str]: ...

    @abstractmethod
    async def get_columns(self, table_name: str) -> list[dict[str, str]]: ...
```

**Step 2: Create PostgreSQL adapter implementation**

**Step 3: Create query models (saved_queries, query_history, query_results)**

**Step 4: Create query service with SELECT-only validation**
- Validate SQL is SELECT only (no INSERT/UPDATE/DELETE/DROP/ALTER/CREATE)
- Execute via adapter
- Store in query_history

**Step 5: Create query router**
- POST `/api/v1/query/execute` — Execute SQL (SELECT only)
- GET `/api/v1/query/history` — Query history
- GET/POST/PATCH/DELETE `/api/v1/query/saved` — Saved queries CRUD
- GET `/api/v1/schema/tables` — List PCORnet tables
- GET `/api/v1/schema/tables/{name}/columns` — Table columns

**Step 6: Commit**
```bash
git add backend/app/modules/query/ backend/app/main.py
git commit -m "feat: Query Adapter pattern with PostgreSQL adapter, SQL execution with SELECT-only guardrail"
```

---

### Task 5: Agent Module — Backend
**Assigned to:** backend
**Blocked by:** #4

**Files:**
- Create: `backend/app/modules/agent/__init__.py`
- Create: `backend/app/modules/agent/llm_adapter.py`
- Create: `backend/app/modules/agent/bedrock_adapter.py`
- Create: `backend/app/modules/agent/graph.py`
- Create: `backend/app/modules/agent/models.py`
- Create: `backend/app/modules/agent/schemas.py`
- Create: `backend/app/modules/agent/service.py`
- Create: `backend/app/modules/agent/router.py`
- Modify: `backend/app/main.py`

**Step 1: Create LLM Provider Adapter interface**
```python
# llm_adapter.py
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel

class LLMProviderAdapter(ABC):
    @abstractmethod
    def get_chat_model(self) -> BaseChatModel: ...
```

**Step 2: Create Bedrock adapter**
```python
# bedrock_adapter.py
from langchain_aws import ChatBedrock
from app.config import settings

class BedrockAdapter(LLMProviderAdapter):
    def get_chat_model(self) -> ChatBedrock:
        return ChatBedrock(
            model_id=settings.BEDROCK_MODEL_ID,
            region_name=settings.AWS_REGION,
        )
```

**Step 3: Create LangGraph agent with ReAct loop**
- Query decomposition for complex questions
- SQL generation (SELECT only)
- Execute via Query Adapter
- Synthesize results

**Step 4: Create agent models (chat_sessions, chat_messages)**

**Step 5: Create agent router**
- POST `/api/v1/agent/query` — Single query (non-streaming)
- WS `/api/v1/agent/ws` — WebSocket streaming chat
- GET `/api/v1/agent/sessions` — List chat sessions
- GET `/api/v1/agent/sessions/{id}` — Session history
- GET `/api/v1/agent/results/{id}` — Agent results

**Step 6: Commit**
```bash
git add backend/app/modules/agent/ backend/app/main.py
git commit -m "feat: agentic AI module with LangGraph ReAct agent, Bedrock adapter, WebSocket streaming"
```

---

### Task 6: Dashboard Module — Backend
**Assigned to:** backend
**Blocked by:** #3, #4

**Files:**
- Create: `backend/app/modules/dashboard/__init__.py`
- Create: `backend/app/modules/dashboard/models.py`
- Create: `backend/app/modules/dashboard/schemas.py`
- Create: `backend/app/modules/dashboard/service.py`
- Create: `backend/app/modules/dashboard/router.py`
- Modify: `backend/app/main.py`

**Step 1: Create dashboard models (dashboards, dashboard_widgets)**

**Step 2: Create dashboard schemas**

**Step 3: Create dashboard service (CRUD + widget management + template definitions)**
Pre-built templates: Patient Demographics, Encounter Trends, Diagnosis Distribution, Lab Results Summary, Prescription Analytics

**Step 4: Create dashboard router**
- GET/POST/PATCH/DELETE `/api/v1/dashboards/` — Dashboard CRUD
- POST/PATCH/DELETE `/api/v1/dashboards/{id}/widgets` — Widget management
- GET `/api/v1/dashboards/templates` — Pre-built templates
- GET `/api/v1/dashboards/{id}/data` — Widget data endpoint

**Step 5: Commit**
```bash
git add backend/app/modules/dashboard/ backend/app/main.py
git commit -m "feat: dashboard module with CRUD API, widget management, pre-built templates"
```

---

### Task 7: Export, Health, Audit Modules — Backend
**Assigned to:** backend
**Blocked by:** #3, #4

**Files:**
- Create: `backend/app/modules/export/__init__.py`
- Create: `backend/app/modules/export/router.py`
- Create: `backend/app/modules/export/service.py`
- Create: `backend/app/modules/health/__init__.py`
- Create: `backend/app/modules/health/router.py`
- Create: `backend/app/modules/health/service.py`
- Create: `backend/app/modules/audit/__init__.py`
- Create: `backend/app/modules/audit/models.py`
- Create: `backend/app/modules/audit/router.py`
- Create: `backend/app/modules/audit/service.py`
- Modify: `backend/app/main.py`

**Step 1: Create export service (CSV + Excel via SheetJS/openpyxl)**
- GET `/api/v1/export/{result_id}/csv`
- GET `/api/v1/export/{result_id}/xlsx`

**Step 2: Create audit log model and service**
```python
# audit/models.py
class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100))
    details: Mapped[str] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

**Step 3: Create health dashboard service**
- GET `/api/v1/health/` — System health status
- GET `/api/v1/health/ingestion` — Ingestion health
- GET `/api/v1/logs/` — Paginated log viewer
- GET `/api/v1/audit/` — Audit log entries

**Step 4: Commit**
```bash
git add backend/app/modules/export/ backend/app/modules/health/ backend/app/modules/audit/ backend/app/main.py
git commit -m "feat: export (CSV/Excel), health dashboard, audit logging modules"
```

---

### Task 8: Alembic Migrations Setup
**Assigned to:** backend
**Blocked by:** #2, #3

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/` (initial migration)

**Step 1: Initialize Alembic**
```bash
cd backend && alembic init alembic
```

**Step 2: Configure alembic/env.py to use async SQLAlchemy and import all models**

**Step 3: Generate initial migration with all PCORnet CDM + platform tables**
```bash
alembic revision --autogenerate -m "initial schema - PCORnet CDM v7.0 + platform tables"
```

**Step 4: Commit**
```bash
git add backend/alembic.ini backend/alembic/
git commit -m "feat: Alembic migrations setup with initial schema (PCORnet CDM v7.0 + platform tables)"
```

---

### Task 9: Frontend Project Scaffolding
**Assigned to:** frontend
**Blocked by:** none

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/next.config.ts`
- Create: `frontend/src/app/layout.tsx`
- Create: `frontend/src/app/page.tsx`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/auth.ts`
- Create: `frontend/src/lib/websocket.ts`
- Create: `frontend/src/types/index.ts`

**Step 1: Initialize Next.js 15 project with TypeScript, Tailwind CSS, App Router**
```bash
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --eslint
```

**Step 2: Install dependencies**
```bash
cd frontend
npm install @shadcn/ui cmdk react-grid-layout react-resizable-panels ag-grid-react ag-grid-community @tremor/react react-monaco-editor monaco-editor xlsx
npm install -D vitest @testing-library/react @testing-library/jest-dom @playwright/test
```

**Step 3: Initialize shadcn/ui**
```bash
npx shadcn@latest init
```

**Step 4: Create API client (src/lib/api.ts)**
Fetch wrapper with JWT token injection, base URL from `NEXT_PUBLIC_API_URL`.

**Step 5: Create auth context (src/lib/auth.ts)**
React context for auth state, login/logout functions, token management.

**Step 6: Create WebSocket client (src/lib/websocket.ts)**
WebSocket wrapper for agent streaming with reconnection.

**Step 7: Create TypeScript types (src/types/index.ts)**
Types for User, Dashboard, Widget, Query, ChatMessage, PCORnet tables, etc.

**Step 8: Commit**
```bash
git add frontend/
git commit -m "feat: Next.js 15 frontend scaffolding with shadcn/ui, Tailwind, API client"
```

---

### Task 10: Sidebar Layout + Navigation
**Assigned to:** frontend
**Blocked by:** #9

**Files:**
- Create: `frontend/src/components/sidebar/sidebar.tsx`
- Create: `frontend/src/components/sidebar/nav-item.tsx`
- Create: `frontend/src/components/ui/command-palette.tsx`
- Modify: `frontend/src/app/layout.tsx`

**Step 1: Create Databricks-style dark sidebar**
- Dark background (#1B1B1B)
- Icon + label navigation
- Collapsible (icon-only mode)
- Nav items: Dashboard, SQL Editor, Agent, Integrations, Quarantine, Admin (conditional on role)
- User avatar + role at bottom

**Step 2: Create Ctrl+K command palette using cmdk**
- Quick navigation to any page
- Quick query search

**Step 3: Update root layout to include sidebar + main content area**
Light content area with sidebar on left.

**Step 4: Commit**
```bash
git add frontend/src/components/sidebar/ frontend/src/components/ui/command-palette.tsx frontend/src/app/layout.tsx
git commit -m "feat: Databricks-style dark sidebar layout with command palette (Ctrl+K)"
```

---

### Task 11: Login Page + Auth Flow
**Assigned to:** frontend
**Blocked by:** #9

**Files:**
- Create: `frontend/src/app/login/page.tsx`
- Modify: `frontend/src/lib/auth.ts`
- Create: `frontend/src/middleware.ts` (route protection)

**Step 1: Create login page**
- Username/password form
- Error handling
- Redirect to dashboard on success

**Step 2: Create auth middleware for route protection**
- Redirect unauthenticated users to /login
- Role-based route protection

**Step 3: Commit**
```bash
git add frontend/src/app/login/ frontend/src/middleware.ts frontend/src/lib/auth.ts
git commit -m "feat: login page with JWT auth flow and route protection middleware"
```

---

### Task 12: SQL Editor Page
**Assigned to:** frontend
**Blocked by:** #9, #10

**Files:**
- Create: `frontend/src/app/sql-editor/page.tsx`
- Create: `frontend/src/components/sql-editor/editor.tsx`
- Create: `frontend/src/components/sql-editor/results-table.tsx`
- Create: `frontend/src/components/data-explorer/tree-view.tsx`

**Step 1: Create Monaco Editor component**
- SQL syntax highlighting
- Schema-aware autocomplete (fetch PCORnet tables/columns from API)
- Multi-tab interface
- Keyboard shortcut: Ctrl+Enter to run query

**Step 2: Create Data Explorer tree view**
- PCORnet tables → columns hierarchy
- Click-to-insert table/column name into editor

**Step 3: Create results table (AG Grid)**
- Sort, filter, pagination, column resize
- CSV/Excel export buttons

**Step 4: Create SQL Editor page layout**
- Three-pane layout using react-resizable-panels:
  - Left: Data Explorer tree
  - Top-right: Monaco Editor (multi-tab)
  - Bottom-right: AG Grid results

**Step 5: Query history sidebar + saved queries**

**Step 6: Commit**
```bash
git add frontend/src/app/sql-editor/ frontend/src/components/sql-editor/ frontend/src/components/data-explorer/
git commit -m "feat: SQL editor page with Monaco, Data Explorer, AG Grid results, split panes"
```

---

### Task 13: Agent Chat Page
**Assigned to:** frontend
**Blocked by:** #9, #10

**Files:**
- Create: `frontend/src/app/agent/page.tsx`
- Create: `frontend/src/components/agent-chat/chat-interface.tsx`
- Create: `frontend/src/components/agent-chat/message-bubble.tsx`
- Create: `frontend/src/components/agent-chat/streaming-text.tsx`

**Step 1: Create chat interface component**
- Message input box
- Message history display
- Token-by-token streaming display (ChatGPT-style)
- Show generated SQL for transparency
- Session management (new chat, history)

**Step 2: Create message bubble component**
- User messages vs agent responses
- Code blocks for SQL
- Results table inline

**Step 3: Create single query mode**
- Quick query box at top
- Inline result display

**Step 4: Export buttons for agent results (CSV/Excel)**

**Step 5: Commit**
```bash
git add frontend/src/app/agent/ frontend/src/components/agent-chat/
git commit -m "feat: agent chat page with streaming responses, SQL display, session history"
```

---

### Task 14: Dashboard Pages
**Assigned to:** frontend
**Blocked by:** #9, #10

**Files:**
- Create: `frontend/src/app/dashboard/page.tsx`
- Create: `frontend/src/app/dashboard/[id]/page.tsx`
- Create: `frontend/src/components/dashboard/dashboard-grid.tsx`
- Create: `frontend/src/components/dashboard/widget-card.tsx`
- Create: `frontend/src/components/dashboard/chart-widgets.tsx`
- Create: `frontend/src/components/dashboard/dashboard-builder.tsx`

**Step 1: Create dashboard grid (react-grid-layout)**
- Drag-and-drop widget placement
- Resizable widgets
- Save/load layout

**Step 2: Create chart widgets using Tremor**
- Bar chart, line chart, pie chart, area chart, donut chart
- KPI card, data table widget, funnel chart

**Step 3: Create dashboard builder**
- Add widget dialog
- Configure data source (SQL query for widget)
- Widget type selector
- Preview mode

**Step 4: Create dashboard list page**
- List user's dashboards
- Pre-built template cards
- Create new dashboard button

**Step 5: Commit**
```bash
git add frontend/src/app/dashboard/ frontend/src/components/dashboard/
git commit -m "feat: dashboard pages with drag-and-drop builder, Tremor charts, react-grid-layout"
```

---

### Task 15: Admin Pages (Users, Integrations, Health, Audit)
**Assigned to:** frontend
**Blocked by:** #9, #10, #11

**Files:**
- Create: `frontend/src/app/admin/page.tsx`
- Create: `frontend/src/app/admin/users/page.tsx`
- Create: `frontend/src/app/admin/health/page.tsx`
- Create: `frontend/src/app/admin/audit/page.tsx`
- Create: `frontend/src/app/admin/logs/page.tsx`
- Create: `frontend/src/app/integrations/page.tsx`
- Create: `frontend/src/app/quarantine/page.tsx`

**Step 1: User management page**
- User list (AG Grid)
- Create user dialog
- Edit role, deactivate user

**Step 2: Integration configuration page**
- FHIR connection form (server URL, auth type, client ID/secret)
- Snowflake connection form (account, username, password, database, schema, warehouse, role)
- Connection test button
- Active integrations list with status
- Trigger ingestion button
- Ingestion history

**Step 3: Quarantine viewer page**
- Browse, filter, search quarantined records
- Error details
- Quarantine stats

**Step 4: Health dashboard page**
- System status
- Ingestion health
- Error counts

**Step 5: Audit log page + Log viewer page**

**Step 6: Commit**
```bash
git add frontend/src/app/admin/ frontend/src/app/integrations/ frontend/src/app/quarantine/
git commit -m "feat: admin pages - user management, integrations, quarantine, health, audit, logs"
```

---

### Task 16: Frontend Theming + Polish
**Assigned to:** frontend
**Blocked by:** #10, #12, #13, #14

**Files:**
- Modify: `frontend/tailwind.config.ts`
- Create/modify: `frontend/src/app/globals.css`

**Step 1: Databricks-style theme**
- Dark sidebar (#1B1B1B)
- Light content area
- Consistent card styling
- Focus on clean, professional look

**Step 2: Responsive layout adjustments**

**Step 3: Loading states and error boundaries**

**Step 4: Commit**
```bash
git add frontend/tailwind.config.ts frontend/src/app/globals.css
git commit -m "feat: Databricks-style theming, loading states, error boundaries"
```

---

### Task 17: FHIR Ingestion Module
**Assigned to:** data-engineer
**Blocked by:** #1, #2

**Files:**
- Create: `backend/app/modules/ingestion/__init__.py`
- Create: `backend/app/modules/ingestion/models.py`
- Create: `backend/app/modules/ingestion/schemas.py`
- Create: `backend/app/modules/ingestion/fhir_client.py`
- Create: `backend/app/modules/ingestion/service.py`
- Create: `backend/app/modules/ingestion/router.py`

**Step 1: Create ingestion models (integrations, ingestion_runs, quarantine)**
```python
class Integration(Base):
    __tablename__ = "integrations"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))  # "fhir" or "snowflake"
    config_json: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    integration_id: Mapped[int] = mapped_column(ForeignKey("integrations.id"))
    status: Mapped[str] = mapped_column(String(20))  # pending, running, completed, failed
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_cursor: Mapped[str] = mapped_column(String(255), nullable=True)

class Quarantine(Base):
    __tablename__ = "quarantine"
    id: Mapped[int] = mapped_column(primary_key=True)
    ingestion_run_id: Mapped[int] = mapped_column(ForeignKey("ingestion_runs.id"))
    source_data: Mapped[dict] = mapped_column(JSON)
    error_message: Mapped[str] = mapped_column(Text)
    source_table: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

**Step 2: Create FHIR client wrapper (fhirpy)**
- Async FHIR client initialization
- R4/R5 auto-detection (check CapabilityStatement)
- Resource fetching with pagination
- Incremental sync (use _lastUpdated parameter)

**Step 3: Create ingestion router**
- GET/POST/PATCH/DELETE `/api/v1/integrations/` — Integration CRUD
- POST `/api/v1/integrations/{id}/test` — Test connection
- POST `/api/v1/ingestion/{integration_id}/run` — Trigger batch
- GET `/api/v1/ingestion/runs` — List runs
- GET `/api/v1/ingestion/runs/{id}` — Run details
- GET `/api/v1/quarantine/` — List quarantined records
- GET `/api/v1/quarantine/stats` — Stats

**Step 4: Commit**
```bash
git add backend/app/modules/ingestion/
git commit -m "feat: FHIR ingestion module with fhirpy client, R4/R5 auto-detect, incremental sync"
```

---

### Task 18: FHIR → PCORnet Transformation Engine
**Assigned to:** data-engineer
**Blocked by:** #2, #17

**Files:**
- Create: `backend/app/modules/transformation/__init__.py`
- Create: `backend/app/modules/transformation/engine.py`
- Create: `backend/app/modules/transformation/fhir_to_pcornet.py`
- Create: `backend/app/modules/transformation/validators.py`

**Step 1: Create transformation engine orchestrator**
- Receives raw FHIR resources
- Routes to appropriate mapper
- Validates output via Pydantic CDM schemas
- Success → insert into PCORnet tables
- Failure → quarantine with error details

**Step 2: Create FHIR→PCORnet mappers**
Based on HL7 CDMH Implementation Guide:
- Patient → DEMOGRAPHIC (name, birth_date, gender→SEX, race, ethnicity→HISPANIC)
- Encounter → ENCOUNTER (class→ENC_TYPE, period→ADMIT_DATE/DISCHARGE_DATE)
- Condition → DIAGNOSIS (code→DX, code.system→DX_TYPE) + CONDITION
- Procedure → PROCEDURES (code→PX, code.system→PX_TYPE)
- Observation (category=vital-signs) → VITAL (HT, WT, BP, etc.)
- Observation (category=laboratory) → LAB_RESULT_CM (code→LAB_LOINC, valueQuantity→RESULT_NUM)
- MedicationRequest → PRESCRIBING (medicationCodeableConcept→RXNORM_CUI)
- MedicationDispense → DISPENSING (medicationCodeableConcept→NDC)
- Immunization → IMMUNIZATION (vaccineCode→VX_CODE)
- Practitioner → PROVIDER
- Patient (deceased) → DEATH

**Step 3: Create validators (Pydantic PCORnet schema validation)**

**Step 4: Commit**
```bash
git add backend/app/modules/transformation/
git commit -m "feat: FHIR→PCORnet CDM transformation engine with mappers for all resource types"
```

---

### Task 19: Batch Ingestion Orchestrator
**Assigned to:** data-engineer
**Blocked by:** #17, #18

**Files:**
- Modify: `backend/app/modules/ingestion/service.py`

**Step 1: Implement batch ingestion orchestrator**
- Fetch FHIR resources in pages (~100K records/batch)
- Pass each resource through transformation engine
- Track progress (records_processed, records_failed)
- Update ingestion_run status
- Track last-synced cursor for incremental sync
- Error handling: continue on individual record failure, quarantine failed

**Step 2: Implement incremental sync**
- Use _lastUpdated parameter to only pull new/changed records
- Store cursor in ingestion_run.last_cursor
- Detect duplicate PATID/ENCOUNTERID and update rather than insert

**Step 3: Commit**
```bash
git add backend/app/modules/ingestion/service.py
git commit -m "feat: batch ingestion orchestrator with incremental sync and progress tracking"
```

---

### Task 20: Snowflake Ingestion Module
**Assigned to:** data-engineer
**Blocked by:** #1, #2, #17

**Files:**
- Create: `backend/app/modules/ingestion/snowflake_client.py`
- Modify: `backend/app/modules/ingestion/service.py`

**Step 1: Create Snowflake client wrapper**
- Connect using snowflake-connector-python
- Connection test
- Schema discovery (list tables, columns)
- Query execution with pagination

**Step 2: Integrate Snowflake ingestion into service**
- Reuse same ingestion_run tracking
- Reuse quarantine system

**Step 3: Commit**
```bash
git add backend/app/modules/ingestion/snowflake_client.py backend/app/modules/ingestion/service.py
git commit -m "feat: Snowflake ingestion module for athenahealth DataView"
```

---

### Task 21: DataView → PCORnet Mapping
**Assigned to:** data-engineer
**Blocked by:** #18, #20

**Files:**
- Create: `backend/app/modules/transformation/dataview_to_pcornet.py`
- Modify: `backend/app/modules/transformation/engine.py`

**Step 1: Create DataView→PCORnet mappers**
- Map athenahealth DataView tables to PCORnet CDM tables
- Schema discovery during development (map dynamically based on discovered schema)
- Reuse Pydantic validators from Task 18

**Step 2: Register DataView mappers in transformation engine**

**Step 3: Commit**
```bash
git add backend/app/modules/transformation/dataview_to_pcornet.py backend/app/modules/transformation/engine.py
git commit -m "feat: DataView→PCORnet CDM mapping for athenahealth Snowflake data"
```

---

### Task 22: CDM Mapping Test Fixtures
**Assigned to:** data-engineer
**Blocked by:** #18

**Files:**
- Create: `backend/tests/mapping/fixtures/` (FHIR R4/R5 JSON bundles)
- Create: `backend/tests/mapping/expected/` (Expected PCORnet output)
- Create: `backend/tests/mapping/conftest.py`

**Step 1: Create FHIR R4 test fixtures**
Create synthetic FHIR R4 JSON bundles:
- `patient_r4.json` — Patient resource → DEMOGRAPHIC
- `encounter_r4.json` — Encounter resource → ENCOUNTER
- `condition_r4.json` — Condition resource → DIAGNOSIS + CONDITION
- `procedure_r4.json` — Procedure resource → PROCEDURES
- `observation_vitals_r4.json` — Observation (vitals) → VITAL
- `observation_labs_r4.json` — Observation (labs) → LAB_RESULT_CM
- `medication_request_r4.json` — MedicationRequest → PRESCRIBING
- `medication_dispense_r4.json` — MedicationDispense → DISPENSING
- `immunization_r4.json` — Immunization → IMMUNIZATION
- `edge_cases_r4.json` — Missing fields, invalid codes → Quarantine

**Step 2: Create FHIR R5 test fixtures (same resource types)**

**Step 3: Create expected PCORnet output JSON files**

**Step 4: Commit**
```bash
git add backend/tests/mapping/
git commit -m "feat: CDM mapping test fixtures - FHIR R4/R5 bundles with expected PCORnet output"
```

---

### Task 23: Backend Unit Tests
**Assigned to:** qa
**Blocked by:** #3, #4, #5, #6, #7

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/unit/test_auth_service.py`
- Create: `backend/tests/unit/test_query_service.py`
- Create: `backend/tests/unit/test_agent_service.py`
- Create: `backend/tests/unit/test_dashboard_service.py`
- Create: `backend/tests/unit/test_export_service.py`
- Create: `backend/tests/unit/test_security.py`
- Create: `backend/tests/unit/test_phi_sanitizer.py`

**Step 1: Create test conftest.py with async fixtures**
- Async test client (httpx AsyncClient)
- In-memory SQLite or testcontainers PostgreSQL
- Test user fixtures (admin, analyst, viewer)
- JWT token fixtures

**Step 2: Test auth service**
- Test login with valid/invalid credentials
- Test JWT token creation/validation
- Test password hashing
- Test role-based access (admin can create users, analyst cannot)
- Test user CRUD operations

**Step 3: Test query service**
- Test SELECT-only validation (reject INSERT/UPDATE/DELETE/DROP)
- Test query execution
- Test query history
- Test saved queries CRUD

**Step 4: Test agent service**
- Test LLM adapter interface
- Test SQL generation guardrails (SELECT only)
- Test chat session management

**Step 5: Test dashboard service**
- Test dashboard CRUD
- Test widget management
- Test template loading

**Step 6: Test export service (CSV, Excel)**

**Step 7: Test PHI sanitizer (no SSNs, dates in log output)**

**Step 8: Commit**
```bash
git add backend/tests/
git commit -m "test: backend unit tests for auth, query, agent, dashboard, export, PHI sanitizer"
```

---

### Task 24: Backend API Tests
**Assigned to:** qa
**Blocked by:** #23

**Files:**
- Create: `backend/tests/api/test_auth_api.py`
- Create: `backend/tests/api/test_query_api.py`
- Create: `backend/tests/api/test_agent_api.py`
- Create: `backend/tests/api/test_dashboard_api.py`
- Create: `backend/tests/api/test_integration_api.py`
- Create: `backend/tests/api/test_health_api.py`

**Step 1: Test auth API endpoints**
- POST /api/v1/auth/login — valid/invalid
- GET /api/v1/auth/me — with/without token
- User management endpoints — RBAC enforcement

**Step 2: Test query API endpoints**
- POST /api/v1/query/execute — valid SELECT, rejected DML
- Schema endpoints

**Step 3: Test all other API endpoints with proper auth and role checks**

**Step 4: Commit**
```bash
git add backend/tests/api/
git commit -m "test: backend API contract tests for all REST endpoints"
```

---

### Task 25: CDM Mapping Tests
**Assigned to:** qa
**Blocked by:** #18, #22

**Files:**
- Create: `backend/tests/mapping/test_fhir_r4_mapping.py`
- Create: `backend/tests/mapping/test_fhir_r5_mapping.py`
- Create: `backend/tests/mapping/test_quarantine.py`
- Create: `backend/tests/mapping/test_incremental.py`

**Step 1: Test FHIR R4→PCORnet mapping**
- Patient → DEMOGRAPHIC (all fields)
- Encounter → ENCOUNTER
- Condition → DIAGNOSIS + CONDITION
- Procedure → PROCEDURES
- Observation (vitals) → VITAL
- Observation (labs) → LAB_RESULT_CM
- MedicationRequest → PRESCRIBING
- MedicationDispense → DISPENSING
- Immunization → IMMUNIZATION

**Step 2: Test FHIR R5→PCORnet mapping (same resource types)**

**Step 3: Test quarantine routing**
- Missing required fields → quarantine
- Invalid codes → quarantine
- Malformed data → quarantine with error details

**Step 4: Test incremental sync (no duplicates)**

**Step 5: Commit**
```bash
git add backend/tests/mapping/
git commit -m "test: CDM mapping test suite - FHIR R4/R5→PCORnet with edge cases and quarantine"
```

---

### Task 26: Backend Integration Tests
**Assigned to:** qa
**Blocked by:** #23

**Files:**
- Create: `backend/tests/integration/test_db_operations.py`
- Create: `backend/tests/integration/test_ingestion_pipeline.py`
- Create: `backend/tests/integration/test_query_adapter.py`

**Step 1: Create integration test conftest with testcontainers PostgreSQL**

**Step 2: Test database operations**
- CRUD on all PCORnet CDM tables
- CRUD on platform tables
- Foreign key constraints

**Step 3: Test full ingestion pipeline (FHIR fetch → transform → store/quarantine)**

**Step 4: Test Query Adapter with real PostgreSQL**

**Step 5: Commit**
```bash
git add backend/tests/integration/
git commit -m "test: integration tests with testcontainers PostgreSQL"
```

---

### Task 27: Frontend Unit Tests
**Assigned to:** qa
**Blocked by:** #10, #11, #12, #13, #14

**Files:**
- Create: `frontend/tests/components/test-sidebar.tsx`
- Create: `frontend/tests/components/test-login.tsx`
- Create: `frontend/tests/components/test-sql-editor.tsx`
- Create: `frontend/tests/components/test-agent-chat.tsx`
- Create: `frontend/tests/components/test-dashboard.tsx`
- Create: `frontend/tests/components/test-data-table.tsx`

**Step 1: Test sidebar navigation**
- Renders correct nav items
- Collapses/expands
- Role-based nav items (Admin sees all, Viewer sees limited)

**Step 2: Test login form**
- Form validation
- Submit with valid/invalid credentials
- Redirect on success

**Step 3: Test SQL editor**
- Monaco editor renders
- Run query button
- Results table renders

**Step 4: Test agent chat**
- Message input
- Message display
- Streaming text rendering

**Step 5: Test dashboard components**
- Widget rendering
- Grid layout
- Chart rendering

**Step 6: Commit**
```bash
git add frontend/tests/
git commit -m "test: frontend component tests for sidebar, login, SQL editor, agent chat, dashboard"
```

---

### Task 28: E2E Tests (Playwright)
**Assigned to:** qa
**Blocked by:** #23, #27, #29

**Files:**
- Create: `frontend/tests/e2e/login.spec.ts`
- Create: `frontend/tests/e2e/sql-editor.spec.ts`
- Create: `frontend/tests/e2e/agent-chat.spec.ts`
- Create: `frontend/tests/e2e/dashboard.spec.ts`
- Create: `frontend/playwright.config.ts`

**Step 1: Configure Playwright**
- Base URL: http://localhost:3000
- Start both backend and frontend before tests

**Step 2: Login flow E2E test**
- Navigate to /login
- Enter credentials
- Verify redirect to dashboard
- Verify sidebar appears

**Step 3: SQL Editor E2E test**
- Navigate to SQL editor
- Type SQL query
- Run query (Ctrl+Enter)
- Verify results table
- Export CSV

**Step 4: Agent Chat E2E test**
- Navigate to agent
- Type question
- Verify streaming response
- Verify SQL display

**Step 5: Dashboard E2E test**
- View pre-built dashboard
- Create new dashboard
- Add widget
- Drag and resize

**Step 6: Commit**
```bash
git add frontend/tests/e2e/ frontend/playwright.config.ts
git commit -m "test: Playwright E2E tests for login, SQL editor, agent chat, dashboard flows"
```

---

### Task 29: Docker Compose Setup
**Assigned to:** devops
**Blocked by:** #1, #9

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `.env.example`

**Step 1: Create backend Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install .
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: Create frontend Dockerfile**
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next .next
COPY --from=builder /app/node_modules node_modules
COPY --from=builder /app/package.json .
EXPOSE 3000
CMD ["npm", "start"]
```

**Step 3: Create docker-compose.yml**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - AWS_REGION=${AWS_REGION}
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/agent/ws
    depends_on: [backend]

  postgres:
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

**Step 4: Create .env.example**

**Step 5: Verify docker compose up --build works**

**Step 6: Commit**
```bash
git add docker-compose.yml backend/Dockerfile frontend/Dockerfile .env.example
git commit -m "feat: Docker Compose setup with FastAPI, Next.js, PostgreSQL services"
```

---

### Task 30: GitLab CI Pipeline
**Assigned to:** devops
**Blocked by:** #29

**Files:**
- Create: `.gitlab-ci.yml`

**Step 1: Create GitLab CI configuration**
```yaml
stages:
  - lint
  - test
  - build
  - push

lint-backend:
  stage: lint
  script:
    - cd backend
    - pip install ruff mypy
    - ruff check .
    - mypy .

lint-frontend:
  stage: lint
  script:
    - cd frontend
    - npm ci
    - npx eslint .

test-backend:
  stage: test
  services:
    - postgres:16
  script:
    - cd backend
    - pip install .[dev]
    - pytest --cov=app --cov-report=term-missing

test-frontend:
  stage: test
  script:
    - cd frontend
    - npm ci
    - npx vitest --coverage

build-backend:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA ./backend

build-frontend:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA ./frontend

push-images:
  stage: push
  script:
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA
  only:
    - main
```

**Step 2: Commit**
```bash
git add .gitlab-ci.yml
git commit -m "feat: GitLab CI pipeline with lint, test, build, push stages"
```

---

### Task 31: Database Migration Scripts
**Assigned to:** devops
**Blocked by:** #8, #29

**Files:**
- Create: `backend/scripts/init_db.sh`
- Create: `backend/scripts/seed_admin.py`

**Step 1: Create database initialization script**
- Run Alembic migrations
- Seed initial admin user (if no users exist)

**Step 2: Create admin seed script**
```python
# seed_admin.py - creates initial admin user
import asyncio
from app.core.database import async_session
from app.modules.auth.models import User, Role
from app.core.security import get_password_hash

async def seed_admin():
    async with async_session() as session:
        # Check if admin exists
        # If not, create default admin user
        admin = User(
            username="admin",
            email="admin@enternal.health",
            password_hash=get_password_hash("changeme"),
            role=Role.ADMIN,
        )
        session.add(admin)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_admin())
```

**Step 3: Update Docker Compose to run migrations on startup**

**Step 4: Commit**
```bash
git add backend/scripts/
git commit -m "feat: database initialization scripts with Alembic migration runner and admin seeder"
```

---

### Task 32: Production Docker Compose + Deployment Guide
**Assigned to:** devops
**Blocked by:** #29, #30, #31

**Files:**
- Create: `docker-compose.prod.yml`
- Create: `docs/deployment.md`

**Step 1: Create production Docker Compose**
- TLS termination notes
- Health checks for all services
- Resource limits
- Log driver configuration
- Restart policies

**Step 2: Create deployment guide**
- Prerequisites (Docker, Docker Compose)
- Quick start instructions
- Environment variable reference
- TLS/HTTPS setup
- Backup and restore
- Upgrade procedure
- Troubleshooting

**Step 3: Commit**
```bash
git add docker-compose.prod.yml docs/deployment.md
git commit -m "feat: production Docker Compose and customer deployment guide"
```

---

## Dependency Summary

```
Task 1 (backend scaffold) ─────┬──→ Task 2 (CDM models) ──→ Task 8 (migrations)
                                ├──→ Task 3 (auth) ──────────→ Task 6 (dashboard API)
                                ├──→ Task 4 (query) ─────────→ Task 5 (agent)
                                ├──→ Task 17 (FHIR ingestion) → Task 18 (transforms) → Task 19 (batch orchestrator)
                                │                                                    → Task 22 (test fixtures)
                                └──→ Task 20 (Snowflake) ────→ Task 21 (DataView mapping)

Task 9 (frontend scaffold) ────┬──→ Task 10 (sidebar) ──→ Task 12 (SQL editor)
                                ├──→ Task 11 (login) ────→ Task 13 (agent chat)
                                │                        → Task 14 (dashboards)
                                │                        → Task 15 (admin pages)
                                └──→ Task 16 (theming)

Task 1, 9 ──→ Task 29 (Docker) ──→ Task 30 (CI) ──→ Task 32 (prod deploy)
Task 8, 29 ──→ Task 31 (DB scripts)

QA tasks (23-28) blocked by their respective implementation tasks.
```
