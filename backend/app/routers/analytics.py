from fastapi import APIRouter
from sqlalchemy import func

from backend.app.database import SessionLocal
from backend.app.models import Publication


router = APIRouter()


@router.get("/summary")
def get_summary():

    db = SessionLocal()

    try:

        total_publications = db.query(
            func.count(Publication.id)
        ).scalar()

        total_citations = db.query(
            func.sum(Publication.cited_by_count)
        ).scalar()

        average_citations = db.query(
            func.avg(Publication.cited_by_count)
        ).scalar()

        retracted = db.query(
            func.count(Publication.id)
        ).filter(
            Publication.is_retracted == True
        ).scalar()

        open_access = db.query(
            func.count(Publication.id)
        ).filter(
            Publication.open_access == True
        ).scalar()

        return {
            "total_publications": total_publications,
            "total_citations": total_citations or 0,
            "average_citations": round(
                float(average_citations or 0), 2
            ),
            "retracted_publications": retracted,
            "open_access_publications": open_access
        }

    finally:
        db.close()

@router.get("/yearly-trend")
def get_yearly_trend():

    db = SessionLocal()

    try:

        results = (
            db.query(
                Publication.publication_year,
                func.count(Publication.id).label("publication_count"),
                func.sum(Publication.cited_by_count).label("total_citations"),
                func.avg(Publication.cited_by_count).label("average_citations")
            )
            .group_by(Publication.publication_year)
            .order_by(Publication.publication_year)
            .all()
        )

        yearly_data = []

        for row in results:

            yearly_data.append({
                "publication_year": row.publication_year,
                "publication_count": row.publication_count,
                "total_citations": row.total_citations or 0,
                "average_citations": round(
                    float(row.average_citations or 0), 2
                )
            })

        return {
            "yearly_trend": yearly_data
        }

    finally:
        db.close()
@router.get("/domain-distribution")
def get_domain_distribution():

    db = SessionLocal()

    try:

        results = (
            db.query(
                Publication.primary_topic,
                func.count(Publication.id).label("publication_count")
            )
            .filter(Publication.primary_topic.isnot(None))
            .group_by(Publication.primary_topic)
            .order_by(
                func.count(Publication.id).desc()
            )
            .all()
        )

        domain_data = []

        for row in results:

            domain_data.append({
                "domain": row.primary_topic,
                "publication_count": row.publication_count
            })

        return {
            "domain_distribution": domain_data
        }

    finally:
        db.close()
@router.get("/topic-distribution")
def get_topic_distribution():

    db = SessionLocal()

    try:

        results = (
            db.query(
                Publication.topics,
                func.count(Publication.id).label("publication_count")
            )
            .filter(
                Publication.topics.isnot(None),
                Publication.topics != ""
            )
            .group_by(Publication.topics)
            .order_by(
                func.count(Publication.id).desc()
            )
            .limit(20)
            .all()
        )

        topic_data = []

        for row in results:

            topic_data.append({
                "topic": row.topics,
                "publication_count": row.publication_count
            })

        return {
            "total_topics_returned": len(topic_data),
            "topics": topic_data
        }

    finally:
        db.close()
@router.get("/citation-analysis")
def citation_analysis():

    db = SessionLocal()

    try:

        total_citations = db.query(
            func.sum(Publication.cited_by_count)
        ).scalar() or 0

        average_citations = db.query(
            func.avg(Publication.cited_by_count)
        ).scalar() or 0

        maximum_citations = db.query(
            func.max(Publication.cited_by_count)
        ).scalar() or 0

        minimum_citations = db.query(
            func.min(Publication.cited_by_count)
        ).scalar() or 0

        return {
            "total_citations": int(total_citations),
            "average_citations": round(
                float(average_citations), 2
            ),
            "maximum_citations": int(maximum_citations),
            "minimum_citations": int(minimum_citations)
        }

    finally:
        db.close()
@router.get("/emerging-topics")
def emerging_topics():

    db = SessionLocal()

    try:

        publications = db.query(
            Publication.publication_year,
            Publication.topics
        ).all()

        topic_year_counts = {}

        for year, topics in publications:

            if not topics:
                continue

            topic_list = [
                topic.strip()
                for topic in topics.split(";")
                if topic.strip()
            ]

            for topic in topic_list:

                key = (topic, year)

                if key not in topic_year_counts:
                    topic_year_counts[key] = 0

                topic_year_counts[key] += 1

        topic_growth = []

        topics = set(
            topic for topic, year in topic_year_counts.keys()
        )

        for topic in topics:

            yearly_counts = {
                year: count
                for (t, year), count
                in topic_year_counts.items()
                if t == topic
            }

            years = sorted(yearly_counts.keys())

            if len(years) < 2:
                continue

            latest_year = years[-1]
            previous_year = years[-2]

            latest_count = yearly_counts.get(
                latest_year, 0
            )

            previous_count = yearly_counts.get(
                previous_year, 0
            )

            if previous_count > 0 and latest_count >= 5:

                growth = (
                    (latest_count - previous_count)
                    / previous_count
                ) * 100
                
                topic_growth.append({
                    "topic": topic,
                    "latest_year": latest_year,
                    "latest_publications": latest_count,
                    "previous_year": previous_year,
                    "previous_publications": previous_count,
                    "growth_percentage": round(
                        growth, 2
                    )
                })

        topic_growth.sort(
            key=lambda x: x["growth_percentage"],
            reverse=True
        )

        return {
            "total_emerging_topics": len(topic_growth),
            "emerging_topics": topic_growth[:20]
        }

    finally:
        db.close()
@router.get("/top-cited")
def top_cited_publications():

    db = SessionLocal()

    try:

        publications = db.query(
            Publication.id,
            Publication.title,
            Publication.publication_year,
            Publication.cited_by_count,
            Publication.doi
        ).order_by(
            Publication.cited_by_count.desc()
        ).limit(20).all()

        return {
            "total_returned": len(publications),
            "top_cited_publications": [
                {
                    "id": publication.id,
                    "title": publication.title,
                    "publication_year": publication.publication_year,
                    "cited_by_count": publication.cited_by_count,
                    "doi": publication.doi
                }
                for publication in publications
            ]
        }

    finally:
        db.close()