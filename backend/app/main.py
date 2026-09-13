from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, users, publications, patents, funding, rag, researcher, collaboration
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

from app.routes import auth, users, publications, patents, funding, rag, researcher, collaboration, dashboard, startup, admin

# Connect Route handlers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administrator Module"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administrator Module"])
app.include_router(users.router, prefix="/api/users", tags=["Users & Profiles"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users & Profiles"])
app.include_router(publications.router, prefix="/api/v1/publications", tags=["Publications"])
app.include_router(patents.router, prefix="/api/patents", tags=["Patents"])
app.include_router(patents.router, prefix="/api/v1/patents", tags=["Patents"])

# Startup Founder Module routes
app.include_router(startup.router, prefix="/api/startup", tags=["Startup Founder Module"])
app.include_router(startup.router, prefix="/api/v1/startup", tags=["Startup Founder Module"])

# Researcher Feature & Intelligence routes
app.include_router(researcher.router, prefix="/api/researcher", tags=["Researcher Features"])
app.include_router(researcher.router, prefix="/api/v1/researcher", tags=["Researcher Features"])
app.include_router(researcher.router, prefix="/api/researchers", tags=["Researcher Intelligence"])
app.include_router(researcher.router, prefix="/api/v1/researchers", tags=["Researcher Intelligence"])

# Collaboration Recommendation routes
app.include_router(collaboration.router, prefix="/api/researchers", tags=["Collaboration Recommendations"])
app.include_router(collaboration.router, prefix="/api/v1/researchers", tags=["Collaboration Recommendations"])

# Funding & Recommendation routes
app.include_router(funding.router, prefix="/api/funding", tags=["Funding & Recommendations"])
app.include_router(funding.router, prefix="/api/v1/funding", tags=["Funding & Recommendations"])

# Integrated Dashboard & Alert routes
app.include_router(dashboard.router, prefix="/api/research-intelligence", tags=["Integrated Intelligence Dashboard"])
app.include_router(dashboard.router, prefix="/api/v1/research-intelligence", tags=["Integrated Intelligence Dashboard"])
app.include_router(dashboard.router, prefix="/api", tags=["Integrated Intelligence Dashboard"])

# Hybrid RAG routes
app.include_router(rag.router, prefix="/api/rag", tags=["Hybrid RAG"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["Hybrid RAG"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Research Funding & Innovation Intelligence Platform Backend",
        "docs": "/docs"
    }
