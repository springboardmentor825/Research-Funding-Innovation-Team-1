from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, func, SmallInteger
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="researcher")
    login_type = Column(String(50), nullable=False, default="email")
    created_at = Column(DateTime, server_default=func.now())
    google_id = Column(String(255), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    auth_provider = Column(String(50), nullable=False, default="email")

    profile = relationship("ResearchProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="user", cascade="all, delete-orphan")
    patents = relationship("Patent", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    collaborations = relationship("Collaboration", back_populates="user", cascade="all, delete-orphan")
    lab_resources = relationship("LabResource", back_populates="user", cascade="all, delete-orphan")
    user_settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")

class ResearchProfile(Base):
    __tablename__ = "research_profile"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    organization = Column(String(255), nullable=False, index=True)
    designation = Column(String(255), nullable=False)
    research_domain = Column(String(255), nullable=False, index=True)
    technology_area = Column(String(255), nullable=False, index=True)
    research_interests = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)

    user = relationship("User", back_populates="profile")

class Publication(Base):
    __tablename__ = "publications"

    publication_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    authors = Column(Text, nullable=False)
    journal = Column(String(255), nullable=False)
    publication_year = Column(Integer, nullable=False, index=True)
    doi = Column(String(100), nullable=True, index=True)

    user = relationship("User", back_populates="publications")

class Patent(Base):
    __tablename__ = "patents"

    patent_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    inventor = Column(String(255), nullable=False)
    assignee = Column(String(255), nullable=False)
    technology_domain = Column(String(255), nullable=False, index=True)
    filing_date = Column(Date, nullable=False, index=True)

    user = relationship("User", back_populates="patents")

class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text, nullable=True)
    publication_year = Column(Integer, nullable=True)
    domain = Column(String(255), nullable=True)
    file_path = Column(String(1000), nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now())

class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    funder = Column(String(255), nullable=False)
    amount_range = Column(String(100), nullable=False)
    deadline = Column(Date, nullable=False)
    semantic_fit = Column(Integer, nullable=True)
    match_badges = Column(String(255), nullable=True)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    document_type = Column(String(50), nullable=True)
    source = Column(String(255), nullable=True)
    upload_date = Column(DateTime, server_default=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)
    generated_date = Column(DateTime, server_default=func.now())
    file_size = Column(String(50), nullable=False)
    preview_snippet = Column(Text, nullable=True)

    user = relationship("User", back_populates="reports")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False)
    message = Column(String(500), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    is_read = Column(SmallInteger, default=0)

    user = relationship("User", back_populates="alerts")

class Collaboration(Base):
    __tablename__ = "collaborations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    researcher_name = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    overlap_topics = Column(String(500), nullable=False)
    collaboration_score = Column(Integer, nullable=False)

    user = relationship("User", back_populates="collaborations")

class LabResource(Base):
    __tablename__ = "lab_resources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)
    availability_status = Column(String(50), nullable=False)
    location = Column(String(255), nullable=False)

    user = relationship("User", back_populates="lab_resources")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email_notifications = Column(SmallInteger, default=1)
    push_notifications = Column(SmallInteger, default=1)
    profile_visibility = Column(String(50), default="public")

    user = relationship("User", back_populates="user_settings")
