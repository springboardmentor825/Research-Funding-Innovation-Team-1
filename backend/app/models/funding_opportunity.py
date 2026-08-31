from sqlalchemy import Column, Integer, String, Text, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    funder = Column(String(255), nullable=False, index=True)
    amount_range = Column(String(100), nullable=False)
    deadline = Column(Date, nullable=False)
    semantic_fit = Column(Integer, nullable=True)
    match_badges = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    research_domains = Column(Text, nullable=True)
    technology_areas = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    eligibility = Column(Text, nullable=True)
    research_stage = Column(String(100), nullable=True)
    geographic_scope = Column(String(255), nullable=True)
    funding_type = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="active")

    recommendations = relationship("FundingRecommendation", back_populates="funding", cascade="all, delete-orphan")
