from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Patent
from app.schemas import PatentCreate, PatentUpdate, Patent as PatentSchema
from app.auth import get_current_user

from app.services import patent_intelligence_service
from app.schemas.research_intelligence import PatentAnalyticsSummary, PatentDetailIntelligence

router = APIRouter()

@router.get("/intelligence", response_model=PatentAnalyticsSummary)
def get_patent_intelligence(db: Session = Depends(get_db)):
    """Retrieve comprehensive Part 8 Patent & Innovation Intelligence analytics."""
    return patent_intelligence_service.get_patent_intelligence_analytics(db)

@router.get("/trends")
def get_patent_trends(db: Session = Depends(get_db)):
    """Retrieve temporal technology growth trends and emerging technology indicators."""
    analytics = patent_intelligence_service.get_patent_intelligence_analytics(db)
    return {
        "trends": analytics["trends"],
        "emerging_technologies": analytics["emerging_technologies"]
    }

@router.get("/{patent_id}/intelligence", response_model=PatentDetailIntelligence)
def get_patent_detail_intelligence(patent_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed innovation intelligence and indicators for a specific patent."""
    detail = patent_intelligence_service.get_patent_detail_intelligence(db, patent_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patent with ID {patent_id} does not exist."
        )
    return detail

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
