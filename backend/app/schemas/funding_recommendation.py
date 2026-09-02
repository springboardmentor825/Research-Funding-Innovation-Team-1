# backend/app/schemas/funding_recommendation.py

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

ALLOWED_FEEDBACK_VALUES = {"viewed", "saved", "relevant", "not_relevant", "dismissed", "applied"}

class FundingFeedbackRequest(BaseModel):
    user_id: int = Field(..., description="Target user ID")
    funding_id: int = Field(..., description="Target funding opportunity ID")
    feedback: str = Field(..., description="User interaction type: viewed, saved, relevant, not_relevant, dismissed, applied")

    @field_validator("feedback")
    def validate_feedback(cls, v: str) -> str:
        clean_v = (v or "").strip().lower()
        if clean_v not in ALLOWED_FEEDBACK_VALUES:
            raise ValueError(f"Invalid feedback value '{v}'. Must be one of: {', '.join(sorted(ALLOWED_FEEDBACK_VALUES))}")
        return clean_v

class FundingFeedbackResponse(BaseModel):
    success: bool = True
    user_id: int
    funding_id: int
    status: str
    message: Optional[str] = None

class FundingRecommendationHistoryItem(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    funding_id: int
    title: str
    funder: Optional[str] = None
    amount_range: Optional[str] = None
    status: str
    feedback: Optional[str] = None
    match_score: float
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class FundingRecommendationHistoryResponse(BaseModel):
    user_id: int
    history: List[FundingRecommendationHistoryItem] = []

class SavedFundingResponse(BaseModel):
    user_id: int
    saved: List[FundingRecommendationHistoryItem] = []

class DismissedFundingResponse(BaseModel):
    user_id: int
    dismissed: List[FundingRecommendationHistoryItem] = []

class AppliedFundingResponse(BaseModel):
    user_id: int
    applied: List[FundingRecommendationHistoryItem] = []
