# backend/app/api/v1/endpoints/innovation.py

from typing import List, Dict, Any
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_innovations() -> List[Dict[str, Any]]:
    """Retrieve list of innovation projects."""
    return []
