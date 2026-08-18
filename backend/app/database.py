from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================
# MYSQL DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = "mysql+pymysql://root:@localhost/publication_trend_db"

# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    echo=False
)

# ============================================================
# SESSION
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================
# BASE CLASS FOR DATABASE MODELS
# ============================================================

Base = declarative_base()


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()