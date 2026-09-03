from typing import List
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, extract
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Patent, ResearchPublication, ResearchPublicationConcept
from app.schemas import PatentCreate, PatentUpdate, Patent as PatentSchema
from app.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[PatentSchema])
def list_my_patents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all patents belonging to the current user."""
    return current_user.patents

@router.post("/", response_model=PatentSchema, status_code=status.HTTP_201_CREATED)
def create_patent(
    patent_in: PatentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new patent record under current user."""
    patent = Patent(**patent_in.model_dump(), user_id=current_user.id)
    db.add(patent)
    db.commit()
    db.refresh(patent)
    return patent

@router.put("/{patent_id}", response_model=PatentSchema)
def update_patent(
    patent_id: int,
    patent_in: PatentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modify a specific patent record."""
    patent = db.query(Patent).filter(
        Patent.patent_id == patent_id,
        Patent.user_id == current_user.id
    ).first()
    if not patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Patent record not found or unauthorized."
        )
        
    update_data = patent_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(patent, field, val)
        
    db.add(patent)
    db.commit()
    db.refresh(patent)
    return patent

@router.delete("/{patent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patent(
    patent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific patent record."""
    patent = db.query(Patent).filter(
        Patent.patent_id == patent_id,
        Patent.user_id == current_user.id
    ).first()
    if not patent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Patent record not found or unauthorized."
        )
    db.delete(patent)
    db.commit()
    return


@router.get("/analysis/domains")
def patent_domains_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Count patents per technology domain."""
    stmt = (
        select(Patent.technology_domain, func.count().label("count"))
        .where(Patent.technology_domain.is_not(None))
        .group_by(Patent.technology_domain)
        .order_by(func.count().desc())
    )
    rows = db.execute(stmt).all()
    return [{"domain": domain, "count": count} for domain, count in rows]


@router.get("/analysis/trends")
def patent_filing_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Patents filed per year."""
    stmt = (
        select(
            extract("year", Patent.filing_date).label("year"),
            func.count().label("count"),
        )
        .where(Patent.filing_date.is_not(None))
        .group_by(extract("year", Patent.filing_date))
        .order_by(extract("year", Patent.filing_date))
    )
    rows = db.execute(stmt).all()
    return [{"year": int(year), "count": count} for year, count in rows]


@router.get("/analysis/growth")
def patent_growth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Year-over-year growth rate per technology domain."""
    stmt = (
        select(
            Patent.technology_domain,
            extract("year", Patent.filing_date).label("year"),
            func.count().label("count"),
        )
        .where(Patent.filing_date.is_not(None), Patent.technology_domain.is_not(None))
        .group_by(Patent.technology_domain, extract("year", Patent.filing_date))
        .order_by(Patent.technology_domain, extract("year", Patent.filing_date))
    )
    rows = db.execute(stmt).all()

    domain_years = defaultdict(list)
    for domain, year, count in rows:
        domain_years[domain].append((int(year), count))

    results = []
    for domain, year_data in domain_years.items():
        year_data.sort(key=lambda x: x[0])
        for i, (year, count) in enumerate(year_data):
            if i == 0:
                growth_rate = 0.0
            else:
                prev = year_data[i - 1][1]
                growth_rate = round(((count - prev) / prev * 100), 1) if prev > 0 else 0.0
            results.append({
                "domain": domain,
                "year": year,
                "count": count,
                "growth_rate": growth_rate,
            })
    return results


@router.get("/analysis/research-overlap")
def research_overlap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cross-reference patent technology domains with research publication topics."""
    patent_domains = db.execute(
        select(func.distinct(Patent.technology_domain))
        .where(Patent.technology_domain.is_not(None))
    ).scalars().all()

    results = []
    for domain in patent_domains:
        patent_count = db.execute(
            select(func.count()).select_from(Patent)
            .where(Patent.technology_domain == domain)
        ).scalar() or 0

        pub_count = db.execute(
            select(func.count()).select_from(ResearchPublication)
            .where(func.lower(ResearchPublication.primary_topic).like(f"%{domain.lower()}%"))
        ).scalar() or 0

        concept_count = db.execute(
            select(func.count()).select_from(ResearchPublicationConcept)
            .where(func.lower(ResearchPublicationConcept.concept_name).like(f"%{domain.lower()}%"))
        ).scalar() or 0

        results.append({
            "domain": domain,
            "patent_count": patent_count,
            "publication_count": pub_count,
            "concept_count": concept_count,
            "total_research": pub_count + concept_count,
        })

    return sorted(results, key=lambda x: x["patent_count"], reverse=True)


@router.get("/analysis/opportunities")
def innovation_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Find domains with high patent activity but low research coverage — innovation gaps."""
    overlap = research_overlap(current_user, db)

    opportunities = []
    for item in overlap:
        if item["patent_count"] > 0:
            ratio = item["total_research"] / item["patent_count"] if item["patent_count"] else 999
            if ratio < 0.5:
                opportunities.append({
                    "domain": item["domain"],
                    "patent_count": item["patent_count"],
                    "research_count": item["total_research"],
                    "gap_score": item["patent_count"] - item["total_research"],
                    "opportunity": (
                        f"Strong patent activity ({item['patent_count']} patents) in "
                        f"{item['domain']} with limited research ({item['total_research']} publications) "
                        f"— potential innovation gap"
                    ),
                })

    return sorted(opportunities, key=lambda x: x["gap_score"], reverse=True)
