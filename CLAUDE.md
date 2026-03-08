# CLAUDE.md — Enternal AI Coding Standards

> LifeScience B2B PaaS/SaaS Healthcare Data Platform

---

## Core Philosophy

- **Simplicity over complexity** — Write the minimum code needed. Don't add abstractions, features, or error handling beyond what was asked.
- **Evidence over assumption** — Read code, git history, and tests before making changes. Never guess what a function does or what a file contains.
- **Read before write** — Understand existing code before modifying it. Every edit starts with a read.
- **Minimal blast radius** — Change only what needs to change. Don't refactor surrounding code, add comments to unchanged code, or "improve" things that weren't asked for.

---

## Phase 0: Mandatory Context Gathering

**Before writing ANY code, complete ALL of the following. No exceptions.**

1. **Git history** — Run `git log` on the target file(s) and function(s). Note the last commit hash touching the code you're about to change.
2. **Jira/ticket search** — Search for existing tickets related to the change. Check for prior decisions, rejected approaches, or known issues.
3. **Read existing tests** — Find and read all tests covering the code you're about to change. Know what's already tested and what assertions exist.
4. **Read the target code** — Read every file and function you plan to modify. Understand the current implementation, not just the interface.
5. **Read PRD / specification docs** — Search for and read any PRD, specification, or requirements documents related to the feature or area you're changing. If a PRD exists, use it to clarify acceptance criteria, edge cases, and intended behavior before writing code. If requirements are ambiguous even after reading the PRD, ask the user for clarification — don't guess.
6. **Context summary** — Before proceeding, produce a brief summary:
   - What the code currently does
   - What needs to change and why
   - What tests exist
   - Last commit hash on the target code
   - Relevant PRD/spec requirements (if any exist)

**You MUST NOT write code until this phase is complete.**

---

## Jira Ticket as Decision Log

Every code change requires a Jira ticket. The ticket is not bureaucracy — it's a decision log.

### Before writing code:
- **Create a Jira ticket** under the relevant Epic using Atlassian MCP tools
- **Transition to "In Progress"** when starting work
- **Post an implementation plan** as the first comment:
  ```
  ## Implementation Plan
  Context: [What exists now, relevant git history]
  Problem: [What needs to change and why]
  Approach: [How you'll implement it]
  Affected tests: [Which tests need updating/creating]
  Key decisions: [Any design choices and rationale]
  ```

### After completing work:
- **Post a completion comment**:
  ```
  ## Completion Summary
  What was done: [Brief description]
  Commit: [hash]
  Test results: [pass/fail summary]
  Deviations from plan: [Any changes from the original approach]
  ```
- **Transition to "In QA"**

---

## Implementation Rules

1. **Don't add features beyond what was asked** — A bug fix is just a bug fix. A simple feature doesn't need extra configurability.
2. **Don't refactor surrounding code** — Unless explicitly asked to refactor, leave adjacent code alone.
3. **Don't add comments/docstrings to unchanged code** — Only add comments where the logic isn't self-evident in code you wrote.
4. **Don't create abstractions for one-time operations** — Three similar lines of code are better than a premature abstraction.
5. **Don't add error handling for impossible scenarios** — Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs).
6. **Prefer editing existing files over creating new ones** — Avoid file bloat. Build on existing work.
7. **If blocked, investigate — don't brute force** — When an approach fails, understand why. Don't retry the same failing approach. Try alternatives or ask for clarification.

---

## Test Integrity

- **Code and tests are committed together** — Every code change includes its test changes in the same commit. Always.
- **After any change, update affected tests** — If you changed behavior, tests must reflect the new behavior.
- **After completing work, run ALL tests** — Not just the ones you changed. The full suite.
- **Fix regressions before completing the task** — If your change broke something, fix it now.
- **Never delete or skip tests to make the suite pass** — A failing test is a signal, not an obstacle.
- **Never mock what you can test directly** — Use real implementations when feasible. Mocks hide bugs.

---

## Git Commit Standards

### Commit message format:
```
[TICKET-KEY] Brief summary

Implementation: What was done and why

Modified:
- path/to/file:function_name (prev commit: abc1234)
- path/to/other_file:ClassName.method (prev commit: def5678)

Tests:
- tests/test_file.py:test_function_name (new)
- tests/test_other.py:test_existing (updated)
```

### Rules:
- **`prev commit`** creates a traceability chain — anyone can trace the full history of a function through commits.
- **Code + tests in a single atomic commit** — Never commit code without its tests, or tests without their code.
- **Stage only relevant files** — Do not use `git add .` or `git add -A`. Stage files explicitly.
- **Write descriptive summaries** — The commit message should explain *why*, not just *what*.

---

## Git Push Policy

- **Never push unless the user explicitly says to push.**
- Commit locally first and wait for instruction.
- This applies to all branches, not just `main`.

---

## Post-Completion Checklist

Before declaring work complete, verify:

- [ ] All tests pass (full suite, not just changed tests)
- [ ] Jira ticket updated with completion comment (commit hash, test results, deviations)
- [ ] Jira ticket transitioned to "In QA"
- [ ] No unintended file changes staged or committed
- [ ] Build/deploy commands run if applicable

---

## Anti-Patterns — Explicit "DON'T" List

| Don't | Do Instead |
|-------|------------|
| Guess file contents | Read the file |
| Assume a function exists | Search for it (`Grep`, `Glob`) |
| Write code without reading the existing implementation | Read first, then write |
| Create duplicate utilities | Search the codebase for existing ones |
| Delete unfamiliar files or branches | Investigate what they are first |
| Bypass safety checks (`--no-verify`, `--force`) | Fix the underlying issue |
| Retry the same failing approach | Analyze the failure, try alternatives |
| Use `git add .` | Stage files explicitly |
| Delete or skip tests to make the suite pass | Fix the code or fix the test |
| Add backwards-compatibility shims for internal code | Just change the code |
| Over-engineer with feature flags, config options, or abstractions | Write the simplest thing that works |

---

## Project-Specific Configuration — Enternal

### Tech Stack

**Backend (Python)**
- **Framework:** FastAPI (async) with Pydantic v2 validation
- **ORM:** SQLAlchemy 2.x (async) with Alembic migrations
- **Database:** PostgreSQL 16 (via Query Adapter pattern — swappable to Databricks/Athena/Fabric)
- **FHIR:** fhirpy (async client) + fhir.resources (Pydantic models) — supports R4 and R5
- **Snowflake:** snowflake-connector-python (athenahealth DataView)
- **Agent:** LangChain + LangGraph (ReAct pattern, query decomposition)
- **LLM:** AWS Bedrock via langchain-aws (ChatBedrock) — BYOM adapter pattern
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **Logging:** structlog (structured JSON, PHI sanitization)
- **Testing:** pytest + pytest-asyncio + httpx + testcontainers

**Frontend (TypeScript)**
- **Framework:** Next.js 15.x (React)
- **UI:** shadcn/ui + Tailwind CSS (Databricks-style dark sidebar theme)
- **SQL Editor:** Monaco Editor (react-monaco-editor) with schema-aware autocomplete
- **Charts:** Tremor (bar, line, pie, area, donut, KPI, funnel)
- **Dashboard Grid:** react-grid-layout (drag-and-drop, resizable)
- **Data Tables:** AG Grid (community edition)
- **Split Panes:** react-resizable-panels
- **Command Palette:** cmdk (via shadcn/ui)
- **Export:** SheetJS (xlsx) + CSV
- **Testing:** Vitest + React Testing Library + Playwright (E2E)

**Infrastructure**
- **Deployment:** Docker Compose (customer-deployable)
- **CI/CD:** GitLab CI
- **Registry:** GitLab Container Registry
- **Source Control:** GitLab

### Build & Deploy

```bash
# Development
docker compose up --build                    # Start all services
docker compose up --build backend            # Backend only
docker compose up --build frontend           # Frontend only

# Backend tests
cd backend
pytest                                       # All backend tests
pytest tests/unit/                           # Unit tests only
pytest tests/integration/                    # Integration tests (needs DB)
pytest tests/mapping/                        # CDM mapping test suite
pytest --cov=app --cov-report=term-missing   # With coverage

# Frontend tests
cd frontend
npm run dev                                  # Dev server
npx vitest                                   # Unit tests
npx vitest --coverage                        # With coverage
npx playwright test                          # E2E tests

# Linting
cd backend && ruff check . && mypy .         # Python lint + type check
cd frontend && npx eslint .                  # TypeScript lint

# Database migrations
cd backend
alembic upgrade head                         # Apply migrations
alembic revision --autogenerate -m "desc"    # Generate migration
```

### Project Structure

```
enternal/
├── CLAUDE.md                    # This file
├── PRD.md                       # Product Requirements Document
├── decisions.md                 # 61 scoping decisions with rationale
├── tech-research.md             # Technology comparisons and references
├── docker-compose.yml           # Docker Compose (FastAPI + Next.js + PostgreSQL)
│
├── backend/                     # FastAPI application
│   ├── Dockerfile
│   ├── pyproject.toml           # Python dependencies (use poetry or pip)
│   ├── alembic/                 # Database migrations
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── dependencies.py      # Shared FastAPI dependencies
│   │   │
│   │   ├── modules/             # Modular monolith modules
│   │   │   ├── auth/            # JWT auth, RBAC, user management
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── models.py    # SQLAlchemy models (users)
│   │   │   │   ├── schemas.py   # Pydantic request/response schemas
│   │   │   │   └── dependencies.py  # Role-based deps (require_admin, etc.)
│   │   │   │
│   │   │   ├── ingestion/       # Data ingestion (FHIR + Snowflake)
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── fhir_client.py       # fhirpy wrapper, R4/R5 auto-detect
│   │   │   │   ├── snowflake_client.py  # Snowflake connector wrapper
│   │   │   │   ├── models.py            # integrations, ingestion_runs, quarantine
│   │   │   │   └── schemas.py
│   │   │   │
│   │   │   ├── transformation/  # FHIR/DataView → PCORnet CDM mapping
│   │   │   │   ├── engine.py            # Transformation orchestrator
│   │   │   │   ├── fhir_to_pcornet.py   # FHIR resource → PCORnet table mappers
│   │   │   │   ├── dataview_to_pcornet.py  # DataView → PCORnet mappers
│   │   │   │   └── validators.py        # Pydantic PCORnet schema validators
│   │   │   │
│   │   │   ├── cdm/             # PCORnet CDM v7.0 data layer
│   │   │   │   ├── models.py    # SQLAlchemy models for all PCORnet tables
│   │   │   │   └── schemas.py   # Pydantic schemas for PCORnet validation
│   │   │   │
│   │   │   ├── query/           # SQL query execution
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── adapter.py           # Query Adapter interface
│   │   │   │   ├── postgres_adapter.py  # PostgreSQL implementation
│   │   │   │   ├── models.py            # saved_queries, query_history, query_results
│   │   │   │   └── schemas.py
│   │   │   │
│   │   │   ├── agent/           # Agentic AI search
│   │   │   │   ├── router.py            # REST + WebSocket endpoints
│   │   │   │   ├── service.py
│   │   │   │   ├── graph.py             # LangGraph agent (ReAct loop)
│   │   │   │   ├── llm_adapter.py       # LLM Provider Adapter interface
│   │   │   │   ├── bedrock_adapter.py   # AWS Bedrock implementation
│   │   │   │   ├── models.py            # chat_sessions, chat_messages
│   │   │   │   └── schemas.py
│   │   │   │
│   │   │   ├── dashboard/       # Dashboard management
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── models.py    # dashboards, dashboard_widgets
│   │   │   │   └── schemas.py
│   │   │   │
│   │   │   ├── export/          # CSV/Excel export
│   │   │   │   ├── router.py
│   │   │   │   └── service.py
│   │   │   │
│   │   │   ├── health/          # Health dashboard + logging
│   │   │   │   ├── router.py
│   │   │   │   └── service.py
│   │   │   │
│   │   │   └── audit/           # Audit logging
│   │   │       ├── router.py
│   │   │       ├── service.py
│   │   │       └── models.py    # audit_log
│   │   │
│   │   └── core/                # Shared infrastructure
│   │       ├── database.py      # Async SQLAlchemy engine + session
│   │       ├── security.py      # JWT utils, password hashing
│   │       ├── logging.py       # structlog config + PHI sanitizer
│   │       └── exceptions.py    # Custom exception handlers
│   │
│   └── tests/
│       ├── unit/                # Unit tests (no DB needed)
│       ├── integration/         # Integration tests (testcontainers)
│       ├── mapping/             # CDM mapping test suite
│       │   ├── fixtures/        # FHIR R4/R5 JSON bundles
│       │   └── expected/        # Expected PCORnet output
│       └── api/                 # API contract tests (httpx)
│
├── frontend/                    # Next.js application
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   ├── sql-editor/
│   │   │   ├── agent/
│   │   │   ├── integrations/
│   │   │   ├── quarantine/
│   │   │   ├── admin/           # User management, health, logs, audit
│   │   │   └── layout.tsx       # Root layout (dark sidebar)
│   │   │
│   │   ├── components/          # React components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── sidebar/         # Databricks-style sidebar nav
│   │   │   ├── sql-editor/      # Monaco editor wrapper
│   │   │   ├── data-explorer/   # PCORnet table/column tree
│   │   │   ├── agent-chat/      # Chat interface + streaming
│   │   │   ├── dashboard/       # Dashboard builder + viewer
│   │   │   └── data-table/      # AG Grid wrapper
│   │   │
│   │   ├── lib/                 # Utilities
│   │   │   ├── api.ts           # API client (fetch wrapper)
│   │   │   ├── auth.ts          # Auth context + token management
│   │   │   └── websocket.ts     # WebSocket client for agent streaming
│   │   │
│   │   └── types/               # TypeScript type definitions
│   │
│   └── tests/
│       ├── components/          # Vitest component tests
│       └── e2e/                 # Playwright E2E tests
│
└── docs/                        # Customer deployment guide
    └── deployment.md
```

### Entity Model / Domain

**PCORnet CDM v7.0 Tables** (core domain — the canonical data model):
- DEMOGRAPHIC, ENCOUNTER, DIAGNOSIS, PROCEDURES, VITAL, LAB_RESULT_CM
- PRESCRIBING, DISPENSING, CONDITION, DEATH, DEATH_CAUSE, ENROLLMENT
- HARVEST, LDS_ADDRESS_HISTORY, MED_ADMIN, OBS_CLIN, OBS_GEN
- PCORNET_TRIAL, PRO_CM, PROVIDER, IMMUNIZATION, HASH_TOKEN

**Platform Tables** (application data — always in PostgreSQL):
- users, integrations, ingestion_runs, quarantine
- saved_queries, query_history, query_results
- dashboards, dashboard_widgets
- audit_log, chat_sessions, chat_messages

**Key Relationships:**
- PATID is the primary patient identifier across all PCORnet tables
- ENCOUNTERID links encounters to diagnoses, procedures, vitals, labs, prescriptions
- integrations → ingestion_runs → quarantine (ingestion tracking chain)
- users → saved_queries, query_history, dashboards, chat_sessions (user ownership)

**Reference:** [PCORnet CDM v7.0 Spec](https://pcornet.org/wp-content/uploads/2025/05/PCORnet_Common_Data_Model_v70_2025_05_01.pdf)

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/enternal

# Auth
JWT_SECRET_KEY=<generate-a-strong-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS Bedrock (LLM)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<from-customer>
AWS_SECRET_ACCESS_KEY=<from-customer>
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# PostgreSQL (Docker Compose)
POSTGRES_DB=enternal
POSTGRES_USER=<db-user>
POSTGRES_PASSWORD=<db-password>

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/agent/ws
```

**Never commit `.env` files. Use `.env.example` with placeholder values.**

### Access Control

| Permission | Admin | Analyst | Viewer |
|------------|-------|---------|--------|
| Manage users | Yes | No | No |
| Configure integrations (FHIR/Snowflake) | Yes | No | No |
| Platform settings | Yes | No | No |
| Trigger ingestion | Yes | No | No |
| View health/logs/audit | Yes | No | No |
| Run SQL queries | Yes | Yes | No |
| Use agentic search | Yes | Yes | No |
| Build/edit dashboards | Yes | Yes | No |
| Export data (CSV/Excel) | Yes | Yes | No |
| View query history | Yes | Yes | No |
| View dashboards | Yes | Yes | Yes |

**Implementation:** FastAPI dependency injection — `require_role(Role.ADMIN)`, `require_role(Role.ANALYST)`, etc.

**Agent guardrail:** All SQL generated by the agent must be SELECT-only. No DDL/DML operations.

### Test Data Policy

- **FHIR test fixtures:** Curated FHIR R4 and R5 JSON bundles in `backend/tests/mapping/fixtures/`. Each bundle has a corresponding expected PCORnet output in `backend/tests/mapping/expected/`.
- **Fixture coverage:** At minimum one fixture per FHIR resource type (Patient, Encounter, Condition, Procedure, Observation, MedicationRequest, MedicationDispense, Immunization).
- **Edge cases:** Include fixtures with missing optional fields, invalid codes, and data type edge cases to validate quarantine routing.
- **No real PHI in tests.** All test data must be synthetic. Use realistic but fictional patient data.
- **Database tests:** Use testcontainers (PostgreSQL) for integration tests — disposable containers, no shared test DB.
- **Snowflake tests:** Mock the Snowflake connector in unit tests. Integration tests against Snowflake require a test account (run separately, not in CI by default).

### HIPAA Compliance Rules

- **No PHI in logs.** structlog PHI sanitizer must strip patient names, SSNs, dates of birth, and all 18 HIPAA identifiers before logging.
- **No PHI in error messages** returned to the frontend.
- **TLS/HTTPS** for all API communication.
- **Audit every access:** Logins, SQL queries, data exports, ingestion runs — all logged to audit_log table.
- **BAA with AWS** required before sending any data to Bedrock.
- **Agent prompts:** Evaluate whether PHI is included in LLM prompts. Strip where possible.
