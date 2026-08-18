from sqlalchemy import Column, Integer, String, Text, Numeric, Date, TIMESTAMP, func
from ..database import Base


class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    grant_name = Column(String(500), nullable=False)
    funding_organization = Column(String(255), nullable=False)
    description = Column(Text)
    research_area = Column(String(255))
    keywords = Column(Text)           # comma-separated keyword string
    eligibility = Column(Text)
    country = Column(String(100))
    funding_amount = Column(Numeric(15, 2))
    deadline = Column(Date)
    application_url = Column(String(500))
    status = Column(String(50), default="open")
    created_at = Column(TIMESTAMP, server_default=func.now())
