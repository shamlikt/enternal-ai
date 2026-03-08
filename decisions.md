# Project Decisions Log

> Auto-generated during project scoping. Last updated: 2026-03-08
> Project: Life Sciences B2B PaaS/SaaS — Healthcare Data Platform

## Summary
| # | Phase | Decision | Choice | Rationale |
|---|-------|----------|--------|-----------|
| 1 | Scoping | Data Model Standard | PCORnet CDM v7.0 | Latest version (May 2025) |
| 2 | Scoping | Data Sources (MVP) | FHIR, athenahealth DataView | PDF deferred to post-MVP |
| 3 | Scoping | Deployment Model | Customer-deployable (on-prem / private cloud) | B2B customers deploy in their own environment |
| 4 | Scoping | End Users | Customer's internal LifeScience & business teams | They ingest data and perform analysis |
| 5 | Scoping | Interaction Modes | SQL queries + Agentic AI search + Dashboards | Three ways users interact with data |
| 6 | Scoping | Database Strategy | Start PostgreSQL, must swap to Databricks/Athena/Fabric | Interchangeable data layer per customer environment |
| 7 | Scoping | Unstructured Data Store | OpenSearch | For PDF/clinical notes storage and search |
| 8 | Scoping | Future Roadmap | Graph Database | For relationship-based querying and entity identification |
| 9 | Architecture | System Architecture | Modular Monolith + Query Adapter | Simple deployment, clean boundaries, adapter for DB swap |
| 10 | Architecture | MVP Database Adapter | PostgreSQL only | Start simple, add others when needed |
| 11 | Architecture | MVP Data Sources | FHIR + athenahealth DataView | PDF deferred to post-MVP |
| 12 | Tech Stack | Backend Framework | FastAPI (Python) | Async-native, Pydantic for PCORnet, best AI ecosystem |
| 13 | Tech Stack | Frontend Framework | Next.js (React/TypeScript) | Best AI code generation, richest dashboard components |
| 14 | Tech Stack | ORM | SQLAlchemy (async) | Standard Python ORM, works with Query Adapter pattern |
| 15 | Tech Stack | FHIR Libraries | fhir.resources + fhirpy | Pydantic models + async FHIR client |
| 16 | Data Ingestion | PCORnet Version | v7.0 (May 2025) | Latest available |
| 17 | Data Ingestion | FHIR Version | R4 + R5 (both) | Auto-detect, use CDMH mapping spec |
| 18 | Data Ingestion | Athena DataView | Snowflake Python connector | DataView exposed via Snowflake |
| 19 | Data Ingestion | Integration UI | Config dashboard in frontend | Customers set connection params via UI |
| 20 | Data Ingestion | Ingestion Mode | Batch, incremental | ~100K records/batch, track last-synced cursor |
| 21 | Agentic AI | Agent Framework | LangChain + LangGraph | Query decomposition, SQLDatabase auto-discovery, BYOM |
| 22 | Agentic AI | LLM Provider (MVP) | AWS Bedrock | Expandable via LLM Provider Adapter |
| 23 | Agentic AI | Interaction Mode | Chat + Single Query | Multi-turn exploration + quick answers |
| 24 | Agentic AI | Output & Export | Results table + CSV/Excel | Stored in DB, exportable |
| 25 | Agentic AI | Guardrails | Read-only (SELECT only) | Keep simple for MVP |
| 26 | Dashboard | SQL Editor | Monaco Editor (react-monaco-editor) | Databricks-like SQL IDE with IntelliSense |
| 27 | Dashboard | Chart Components | Tremor | 35+ chart types, Tailwind CSS styled |
| 28 | Dashboard | Dashboard Grid | react-grid-layout | Drag-and-drop, resizable widgets (used by Grafana) |
| 29 | Dashboard | Data Table | AG Grid (community) | Sort/filter/export for query results |
| 30 | Dashboard | Export | AG Grid CSV + SheetJS (xlsx) | CSV and Excel export |
| 31 | Dashboard | UI Framework | shadcn/ui + Tailwind CSS | Consistent UI across the app |
| 32 | Dashboard | Dashboard Mode | Pre-built templates + self-service builder | Both out-of-box and customizable |
| 33 | Dashboard | Sharing | Not in MVP | Deferred |
| 34 | Auth | Auth Method | Username/password (local) | SSO deferred to later |
| 35 | Auth | User Roles | Admin, Analyst, Viewer | Three-tier RBAC |
| 36 | Auth | Tenancy | Single-tenant per deployment | One org per Docker Compose instance |
| 37 | Auth | API Keys | Not in MVP | No external API access needed |
| 38 | API | API Style | REST | Simple, standard |
| 39 | API | Agent Streaming | WebSocket + token streaming | ChatGPT-like response streaming |
| 40 | API | API Versioning | Yes, /api/v1/ from start | Backward compatibility |
| 41 | DevOps | Source Control | GitLab | — |
| 42 | DevOps | CI/CD | GitLab CI | Native integration |
| 43 | DevOps | Container Registry | GitLab Container Registry | Free, built into GitLab |
| 44 | DevOps | Environments | Dev only for now | Staging + prod later |
| 45 | DevOps | Customer Updates | TBD | Decide later |
| 46 | Security | HIPAA Compliance | Yes, required | Handling PHI |
| 47 | Security | Encryption | In-transit (TLS/HTTPS) for MVP | At-rest deferred |
| 48 | Security | Audit Logging | Basic for now | Logins, queries, exports |
| 49 | Security | PHI in Logs | No PHI in logs | Sanitize all log output |
| 50 | Security | BAA | Yes, required with AWS (Bedrock) | Standard HIPAA requirement |
| 51 | Security | Data Retention | Keep until explicit delete request | No auto-purge |
| 52 | Testing | Coverage Level | Comprehensive from day one | Critical for healthcare data |
| 53 | Testing | E2E Tests | Yes, Playwright | Automated browser tests |
| 54 | Testing | CDM Mapping Tests | Yes, dedicated test suite | Known FHIR bundles → expected PCORnet rows |
| 55 | Monitoring | Logging | Structured JSON stdout + in-app log viewer | Both Docker-native and UI |
| 56 | Monitoring | Error Tracking | Logs + built-in health dashboard | System status, ingestion health, errors |
| 57 | Monitoring | Metrics | Not in MVP | Prometheus endpoint deferred |
| 58 | UI/UX | Design Reference | Databricks UI | Dark sidebar, light content, IDE-style layout |
| 59 | UI/UX | Split Panes | react-resizable-panels | Draggable dividers (editor/results, sidebar/content) |
| 60 | UI/UX | Command Palette | cmdk (shadcn/ui) | Ctrl+K search |
| 61 | UI/UX | Data Explorer | Tree view (sidebar) | PCORnet tables → columns, click-to-insert |

---

## Detailed Decisions

### Decision 1: PCORnet CDM as Standard Data Model
- **Phase:** Project Scoping
- **Date:** 2026-03-08
- **Choice:** PCORnet CDM (not OMOP)
- **Rationale:** User's explicit requirement
- **Tables Expected:** DEMOGRAPHIC, ENCOUNTER, DIAGNOSIS, PROCEDURES, VITAL, LAB_RESULT_CM, PRESCRIBING, DISPENSING, etc.
- **Revisit If:** Customer base requests OMOP compatibility

### Decision 2: Data Sources
- **Phase:** Project Scoping
- **Date:** 2026-03-08
- **Choice:** FHIR APIs, athenahealth DataView API, PDF documents
- **Details:** PDFs include both scanned (OCR needed) and digital/text-based
- **Revisit If:** Additional EHR integrations needed (Epic, Cerner, etc.)

### Decision 3: Deployment Model
- **Phase:** Project Scoping
- **Date:** 2026-03-08
- **Choice:** Customer-deployable platform
- **Rationale:** B2B customers deploy in their own environment (on-prem or private cloud)
- **Implications:** Must be containerized, config-driven, minimal external dependencies
- **Revisit If:** Hosted SaaS model is added later

### Decision 4: Interaction Modes
- **Phase:** Project Scoping
- **Date:** 2026-03-08
- **Choice:** SQL query interface + Agentic AI search + Dashboards
- **Rationale:** Users need multiple ways to interact — technical (SQL), AI-assisted (agent), visual (dashboards)

### Decision 5: Database Abstraction
- **Phase:** Project Scoping
- **Date:** 2026-03-08
- **Choice:** PostgreSQL as default, interchangeable with Databricks, AWS Athena, Microsoft Fabric/Synapse
- **Rationale:** Different customers have different data infrastructure preferences
- **Implications:** Need a database abstraction layer / query engine adapter

### Decision 6: Unstructured Data
- **Phase:** Project Scoping
- **Date:** 2026-03-08
- **Choice:** OpenSearch for unstructured data storage and search
- **Rationale:** User requirement for storing and searching PDFs, clinical notes

### Decision 7: Graph DB (Future)
- **Phase:** Project Scoping
- **Date:** 2026-03-08
- **Choice:** Graph database planned for future phase
- **Rationale:** Enable relationship-based querying and easier entity identification
- **Status:** Roadmap item, not MVP

### Decision 8: System Architecture
- **Phase:** Architecture
- **Date:** 2026-03-08
- **Options Considered:** Traditional Microservices, Modular Monolith, Data Lakehouse, Hybrid (Modular Monolith + Query Adapter)
- **Choice:** Modular Monolith with Query Adapter Interface
- **Rationale:** Simple customer deployment (Docker Compose), clean module boundaries, adapter pattern for future DB interchangeability
- **Trade-offs Accepted:** Scales as one unit (acceptable for ~50 users)
- **Revisit If:** Need independent scaling of modules or multi-team parallel development

### Decision 9: MVP Database Adapter
- **Phase:** Architecture
- **Date:** 2026-03-08
- **Choice:** PostgreSQL adapter only for MVP
- **Rationale:** Start simple, add Databricks/Athena/Fabric adapters when customers need them
- **Revisit If:** First customer requires a different backend

### Decision 10: MVP Data Sources
- **Phase:** Architecture
- **Date:** 2026-03-08
- **Choice:** FHIR and athenahealth DataView only for MVP
- **Deferred:** PDF ingestion (OCR + digital) moved to post-MVP
- **Rationale:** Focus on structured data ingestion first

### Decision 11: Backend Framework
- **Phase:** Tech Stack
- **Date:** 2026-03-08
- **Options Considered:** FastAPI, Django + DRF, Litestar, Flask
- **Choice:** FastAPI
- **Rationale:** Async-native (critical for FHIR/Athena/LLM API calls), Pydantic v2 built-in (PCORnet data validation), best AI/agent framework integrations, ~20K req/sec performance
- **Trade-offs Accepted:** No built-in ORM or admin (using SQLAlchemy + custom admin)
- **Revisit If:** N/A — strong fit

### Decision 12: Frontend Framework
- **Phase:** Tech Stack
- **Date:** 2026-03-08
- **Options Considered:** Next.js (React), Reflex (Python), Streamlit/Gradio, Vue.js + Nuxt
- **Choice:** Next.js (React/TypeScript)
- **Rationale:** Best AI code generation support, richest dashboard/charting ecosystem (Tremor, shadcn/ui, AG Grid), Monaco Editor for SQL, largest community
- **Trade-offs Accepted:** Adds TypeScript as second language
- **Revisit If:** Team struggles with TypeScript

### Decision 13: PCORnet CDM Version
- **Phase:** Data Ingestion
- **Date:** 2026-03-08
- **Choice:** PCORnet CDM v7.0 (latest, released May 2025)
- **Note:** Originally planned v6.1, upgraded to v7.0 based on research
- **Reference:** https://pcornet.org/data/common-data-model/

### Decision 14: FHIR Version Support
- **Phase:** Data Ingestion
- **Date:** 2026-03-08
- **Choice:** Support both FHIR R4 and R5
- **Rationale:** Customers may be on either version
- **Approach:** Auto-detect version, use HL7 CDMH mapping spec as base for FHIR→PCORnet transformation

### Decision 15: Athena DataView Connection
- **Phase:** Data Ingestion
- **Date:** 2026-03-08
- **Choice:** Snowflake Python connector (snowflake-connector-python)
- **Rationale:** DataView exposes data via Snowflake; use native Python connector
- **Reference:** https://docs.athenahealth.com/dataview/workflows/connecting-to-data-view

### Decision 16: Integration Dashboard
- **Phase:** Data Ingestion
- **Date:** 2026-03-08
- **Choice:** UI-based integration configuration dashboard
- **Details:** Customers configure connection parameters (FHIR server URL, auth, Snowflake credentials) via the frontend — no manual config files

### Decision 17: Ingestion Mode
- **Phase:** Data Ingestion
- **Date:** 2026-03-08
- **Choice:** Batch ingestion, incremental updates
- **Volume:** ~100K records per batch
- **Details:** Track last-synced timestamp/cursor, only pull new/changed records

### Decision 18: Athena DataView Schema Discovery
- **Phase:** Data Ingestion
- **Date:** 2026-03-08
- **Choice:** Discover DataView schema during development
- **Rationale:** No pre-existing documentation available; will query DataView's Snowflake schema and build mapping dynamically

### Decision 19: Error Handling Strategy
- **Phase:** Data Ingestion
- **Date:** 2026-03-08
- **Choice:** Quarantine failed records for manual review
- **Details:** Ingest what maps successfully, quarantine failed records with error details in a separate table, provide UI for reviewing/fixing quarantined records
- **Rationale:** Maximizes data throughput while maintaining data quality visibility

### Decision 20: Agent Framework
- **Phase:** Agentic AI
- **Date:** 2026-03-08
- **Options Considered:** LangChain + LangGraph, LlamaIndex, AWS Bedrock Agents (native), Custom Agent
- **Choice:** LangChain + LangGraph
- **Rationale:** Built-in SQLDatabase abstraction auto-discovers PCORnet schema, LangGraph enables multi-step query decomposition (ReAct pattern), Bedrock natively supported, easy to swap LLM providers later (BYOM)
- **Trade-offs Accepted:** Heavy abstraction, frequent version changes
- **Revisit If:** LangChain instability becomes a maintenance burden

### Decision 21: LLM Provider (MVP)
- **Phase:** Agentic AI
- **Date:** 2026-03-08
- **Choice:** AWS Bedrock (start), expandable to other providers via LLM Provider Adapter
- **Rationale:** Customer requirement; LangChain's ChatBedrock makes this trivial
- **Future Providers:** OpenAI, Anthropic direct, Azure OpenAI, Ollama/vLLM (self-hosted)

### Decision 22: Agent Interaction Mode
- **Phase:** Agentic AI
- **Date:** 2026-03-08
- **Choice:** Both chat (multi-turn) and single query modes
- **Details:** Chat for exploration, single query for quick answers

### Decision 23: Agent Output & Export
- **Phase:** Agentic AI
- **Date:** 2026-03-08
- **Choice:** Results stored in database table + CSV/Excel export
- **Details:** Agent stores query results in a results table, users can export as CSV or Excel (.xlsx)

### Decision 24: Agent Guardrails
- **Phase:** Agentic AI
- **Date:** 2026-03-08
- **Choice:** Read-only operations only (SELECT queries only)
- **Rationale:** Keep it simple for MVP; no INSERT/UPDATE/DELETE via agent

### Decision 25: SQL Editor
- **Phase:** Dashboard & SQL
- **Date:** 2026-03-08
- **Options Considered:** Monaco Editor, CodeMirror 6, Ace Editor, SQLRooms
- **Choice:** Monaco Editor (react-monaco-editor)
- **Rationale:** Same engine as VS Code, SQL IntelliSense, schema-aware autocomplete for PCORnet tables
- **Features:** Syntax highlighting, autocomplete, query history, saved queries, multi-tab

### Decision 26: Dashboard Components
- **Phase:** Dashboard & SQL
- **Date:** 2026-03-08
- **Options Considered:** Tremor + react-grid-layout, Apache Superset (embedded), Luzmo (commercial), Recharts + custom
- **Choice:** Tremor + react-grid-layout
- **Rationale:** Open-source, Tailwind CSS styled, react-grid-layout used by Grafana, full control over builder UX
- **Chart Types:** Bar, line, pie, area, donut, KPI cards, time-series, funnel
- **Trade-offs Accepted:** Must build the dashboard builder UI ourselves

### Decision 27: Dashboard Mode
- **Phase:** Dashboard & SQL
- **Date:** 2026-03-08
- **Choice:** Pre-built templates + self-service builder
- **Pre-built Templates:** Patient Demographics, Encounter Trends, Diagnosis Distribution, Lab Results, Prescription Analytics
- **Self-service:** Users drag-and-drop widgets, configure data sources, resize/rearrange

### Decision 28: Data Table & Export
- **Phase:** Dashboard & SQL
- **Date:** 2026-03-08
- **Choice:** AG Grid (community edition) for results table + SheetJS for Excel export
- **Features:** Sort, filter, pagination, CSV export, Excel (.xlsx) export

### Decision 29: Authentication Method
- **Phase:** Auth
- **Date:** 2026-03-08
- **Choice:** Username/password with JWT tokens (OAuth2PasswordBearer)
- **Details:** bcrypt password hashing (passlib), HTTP-only cookies, short-lived access tokens
- **Deferred:** SSO (Okta, Azure AD) for future
- **Revisit If:** Enterprise customers require SSO

### Decision 30: RBAC Model
- **Phase:** Auth
- **Date:** 2026-03-08
- **Choice:** Three roles — Admin, Analyst, Viewer
- **Implementation:** FastAPI dependency injection for role checks
- **Admin:** Full access (users, integrations, settings, queries, dashboards)
- **Analyst:** Queries, agent, dashboards (build + view), export
- **Viewer:** View dashboards only

### Decision 31: Tenancy Model
- **Phase:** Auth
- **Date:** 2026-03-08
- **Choice:** Single-tenant (one org per deployment)
- **Rationale:** Simplifies auth, data isolation, and deployment

### Decision 32: API Style
- **Phase:** API Design
- **Date:** 2026-03-08
- **Choice:** REST API
- **Versioning:** /api/v1/ prefix from day one
- **Docs:** Auto-generated via FastAPI OpenAPI (Swagger UI + ReDoc)

### Decision 33: Agent Streaming
- **Phase:** API Design
- **Date:** 2026-03-08
- **Choice:** WebSocket for agent chat with token-by-token streaming
- **Details:** Server-Sent Events (SSE) or WebSocket — user sees response being typed like ChatGPT
- **Implementation:** FastAPI WebSocket endpoint + LangGraph streaming callbacks

### Decision 34: DevOps Stack
- **Phase:** DevOps
- **Date:** 2026-03-08
- **Choice:** GitLab (source) + GitLab CI (pipelines) + GitLab Container Registry (images)
- **Rationale:** All-in-one, free container registry, native CI integration
- **Environments:** Dev only for now; staging + prod added later
- **Customer Updates:** TBD — decide delivery mechanism later

### Decision 35: HIPAA Compliance
- **Phase:** Security
- **Date:** 2026-03-08
- **Choice:** HIPAA compliant — required
- **Key Implications:**
  - TLS/HTTPS for all data in transit (MVP)
  - Encryption at rest (deferred, add later)
  - Audit logging for access tracking
  - No PHI in application logs — sanitize all output
  - BAA required with AWS for Bedrock
  - Data retained until explicit deletion request
- **Audit Scope (MVP):** User logins, SQL query executions, data exports, ingestion runs
- **Audit Scope (Future):** Every API call, record-level access, dashboard views

### Decision 36: Testing Strategy
- **Phase:** Testing
- **Date:** 2026-03-08
- **Choice:** Comprehensive testing from day one
- **Stack:**

| Type | Tool | Scope |
|------|------|-------|
| Unit (Backend) | **pytest** + pytest-asyncio | FastAPI endpoints, services, transformations |
| Unit (Frontend) | **Vitest** + React Testing Library | Components, hooks, utils |
| Integration | **pytest** + testcontainers | DB queries, ingestion pipeline, agent flow |
| E2E | **Playwright** | Full browser tests — login, query, dashboard |
| CDM Mapping | **pytest** (dedicated suite) | Known FHIR bundles → expected PCORnet rows |
| API | **pytest** + httpx | REST endpoint contracts |
| CI | **GitLab CI** | Run all tests on every MR |

- **CDM Mapping Tests:** Curated test fixtures of FHIR R4/R5 bundles with expected PCORnet output; validates every resource type mapping
- **Rationale:** Healthcare data — correctness is non-negotiable

### Decision 37: Monitoring & Observability
- **Phase:** Monitoring
- **Date:** 2026-03-08
- **Logging:** Structured JSON logs to stdout (Docker-native) + in-app log viewer (Admin only)
- **Library:** Python `structlog` for structured JSON logging
- **Error Tracking:** Built-in health dashboard showing system status, ingestion health, error counts
- **Metrics:** Deferred to post-MVP (Prometheus endpoint planned)
- **PHI Reminder:** Log sanitization — no PHI in any log output

### Decision 38: UI/UX Design Reference
- **Phase:** UI/UX
- **Date:** 2026-03-08
- **Choice:** Databricks-style UI
- **Key Design Elements:**
  - Dark sidebar (#1B1B1B) with icon + label navigation, collapsible
  - Light content area
  - IDE-style SQL editor with Data Explorer tree on left
  - Resizable split panes (react-resizable-panels)
  - Multi-tab query interface
  - Ctrl+K command palette (cmdk)
  - AG Grid results panel below editor
  - Clean card-based dashboard widgets
- **Additional Libraries:** react-resizable-panels, cmdk (via shadcn/ui)
