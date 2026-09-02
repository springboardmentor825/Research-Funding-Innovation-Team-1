# backend/app/models/funding_recommendation.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, func
from sqlalchemy.orm import relationship
from app.database import Base

class FundingRecommendation(Base):
    __tablename__ = "funding_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"), nullable=False, index=True)
    funding_id = Column(Integer, ForeignKey("funding_opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    generated_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status = Column(String(50), default="recommended")
    feedback = Column(String(50), nullable=True)

    user = relationship("User", back_populates="recommendations")
    funding = relationship("FundingOpportunity", back_populates="recommendations")
