from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Publication


router = APIRouter()


# ============================================================
# GET PUBLICATIONS
# ============================================================

@router.get("/")
def get_publications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Return publications directly from MySQL.
    """

    total = db.query(Publication).count()

    publications = (
        db.query(Publication)
        .offset(offset)
        .limit(limit)
        .all()
    )

    data = []

    for publication in publications:
        data.append({
            "id": publication.id,
            "title": publication.title,
            "publication_year": publication.publication_year,
            "publication_date": (
                publication.publication_date.isoformat()
                if publication.publication_date
                else None
            ),
            "type": publication.type,
            "authors": publication.authors,
            "institutions": publication.institutions,
            "topics": publication.topics,
            "primary_topic": publication.primary_topic,
            "concepts": publication.concepts,
            "cited_by_count": publication.cited_by_count,
            "doi": publication.doi,
            "source": publication.source,
            "is_retracted": publication.is_retracted,
            "open_access": publication.open_access
        })

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "publications": data
    }


# ============================================================
# DATASET INFORMATION
# ============================================================

@router.get("/info")
def dataset_info(db: Session = Depends(get_db)):
    """
    Return basic information about the dataset.
    """

    total = db.query(Publication).count()

    return {
        "dataset": "OpenAlex",
        "total_publications": total,
        "year_range": {
            "minimum": db.query(Publication.publication_year).order_by(
                Publication.publication_year.asc()
            ).first()[0],

            "maximum": db.query(Publication.publication_year).order_by(
                Publication.publication_year.desc()
            ).first()[0]
        }
    }