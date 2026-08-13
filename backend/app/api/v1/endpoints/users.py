# backend/app/api/v1/endpoints/users.py

from fastapi import APIRouter
from app.schemas import User

router = APIRouter()

@router.get("/me", response_model=User)
def read_current_user_me():
    """Retrieve logged-in user profile info."""
    return {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Default User",
        "role": "researcher",
        "login_type": "email",
        "created_at": "2026-08-13T00:00:00"
    }
