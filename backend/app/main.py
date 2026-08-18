"""
FastAPI Application Entry Point
AI-powered Research Funding Innovation Intelligence Platform
"""

from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import database configuration and models
from .database import engine, Base, get_db
from .core.config import settings

# Import all models to register them with SQLAlchemy Base
from .models.user import User
from .models.research_profile import ResearchProfile
from .models.publication import Publication
from .models.patent import Patent
from .models.grant import Grant

# Import routers
from .routes.grants import router as grants_router

# Create all tables in the database (idempotent if they already exist)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Research Funding Innovation Intelligence Platform",
    version="0.1.0",
)

# Register routers
app.include_router(grants_router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint - Confirms API is running
    """
    return {
        "message": "Research Funding Innovation Intelligence Platform API is running",
        "version": "0.1.0",
        "project": settings.PROJECT_NAME,
    }


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint - Verifies FastAPI and database connectivity
    """
    try:
        # Test database connection by executing a simple query
        db.execute(text("SELECT 1"))
        db_status = "healthy"
        db_message = "Database connection successful"
    except Exception as e:
        db_status = "unhealthy"
        db_message = f"Database connection failed: {str(e)}"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": "Health check failed",
                "api": "healthy",
                "database": {
                    "status": db_status,
                    "message": db_message,
                },
            },
        )

    return {
        "status": "healthy",
        "message": "All systems operational",
        "api": "healthy",
        "database": {
            "status": db_status,
            "message": db_message,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
