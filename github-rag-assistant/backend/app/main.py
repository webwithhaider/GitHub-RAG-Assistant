"""FastAPI application entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, query, repos
from app.config import get_settings
from app.core.logging_config import configure_logging

settings = get_settings()
configure_logging()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(repos.router, prefix="/repos", tags=["repos"])
app.include_router(query.router, prefix="/query", tags=["query"])


@app.get("/")
def root():
    return {"name": settings.APP_NAME, "status": "running"}
