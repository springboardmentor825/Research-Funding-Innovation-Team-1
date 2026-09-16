"""
Import the OpenAlex scholarly dataset (datasets/openalex_50000_clean.csv) into MySQL.

Idempotent: the tables are wiped and rebuilt inside a single transaction, so this
script can be re-run safely at any time. Parent rows are inserted with explicit
research_id values so child rows (authors/institutions/topics/concepts) can be
loaded with fast multi-row inserts.

Usage:
    python scripts/import_dataset.py [path/to/openalex_50000_clean.csv]

DB credentials are read from backend/.env (same as the API).
"""
import csv
import os
import re
import sys
from datetime import date

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import func, insert, select

from app.database import engine, Base
from app import models  # noqa: F401  (registers ORM models with metadata)
from app.models import (
    ResearchPublication,
    ResearchPublicationAuthor,
    ResearchPublicationInstitution,
    ResearchPublicationTopic,
    ResearchPublicationConcept,
)

PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DEFAULT_CSV = os.path.join(PROJECT_ROOT, "datasets", "openalex_50000_clean.csv")

EXPECTED_COLUMNS = [
    "id", "title", "publication_year", "publication_date", "type",
    "authors", "institutions", "topics", "primary_topic", "concepts",
    "cited_by_count", "doi", "source", "is_retracted", "open_access",
]

PARENT_BATCH = 1000


def _clean(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.lower() in ("nan", "none", "n/a", "null", "nat"):
        return None
    return s


def _to_year(value):
    s = _clean(value)
    if s is None:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def _to_date(value):
    s = _clean(value)
    if s is None:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _to_int(value, default=0):
    s = _clean(value)
    if s is None:
        return default
    try:
        return int(float(s))
    except ValueError:
        return default


def _to_bool(value):
    s = _clean(value)
    if s is None:
        return 0
    return 1 if s.lower() in ("true", "1", "yes", "y") else 0


def _split(value):
    s = _clean(value)
    if s is None:
        return []
    return [p.strip() for p in re.split(r"\s*;\s*", s) if p and p.strip()]


def import_csv(csv_path):
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        for child in (ResearchPublicationAuthor, ResearchPublicationInstitution,
                      ResearchPublicationTopic, ResearchPublicationConcept):
            conn.execute(child.__table__.delete())
        conn.execute(ResearchPublication.__table__.delete())

        research_id = 1
        imported = 0
        parent_rows = []
        author_rows = []
        inst_rows = []
        topic_rows = []
        concept_rows = []

        def flush_batch():
            nonlocal parent_rows, author_rows, inst_rows, topic_rows, concept_rows
            if parent_rows:
                conn.execute(insert(ResearchPublication), parent_rows)
            if author_rows:
                conn.execute(insert(ResearchPublicationAuthor), author_rows)
            if inst_rows:
                conn.execute(insert(ResearchPublicationInstitution), inst_rows)
            if topic_rows:
                conn.execute(insert(ResearchPublicationTopic), topic_rows)
            if concept_rows:
                conn.execute(insert(ResearchPublicationConcept), concept_rows)
            parent_rows = []
            author_rows = []
            inst_rows = []
            topic_rows = []
            concept_rows = []

        with open(csv_path, "r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            missing = set(EXPECTED_COLUMNS) - set(reader.fieldnames or [])
            if missing:
                raise SystemExit(f"CSV is missing columns: {sorted(missing)}")

            for row in reader:
                rid = research_id
                research_id += 1
                parent_rows.append({
                    "research_id": rid,
                    "external_id": _clean(row.get("id")) or f"row-{rid}",
                    "title": _clean(row.get("title")) or "Untitled",
                    "publication_year": _to_year(row.get("publication_year")),
                    "publication_date": _to_date(row.get("publication_date")),
                    "publication_type": _clean(row.get("type")),
                    "authors_raw": _clean(row.get("authors")),
                    "institutions_raw": _clean(row.get("institutions")),
                    "topics_raw": _clean(row.get("topics")),
                    "primary_topic": _clean(row.get("primary_topic")),
                    "concepts_raw": _clean(row.get("concepts")),
                    "cited_by_count": _to_int(row.get("cited_by_count")),
                    "doi": _clean(row.get("doi")),
                    "source": _clean(row.get("source")),
                    "is_retracted": _to_bool(row.get("is_retracted")),
                    "open_access": _to_bool(row.get("open_access")),
                })
                for pos, name in enumerate(_split(row.get("authors"))):
                    author_rows.append({"research_id": rid, "author_name": name, "position": pos})
                for pos, name in enumerate(_split(row.get("institutions"))):
                    inst_rows.append({"research_id": rid, "institution_name": name, "position": pos})
                for pos, name in enumerate(_split(row.get("topics"))):
                    topic_rows.append({"research_id": rid, "topic_name": name, "position": pos})
                for pos, name in enumerate(_split(row.get("concepts"))):
                    concept_rows.append({"research_id": rid, "concept_name": name, "position": pos})

                imported += 1
                if len(parent_rows) >= PARENT_BATCH:
                    flush_batch()
            flush_batch()

        total = conn.execute(select(func.count()).select_from(ResearchPublication)).scalar()
        n_authors = conn.execute(select(func.count()).select_from(ResearchPublicationAuthor)).scalar()
        n_institutions = conn.execute(select(func.count()).select_from(ResearchPublicationInstitution)).scalar()
        n_topics = conn.execute(select(func.count()).select_from(ResearchPublicationTopic)).scalar()
        n_concepts = conn.execute(select(func.count()).select_from(ResearchPublicationConcept)).scalar()

    print(f"Imported rows: {imported}")
    print(f"Tables: publications={total}, authors={n_authors}, "
          f"institutions={n_institutions}, topics={n_topics}, concepts={n_concepts}")


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    if not os.path.exists(csv_path):
        raise SystemExit(f"CSV not found: {csv_path}")
    import_csv(csv_path)