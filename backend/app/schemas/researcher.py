# backend/app/schemas/researcher.py

from typing import List, Optional
from pydantic import BaseModel, Field

class ResearcherProfileSummary(BaseModel):
    user_id: int = Field(..., description="ID of the user")
    full_name: Optional[str] = Field(None, description="Full name of researcher")
    email: Optional[str] = Field(None, description="Email address")
    organization: Optional[str] = Field(None, description="Current organization / institution")
    designation: Optional[str] = Field(None, description="Academic or professional designation")
    bio: Optional[str] = Field(None, description="Researcher biography")
    
    research_domain: List[str] = Field(default_factory=list, description="Primary research domains")
    technology_areas: List[str] = Field(default_factory=list, description="Technology areas of expertise")
    research_interests: List[str] = Field(default_factory=list, description="Specific research interests")
    keywords: List[str] = Field(default_factory=list, description="Relevant expertise keywords")
    
    publication_topics: List[str] = Field(default_factory=list, description="Publication titles/topics")
    patent_domains: List[str] = Field(default_factory=list, description="Patent domains and innovation topics")
    
    combined_research_text: str = Field("", description="Unified text representation for semantic vector embeddings")
    
    publication_count: int = Field(0, description="Total number of published papers")
    patent_count: int = Field(0, description="Total number of patents")
    interest_count: int = Field(0, description="Total count of research interests")
    keyword_count: int = Field(0, description="Total count of keywords")
    
    has_profile: bool = Field(True, description="Whether a structured research_profile record exists")

    class Config:
        from_attributes = True
