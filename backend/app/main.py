"""
=============================================================================
RESEARCH FUNDING & INNOVATION INTELLIGENCE PLATFORM — MAIN APP
=============================================================================
Combines Publication Trend Analysis (Member 2) with
Researcher Intelligence (Member 4) into a single FastAPI application.

Routers:
  /api/researcher-intelligence — Researcher Intelligence (Member 4)
  /api/publications           — Publication trend analysis (Member 2, requires MySQL)
  /api/analytics              — Analytics endpoints (Member 2, requires MySQL)
=============================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Researcher Intelligence (always available - no database needed)
from backend.app.services.researcher_intelligence_engine import (
    get_intelligence_data,
)
from backend.app.routers import researcher_intelligence


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: pre-load the researcher intelligence pipeline so the
    first API request is served instantly.
    """
    print("[startup] Loading researcher intelligence pipeline...")
    get_intelligence_data()
    print("[startup] Researcher intelligence data ready.")
    yield
    print("[shutdown] Shutting down.")


app = FastAPI(
    title="Research Funding & Innovation Intelligence Platform",
    description=(
        "API for analyzing research publications, patent landscapes, "
        "and researcher intelligence profiles."
    ),
    version="2.0.0",
    lifespan=lifespan,
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS — Researcher Intelligence (Member 4, always active)
# ============================================================

app.include_router(
    researcher_intelligence.router,
    prefix="/api/researcher-intelligence",
    tags=["Researcher Intelligence"],
)


# ============================================================
# ROUTERS — Publication Trend Analysis (Member 2, requires MySQL)
# ============================================================

try:
    from backend.app.routers import publications
    app.include_router(
        publications.router,
        prefix="/api/publications",
        tags=["Publications"],
    )
except Exception:
    pass

try:
    from backend.app.routers import analytics
    app.include_router(
        analytics.router,
        prefix="/api/analytics",
        tags=["Analytics"],
    )
except Exception:
    pass


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Research Funding & Innovation Intelligence Platform",
        "version": "2.0.0",
        "modules": [
            "Researcher Intelligence",
            "Publication Trend Analysis (requires MySQL)",
        ],
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
