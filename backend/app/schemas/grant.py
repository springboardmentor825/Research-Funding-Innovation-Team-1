from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, field_validator


class GrantCreate(BaseModel):
    grant_name: str
    funding_organization: str
    description: Optional[str] = None
    research_area: Optional[str] = None
    keywords: Optional[str] = None       # comma-separated
    eligibility: Optional[str] = None
    country: Optional[str] = None
    funding_amount: Optional[Decimal] = None
    deadline: Optional[date] = None
    application_url: Optional[str] = None
    status: Optional[str] = "open"

    @field_validator("funding_amount")
    @classmethod
    def funding_amount_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError("funding_amount must be non-negative")
        return v

    @field_validator("deadline")
    @classmethod
    def deadline_not_past(cls, v):
        if v is not None and v < date.today():
            raise ValueError("deadline cannot be in the past")
        return v


class GrantUpdate(BaseModel):
    grant_name: Optional[str] = None
    funding_organization: Optional[str] = None
    description: Optional[str] = None
    research_area: Optional[str] = None
    keywords: Optional[str] = None
    eligibility: Optional[str] = None
    country: Optional[str] = None
    funding_amount: Optional[Decimal] = None
    deadline: Optional[date] = None
    application_url: Optional[str] = None
    status: Optional[str] = None


class GrantResponse(BaseModel):
    id: int
    grant_name: str
    funding_organization: str
    description: Optional[str]
    research_area: Optional[str]
    keywords: Optional[str]
    eligibility: Optional[str]
    country: Optional[str]
    funding_amount: Optional[Decimal]
    deadline: Optional[date]
    application_url: Optional[str]
    status: Optional[str]

    model_config = {"from_attributes": True}


# ---------- Matching ----------

class GrantMatchRequest(BaseModel):
    research_area: str
    keywords: List[str]
    country: Optional[str] = None
    eligibility: Optional[str] = None

    @field_validator("keywords")
    @classmethod
    def keywords_not_empty(cls, v):
        if not v:
            raise ValueError("keywords list must not be empty")
        return v


class GrantMatchResult(BaseModel):
    grant_id: int
    grant_name: str
    organization: str
    match_score: int
    matching_reasons: List[str]
    deadline: Optional[date]
    funding_amount: Optional[Decimal]
    application_url: Optional[str]


class GrantMatchResponse(BaseModel):
    matches: List[GrantMatchResult]
