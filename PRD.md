# LifeScience Data Platform — Product Requirements Document

> Version: 1.0
> Last Updated: 2026-03-08
> Status: Draft
> Author: AI Project Manager + Product Owner

---

## 1. Executive Summary

The LifeScience Data Platform is a B2B PaaS/SaaS solution designed for life sciences companies to ingest, standardize, and analyze patient healthcare data. The platform integrates data from multiple clinical sources — FHIR-compliant EHR systems and athenahealth DataView — and transforms it into the PCORnet Common Data Model (CDM) v7.0, providing a unified analytical layer.

The platform is **agent-first**, meaning AI-powered natural language querying is a primary interaction mode alongside traditional SQL and visual dashboards. It is designed to be **customer-deployable** — each client deploys the platform within their own infrastructure (on-prem or private cloud) via Docker Compose, ensuring full data sovereignty and HIPAA compliance.

The architecture follows a **modular monolith with a Query Adapter pattern**, starting with PostgreSQL but designed to be interchangeable with Databricks, AWS Athena, or Microsoft Fabric/Synapse as customers scale.

---

## 2. Problem Statement

Life sciences companies face significant challenges working with patient data:

- **Fragmented data sources:** Patient data is scattered across FHIR servers, EHR systems (athenahealth), and unstructured documents (PDFs). Each source has its own schema and format.
- **No common data model:** Without standardization, cross-source analysis is manual, error-prone, and time-consuming. Analysts spend more time wrangling data than analyzing it.
- **Technical barriers to analysis:** Current solutions require deep SQL expertise or expensive BI tools. Business teams are locked out of data exploration without engineering support.
- **Compliance complexity:** Healthcare data (PHI) requires HIPAA-compliant infrastructure. Most analytics tools don't provide the deployment flexibility needed for on-prem/private cloud environments.

Existing solutions fall short because:
- Tools like Databricks or Snowflake are powerful but require significant setup, are cloud-locked, and don't provide healthcare-specific data modeling (PCORnet CDM).
- EHR vendors provide limited analytics within their own ecosystems but don't unify across sources.
- There is no turnkey, customer-deployable platform that combines healthcare data ingestion, PCORnet standardization, SQL analytics, AI-powered querying, and visual dashboards in a single product.

---

## 3. Goals & Success Metrics

| Goal | Metric | Target |
|------|--------|--------|
| Unified data ingestion | Sources integrated | FHIR R4/R5 + athenahealth DataView (MVP) |
| Data standardization | PCORnet CDM compliance | 100% of core tables mapped (v7.0) |
| Data quality | Ingestion success rate | >95% records mapped successfully |
| Query accessibility | Active users per deployment | 50 concurrent users |
| Agent effectiveness | Query accuracy | Agent generates correct SQL for >80% of natural language questions |
| Deployment simplicity | Time to deploy | <1 hour via Docker Compose |
| HIPAA compliance | Audit findings | Zero PHI leaks in logs; all access audited |
| Data volume | Records per deployment | 100K initial, scalable to millions |

---

## 4. Target Users & Personas

### Persona 1: Data Analyst (Analyst Role)
- **Role:** LifeScience company data analyst
- **Pain Points:** Spends 60%+ of time extracting and cleaning data from multiple sources; limited to tools provided by EHR vendors; can't easily cross-reference data across sources
- **Goals:** Write SQL queries against unified data; build custom dashboards; export results for reports
- **Technical Proficiency:** High — comfortable with SQL, familiar with PCORnet CDM

### Persona 2: Business User (Viewer Role)
- **Role:** LifeScience business team member (operations, strategy, compliance)
- **Pain Points:** Depends on analysts to get data; can't self-serve; waits days for reports
- **Goals:** View pre-built dashboards; ask questions in natural language via the AI agent; export data for presentations
- **Technical Proficiency:** Low to medium — not comfortable with SQL, prefers visual/conversational interfaces

### Persona 3: Platform Administrator (Admin Role)
- **Role:** IT or data engineering lead at the customer's organization
- **Pain Points:** Managing data connections, user access, and platform health across the organization
- **Goals:** Configure data integrations (FHIR servers, Snowflake); manage users and roles; monitor platform health and ingestion status
- **Technical Proficiency:** High — manages infrastructure, comfortable with Docker and configuration

---

## 5. Scope

### 5.1 In Scope (MVP)

- FHIR R4/R5 data ingestion with auto-detection
- athenahealth DataView ingestion via Snowflake connector
- PCORnet CDM v7.0 transformation and storage
- Integration configuration dashboard (UI-based)
- Batch ingestion with incremental updates (~100K records)
- Quarantine system for failed records with review UI
- SQL editor (Databricks-style with Monaco Editor)
- Query history and saved queries
- Agentic AI search (LangChain + LangGraph, AWS Bedrock)
- Chat interface (multi-turn) + single query mode
- Token-by-token streaming responses (WebSocket)
- Pre-built dashboard templates + self-service dashboard builder
- Drag-and-drop dashboard with Tremor charts + react-grid-layout
- CSV and Excel export
- JWT authentication with RBAC (Admin, Analyst, Viewer)
- HIPAA compliance (TLS, audit logging, PHI-free logs)
- Health dashboard and in-app log viewer
- Docker Compose deployment
- Comprehensive test suite (unit, integration, E2E, CDM mapping)

### 5.2 In Scope (Post-MVP)

- PDF ingestion (OCR for scanned + digital text extraction)
- OpenSearch for unstructured data storage and search
- Database adapters for Databricks, AWS Athena, Microsoft Fabric/Synapse
- Graph database for relationship-based querying
- SSO integration (Okta, Azure AD, Google Workspace)
- Dashboard sharing between users
- API keys for external system access
- Encryption at rest
- Detailed audit logging (every API call, record-level access)
- Prometheus metrics endpoint
- Additional LLM providers (OpenAI, Anthropic, Azure OpenAI, Ollama/vLLM)
- Staging and production environment configurations
- Automated customer update mechanism

### 5.3 Explicitly Out of Scope

- Real-time / streaming data ingestion
- OMOP CDM support (PCORnet only, may revisit)
- Direct EHR integrations beyond FHIR and athenahealth (Epic, Cerner, etc.)
- Mobile application
- Multi-tenant architecture (single-tenant per deployment)
- Data write-back to source EHR systems
- Custom ML model training within the platform
- Hosted SaaS deployment (customer-deployed only)

---

## 6. Feature Requirements

### 6.1 Feature: FHIR Data Ingestion

- **Priority:** Must Have
- **User Story:** As an Admin, I want to connect a FHIR server and ingest patient data so that it is available in the PCORnet CDM for analysis.
- **Acceptance Criteria:**
  - [ ] Admin can configure FHIR connection (server URL, auth type, client ID/secret) via UI
  - [ ] System auto-detects FHIR version (R4 or R5)
  - [ ] Batch ingestion processes ~100K records
  - [ ] Incremental sync tracks last-synced cursor, only pulls new/changed records
  - [ ] FHIR resources map to PCORnet CDM v7.0 tables (Patient→DEMOGRAPHIC, Encounter→ENCOUNTER, Condition→DIAGNOSIS, etc.)
  - [ ] Pydantic validation ensures data conforms to PCORnet schema
  - [ ] Failed records are quarantined with error details
  - [ ] Ingestion progress and status visible in UI
- **Technical Notes:** Uses fhirpy (async client) + fhir.resources (Pydantic models). Mapping based on HL7 CDMH Implementation Guide.

### 6.2 Feature: Athena DataView Ingestion

- **Priority:** Must Have
- **User Story:** As an Admin, I want to connect to athenahealth DataView via Snowflake and ingest patient data into the PCORnet CDM.
- **Acceptance Criteria:**
  - [ ] Admin can configure Snowflake connection (account, username, password, database, schema, warehouse, role) via UI
  - [ ] System queries DataView tables from Snowflake
  - [ ] Data maps to PCORnet CDM v7.0 tables
  - [ ] Incremental sync supported
  - [ ] Failed records quarantined
- **Technical Notes:** Uses snowflake-connector-python. DataView schema to be discovered during development.

### 6.3 Feature: PCORnet CDM Data Store

- **Priority:** Must Have
- **User Story:** As an Analyst, I want all ingested data stored in PCORnet CDM v7.0 format so I can query it using standard PCORnet table structures.
- **Acceptance Criteria:**
  - [ ] All PCORnet CDM v7.0 core tables created in PostgreSQL (DEMOGRAPHIC, ENCOUNTER, DIAGNOSIS, PROCEDURES, VITAL, LAB_RESULT_CM, PRESCRIBING, DISPENSING, CONDITION, DEATH, DEATH_CAUSE, ENROLLMENT, HARVEST, LDS_ADDRESS_HISTORY, MED_ADMIN, OBS_CLIN, OBS_GEN, PCORNET_TRIAL, PRO_CM, PROVIDER, IMMUNIZATION, HASH_TOKEN)
  - [ ] SQLAlchemy models with Pydantic validation for all tables
  - [ ] Query Adapter interface abstracts database access (PostgreSQL adapter for MVP)
- **Technical Notes:** Query Adapter pattern enables future swap to Databricks/Athena/Fabric without changing application code.

### 6.4 Feature: SQL Query Editor

- **Priority:** Must Have
- **User Story:** As an Analyst, I want a Databricks-like SQL editor so I can write, run, and save SQL queries against the PCORnet CDM.
- **Acceptance Criteria:**
  - [ ] Monaco Editor with SQL syntax highlighting and IntelliSense
  - [ ] Schema-aware autocomplete (PCORnet table and column names)
  - [ ] Data Explorer tree view (tables → columns) in left sidebar
  - [ ] Click-to-insert table/column names from Data Explorer
  - [ ] Multi-tab query interface
  - [ ] Run query button, keyboard shortcut (Ctrl+Enter)
  - [ ] Results displayed in AG Grid (sort, filter, pagination, column resize)
  - [ ] Query history with timestamps
  - [ ] Save/load named queries
  - [ ] CSV and Excel export of results
  - [ ] Read-only queries only (SELECT)
  - [ ] Resizable split pane between editor and results
- **Technical Notes:** Databricks-style UI. react-resizable-panels for split panes.

### 6.5 Feature: Agentic AI Search

- **Priority:** Must Have
- **User Story:** As a Business User, I want to ask questions in plain English and get data-driven answers so I don't need to know SQL.
- **Acceptance Criteria:**
  - [ ] Chat interface (multi-turn conversational) with streaming responses
  - [ ] Single query box for quick one-off questions
  - [ ] Agent decomposes complex questions into sub-queries (e.g., "How many diabetic patients over 60 had ER visits in the last 6 months and were prescribed metformin?" → 4 sub-queries)
  - [ ] Agent generates read-only SQL (SELECT only)
  - [ ] Shows generated SQL for transparency
  - [ ] Results stored in database table
  - [ ] CSV and Excel export of agent results
  - [ ] Token-by-token streaming via WebSocket (ChatGPT-like experience)
  - [ ] BYOM: AWS Bedrock as default LLM provider, expandable via adapter
- **Technical Notes:** LangChain + LangGraph with ReAct pattern. LLM Provider Adapter abstracts Bedrock; future providers added without code changes.

### 6.6 Feature: Dashboards

- **Priority:** Must Have
- **User Story:** As a Business User, I want to view pre-built dashboards and create custom ones so I can visualize patient data trends.
- **Acceptance Criteria:**
  - [ ] Pre-built dashboard templates: Patient Demographics, Encounter Trends, Diagnosis Distribution, Lab Results Summary, Prescription Analytics
  - [ ] Self-service dashboard builder: add widgets, configure data source, drag-and-drop, resize
  - [ ] Widget types: bar chart, line chart, pie chart, area chart, donut chart, KPI card, data table, funnel chart
  - [ ] Dashboard layout saved and persisted
  - [ ] Dashboards accessible to all roles (Viewer can view, Analyst/Admin can build)
- **Technical Notes:** Tremor for charts, react-grid-layout for drag-and-drop grid.

### 6.7 Feature: Integration Configuration Dashboard

- **Priority:** Must Have
- **User Story:** As an Admin, I want to configure data source connections through the UI so I don't need to edit config files.
- **Acceptance Criteria:**
  - [ ] FHIR connection form (server URL, auth type, client ID/secret, FHIR version)
  - [ ] Snowflake connection form (account, username, password, database, schema, warehouse, role)
  - [ ] Connection test button (verify connectivity before saving)
  - [ ] View active integrations and their status
  - [ ] Trigger manual ingestion run
  - [ ] View ingestion history (runs, record counts, errors)
- **Technical Notes:** Admin-only access. Credentials stored securely in PostgreSQL.

### 6.8 Feature: Quarantine Management

- **Priority:** Must Have
- **User Story:** As an Admin, I want to review records that failed to ingest so I can identify data quality issues.
- **Acceptance Criteria:**
  - [ ] Quarantine table stores failed records with source data, error message, timestamp
  - [ ] UI to browse, filter, and search quarantined records
  - [ ] Error details (which field failed, why)
  - [ ] Counts and trends of quarantine rates per ingestion run

### 6.9 Feature: User Management & Authentication

- **Priority:** Must Have
- **User Story:** As an Admin, I want to create and manage user accounts with different roles so I can control access to the platform.
- **Acceptance Criteria:**
  - [ ] Login page (username/password)
  - [ ] JWT-based authentication with HTTP-only cookies
  - [ ] Three roles: Admin, Analyst, Viewer
  - [ ] Admin can create, edit, deactivate users
  - [ ] Admin can assign/change user roles
  - [ ] Password hashing with bcrypt
  - [ ] Session expiry with token refresh

### 6.10 Feature: Health Dashboard & Logging

- **Priority:** Must Have
- **User Story:** As an Admin, I want to see the platform's health status and view logs so I can troubleshoot issues.
- **Acceptance Criteria:**
  - [ ] Health dashboard showing: system status, ingestion health, error counts, last successful ingestion
  - [ ] In-app log viewer (Admin only) with search and filter
  - [ ] Structured JSON logs to stdout for Docker-native log aggregation
  - [ ] No PHI in any log output (sanitized)
  - [ ] Audit log entries for: user logins, SQL query executions, data exports, ingestion runs

---

## 7. Technical Architecture

### 7.1 System Overview

```
┌──────────────────────────────────────────────────────────────┐
│              MODULAR MONOLITH (Docker Compose)                │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────────────┐  │
│  │ FHIR     │  │ Snowflake│  │ Transformation Engine     │  │
│  │ Ingestion│  │ Ingestion│  │ (FHIR/DataView → PCORnet) │  │
│  │ Module   │  │ Module   │  │ Pydantic Validation       │  │
│  └─────┬────┘  └────┬─────┘  └─────────────┬─────────────┘  │
│        └──────┬──────┘                      │                │
│               ▼                             ▼                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Query Adapter Interface                   │    │
│  │  ┌────────────┐  ┌──────────┐  ┌──────┐  ┌────────┐ │    │
│  │  │  Postgres  │  │Databricks│  │Athena│  │ Fabric │ │    │
│  │  │  Adapter   │  │ (future) │  │(fut.)│  │ (fut.) │ │    │
│  │  └────────────┘  └──────────┘  └──────┘  └────────┘ │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │
│  │  Auth    │  │  SQL     │  │  Agentic  │  │ Dashboard │  │
│  │  Module  │  │  Query   │  │  Search   │  │  Module   │  │
│  │  (JWT/   │  │  Module  │  │  Module   │  │  (Tremor/ │  │
│  │  RBAC)   │  │ (Monaco) │  │(LangGraph)│  │  Grid)    │  │
│  └──────────┘  └──────────┘  └───────────┘  └───────────┘  │
│                                                              │
│  ┌──────────┐  ┌──────────┐                                 │
│  │  Audit   │  │  Health  │                                 │
│  │  Module  │  │  Module  │                                 │
│  └──────────┘  └──────────┘                                 │
└──────────────────────────────────────────────────────────────┘

External Dependencies:
├── PostgreSQL (data store)
├── AWS Bedrock (LLM API — via internet)
└── Customer's FHIR Server / Snowflake (data sources)
```

### 7.2 Design Patterns

- **Modular Monolith:** Single deployable unit with strictly isolated internal modules. Each module has its own domain models, services, and routes. Modules communicate via internal Python interfaces, not network calls.
- **Query Adapter Pattern:** Abstract interface for database operations. PostgreSQL adapter implements the interface for MVP. Future adapters (Databricks, Athena, Fabric) implement the same interface, enabling database swap via configuration.
- **LLM Provider Adapter:** Abstract interface for LLM calls. AWS Bedrock adapter for MVP. Future adapters for OpenAI, Anthropic, Azure OpenAI, Ollama/vLLM.
- **Repository Pattern:** Data access through repository classes, not direct ORM queries in business logic.
- **Dependency Injection:** FastAPI's built-in DI for auth, role checks, and service injection.

### 7.3 Data Flow

```
1. INGESTION FLOW
   FHIR Server / Snowflake
     → Ingestion Module (fetch raw data, incremental cursor)
     → Transformation Engine (map to PCORnet CDM, Pydantic validate)
     → Success → PostgreSQL (PCORnet tables)
     → Failure → Quarantine Table (with error details)

2. QUERY FLOW (SQL)
   User writes SQL in Monaco Editor
     → REST API (/api/v1/query/)
     → Query Adapter (PostgreSQL adapter)
     → Execute SELECT query
     → Return results → AG Grid
     → Optional: Export CSV/Excel

3. QUERY FLOW (Agent)
   User asks natural language question
     → WebSocket (/api/v1/agent/ws)
     → LangGraph Agent (ReAct loop)
       → Step 1: Decompose question into sub-queries
       → Step 2: Generate SQL per sub-query (SELECT only)
       → Step 3: Execute via Query Adapter
       → Step 4: Synthesize results
       → Step 5: Stream answer token-by-token
     → Store results in results table
     → Optional: Export CSV/Excel

4. DASHBOARD FLOW
   Dashboard loads → fetch widget configs
     → Each widget calls data endpoint
     → Query Adapter returns aggregated data
     → Tremor renders charts
```

---

## 8. Tech Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Frontend** | Next.js (React/TypeScript) | 15.x | Best AI code generation, richest dashboard ecosystem |
| UI Components | shadcn/ui + Tailwind CSS | Latest | Consistent, accessible, Databricks-style theming |
| SQL Editor | Monaco Editor (react-monaco-editor) | Latest | VS Code engine, SQL IntelliSense |
| Charts | Tremor | Latest | 35+ chart types, Tailwind CSS styled |
| Dashboard Grid | react-grid-layout | Latest | Drag-and-drop, resizable (used by Grafana) |
| Data Tables | AG Grid (community) | Latest | Sort, filter, pagination, export |
| Split Panes | react-resizable-panels | Latest | IDE-style resizable panels |
| Command Palette | cmdk (via shadcn/ui) | Latest | Ctrl+K search |
| Export | SheetJS (xlsx) | Latest | Excel export |
| E2E Tests | Playwright | Latest | Browser automation |
| Unit Tests | Vitest + React Testing Library | Latest | Component testing |
| **Backend** | FastAPI (Python) | 0.115+ | Async-native, Pydantic v2, AI ecosystem |
| ORM | SQLAlchemy (async) | 2.x | Standard Python ORM, Query Adapter compatible |
| Validation | Pydantic v2 | 2.x | PCORnet CDM schema validation |
| FHIR Client | fhirpy | 2.x | Async FHIR R4/R5 client |
| FHIR Models | fhir.resources | 8.x | Pydantic FHIR resource models |
| Snowflake | snowflake-connector-python | 3.x | athenahealth DataView connector |
| Agent Framework | LangChain + LangGraph | 0.3.x | Query decomposition, ReAct pattern |
| LLM Provider | langchain-aws (ChatBedrock) | Latest | AWS Bedrock integration |
| Auth | python-jose (JWT) + passlib (bcrypt) | Latest | Token auth + password hashing |
| Logging | structlog | Latest | Structured JSON logging |
| Unit Tests | pytest + pytest-asyncio | Latest | Async test support |
| Integration Tests | testcontainers | Latest | DB + service testing |
| API Tests | httpx | Latest | Async HTTP client for testing |
| **Database** | PostgreSQL | 16.x | Primary data store (MVP) |
| **Search** | OpenSearch | Latest | Unstructured data (post-MVP) |
| **DevOps** | Docker Compose | Latest | Deployment packaging |
| CI/CD | GitLab CI | Latest | Pipeline automation |
| Registry | GitLab Container Registry | Latest | Free Docker image hosting |
| Source Control | GitLab | Latest | Code repository |

See: [tech-research.md](./tech-research.md) for detailed tool comparisons.

---

## 9. Data Model

### 9.1 Entity Relationship Overview

The core data model follows the **PCORnet CDM v7.0** specification. All ingested data (from FHIR and athenahealth DataView) is transformed into this canonical model.

Reference: [PCORnet CDM v7.0 Specification](https://pcornet.org/wp-content/uploads/2025/05/PCORnet_Common_Data_Model_v70_2025_05_01.pdf)

### 9.2 Key Entities (PCORnet CDM v7.0 Tables)

| Table | Description | Key Fields |
|-------|------------|------------|
| DEMOGRAPHIC | Patient demographics | PATID, BIRTH_DATE, SEX, RACE, HISPANIC, SEXUAL_ORIENTATION |
| ENCOUNTER | Patient encounters/visits | ENCOUNTERID, PATID, ENC_TYPE, ADMIT_DATE, DISCHARGE_DATE |
| DIAGNOSIS | Diagnoses | DIAGNOSISID, PATID, ENCOUNTERID, DX, DX_TYPE, DX_SOURCE |
| PROCEDURES | Procedures performed | PROCEDURESID, PATID, ENCOUNTERID, PX, PX_TYPE |
| VITAL | Vital signs | VITALID, PATID, ENCOUNTERID, HT, WT, SYSTOLIC, DIASTOLIC |
| LAB_RESULT_CM | Lab results | LAB_RESULT_CM_ID, PATID, ENCOUNTERID, LAB_LOINC, RESULT_NUM |
| PRESCRIBING | Prescriptions | PRESCRIBINGID, PATID, ENCOUNTERID, RXNORM_CUI |
| DISPENSING | Medication dispensing | DISPENSINGID, PATID, NDC |
| CONDITION | Conditions | CONDITIONID, PATID, CONDITION, CONDITION_TYPE |
| DEATH | Death records | PATID, DEATH_DATE, DEATH_SOURCE |
| DEATH_CAUSE | Cause of death | PATID, DEATH_CAUSE, DEATH_CAUSE_CODE |
| ENROLLMENT | Enrollment periods | PATID, ENR_START_DATE, ENR_END_DATE |
| HARVEST | Data source metadata | NETWORKID, REFRESH_DATE |
| LDS_ADDRESS_HISTORY | Address history | PATID, ADDRESS_ZIP5, ADDRESS_COUNTY |
| MED_ADMIN | Medication administration | MEDADMINID, PATID, ENCOUNTERID |
| OBS_CLIN | Clinical observations | OBSCLINID, PATID, ENCOUNTERID |
| OBS_GEN | General observations | OBSGENID, PATID, ENCOUNTERID |
| PCORNET_TRIAL | Clinical trial enrollment | PATID, TRIALID |
| PRO_CM | Patient-reported outcomes | PRO_CM_ID, PATID, ENCOUNTERID |
| PROVIDER | Provider information | PROVIDERID, PROVIDER_SPECIALTY |
| IMMUNIZATION | Immunizations | IMMUNIZATIONID, PATID, VX_CODE |
| HASH_TOKEN | De-identified patient tokens | PATID, TOKEN_ENCRYPTION_KEY |

### 9.3 Platform-Specific Tables (Non-PCORnet)

| Table | Description |
|-------|------------|
| users | Platform user accounts (id, username, email, password_hash, role, created_at) |
| integrations | Data source connection configs (id, type, config_json, status, created_by) |
| ingestion_runs | Ingestion batch history (id, integration_id, status, records_processed, records_failed, started_at, completed_at) |
| quarantine | Failed ingestion records (id, ingestion_run_id, source_data, error_message, source_table, created_at) |
| saved_queries | User-saved SQL queries (id, user_id, name, sql_text, created_at) |
| query_history | SQL query execution log (id, user_id, sql_text, executed_at, row_count, duration_ms) |
| query_results | Stored results from agent queries (id, user_id, query_text, result_data, created_at) |
| dashboards | Dashboard definitions (id, user_id, name, layout_json, created_at) |
| dashboard_widgets | Widget configurations (id, dashboard_id, type, config_json, position_json) |
| audit_log | Access audit trail (id, user_id, action, details, ip_address, timestamp) |
| chat_sessions | Agent chat history (id, user_id, started_at) |
| chat_messages | Individual chat messages (id, session_id, role, content, sql_generated, created_at) |

### 9.4 Data Storage Strategy

- **Structured data (PCORnet CDM):** PostgreSQL (MVP), swappable via Query Adapter
- **Unstructured data (PDFs, clinical notes):** OpenSearch (post-MVP)
- **Application data (users, configs, audit):** PostgreSQL (always, not swappable)

---

## 10. API Design

### 10.1 API Style

- **REST API** with `/api/v1/` prefix
- **WebSocket** for agent chat streaming
- **Auto-generated documentation** via FastAPI OpenAPI (Swagger UI at `/docs`, ReDoc at `/redoc`)

### 10.2 Key Endpoints

```
Authentication
  POST   /api/v1/auth/login              — Login, returns JWT
  POST   /api/v1/auth/logout             — Logout, invalidate token
  POST   /api/v1/auth/refresh            — Refresh access token
  GET    /api/v1/auth/me                 — Current user profile

User Management (Admin only)
  GET    /api/v1/users/                  — List all users
  POST   /api/v1/users/                  — Create user
  PATCH  /api/v1/users/{id}             — Update user (role, status)
  DELETE /api/v1/users/{id}             — Deactivate user

Integrations (Admin only)
  GET    /api/v1/integrations/           — List configured integrations
  POST   /api/v1/integrations/           — Create integration config
  PATCH  /api/v1/integrations/{id}      — Update integration
  POST   /api/v1/integrations/{id}/test — Test connection
  DELETE /api/v1/integrations/{id}      — Remove integration

Ingestion (Admin only)
  POST   /api/v1/ingestion/{integration_id}/run  — Trigger batch ingestion
  GET    /api/v1/ingestion/runs                   — List ingestion runs
  GET    /api/v1/ingestion/runs/{id}              — Run details + stats
  GET    /api/v1/ingestion/runs/{id}/status       — Run status (polling)

Quarantine (Admin only)
  GET    /api/v1/quarantine/             — List quarantined records (paginated)
  GET    /api/v1/quarantine/{id}        — Record details + error info
  GET    /api/v1/quarantine/stats       — Quarantine statistics

SQL Query (Admin, Analyst)
  POST   /api/v1/query/execute           — Execute SQL query (SELECT only)
  GET    /api/v1/query/history           — Query history
  GET    /api/v1/query/saved             — List saved queries
  POST   /api/v1/query/saved             — Save a query
  PATCH  /api/v1/query/saved/{id}       — Update saved query
  DELETE /api/v1/query/saved/{id}       — Delete saved query

Data Explorer (Admin, Analyst)
  GET    /api/v1/schema/tables           — List PCORnet tables
  GET    /api/v1/schema/tables/{name}/columns — List columns for a table

Agent (Admin, Analyst)
  POST   /api/v1/agent/query             — Single query (non-streaming)
  WS     /api/v1/agent/ws                — WebSocket for streaming chat
  GET    /api/v1/agent/sessions          — List chat sessions
  GET    /api/v1/agent/sessions/{id}    — Chat session history
  GET    /api/v1/agent/results/{id}     — Get stored agent results

Dashboards (Admin, Analyst can edit; Viewer can read)
  GET    /api/v1/dashboards/             — List dashboards
  POST   /api/v1/dashboards/             — Create dashboard
  GET    /api/v1/dashboards/{id}        — Get dashboard with widgets
  PATCH  /api/v1/dashboards/{id}        — Update dashboard layout
  DELETE /api/v1/dashboards/{id}        — Delete dashboard
  POST   /api/v1/dashboards/{id}/widgets — Add widget
  PATCH  /api/v1/dashboards/{id}/widgets/{wid} — Update widget config
  DELETE /api/v1/dashboards/{id}/widgets/{wid} — Remove widget
  GET    /api/v1/dashboards/templates    — List pre-built templates

Export (Admin, Analyst)
  GET    /api/v1/export/{result_id}/csv  — Download results as CSV
  GET    /api/v1/export/{result_id}/xlsx — Download results as Excel

Health & Monitoring (Admin only)
  GET    /api/v1/health/                 — Platform health status
  GET    /api/v1/health/ingestion        — Ingestion health summary
  GET    /api/v1/logs/                   — Application logs (paginated, filtered)

Audit (Admin only)
  GET    /api/v1/audit/                  — Audit log entries (paginated)
```

### 10.3 Authentication & Rate Limiting

- **Authentication:** JWT tokens via OAuth2PasswordBearer. Access tokens are short-lived, stored in HTTP-only cookies. Refresh tokens for session continuity.
- **Rate Limiting:** Not in MVP. Consider adding for agent endpoints in future to manage LLM API costs.

---

## 11. Third-Party Integrations

| Service | Purpose | Pricing Model |
|---------|---------|--------------|
| AWS Bedrock | LLM provider for agentic search | Pay-per-token (Claude/Titan models) |
| FHIR Server (customer's) | Source data — patient records via FHIR R4/R5 | Customer's own infrastructure |
| athenahealth DataView (via Snowflake) | Source data — athenahealth EHR data | Customer's Snowflake account |

---

## 12. Security & Compliance

### 12.1 Authentication Method

- Username/password with JWT tokens (OAuth2PasswordBearer)
- bcrypt password hashing (passlib)
- HTTP-only cookies for token storage
- Short-lived access tokens with refresh mechanism
- SSO (Okta, Azure AD) planned for post-MVP

### 12.2 Authorization Model

Role-Based Access Control (RBAC) with three roles:

| Permission | Admin | Analyst | Viewer |
|------------|-------|---------|--------|
| Manage users | ✅ | ❌ | ❌ |
| Configure integrations | ✅ | ❌ | ❌ |
| Platform settings | ✅ | ❌ | ❌ |
| Run SQL queries | ✅ | ✅ | ❌ |
| Use agentic search | ✅ | ✅ | ❌ |
| Build/edit dashboards | ✅ | ✅ | ❌ |
| View dashboards | ✅ | ✅ | ✅ |
| Export data (CSV/Excel) | ✅ | ✅ | ❌ |
| View query history | ✅ | ✅ | ❌ |
| View health/logs | ✅ | ❌ | ❌ |
| View audit log | ✅ | ❌ | ❌ |

### 12.3 Data Protection

- **In Transit:** TLS/HTTPS for all communication (MVP)
- **At Rest:** Encryption planned for post-MVP
- **PHI Protection:** No PHI in application logs — all log output sanitized via structlog processors
- **Data Retention:** Data retained indefinitely until explicit deletion request from customer
- **Agent Guardrails:** Read-only SQL only (SELECT). No DDL/DML operations permitted via agent or SQL editor.

### 12.4 Compliance Requirements

- **HIPAA Compliance:** Required. Platform handles PHI (Protected Health Information).
- **BAA (Business Associate Agreement):** Required with AWS for Bedrock usage. AWS Bedrock is HIPAA-eligible.
- **Audit Trail:** All user logins, SQL query executions, data exports, and ingestion runs are logged with timestamps and user IDs.
- **PHI in LLM Prompts:** Must evaluate whether PHI is included in prompts sent to Bedrock. If yes, BAA must cover this. Recommend stripping PHI before sending to LLM where possible.

---

## 13. Testing Strategy

| Type | Tool | Coverage Target |
|------|------|----------------|
| Unit (Backend) | pytest + pytest-asyncio | All services, transformations, adapters |
| Unit (Frontend) | Vitest + React Testing Library | All components, hooks, utilities |
| Integration | pytest + testcontainers | DB queries, ingestion pipeline, agent flow |
| E2E | Playwright | Critical user flows (login → query → export → dashboard) |
| CDM Mapping | pytest (dedicated suite) | 100% of FHIR→PCORnet resource type mappings |
| API Contract | pytest + httpx | All REST endpoints |
| CI Pipeline | GitLab CI | All tests run on every merge request |

### CDM Mapping Test Suite

A dedicated test suite with curated FHIR R4/R5 bundles as fixtures. Each fixture has expected PCORnet CDM output. Tests validate:
- Every FHIR resource type maps correctly (Patient→DEMOGRAPHIC, Encounter→ENCOUNTER, etc.)
- Edge cases (missing fields, invalid codes) route to quarantine
- Incremental updates don't create duplicates
- Data type conversions are correct (dates, codes, numeric values)

---

## 14. DevOps & Infrastructure

### 14.1 Hosting / Cloud Provider

Customer-deployed. The platform runs on the customer's own infrastructure:
- On-premise servers
- Private cloud (AWS, Azure, GCP)
- Any environment that supports Docker

### 14.2 CI/CD Pipeline

```
GitLab CI Pipeline:
  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
  │ Lint │ →  │ Test │ →  │Build │ →  │ Push │ →  │Deploy│
  │      │    │      │    │Docker│    │Image │    │ (dev)│
  └──────┘    └──────┘    └──────┘    └──────┘    └──────┘
  - ruff       - pytest    - docker     - GitLab    - docker
  - eslint     - vitest      build       Container   compose
  - mypy       - playwright              Registry     up
```

### 14.3 Environment Strategy

- **Dev:** Active for MVP development
- **Staging:** Planned for post-MVP (pre-release testing)
- **Production:** Customer-managed deployments

### 14.4 Containerization & Orchestration

**Docker Compose** with the following services:

```yaml
services:
  backend:      # FastAPI application
  frontend:     # Next.js application
  postgres:     # PostgreSQL 16
  # Future:
  # opensearch: # OpenSearch (post-MVP)
```

---

## 15. Monitoring & Observability

### 15.1 Logging

- **Library:** Python `structlog` for structured JSON logging
- **Output:** JSON to stdout (Docker-native, customers can pipe to their log aggregator)
- **In-App Viewer:** Admin-only log viewer with search and filter in the platform UI
- **PHI Sanitization:** Custom structlog processor strips all PHI fields before logging

### 15.2 Metrics & Alerting

- **MVP:** No metrics endpoint. Basic health checks only.
- **Post-MVP:** Prometheus-compatible `/metrics` endpoint planned. Customers can scrape with their monitoring stack.

### 15.3 Error Tracking

- **Built-in Health Dashboard** (Admin only):
  - System status (services up/down)
  - Ingestion health (last run, success/failure rates, quarantine counts)
  - Error counts and recent errors
  - Database connection status

---

## 16. Performance Requirements

| Metric | Target |
|--------|--------|
| SQL Query Response (p95) | < 5 seconds for queries against 100K records |
| SQL Query Response (p95) | < 30 seconds for queries against 1M records |
| Agent Response (first token) | < 3 seconds |
| Agent Response (full answer) | < 30 seconds for simple questions |
| Dashboard Load Time | < 3 seconds |
| Ingestion Throughput | ~100K records per batch |
| Concurrent Users | 50 per deployment |
| API Response (non-query) | < 500ms (p95) |

---

## 17. Cost Estimation

| Item | Monthly Estimate | Notes |
|------|-----------------|-------|
| AWS Bedrock (LLM) | $200–$2,000 | Depends on query volume and model choice (Claude vs Titan) |
| Customer Infrastructure | Customer-owned | Docker Compose on their servers |
| GitLab (SaaS) | $0–$29/user | Free tier or Premium |
| GitLab Container Registry | $0 | Included with GitLab |
| Development (2 devs) | [Internal cost] | Team salary |
| Snowflake (DataView) | Customer-owned | Customer's existing Snowflake account |

**Note:** Since the platform is customer-deployed, the primary recurring cost for the product team is development and GitLab. Customers bear infrastructure and LLM API costs.

---

## 18. Milestones & Timeline

| Milestone | Description | Dependencies |
|-----------|------------|--------------|
| **M1: Foundation & FHIR Ingestion** | Project setup, PCORnet CDM schema, auth, FHIR ingestion pipeline, integration dashboard, Docker Compose, GitLab CI | None |
| **M2: SQL Editor & Query Engine** | Query Adapter + PostgreSQL adapter, Monaco SQL editor, Data Explorer, results table (AG Grid), query history, saved queries, CSV/Excel export | M1 |
| **M3: Agentic Search** | LLM Provider Adapter (Bedrock), LangGraph agent (ReAct + decomposition), WebSocket streaming, chat UI, single query mode | M1, M2 |
| **M4: Dashboards** | Dashboard CRUD API, Tremor charts, react-grid-layout builder, pre-built templates, widget configuration | M2 |
| **M5: Athena DataView Integration** | Snowflake ingestion module, DataView schema discovery, PCORnet mapping, Snowflake connection UI | M1 (can parallel with M2/M3) |
| **M6: Hardening & Polish** | Structured logging (structlog), audit logging, health dashboard, E2E tests (Playwright), security hardening (TLS, CORS), deployment guide | M1–M5 |

### Milestone Dependency Chain

```
M1: Foundation & FHIR ──→ M2: SQL Editor ──→ M3: Agent ──→ M4: Dashboards
                     └──→ M5: Athena DataView (parallel with M2/M3)
                                                          └──→ M6: Hardening
```

### Team Allocation

| Dev | Primary Track | Secondary |
|-----|--------------|-----------|
| Dev 1 | Backend (FastAPI, ingestion, agent, APIs) | DevOps (Docker, CI) |
| Dev 2 | Frontend (Next.js, Monaco, dashboards, chat UI) | E2E tests |

---

## 19. Epics & Task Breakdown

### Epic 1: Project Foundation
| Story | Description | Complexity | Dependencies |
|-------|-------------|-----------|--------------|
| 1.1 | FastAPI project setup with modular structure | S | None |
| 1.2 | Next.js project setup with shadcn/ui + Tailwind | S | None |
| 1.3 | Docker Compose (FastAPI + PostgreSQL + Next.js) | S | 1.1, 1.2 |
| 1.4 | GitLab CI pipeline (lint, test, build) | M | 1.3 |
| 1.5 | PCORnet CDM v7.0 SQLAlchemy models (all core tables) | L | 1.1 |
| 1.6 | Query Adapter interface + PostgreSQL adapter | M | 1.5 |
| 1.7 | Database migrations setup (Alembic) | S | 1.5 |

### Epic 2: Authentication & User Management
| Story | Description | Complexity | Dependencies |
|-------|-------------|-----------|--------------|
| 2.1 | JWT auth backend (login, logout, refresh, bcrypt) | M | 1.1 |
| 2.2 | RBAC middleware (Admin, Analyst, Viewer role checks) | M | 2.1 |
| 2.3 | Login page UI | S | 1.2 |
| 2.4 | User management UI (Admin: create, edit, deactivate users) | M | 2.1, 2.2 |

### Epic 3: FHIR Data Ingestion
| Story | Description | Complexity | Dependencies |
|-------|-------------|-----------|--------------|
| 3.1 | FHIR connection config API (CRUD) | M | 2.2 |
| 3.2 | FHIR connection config UI (Admin integration dashboard) | M | 3.1 |
| 3.3 | FHIR client (fhirpy) with R4/R5 auto-detection | L | 1.1 |
| 3.4 | FHIR→PCORnet mapping engine (Patient→DEMOGRAPHIC, Encounter→ENCOUNTER, etc.) | L | 1.5, 3.3 |
| 3.5 | Batch ingestion orchestrator (incremental sync, cursor tracking) | L | 3.4 |
| 3.6 | Quarantine system (failed records table, error logging) | M | 3.5 |
| 3.7 | Ingestion status API + UI (progress, history, errors) | M | 3.5 |
| 3.8 | Quarantine viewer UI | M | 3.6 |
| 3.9 | CDM mapping test suite (FHIR R4/R5 fixtures) | L | 3.4 |

### Epic 4: SQL Editor & Query Engine
| Story | Description | Complexity | Dependencies |
|-------|-------------|-----------|--------------|
| 4.1 | SQL execution endpoint (read-only, via Query Adapter) | M | 1.6 |
| 4.2 | Monaco SQL Editor component (syntax highlighting, autocomplete) | L | 1.2 |
| 4.3 | Schema-aware autocomplete (PCORnet table/column names) | M | 4.1, 4.2 |
| 4.4 | Data Explorer tree view (tables → columns) | M | 4.1 |
| 4.5 | Results table (AG Grid with sort/filter/pagination) | M | 4.1 |
| 4.6 | Query history API + UI | M | 4.1 |
| 4.7 | Saved queries CRUD API + UI | M | 4.1 |
| 4.8 | CSV/Excel export endpoints + UI buttons | M | 4.1 |
| 4.9 | Resizable split panes (editor/results, sidebar/content) | S | 4.2 |
| 4.10 | Multi-tab query interface | M | 4.2 |
| 4.11 | Databricks-style layout (dark sidebar, light content) | M | 4.2, 4.4 |

### Epic 5: Agentic Search
| Story | Description | Complexity | Dependencies |
|-------|-------------|-----------|--------------|
| 5.1 | LLM Provider Adapter interface + Bedrock adapter | M | 1.1 |
| 5.2 | LangGraph agent with ReAct loop + query decomposition | L | 5.1, 1.6 |
| 5.3 | SQL generation guardrails (SELECT only validation) | M | 5.2 |
| 5.4 | WebSocket streaming endpoint | M | 5.2 |
| 5.5 | Chat UI (multi-turn, streaming display, show SQL) | L | 5.4 |
| 5.6 | Single query mode UI | M | 5.2 |
| 5.7 | Agent results storage + export | M | 5.2 |
| 5.8 | Chat session history API + UI | M | 5.2 |

### Epic 6: Dashboards
| Story | Description | Complexity | Dependencies |
|-------|-------------|-----------|--------------|
| 6.1 | Dashboard CRUD API (layouts, widgets) | M | 1.6 |
| 6.2 | Widget data endpoints (aggregated chart data) | M | 6.1 |
| 6.3 | Dashboard viewer (Tremor charts rendering) | L | 6.2 |
| 6.4 | Dashboard builder (add widget, configure, drag-and-drop) | L | 6.3 |
| 6.5 | Pre-built templates (5 templates) | M | 6.3 |
| 6.6 | Widget types (bar, line, pie, area, donut, KPI, table, funnel) | L | 6.3 |

### Epic 7: Athena DataView Integration
| Story | Description | Complexity | Dependencies |
|-------|-------------|-----------|--------------|
| 7.1 | Snowflake connection config API + UI | M | 3.1 |
| 7.2 | Snowflake ingestion module | L | 7.1 |
| 7.3 | DataView schema discovery | M | 7.2 |
| 7.4 | DataView → PCORnet mapping | L | 7.3, 3.4 |
| 7.5 | Integration tests with Snowflake test data | M | 7.4 |

### Epic 8: Hardening & Observability
| Story | Description | Complexity | Dependencies |
|-------|-------------|-----------|--------------|
| 8.1 | Structured logging (structlog) + PHI sanitization | M | 1.1 |
| 8.2 | Audit logging (logins, queries, exports, ingestion) | M | 8.1 |
| 8.3 | Health dashboard API | M | 1.1 |
| 8.4 | Health dashboard UI | M | 8.3 |
| 8.5 | In-app log viewer (Admin) | M | 8.1 |
| 8.6 | E2E tests (Playwright — login, query, dashboard flows) | L | All epics |
| 8.7 | Security hardening (TLS config, CORS, rate limiting, input validation) | M | 1.1 |
| 8.8 | Production Docker Compose (TLS, env configs, health checks) | M | 1.3 |
| 8.9 | Customer deployment guide | M | 8.8 |

**Complexity Guide:** S = < 1 day, M = 1–3 days, L = 3–5+ days

---

## 20. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| FHIR→PCORnet mapping complexity (edge cases, non-standard FHIR data) | High | High | Dedicated CDM mapping test suite; quarantine system captures failures; iterative mapping improvement |
| athenahealth DataView schema unknown until development | Medium | Medium | Plan for schema discovery phase; flexible mapping engine |
| LangChain breaking changes between versions | Medium | Medium | Pin versions; abstract via LLM Provider Adapter; monitor changelogs |
| Agent generates incorrect SQL | Medium | High | Read-only guardrails; show SQL for transparency; user can verify before trusting results |
| PHI leakage in LLM prompts | Medium | High | Strip PHI before sending to Bedrock where possible; BAA with AWS; audit all LLM calls |
| PHI leakage in application logs | Low | High | structlog PHI sanitization processor; automated tests to verify no PHI in log output |
| PostgreSQL performance at millions of records | Medium | Medium | Query Adapter enables migration to Databricks/Athena; index optimization; query timeout limits |
| Two-developer team bandwidth | High | Medium | Parallel frontend/backend tracks; prioritize MVP features; defer post-MVP items aggressively |
| Customer deployment issues (Docker Compose variability) | Medium | Medium | Comprehensive deployment guide; health check endpoints; structured logging for debugging |
| HIPAA compliance gaps | Low | High | Security audit before first customer deployment; TLS enforcement; audit logging from day one |

---

## 21. Open Questions

- [ ] What specific FHIR resources will customers' servers expose? (Determines mapping priority)
- [ ] Will PHI be included in LLM prompts sent to Bedrock? (Affects BAA scope and prompt engineering)
- [ ] What is the customer update/upgrade mechanism? (Docker image versioning strategy)
- [ ] Should the platform support multiple simultaneous FHIR server connections per deployment?
- [ ] What is the exact athenahealth DataView Snowflake schema? (Discovered during development)
- [ ] Are there specific PCORnet CDM v7.0 tables that are higher priority than others for MVP?
- [ ] What Bedrock model(s) should be the default? (Claude 4.x vs Amazon Titan)
- [ ] Should the platform support data deletion per HIPAA right-of-access requests (patient-level delete)?
- [ ] What is the target price point for the platform? (Affects feature packaging)
- [ ] Do customers need a staging/test environment within their deployment?

---

## 22. Appendix

### A. Decision Log Reference
See: [decisions.md](./decisions.md) — 61 decisions recorded across 12 phases.

### B. Technology Research Reference
See: [tech-research.md](./tech-research.md) — Detailed tool comparisons, evaluated alternatives, and reference links.

### C. Key Reference Documents

| Document | URL |
|----------|-----|
| PCORnet CDM v7.0 Specification | https://pcornet.org/wp-content/uploads/2025/05/PCORnet_Common_Data_Model_v70_2025_05_01.pdf |
| PCORnet CDM Official Page | https://pcornet.org/data/common-data-model/ |
| HL7 CDMH Implementation Guide (FHIR→CDM Mapping) | https://build.fhir.org/ig/HL7/cdmh/profiles.html |
| athenahealth DataView Docs | https://docs.athenahealth.com/dataview/workflows/connecting-to-data-view |
| FHIR R4 Specification | https://hl7.org/fhir/R4/ |
| FHIR R5 Specification | https://hl7.org/fhir/R5/ |
| AWS HIPAA Compliance | https://aws.amazon.com/compliance/hipaa-compliance/ |
| LangGraph SQL Agent Tutorial | https://docs.langchain.com/oss/python/langgraph/sql-agent |

### D. FHIR → PCORnet Mapping Reference

| FHIR Resource | PCORnet CDM Table |
|---------------|-------------------|
| Patient | DEMOGRAPHIC |
| Encounter | ENCOUNTER |
| Condition | DIAGNOSIS, CONDITION |
| Procedure | PROCEDURES |
| Observation (vitals) | VITAL |
| Observation (labs) | LAB_RESULT_CM |
| MedicationRequest | PRESCRIBING |
| MedicationDispense | DISPENSING |
| Immunization | IMMUNIZATION |
| AllergyIntolerance | OBS_CLIN |
| Practitioner | PROVIDER |
| Patient (deceased) | DEATH, DEATH_CAUSE |
| Coverage | ENROLLMENT |

### E. Docker Compose Architecture (MVP)

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/lifescience
      - AWS_REGION=us-east-1
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000/api/v1

  postgres:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=lifescience
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}

volumes:
  pgdata:
```
