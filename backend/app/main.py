from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import configure_logging

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
