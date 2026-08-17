from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Float, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="researcher")
    login_type = Column(String(50), nullable=False, default="email")
    created_at = Column(DateTime, server_default=func.now())
    google_id = Column(String(255), unique=True, nullable=True)
    profile_picture = Column(String(500), nullable=True)
    auth_provider = Column(String(50), nullable=False, default="email")

    # Child relationships (cascade delete handled by database layer or ORM context)
    profile = relationship("ResearchProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="user", cascade="all, delete-orphan")
    patents = relationship("Patent", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("FundingRecommendation", back_populates="user", cascade="all, delete-orphan")

class ResearchProfile(Base):
    __tablename__ = "Research_Profile"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"), unique=True, nullable=False)
    organization = Column(String(255), nullable=False, index=True)
    designation = Column(String(255), nullable=False)
    research_domain = Column(String(255), nullable=False, index=True)
    technology_area = Column(String(255), nullable=False, index=True)
    research_interests = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)

    user = relationship("User", back_populates="profile")

class Publication(Base):
    __tablename__ = "Publications"

    publication_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    authors = Column(Text, nullable=False)
    journal = Column(String(255), nullable=False)
    publication_year = Column(Integer, nullable=False, index=True)
    doi = Column(String(100), nullable=True, index=True)

    user = relationship("User", back_populates="publications")

class Patent(Base):
    __tablename__ = "Patents"

    patent_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    inventor = Column(String(255), nullable=False)
    assignee = Column(String(255), nullable=False)
    technology_domain = Column(String(255), nullable=False, index=True)
    filing_date = Column(Date, nullable=False, index=True)

    user = relationship("User", back_populates="patents")

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
    research_domains = Column(String(500), nullable=True)
    technology_areas = Column(String(500), nullable=True)
    keywords = Column(String(500), nullable=True)
    eligibility = Column(String(500), nullable=True)
    research_stage = Column(String(100), nullable=True)
    geographic_scope = Column(String(100), nullable=True)
    funding_type = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="open")

    recommendations = relationship("FundingRecommendation", back_populates="funding", cascade="all, delete-orphan")

class FundingRecommendation(Base):
    __tablename__ = "funding_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="CASCADE"), nullable=False, index=True)
    funding_id = Column(Integer, ForeignKey("funding_opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    generated_at = Column(DateTime, server_default=func.now())
    status = Column(String(50), default="recommended")
    feedback = Column(String(50), nullable=True)

    user = relationship("User", back_populates="recommendations")
    funding = relationship("FundingOpportunity", back_populates="recommendations")
