from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

ALLOWED_STATUSES = {"active", "closed", "draft"}
ALLOWED_RESEARCH_STAGES = {
    "Basic Research",
    "Applied Research",
    "Experimental Development",
    "Translational Research",
    "Commercialization",
    "Prototyping",
    "Development"
}
ALLOWED_FUNDING_TYPES = {
    "Research Grant",
    "Fellowship",
    "Innovation Grant",
    "Challenge Grant",
    "Accelerator",
    "Seed Funding",
    "Contract",
    "Award"
}

class FundingOpportunityBase(BaseModel):
    title: str = Field(..., description="Title of the funding opportunity")
    funder: str = Field(..., description="Funding organization name")
    amount_range: str = Field(..., description="Funding amount range e.g. $50,000 - $100,000")
    deadline: date = Field(..., description="Application deadline date")
    semantic_fit: Optional[int] = Field(None, description="Optional legacy fit score")
    match_badges: Optional[str] = Field(None, description="Comma-separated match badges")
    description: Optional[str] = Field(None, description="Detailed program summary")
    research_domains: Optional[str] = Field(None, description="Comma-separated research domains")
    technology_areas: Optional[str] = Field(None, description="Comma-separated technology areas")
    keywords: Optional[str] = Field(None, description="Comma-separated keywords")
    eligibility: Optional[str] = Field(None, description="Eligibility criteria")
    research_stage: Optional[str] = Field(None, description="Research stage e.g. Applied Research")
    geographic_scope: Optional[str] = Field(None, description="Geographic eligibility e.g. Global")
    funding_type: Optional[str] = Field(None, description="Type of funding e.g. Research Grant")
    status: str = Field("active", description="Status e.g. active, closed, draft")

    @field_validator("title", "funder")
    @classmethod
    def string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace.")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        val = v.strip().lower() if v else "active"
        if val == "open":
            val = "active"
        if val not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status '{v}'. Allowed: {', '.join(sorted(ALLOWED_STATUSES))}")
        return val

    @field_validator("research_stage")
    @classmethod
    def validate_research_stage(cls, v: Optional[str]) -> Optional[str]:
        if v is None or not v.strip():
            return None
        clean_v = v.strip()
        # Case insensitive match helper
        matched = next((stage for stage in ALLOWED_RESEARCH_STAGES if stage.lower() == clean_v.lower()), None)
        if matched:
            return matched
        return clean_v

    @field_validator("funding_type")
    @classmethod
    def validate_funding_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None or not v.strip():
            return None
        clean_v = v.strip()
        matched = next((ft for ft in ALLOWED_FUNDING_TYPES if ft.lower() == clean_v.lower()), None)
        if matched:
            return matched
        return clean_v

class FundingOpportunityCreate(FundingOpportunityBase):
    pass

class FundingOpportunityUpdate(BaseModel):
    title: Optional[str] = None
    funder: Optional[str] = None
    amount_range: Optional[str] = None
    deadline: Optional[date] = None
    semantic_fit: Optional[int] = None
    match_badges: Optional[str] = None
    description: Optional[str] = None
    research_domains: Optional[str] = None
    technology_areas: Optional[str] = None
    keywords: Optional[str] = None
    eligibility: Optional[str] = None
    research_stage: Optional[str] = None
    geographic_scope: Optional[str] = None
    funding_type: Optional[str] = None
    status: Optional[str] = None

class FundingOpportunitySchema(FundingOpportunityBase):
    id: int

    class Config:
        from_attributes = True

class FundingOpportunityNormalized(BaseModel):
    id: int
    title: str
    funder: str
    amount_range: str
    deadline: date
    deadline_status: str  # active, closing_soon, expired
    description: Optional[str] = ""
    domains: List[str] = []
    technologies: List[str] = []
    keywords: List[str] = []
    eligibility: Optional[str] = ""
    research_stage: Optional[str] = ""
    geographic_scope: Optional[str] = ""
    funding_type: Optional[str] = ""
    status: str = "active"
    match_badges: List[str] = []

    class Config:
        from_attributes = True

# ==========================================
# ELIGIBILITY FILTER SCHEMAS (PART 3)
# ==========================================
class EligibilityItemResult(BaseModel):
    funding_id: int
    title: str
    funder: str
    eligible: bool
    deadline_status: str  # open, closing_soon, expired, unknown
    status_check: str     # passed, failed, unknown
    research_stage_check: str  # passed, failed, unknown
    geographic_check: str      # passed, failed, unknown
    eligibility_check: str     # passed, failed, unknown
    reason: str
    
    # Detail fields
    amount_range: Optional[str] = None
    deadline: Optional[date] = None
    research_stage: Optional[str] = None
    geographic_scope: Optional[str] = None
    funding_type: Optional[str] = None

class EligibilityFilterResponse(BaseModel):
    user_id: int
    total_opportunities: int
    eligible_count: int
    excluded_count: int
    eligible: List[EligibilityItemResult] = []
    excluded: List[EligibilityItemResult] = []

