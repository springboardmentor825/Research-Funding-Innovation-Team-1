# backend/app/schemas/research_intelligence.py

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ==========================================
# PART 7: RESEARCH COLLABORATION SCHEMAS
# ==========================================

class EvidenceItem(BaseModel):
    id: Optional[int] = None
    title: str
    type: str  # "publication" or "patent"
    technology_domain: Optional[str] = None

class CollaboratorMatch(BaseModel):
    researcher_id: int
    name: str
    email: Optional[str] = None
    organization: Optional[str] = None
    designation: Optional[str] = None
    bio: Optional[str] = None
    score: int = Field(..., ge=0, le=100, description="Overall collaboration compatibility score (0-100)")
    match_category: str  # "Strong Collaboration", "Moderate Collaboration", "Complementary Focus", "Weak Overlap"
    shared_domains: List[str] = []
    shared_technologies: List[str] = []
    shared_interests: List[str] = []
    shared_keywords: List[str] = []
    complementary_expertise: List[str] = []
    publication_evidence: List[EvidenceItem] = []
    patent_evidence: List[EvidenceItem] = []
    explanation: str

class CollaborationResponse(BaseModel):
    user_id: int
    researcher: Dict[str, Any]
    total_candidates_evaluated: int
    collaborators: List[CollaboratorMatch]


# ==========================================
# PART 8: PATENT & INNOVATION SCHEMAS
# ==========================================

class TechnologyDistribution(BaseModel):
    technology: str
    count: int
    percentage: float

class DomainDistribution(BaseModel):
    domain: str
    count: int
    percentage: float

class TechnologyTrend(BaseModel):
    technology: str
    trend: str  # "increasing", "stable", "declining", "new"
    recent_count: int
    previous_count: int
    growth_rate: float
    is_emerging: bool

class InventorActivity(BaseModel):
    researcher_id: Optional[int] = None
    name: str
    patent_count: int
    primary_domain: Optional[str] = None

class InstitutionActivity(BaseModel):
    institution: str
    patent_count: int

class PatentAnalyticsSummary(BaseModel):
    total_patents: int
    active_patents: int
    expired_patents: int
    patents_by_year: Dict[str, int]
    technology_distribution: List[TechnologyDistribution]
    domain_distribution: List[DomainDistribution]
    trends: List[TechnologyTrend]
    emerging_technologies: List[TechnologyTrend]
    top_inventors: List[InventorActivity]
    top_institutions: List[InstitutionActivity]

class PatentDetailIntelligence(BaseModel):
    patent_id: int
    title: str
    inventor: str
    assignee: str
    technology_domain: str
    filing_date: str
    status: str
    researcher_id: Optional[int] = None
    researcher_name: Optional[str] = None
    related_publications: List[Dict[str, Any]] = []
    innovation_score: int = Field(..., ge=0, le=100)
    innovation_indicators: Dict[str, Any] = {}


# ==========================================
# PART 9: RESEARCHER PROFILE INTELLIGENCE SCHEMAS
# ==========================================

class TechnologyProfileItem(BaseModel):
    technology: str
    evidence_count: int
    publication_count: int
    patent_count: int
    prominence: str  # "High", "Medium", "Emerging"

class ResearcherCompleteness(BaseModel):
    completeness_score: int = Field(..., ge=0, le=100)
    missing_fields: List[str] = []

class ResearcherIntelligenceResponse(BaseModel):
    researcher_id: int
    name: str
    email: Optional[str] = None
    organization: Optional[str] = None
    designation: Optional[str] = None
    bio: Optional[str] = None
    primary_domain: Optional[str] = None
    research_domains: List[str] = []
    technology_profile: List[TechnologyProfileItem] = []
    research_interests: List[str] = []
    keywords: List[str] = []
    publication_count: int
    patent_count: int
    publication_intelligence: Dict[str, Any] = {}
    patent_intelligence: Dict[str, Any] = {}
    funding_intelligence: Dict[str, Any] = {}
    collaboration_intelligence: Dict[str, Any] = {}
    research_activity_score: int = Field(..., ge=0, le=100)
    profile_completeness: ResearcherCompleteness
    trends: List[Dict[str, Any]] = []

class ResearcherComparisonResponse(BaseModel):
    researcher1: Dict[str, Any]
    researcher2: Dict[str, Any]
    shared_domains: List[str] = []
    shared_technologies: List[str] = []
    shared_interests: List[str] = []
    complementary_capabilities: List[Dict[str, Any]] = []
    comparison_matrix: Dict[str, Any] = {}
