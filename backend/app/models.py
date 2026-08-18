from sqlalchemy import Column, String, Integer, Boolean, Text, Date
from backend.app.database import Base


class Publication(Base):

    __tablename__ = "publications"

    # OpenAlex ID
    id = Column(String(100), primary_key=True, index=True)

    # Basic publication information
    title = Column(Text, nullable=True)

    publication_year = Column(Integer, nullable=False)

    publication_date = Column(Date, nullable=True)

    type = Column(String(100), nullable=True)

    # Research information
    authors = Column(Text, nullable=True)

    institutions = Column(Text, nullable=True)

    topics = Column(Text, nullable=True)

    primary_topic = Column(Text, nullable=True)

    concepts = Column(Text, nullable=True)

    # Citation information
    cited_by_count = Column(Integer, default=0)

    # DOI
    doi = Column(Text, nullable=True)

    # Journal/source
    source = Column(Text, nullable=True)

    # Boolean fields
    is_retracted = Column(Boolean, default=False)

    open_access = Column(Boolean, default=False)