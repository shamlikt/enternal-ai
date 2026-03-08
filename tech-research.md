# Technology Research

> Compiled during project scoping. Last updated: 2026-03-08
> Project: Life Sciences B2B PaaS/SaaS — Healthcare Data Platform

## Table of Contents
- [Data Ingestion & ETL](#data-ingestion--etl)
- [Common Data Model](#common-data-model)
- [Database & Query Engine](#database--query-engine)
- [Unstructured Data / Search](#unstructured-data--search)
- [Agentic AI / LLM Layer](#agentic-ai--llm-layer)
- [Graph Database](#graph-database)
- [Backend Framework](#backend-framework)
- [Frontend Framework](#frontend-framework)

---

## Backend Framework

### Research Context
- **Decision Phase:** Tech Stack
- **Key Requirements:** Async, Pydantic, AI ecosystem, modular monolith
- **Research Date:** 2026-03-08

### Tools Evaluated

| Tool | Version | License | Maintained | Our Pick? |
|------|---------|---------|------------|-----------|
| FastAPI | 0.115+ | MIT | ✅ Active | ⭐ Selected |
| Django + DRF | 5.x | BSD | ✅ Active | |
| Litestar | 2.x | MIT | ✅ Active | |
| Flask | 3.x | BSD | ✅ Active | |

### Selected: FastAPI
**Why:** Async-native, Pydantic v2 built-in, best AI/agent framework integration, ~20K req/sec
**Official Docs:** https://fastapi.tiangolo.com/
**GitHub:** https://github.com/tiangolo/fastapi

---

## Frontend Framework

### Research Context
- **Decision Phase:** Tech Stack
- **Key Requirements:** AI-manageable, dashboard components, SQL editor, human + AI maintained
- **Research Date:** 2026-03-08

### Tools Evaluated

| Tool | Version | License | Maintained | Our Pick? |
|------|---------|---------|------------|-----------|
| Next.js (React) | 15.x | MIT | ✅ Active | ⭐ Selected |
| Reflex | 0.6+ | Apache 2.0 | ✅ Active | |
| Streamlit | 1.4x | Apache 2.0 | ✅ Active | |
| Vue.js + Nuxt | 3.x | MIT | ✅ Active | |

### Selected: Next.js (React/TypeScript)
**Why:** Largest AI training dataset, richest dashboard ecosystem (Tremor, shadcn/ui, AG Grid), Monaco Editor for SQL
**Official Docs:** https://nextjs.org/docs

---

## Data Ingestion & ETL

### Research Context
- **Decision Phase:** Data Ingestion
- **Key Requirements:** FHIR R4/R5, athenahealth DataView via Snowflake, batch/incremental, 100K records
- **Research Date:** 2026-03-08

### FHIR Libraries

| Tool | Version | License | Purpose | Our Pick? |
|------|---------|---------|---------|-----------|
| fhir.resources | 8.2.0 | BSD | Pydantic FHIR models (R4/R5) | ⭐ Selected |
| fhirpy | 2.x | MIT | Async/sync FHIR client | ⭐ Selected |
| fhirclient (SMART) | 4.x | Apache 2.0 | SMART on FHIR client | Considered |

### Athena DataView Connector

| Tool | Version | License | Purpose | Our Pick? |
|------|---------|---------|---------|-----------|
| snowflake-connector-python | 3.x | Apache 2.0 | Direct Snowflake connection | ⭐ Selected |

**Docs:** https://docs.athenahealth.com/dataview/workflows/connecting-to-data-view

### FHIR-to-PCORnet Mapping Reference
- **HL7 CDMH Implementation Guide:** https://build.fhir.org/ig/HL7/cdmh/profiles.html
- **NIH CDM Catalog:** https://datascience.nih.gov/fhir-initiatives/resources/cdmcatalog
- **CAMP FHIR (reference):** https://github.com/NCTraCSIDSci/camp-fhir

---

## Common Data Model

### Research Context
- **Decision Phase:** Data Ingestion
- **Key Requirements:** PCORnet CDM latest version
- **Research Date:** 2026-03-08

### PCORnet CDM v7.0 (May 2025)
- **Spec PDF:** https://pcornet.org/wp-content/uploads/2025/05/PCORnet_Common_Data_Model_v70_2025_05_01.pdf
- **Official Page:** https://pcornet.org/data/common-data-model/
- **GitHub (CDM Forum):** https://github.com/CDMFORUM

### Core Tables (v7.0)
DEMOGRAPHIC, ENCOUNTER, DIAGNOSIS, PROCEDURES, VITAL, LAB_RESULT_CM, PRESCRIBING, DISPENSING, CONDITION, DEATH, DEATH_CAUSE, ENROLLMENT, HARVEST, LDS_ADDRESS_HISTORY, MED_ADMIN, OBS_CLIN, OBS_GEN, PCORNET_TRIAL, PRO_CM, PROVIDER, IMMUNIZATION, HASH_TOKEN

---

## Agentic AI / LLM Layer

### Research Context
- **Decision Phase:** Agentic AI
- **Key Requirements:** Query decomposition, text-to-SQL, BYOM (start Bedrock), read-only, chat + single query
- **Research Date:** 2026-03-08

### Frameworks Evaluated

| Tool | Version | License | Maintained | Our Pick? |
|------|---------|---------|------------|-----------|
| LangChain + LangGraph | 0.3.x / 0.2.x | MIT | ✅ Active | ⭐ Selected |
| LlamaIndex | 0.12.x | MIT | ✅ Active | |
| AWS Bedrock Agents SDK | 1.x | Apache 2.0 | ✅ Active | |
| Custom (no framework) | N/A | N/A | N/A | |

### Selected: LangChain + LangGraph
**Why:** SQLDatabase auto-discovers PCORnet schema, LangGraph enables ReAct-pattern query decomposition, ChatBedrock for AWS Bedrock, easy to swap LLM providers (BYOM)
**LangChain Docs:** https://docs.langchain.com/
**LangGraph Docs:** https://langchain-ai.github.io/langgraph/
**SQL Agent Tutorial:** https://docs.langchain.com/oss/python/langgraph/sql-agent

### Key Libraries
| Library | Purpose |
|---------|---------|
| `langchain-core` | Core abstractions |
| `langchain-community` | SQLDatabase, tool integrations |
| `langchain-aws` | ChatBedrock LLM provider |
| `langgraph` | Multi-step agent orchestration |
| `openpyxl` | Excel (.xlsx) export |

### Agent Architecture Pattern
- **ReAct Loop:** Plan → Generate SQL → Execute → Synthesize → Answer
- **Query Decomposition:** Complex question → multiple sub-queries → combine results
- **LLM Provider Adapter:** Abstract interface, start with Bedrock, add OpenAI/Anthropic/Ollama later
- **Guardrails:** Read-only (SELECT only), no DDL/DML via agent
- **Output:** Results stored in DB table, exportable as CSV/Excel
