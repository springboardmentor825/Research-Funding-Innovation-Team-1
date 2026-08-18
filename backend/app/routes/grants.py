from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.grant import Grant
from ..schemas.grant import GrantCreate, GrantUpdate, GrantResponse, GrantMatchRequest, GrantMatchResponse
from ..services.grant_matching import match_grants

router = APIRouter(prefix="/grants", tags=["Grants"])


# ---------- CRUD ----------

@router.post("/", response_model=GrantResponse, status_code=status.HTTP_201_CREATED)
def create_grant(payload: GrantCreate, db: Session = Depends(get_db)):
    """Create a new grant opportunity."""
    grant = Grant(**payload.model_dump())
    db.add(grant)
    db.commit()
    db.refresh(grant)
    return grant


@router.get("/", response_model=List[GrantResponse])
def list_grants(db: Session = Depends(get_db)):
    """Return all grant opportunities."""
    return db.query(Grant).all()


@router.get("/{grant_id}", response_model=GrantResponse)
def get_grant(grant_id: int, db: Session = Depends(get_db)):
    """Return a single grant by ID."""
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")
    return grant


@router.put("/{grant_id}", response_model=GrantResponse)
def update_grant(grant_id: int, payload: GrantUpdate, db: Session = Depends(get_db)):
    """Update an existing grant."""
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(grant, field, value)
    db.commit()
    db.refresh(grant)
    return grant


@router.delete("/{grant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grant(grant_id: int, db: Session = Depends(get_db)):
    """Delete a grant by ID."""
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")
    db.delete(grant)
    db.commit()


# ---------- Matching ----------

@router.post("/match", response_model=GrantMatchResponse)
def match_grants_endpoint(payload: GrantMatchRequest, db: Session = Depends(get_db)):
    """
    Match a researcher's profile against all open grants.
    Returns grants ranked by match score (0-100), highest first.
    """
    results = match_grants(db, payload)
    return GrantMatchResponse(matches=results)
