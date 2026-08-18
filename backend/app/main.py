from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import publications
from backend.app.routers import analytics


app = FastAPI(
    title="OpenAlex Publication Trend Analysis API",
    description="API for analyzing 50,000 OpenAlex research publications",
    version="1.0.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    publications.router,
    prefix="/api/publications",
    tags=["Publications"]
)

app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["Analytics"]
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "OpenAlex Publication Trend Analysis API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }