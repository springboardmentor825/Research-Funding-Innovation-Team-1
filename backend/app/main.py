# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models  # Ensures all 13 ORM models are registered with Base metadata
from app.routes import auth, users, publications, patents
from app.api.v1.endpoints import rag
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
    "http://localhost:3000"
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
app.include_router(users.router, prefix="/api/v1/users", tags=["Users & Profiles"])
app.include_router(publications.router, prefix="/api/v1/publications", tags=["Publications"])
app.include_router(patents.router, prefix="/api/v1/patents", tags=["Patents"])

# RAG Routers (Available at both /api/v1/rag and /api/rag for full compatibility)
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG & Intelligence"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG & Intelligence (Legacy Route)"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Research Funding & Innovation Intelligence Platform Backend",
        "docs": "/docs"
    }
