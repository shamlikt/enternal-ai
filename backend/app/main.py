from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import configure_logging
from app.modules.auth.router import router as auth_router
from app.modules.auth.router import users_router
from app.modules.agent.router import router as agent_router
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


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}
