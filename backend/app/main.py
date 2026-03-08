from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import configure_logging
from app.modules.auth.router import router as auth_router
from app.modules.auth.router import users_router
from app.modules.agent.router import router as agent_router
from app.modules.audit.router import router as audit_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.export.router import router as export_router
from app.modules.health.router import router as health_router
from app.modules.query.router import router as query_router
from app.modules.query.router import schema_router

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

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(query_router, prefix="/api/v1/query", tags=["query"])
app.include_router(schema_router, prefix="/api/v1/schema", tags=["schema"])
app.include_router(agent_router, prefix="/api/v1/agent", tags=["agent"])
app.include_router(dashboard_router, prefix="/api/v1/dashboards", tags=["dashboards"])
app.include_router(export_router, prefix="/api/v1/export", tags=["export"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["audit"])
