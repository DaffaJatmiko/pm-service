"""Main application module for Performance Management System."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import settings
from src.core.database import create_db_and_tables
from src.api import api_router


def create_application() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    # Create FastAPI app with metadata
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="API for Performance Management System with BSC, MPM, and IPM modules",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=settings.CORS_METHODS.split(","),
        allow_headers=settings.CORS_HEADERS.split(","),
    )
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add startup event to create tables
    @app.on_event("startup")
    def startup_event():
        create_db_and_tables()
    
    # Add health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "version": settings.VERSION}
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    """Run the application with Uvicorn when executed directly."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "error",
    )