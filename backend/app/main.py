from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, users, publications, patents, analytics, funding, rag, applications, admin
from app.services import rag_retrieval
import os
from dotenv import load_dotenv
from app.database import get_db
from app.models import User
from app.auth import get_password_hash

load_dotenv()

def _seed_fixed_admin():
    """Ensures the fixed admin account (email + password) always exists so the
    Administrator Control Center can always be signed into with known credentials."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@infera.app")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin@12345")
    db = next(get_db())
    try:
        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            db.add(User(
                full_name="Platform Administrator",
                email=admin_email,
                password=get_password_hash(admin_password),
                role="admin",
                login_type="email",
                auth_provider="system",
            ))
            db.commit()
    finally:
        db.close()

# Build database tables if they do not exist
Base.metadata.create_all(bind=engine)

# Seed a stable admin account (idempotent) so admin sign-in never breaks
_seed_fixed_admin()

app = FastAPI(
    title="Infera API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS Origins list
# Fallback to local react client; override with CORS_ORIGINS (comma-separated) in deployments.
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000"
]
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()] or default_origins

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
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

# Funding & Recommendation routes
app.include_router(funding.router, prefix="/api/funding", tags=["Funding & Recommendations"])
app.include_router(funding.router, prefix="/api/v1/funding", tags=["Funding & Recommendations"])

# Grant Applications routes
app.include_router(applications.router, prefix="/api/applications", tags=["Grant Applications"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["Grant Applications"])

# Platform Administration routes
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administration"])

# Hybrid RAG routes
app.include_router(rag.router, prefix="/api/rag", tags=["Hybrid RAG"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["Hybrid RAG"])

@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {
        "status": "online",
        "service": "Infera Backend",
        "docs": "/docs"
    }

@app.api_route("/healthz", methods=["GET", "HEAD"])
def healthz():
    return {"status": "ok"}

# Warm the RAG index in the background so the first chat is fast and
# the index build never blocks (or spikes memory on) an incoming request.
rag_retrieval.prewarm()
