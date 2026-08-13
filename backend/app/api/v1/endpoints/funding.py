# backend/app/api/v1/endpoints/funding.py

from typing import List, Dict, Any
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_funding() -> List[Dict[str, Any]]:
    """Retrieve all funding opportunities."""
    return []
