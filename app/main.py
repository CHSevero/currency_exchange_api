"""
FastAPI application entry point.

This module initializes the FastAPI application and includes the root and health check endpoints.
It also sets up the application with the project name, description, version, and API documentation URLs.
"""
from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url=settings.PROJECT_DOCS_URL,
    redoc_url=settings.PROJECT_REDOC_URL,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to the Currency Converter API!"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
