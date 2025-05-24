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
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to the Currency Converter API!"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
