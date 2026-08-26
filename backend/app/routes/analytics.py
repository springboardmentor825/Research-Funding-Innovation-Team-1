from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import (
    ResearchPublication as Publication,
    ResearchPublicationAuthor as Author,
    ResearchPublicationInstitution as Institution,
    ResearchPublicationTopic as Topic,
    ResearchPublicationConcept as Concept,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


def _scalar(db: Session, stmt):
    return db.execute(stmt).scalar() or 0


@router.get("/overview")
def analytics_overview(db: Session = Depends(get_db)):
    """Headline KPIs over the whole global research corpus."""
    total = _scalar(db, select(func.count()).select_from(Publication))
    citations = _scalar(db, select(func.coalesce(func.sum(Publication.cited_by_count), 0)))
    open_access = _scalar(db, select(func.count()).select_from(Publication).where(Publication.open_access == 1))
    retracted = _scalar(db, select(func.count()).select_from(Publication).where(Publication.is_retracted == 1))
    distinct_authors = _scalar(db, select(func.count(func.distinct(Author.author_name))))
    distinct_institutions = _scalar(db, select(func.count(func.distinct(Institution.institution_name))))
    distinct_topics = _scalar(db, select(func.count(func.distinct(Topic.topic_name))))
    distinct_sources = _scalar(
        db, select(func.count(func.distinct(Publication.source))).where(Publication.source.is_not(None)))
    first_year = db.execute(select(func.min(Publication.publication_year))).scalar()
    last_year = db.execute(select(func.max(Publication.publication_year))).scalar()

    return {
        "total_publications": total,
        "total_citations": citations,
        "avg_citations": round(citations / total, 1) if total else 0,
        "open_access_count": open_access,
        "open_access_pct": round(open_access / total * 100, 1) if total else 0,
        "retracted_count": retracted,
        "retracted_pct": round(retracted / total * 100, 1) if total else 0,
        "distinct_authors": distinct_authors,
        "distinct_institutions": distinct_institutions,
        "distinct_topics": distinct_topics,
        "distinct_sources": distinct_sources,
        "year_range": [first_year, last_year],
    }


@router.get("/publication-trends")
def publication_trends(
    from_year: Optional[int] = Query(None, alias="from"),
    to_year: Optional[int] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    """Yearly publication counts and total citations, optionally filtered to a year window."""
    stmt = (
        select(
            Publication.publication_year,
            func.count().label("count"),
            func.coalesce(func.sum(Publication.cited_by_count), 0).label("citations"),
        )
        .where(Publication.publication_year.is_not(None))
        .group_by(Publication.publication_year)
        .order_by(Publication.publication_year)
    )
    if from_year is not None:
        stmt = stmt.where(Publication.publication_year >= from_year)
    if to_year is not None:
        stmt = stmt.where(Publication.publication_year <= to_year)
    rows = db.execute(stmt).all()
    return [
        {"year": year, "count": count, "citations": int(citations)}
        for year, count, citations in rows
    ]


@router.get("/publication-types")
def publication_types(db: Session = Depends(get_db)):
    """Distribution of publication types."""
    rows = (
        db.execute(
            select(Publication.publication_type, func.count().label("count"))
            .where(Publication.publication_type.is_not(None))
            .group_by(Publication.publication_type)
            .order_by(func.count().desc(), Publication.publication_type)
        )
        .all()
    )
    return [{"type": ptype, "count": count} for ptype, count in rows]


def _top_items(db: Session, model, name_col, limit: int):
    rows = (
        db.execute(
            select(name_col, func.count().label("count"))
            .group_by(name_col)
            .order_by(func.count().desc(), name_col.asc())
            .limit(limit)
        )
        .all()
    )
    return [{"name": name, "count": count} for name, count in rows]


@router.get("/topics")
def topics(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Most frequent research topics across the corpus."""
    return _top_items(db, Topic, Topic.topic_name, limit)


@router.get("/institutions")
def institutions(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Most productive institutions."""
    return _top_items(db, Institution, Institution.institution_name, limit)


@router.get("/authors")
def authors(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Most prolific authors."""
    return _top_items(db, Author, Author.author_name, limit)


@router.get("/primary-topics")
def primary_topics(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Most common primary topics."""
    rows = (
        db.execute(
            select(Publication.primary_topic, func.count().label("count"))
            .where(Publication.primary_topic.is_not(None))
            .group_by(Publication.primary_topic)
            .order_by(func.count().desc(), Publication.primary_topic)
            .limit(limit)
        )
        .all()
    )
    return [{"name": name, "count": count} for name, count in rows]


@router.get("/concepts")
def concepts(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Most frequent research concepts."""
    return _top_items(db, Concept, Concept.concept_name, limit)


@router.get("/top-cited")
def top_cited(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Highest-cited publications in the corpus."""
    rows = (
        db.execute(
            select(
                Publication.title,
                Publication.publication_year,
                Publication.cited_by_count,
                Publication.source,
                Publication.authors_raw,
                Publication.doi,
            )
            .order_by(Publication.cited_by_count.desc(), Publication.title)
            .limit(limit)
        )
        .all()
    )
    return [
        {
            "title": title,
            "year": year,
            "cited_by_count": cited_by_count,
            "source": source,
            "authors": authors_raw,
            "doi": doi,
        }
        for title, year, cited_by_count, source, authors_raw, doi in rows
    ]


@router.get("/open-access-status")
def open_access_status(db: Session = Depends(get_db)):
    """Open access vs closed access split."""
    rows = db.execute(
        select(Publication.open_access, func.count().label("count")).group_by(Publication.open_access)
    ).all()
    return [{"status": "Open Access" if value else "Closed Access", "count": count} for value, count in rows]


@router.get("/retraction-status")
def retraction_status(db: Session = Depends(get_db)):
    """Retracted vs non-retracted split."""
    rows = db.execute(
        select(Publication.is_retracted, func.count().label("count")).group_by(Publication.is_retracted)
    ).all()
    return [{"status": "Retracted" if value else "Not Retracted", "count": count} for value, count in rows]


@router.get("/sources")
def sources(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Top publication venues (journals / sources)."""
    rows = (
        db.execute(
            select(Publication.source, func.count().label("count"))
            .where(Publication.source.is_not(None))
            .group_by(Publication.source)
            .order_by(func.count().desc(), Publication.source)
            .limit(limit)
        )
        .all()
    )
    return [{"source": source, "count": count} for source, count in rows]