"""
=============================================================================
RESEARCHER INTELLIGENCE — FASTAPI ROUTER
=============================================================================
Endpoints for the Researcher Intelligence module (Member 4).

Routes:
  GET /researcher-intelligence              → All researchers, sorted by score
  GET /researcher-intelligence/{researcher_id} → Single researcher profile

Consumed by Member 5's dashboard integration.

Author: Member 4 (Researcher Intelligence)
=============================================================================
"""

from fastapi import APIRouter, HTTPException

from backend.app.services.researcher_intelligence_engine import (
    get_intelligence_data,
    get_researcher_by_id,
    get_all_researchers_sorted,
)


router = APIRouter()


# ============================================================
# GET /researcher-intelligence
# ============================================================
# Returns all researchers sorted by overall_researcher_score (desc).
# This is the primary endpoint for Member 5's dashboard.

@router.get("")
def get_all_researcher_intelligence():
    """
    Retrieve intelligence profiles for all researchers, sorted by
    overall_researcher_score in descending order.

    Response:
    [
        {
            "researcher_id": "R001",
            "name": "Dr. Ananya Krishnan",
            "institution": "IIT Madras",
            "top_expertise_areas": ["ai", "machine learning", ...],
            "publication_strength_score": 45.23,
            "patent_strength_score": 12.67,
            "overall_researcher_score": 32.41,
            "matched_publications_sample": [...],
            "matched_patents_sample": [...],
            "explanation": "..."
        },
        ...
    ]
    """
    data = get_all_researchers_sorted()
    return {
        "total_researchers": len(data),
        "researchers": data,
    }


# ============================================================
# GET /researcher-intelligence/{researcher_id}
# ============================================================
# Returns a single researcher's full intelligence profile.
# Returns 404 if the researcher_id is not found.

@router.get("/{researcher_id}")
def get_researcher_intelligence(researcher_id: str):
    """
    Retrieve the intelligence profile for a single researcher by ID.

    Path Parameters:
        researcher_id (str): The researcher's unique ID (e.g., "R001")

    Response: Single researcher intelligence object.
    Error: 404 if researcher_id is not found.
    """
    researcher = get_researcher_by_id(researcher_id)

    if researcher is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Researcher not found",
                "researcher_id": researcher_id,
                "message": (
                    f"No researcher found with ID '{researcher_id}'. "
                    f"Valid IDs: R001–R008"
                ),
            },
        )

    return researcher
