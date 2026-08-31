from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, users, publications, patents, funding, rag, researcher
import os
from dotenv import load_dotenv

load_dotenv()

# Build database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Funding & Innovation Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS Origins list
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect Route handlers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users & Profiles"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users & Profiles"])
app.include_router(publications.router, prefix="/api/v1/publications", tags=["Publications"])
app.include_router(patents.router, prefix="/api/v1/patents", tags=["Patents"])

# Researcher Feature Extraction routes
app.include_router(researcher.router, prefix="/api/researcher", tags=["Researcher Features"])
app.include_router(researcher.router, prefix="/api/v1/researcher", tags=["Researcher Features"])

# Funding & Recommendation routes (mounted on both /api/funding and /api/v1/funding for maximum compatibility)
app.include_router(funding.router, prefix="/api/funding", tags=["Funding & Recommendations"])
app.include_router(funding.router, prefix="/api/v1/funding", tags=["Funding & Recommendations"])

# Hybrid RAG routes (mounted on /api/rag and /api/v1/rag)
app.include_router(rag.router, prefix="/api/rag", tags=["Hybrid RAG"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["Hybrid RAG"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Research Funding & Innovation Intelligence Platform Backend",
        "docs": "/docs"
    }
