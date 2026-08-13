# backend/app/rag/database_loader.py

import os
import logging
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

from app.rag.document_loader import load_documents

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "research_platform")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def load_database_records():
    """
    Extract structured records from MySQL database tables for Hybrid RAG ingestion.
    Tables: publications, patents, research_profile, funding_opportunities, documents.
    Returns list of searchable text documents with metadata.
    """
    logger.info("Loading Database Records from MySQL...")
    db_documents = []

    try:
        with engine.connect() as conn:
            # 1. Publications Table
            try:
                pubs = conn.execute(text("SELECT publication_id, title, authors, journal, publication_year, doi FROM publications")).fetchall()
                for p in pubs:
                    content = f"Publication: Title: {p[1]}. Authors: {p[2]}. Journal: {p[3]}. Year: {p[4]}. DOI: {p[5] or 'N/A'}."
                    db_documents.append({
                        "content": content,
                        "metadata": {
                            "source_type": "database",
                            "table": "publications",
                            "record_id": p[0],
                            "source_name": p[1]
                        }
                    })
                logger.info(f"Loaded {len(pubs)} publication records.")
            except Exception as e:
                logger.error(f"Error reading publications: {e}")

            # 2. Patents Table
            try:
                patents = conn.execute(text("SELECT patent_id, title, inventor, assignee, technology_domain, filing_date FROM patents")).fetchall()
                for pat in patents:
                    content = f"Patent: Title: {pat[1]}. Inventor: {pat[2]}. Assignee: {pat[3]}. Domain: {pat[4]}. Filing Date: {pat[5]}."
                    db_documents.append({
                        "content": content,
                        "metadata": {
                            "source_type": "database",
                            "table": "patents",
                            "record_id": pat[0],
                            "source_name": pat[1]
                        }
                    })
                logger.info(f"Loaded {len(patents)} patent records.")
            except Exception as e:
                logger.error(f"Error reading patents: {e}")

            # 3. Research Profile Table
            try:
                profiles = conn.execute(text("SELECT profile_id, user_id, organization, designation, research_domain, technology_area, research_interests, keywords, bio FROM research_profile")).fetchall()
                for prof in profiles:
                    content = (
                        f"Research Profile: Organization: {prof[2]}. Designation: {prof[3]}. "
                        f"Research Domain: {prof[4]}. Technology Area: {prof[5]}. "
                        f"Interests: {prof[6] or 'N/A'}. Keywords: {prof[7] or 'N/A'}. Bio: {prof[8] or 'N/A'}."
                    )
                    source_title = f"{prof[3]} at {prof[2]}"
                    db_documents.append({
                        "content": content,
                        "metadata": {
                            "source_type": "database",
                            "table": "research_profile",
                            "record_id": prof[0],
                            "source_name": source_title
                        }
                    })
                logger.info(f"Loaded {len(profiles)} research profile records.")
            except Exception as e:
                logger.error(f"Error reading research_profile: {e}")

            # 4. Funding Opportunities Table
            try:
                fundings = conn.execute(text("SELECT id, title, funder, amount_range, deadline, match_badges FROM funding_opportunities")).fetchall()
                for f in fundings:
                    content = f"Funding: Title: {f[1]}. Agency: {f[2]}. Amount: {f[3]}. Deadline: {f[4]}. Badges: {f[5] or 'N/A'}."
                    db_documents.append({
                        "content": content,
                        "metadata": {
                            "source_type": "database",
                            "table": "funding_opportunities",
                            "record_id": f[0],
                            "source_name": f[1]
                        }
                    })
                logger.info(f"Loaded {len(fundings)} funding opportunity records.")
            except Exception as e:
                logger.error(f"Error reading funding_opportunities: {e}")

            # 5. Documents Table
            try:
                docs = conn.execute(text("SELECT id, title, document_type, source FROM documents")).fetchall()
                for d in docs:
                    content = f"Document: Title: {d[1]}. Type: {d[2] or 'N/A'}. Source: {d[3] or 'N/A'}."
                    db_documents.append({
                        "content": content,
                        "metadata": {
                            "source_type": "database",
                            "table": "documents",
                            "record_id": d[0],
                            "source_name": d[1] or "Document"
                        }
                    })
                logger.info(f"Loaded {len(docs)} document metadata records.")
            except Exception as e:
                logger.error(f"Error reading documents table: {e}")

    except Exception as e:
        logger.error(f"Failed to connect to MySQL database: {e}")

    logger.info(f"Total Database Documents Loaded: {len(db_documents)}")
    return db_documents

def load_hybrid_documents():
    """
    Load PDF research documents and MySQL database records, merging both sources
    with preserved structured metadata.
    """
    logger.info("Starting Hybrid Document Loading...")
    hybrid_docs = []

    # 1. Load PDF documents
    pdf_docs = load_documents()
    for doc in pdf_docs:
        hybrid_docs.append({
            "content": doc["content"],
            "metadata": {
                "source_type": "pdf",
                "source_name": doc["title"]
            }
        })
    logger.info(f"Loaded PDF Documents: {len(pdf_docs)}")

    # 2. Load DB records
    db_records = load_database_records()
    hybrid_docs.extend(db_records)

    logger.info(f"Total Hybrid Documents Loaded: {len(hybrid_docs)}")
    return hybrid_docs

if __name__ == "__main__":
    docs = load_hybrid_documents()
    print(f"\n✅ Total Loaded Hybrid Documents: {len(docs)}")
    for d in docs[:3]:
        print("Sample:", d)
