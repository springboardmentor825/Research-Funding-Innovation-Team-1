import sys
import os
from datetime import date, timedelta

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import FundingOpportunity

def seed_demo_opportunities():
    db = SessionLocal()
    today = date.today()

    demo_opps = [
        {
            "title": "Generative AI and Large Language Models Research Grant",
            "funder": "National Science Foundation (NSF)",
            "amount_range": "$250,000 – $750,000",
            "deadline": today + timedelta(days=10),
            "semantic_fit": 95,
            "match_badges": "High Fit, Generative AI, RAG",
            "description": "Funding for research on generative artificial intelligence, large language models, natural language processing, retrieval augmented generation, semantic search, and trustworthy AI systems.",
            "research_domains": "Artificial Intelligence, Computer Science, Natural Language Processing",
            "technology_areas": "Generative AI, Large Language Models, Natural Language Processing, Retrieval-Augmented Generation, Semantic Search",
            "keywords": "AI, Generative AI, LLM, NLP, RAG, Semantic Search",
            "eligibility": "Open to all faculty and researchers at accredited universities and non-profit research institutes.",
            "research_stage": "Faculty / Graduate Research",
            "geographic_scope": "Global",
            "funding_type": "Research Grant",
            "status": "open"
        },
        {
            "title": "AI and Natural Language Processing Innovation Grant",
            "funder": "DARPA Information Innovation Office",
            "amount_range": "$300,000 – $600,000",
            "deadline": today + timedelta(days=20),
            "semantic_fit": 90,
            "match_badges": "Strong Fit, NLP, LLM",
            "description": "Supports research in natural language processing, machine learning, language models, text analytics, and intelligent language systems.",
            "research_domains": "Artificial Intelligence, Natural Language Processing",
            "technology_areas": "NLP, Machine Learning, Large Language Models",
            "keywords": "NLP, ML, Language Models, Text Analytics",
            "eligibility": "Faculty and post-doctoral researchers in AI or Computational Linguistics.",
            "research_stage": "Faculty / Post-Doctoral",
            "geographic_scope": "Global",
            "funding_type": "Innovation Grant",
            "status": "open"
        },
        {
            "title": "Knowledge Graph and Retrieval Intelligence Seed Fund",
            "funder": "Microsoft Research & AI Institute",
            "amount_range": "$150,000 – $400,000",
            "deadline": today + timedelta(days=35),
            "semantic_fit": 88,
            "match_badges": "Strong Fit, Knowledge Graph, RAG",
            "description": "Supports intelligent information retrieval, knowledge graphs, vector databases, semantic search, and retrieval augmented generation.",
            "research_domains": "Artificial Intelligence, Knowledge Representation",
            "technology_areas": "Knowledge Graphs, RAG, Vector Databases, Semantic Search",
            "keywords": "Knowledge Graph, RAG, Vector Database, Semantic Search",
            "eligibility": "Open to researchers working on knowledge representation and search.",
            "research_stage": "Early Career / Faculty",
            "geographic_scope": "Global",
            "funding_type": "Seed Fund",
            "status": "open"
        },
        {
            "title": "Advanced Machine Learning Research Program",
            "funder": "US Department of Energy (DOE) Office of Science",
            "amount_range": "$500,000 – $1,200,000",
            "deadline": today + timedelta(days=50),
            "semantic_fit": 82,
            "match_badges": "Moderate Fit, Machine Learning",
            "description": "Supports machine learning and deep learning research including predictive modeling, neural networks, representation learning, and intelligent systems.",
            "research_domains": "Artificial Intelligence, Computer Science",
            "technology_areas": "Machine Learning, Deep Learning",
            "keywords": "Machine Learning, Deep Learning, Neural Networks",
            "eligibility": "Academic institutions and national research laboratories.",
            "research_stage": "Senior Faculty / Lab Principal Investigators",
            "geographic_scope": "Global",
            "funding_type": "Research Grant",
            "status": "open"
        },
        {
            "title": "Explainable and Trustworthy Artificial Intelligence Grant",
            "funder": "National Institutes of Health (NIH) Data Science Initiative",
            "amount_range": "$200,000 – $500,000",
            "deadline": today + timedelta(days=70),
            "semantic_fit": 78,
            "match_badges": "Moderate Fit, Explainable AI",
            "description": "Funding for explainable AI, interpretable machine learning, responsible AI, trustworthy AI systems, and transparent models.",
            "research_domains": "Artificial Intelligence",
            "technology_areas": "Explainable AI, Machine Learning, Trustworthy AI",
            "keywords": "XAI, Explainable AI, Responsible AI",
            "eligibility": "University faculty and interdisciplinary research teams.",
            "research_stage": "Faculty / Graduate Research",
            "geographic_scope": "Global",
            "funding_type": "Research Grant",
            "status": "open"
        },
        {
            "title": "Artificial Intelligence for Healthcare Innovation Grant",
            "funder": "Wellcome Trust Digital Health Innovation",
            "amount_range": "$350,000 – $800,000",
            "deadline": today + timedelta(days=15),
            "semantic_fit": 72,
            "match_badges": "Moderate Fit, Healthcare AI",
            "description": "Supports AI applications in healthcare including intelligent decision support, medical data analysis, machine learning, natural language processing, and trustworthy AI.",
            "research_domains": "Artificial Intelligence, Healthcare",
            "technology_areas": "Machine Learning, NLP, Explainable AI",
            "keywords": "AI, Healthcare AI, Medical NLP, Machine Learning",
            "eligibility": "Interdisciplinary teams in AI, Computer Science, or Biomedical Informatics.",
            "research_stage": "Faculty / Clinical Researchers",
            "geographic_scope": "Global",
            "funding_type": "Innovation Grant",
            "status": "open"
        },
        {
            "title": "AI for Sustainable Agriculture Research Grant",
            "funder": "USDA National Institute of Food and Agriculture",
            "amount_range": "$100,000 – $300,000",
            "deadline": today + timedelta(days=45),
            "semantic_fit": 55,
            "match_badges": "Weak Fit, Agriculture",
            "description": "Supports applications of artificial intelligence and data science for crop monitoring, agricultural prediction, smart farming, and sustainable agriculture.",
            "research_domains": "Artificial Intelligence, Agriculture",
            "technology_areas": "Machine Learning, Computer Vision, Predictive Analytics",
            "keywords": "AI, Agriculture, Smart Farming, Crop Prediction",
            "eligibility": "Agricultural and environmental data science researchers.",
            "research_stage": "Faculty / Research Scientists",
            "geographic_scope": "Global",
            "funding_type": "Research Grant",
            "status": "open"
        },
        {
            "title": "AI-Driven Cybersecurity Research Fund",
            "funder": "Department of Homeland Security (DHS) S&T Directorate",
            "amount_range": "$250,000 – $600,000",
            "deadline": today + timedelta(days=60),
            "semantic_fit": 50,
            "match_badges": "Weak Fit, Cybersecurity",
            "description": "Supports research in machine learning for cybersecurity, threat detection, anomaly detection, and intelligent security systems.",
            "research_domains": "Artificial Intelligence, Cybersecurity",
            "technology_areas": "Machine Learning, Anomaly Detection",
            "keywords": "AI Security, Cybersecurity, Threat Detection",
            "eligibility": "Cybersecurity and Machine Learning research faculty.",
            "research_stage": "Faculty / Lead Investigators",
            "geographic_scope": "Global",
            "funding_type": "Research Grant",
            "status": "open"
        },
        {
            "title": "Advanced Mechanical Systems Research Grant",
            "funder": "National Mechanical Engineering Foundation",
            "amount_range": "$150,000 – $400,000",
            "deadline": today + timedelta(days=80),
            "semantic_fit": 20,
            "match_badges": "Unrelated, Mechanical Systems",
            "description": "Supports research in mechanical system design, thermal engineering, structural mechanics, manufacturing systems, and mechanical materials.",
            "research_domains": "Mechanical Engineering",
            "technology_areas": "Mechanical Design, Thermal Systems, Manufacturing",
            "keywords": "Mechanical Engineering, Thermal Engineering",
            "eligibility": "Mechanical Engineering faculty and researchers.",
            "research_stage": "Faculty / Post-Doctoral",
            "geographic_scope": "Global",
            "funding_type": "Research Grant",
            "status": "open"
        },
        {
            "title": "Renewable Energy Systems Innovation Grant",
            "funder": "Clean Energy Research Council",
            "amount_range": "$200,000 – $500,000",
            "deadline": today + timedelta(days=90),
            "semantic_fit": 15,
            "match_badges": "Unrelated, Renewable Energy",
            "description": "Supports research in solar energy, wind energy, energy storage, power systems, and renewable energy technologies.",
            "research_domains": "Renewable Energy, Electrical Engineering",
            "technology_areas": "Solar Energy, Energy Storage, Wind Energy",
            "keywords": "Renewable Energy, Solar, Wind, Energy Storage",
            "eligibility": "Energy engineering researchers and faculty.",
            "research_stage": "Faculty / Research Engineers",
            "geographic_scope": "Global",
            "funding_type": "Innovation Grant",
            "status": "open"
        }
    ]

    added_count = 0
    updated_count = 0

    for item in demo_opps:
        existing = db.query(FundingOpportunity).filter(FundingOpportunity.title == item["title"]).first()
        if existing:
            # Update deadline and status to ensure future validity
            existing.deadline = item["deadline"]
            existing.status = item["status"]
            existing.amount_range = item["amount_range"]
            updated_count += 1
        else:
            opp = FundingOpportunity(**item)
            db.add(opp)
            added_count += 1

    db.commit()
    print(f"Seed completed successfully! Added: {added_count}, Updated: {updated_count}, Total opportunities in DB: {db.query(FundingOpportunity).count()}")
    db.close()

if __name__ == "__main__":
    seed_demo_opportunities()
