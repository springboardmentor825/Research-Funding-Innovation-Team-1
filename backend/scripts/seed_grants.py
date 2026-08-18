"""
Seed script — inserts sample grant data into the grants table.
Run from the backend/ directory:
    python -m scripts.seed_grants

Safe to re-run: skips insertion if grants already exist.
NOTE: These are SAMPLE/FICTIONAL grants for testing purposes only.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from app.database import SessionLocal, engine, Base
from app.models.grant import Grant  # ensures table is registered

Base.metadata.create_all(bind=engine)

SAMPLE_GRANTS = [
    {
        "grant_name": "AI Research Excellence Grant",
        "funding_organization": "National Science Foundation (Sample)",
        "description": "Supports cutting-edge research in artificial intelligence, machine learning, and deep learning applications.",
        "research_area": "Artificial Intelligence",
        "keywords": "machine learning,deep learning,neural networks,AI,artificial intelligence",
        "eligibility": "University Researcher,PhD Student,Postdoctoral Researcher",
        "country": "India",
        "funding_amount": 150000.00,
        "deadline": date(2026, 6, 30),
        "application_url": "https://example.org/ai-research-grant",
        "status": "open",
    },
    {
        "grant_name": "Computer Vision Innovation Fund",
        "funding_organization": "Tech Innovation Council (Sample)",
        "description": "Funding for projects advancing computer vision, image recognition, and visual AI systems.",
        "research_area": "Computer Vision",
        "keywords": "computer vision,image recognition,object detection,deep learning,convolutional neural networks",
        "eligibility": "University Researcher,Industry Researcher",
        "country": "India",
        "funding_amount": 80000.00,
        "deadline": date(2026, 9, 15),
        "application_url": "https://example.org/cv-innovation-fund",
        "status": "open",
    },
    {
        "grant_name": "Healthcare AI Research Program",
        "funding_organization": "Medical Research Council (Sample)",
        "description": "Grants for AI-driven healthcare solutions including diagnostics, drug discovery, and patient monitoring.",
        "research_area": "Healthcare AI",
        "keywords": "healthcare,medical AI,diagnostics,drug discovery,machine learning,clinical data",
        "eligibility": "University Researcher,Medical Researcher,PhD Student",
        "country": "International",
        "funding_amount": 200000.00,
        "deadline": date(2026, 12, 31),
        "application_url": "https://example.org/healthcare-ai",
        "status": "open",
    },
    {
        "grant_name": "Climate Technology Research Grant",
        "funding_organization": "Environmental Research Institute (Sample)",
        "description": "Supports research in climate change mitigation, renewable energy, and environmental monitoring using AI.",
        "research_area": "Climate Technology",
        "keywords": "climate change,renewable energy,environmental monitoring,sustainability,AI,machine learning",
        "eligibility": "University Researcher,Government Researcher",
        "country": "International",
        "funding_amount": 120000.00,
        "deadline": date(2026, 8, 31),
        "application_url": "https://example.org/climate-tech-grant",
        "status": "open",
    },
    {
        "grant_name": "Robotics and Autonomous Systems Fellowship",
        "funding_organization": "Robotics Society (Sample)",
        "description": "Fellowship for researchers working on robotics, autonomous systems, and human-robot interaction.",
        "research_area": "Robotics",
        "keywords": "robotics,autonomous systems,human-robot interaction,control systems,machine learning,computer vision",
        "eligibility": "PhD Student,Postdoctoral Researcher,University Researcher",
        "country": "India",
        "funding_amount": 60000.00,
        "deadline": date(2026, 7, 31),
        "application_url": "https://example.org/robotics-fellowship",
        "status": "open",
    },
    {
        "grant_name": "Natural Language Processing Research Award",
        "funding_organization": "Language Technology Foundation (Sample)",
        "description": "Award for advances in NLP, text mining, conversational AI, and multilingual systems.",
        "research_area": "Natural Language Processing",
        "keywords": "NLP,natural language processing,text mining,conversational AI,transformers,large language models",
        "eligibility": "University Researcher,PhD Student",
        "country": "India",
        "funding_amount": 90000.00,
        "deadline": date(2026, 10, 15),
        "application_url": "https://example.org/nlp-award",
        "status": "open",
    },
    {
        "grant_name": "Cybersecurity and AI Defense Grant",
        "funding_organization": "National Cyber Agency (Sample)",
        "description": "Research into AI-powered cybersecurity, threat detection, and adversarial machine learning.",
        "research_area": "Cybersecurity",
        "keywords": "cybersecurity,threat detection,adversarial machine learning,AI security,intrusion detection",
        "eligibility": "University Researcher,Industry Researcher,Government Researcher",
        "country": "India",
        "funding_amount": 175000.00,
        "deadline": date(2026, 11, 30),
        "application_url": "https://example.org/cybersecurity-grant",
        "status": "open",
    },
    {
        "grant_name": "Data Science and Big Data Innovation Grant",
        "funding_organization": "Data Science Consortium (Sample)",
        "description": "Supports research in big data analytics, data engineering, and scalable machine learning pipelines.",
        "research_area": "Data Science",
        "keywords": "data science,big data,analytics,machine learning,data engineering,deep learning",
        "eligibility": "University Researcher,Industry Researcher,PhD Student",
        "country": "International",
        "funding_amount": 100000.00,
        "deadline": date(2026, 5, 31),
        "application_url": "https://example.org/data-science-grant",
        "status": "open",
    },
    {
        "grant_name": "Biomedical Engineering Research Fund",
        "funding_organization": "Biomedical Research Foundation (Sample)",
        "description": "Funding for biomedical engineering projects combining AI with medical devices and bioinformatics.",
        "research_area": "Biomedical Engineering",
        "keywords": "biomedical,bioinformatics,medical devices,AI,machine learning,genomics",
        "eligibility": "University Researcher,Medical Researcher",
        "country": "International",
        "funding_amount": 130000.00,
        "deadline": date(2026, 9, 30),
        "application_url": "https://example.org/biomedical-fund",
        "status": "open",
    },
    {
        "grant_name": "Edge Computing and IoT Research Grant",
        "funding_organization": "IoT Research Alliance (Sample)",
        "description": "Research on edge AI, IoT systems, embedded machine learning, and smart infrastructure.",
        "research_area": "Edge Computing",
        "keywords": "edge computing,IoT,embedded machine learning,smart infrastructure,deep learning,computer vision",
        "eligibility": "University Researcher,Industry Researcher,PhD Student",
        "country": "India",
        "funding_amount": 70000.00,
        "deadline": date(2026, 8, 15),
        "application_url": "https://example.org/edge-iot-grant",
        "status": "open",
    },
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(Grant).count()
        if existing > 0:
            print(f"Grants table already has {existing} records. Skipping seed.")
            return
        for data in SAMPLE_GRANTS:
            db.add(Grant(**data))
        db.commit()
        print(f"Inserted {len(SAMPLE_GRANTS)} sample grants successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
