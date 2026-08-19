# backend/app/schemas/__init__.py

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# ==========================================
# RESEARCH PROFILE SCHEMAS
# ==========================================
class ResearchProfileBase(BaseModel):
    organization: str
    designation: str
    research_domain: str
    technology_area: str
    research_interests: Optional[str] = None
    keywords: Optional[str] = None
    bio: Optional[str] = None

class ResearchProfileCreate(ResearchProfileBase):
    pass

class ResearchProfileUpdate(BaseModel):
    organization: Optional[str] = None
    designation: Optional[str] = None
    research_domain: Optional[str] = None
    technology_area: Optional[str] = None
    research_interests: Optional[str] = None
    keywords: Optional[str] = None
    bio: Optional[str] = None

class ResearchProfile(ResearchProfileBase):
    profile_id: int
    user_id: int

    class Config:
        from_attributes = True

# ==========================================
# PUBLICATION SCHEMAS
# ==========================================
class PublicationBase(BaseModel):
    title: str
    authors: str
    journal: str
    publication_year: int
    doi: Optional[str] = None

class PublicationCreate(PublicationBase):
    pass

class PublicationUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    publication_year: Optional[int] = None
    doi: Optional[str] = None

class Publication(PublicationBase):
    publication_id: int
    user_id: int

    class Config:
        from_attributes = True

# ==========================================
# PATENT SCHEMAS
# ==========================================
class PatentBase(BaseModel):
    title: str
    inventor: str
    assignee: str
    technology_domain: str
    filing_date: date

class PatentCreate(PatentBase):
    pass

class PatentUpdate(BaseModel):
    title: Optional[str] = None
    inventor: Optional[str] = None
    assignee: Optional[str] = None
    technology_domain: Optional[str] = None
    filing_date: Optional[date] = None

class Patent(PatentBase):
    patent_id: int
    user_id: int

    class Config:
        from_attributes = True

# ==========================================
# USER SCHEMAS
# ==========================================
class UserBase(BaseModel):
    full_name: str
    email: str
    role: str = "researcher"
    login_type: str = "email"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    login_type: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    
    profile: Optional[ResearchProfile] = None
    publications: List[Publication] = []
    patents: List[Patent] = []

    class Config:
        from_attributes = True

# ==========================================
# TOKEN SCHEMAS
# ==========================================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: str

# ==========================================
# FUNDING SCHEMAS
# ==========================================
class FundingOpportunityBase(BaseModel):
    title: str
    funder: str
    amount_range: str
    deadline: date
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
    status: str = "open"

class FundingOpportunityCreate(FundingOpportunityBase):
    pass

class FundingOpportunitySchema(FundingOpportunityBase):
    id: int

    class Config:
        from_attributes = True

class FundingRecommendationItem(BaseModel):
    funding_id: int
    title: str
    funder: str
    amount_range: str
    deadline: str
    match_score: int
    reason: str
    matched_signals: List[str] = []
    unmatched_signals: List[str] = []
    status: Optional[str] = "recommended"
    
    # Expanded detail fields
    description: Optional[str] = None
    research_domains: List[str] = []
    technology_areas: List[str] = []
    keywords: List[str] = []
    eligibility: Optional[str] = None
    research_stage: Optional[str] = None
    geographic_scope: Optional[str] = None
    funding_type: Optional[str] = None
    match_badges: List[str] = []
    
    # Detailed match breakdown weights out of max available points
    match_breakdown: Optional[dict] = None

class FundingRecommendationResponse(BaseModel):
    user_id: int
    researcher_profile: Optional[dict] = None
    recommendations: List[FundingRecommendationItem] = []

class FundingFeedbackRequest(BaseModel):
    user_id: int
    funding_id: int
    feedback: str

# ==========================================
# RAG SCHEMAS
# ==========================================
class RAGChatRequest(BaseModel):
    query: Optional[str] = None
    question: Optional[str] = None
    top_k: Optional[int] = 5

    def get_query(self) -> str:
        return self.query or self.question or ""

class RAGChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[dict] = []

class ChatRequest(BaseModel):
    question: str = Field(..., example="What is Retrieval Augmented Generation?")

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[str] = []

class SearchRequest(BaseModel):
    query: str = Field(..., example="Deep Learning Protein Folding")
    top_k: int = Field(5, ge=1, le=20)

class SearchResultItem(BaseModel):
    title: str
    content: str
    source_type: Optional[str] = None
    table: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]

class StatsResponse(BaseModel):
    total_vectors: int
    total_chunks: int
    index_status: str
    pdf_sources: int
    db_sources: int
