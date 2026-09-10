"""Seed funding_opportunities with realistic grant data for the integrated Infera project.

Idempotent: skips grants whose title already exists. Run from backend/ as:
    .venv/Scripts/python scripts/seed_funding.py
"""
import os
from datetime import date

import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3307")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "research_platform"),
}

GRANTS = [
    {
        "title": "National AI Research Acceleration Grant",
        "funder": "National Research Foundation",
        "amount_range": "$100,000 - $500,000",
        "deadline": date(2026, 12, 15),
        "semantic_fit": 95,
        "match_badges": "Strong Research Match, AI Focus",
        "description": "High-impact research in artificial intelligence, machine learning, large language models, and applied NLP systems.",
        "research_domains": "AI;Artificial Intelligence;Machine Learning;NLP",
        "technology_areas": "Generative AI;LLMs;RAG;Deep Learning",
        "keywords": "LLM;RAG;NLP;transformers;neural networks;AI",
        "eligibility": "Open to researchers at academic institutions with demonstrated publication track record.",
        "research_stage": "Applied",
        "geographic_scope": "International",
        "funding_type": "Research Grant",
        "status": "open",
    },
    {
        "title": "European Innovation Council AI Pathfinder",
        "funder": "European Commission",
        "amount_range": "$250,000 - $2,000,000",
        "deadline": date(2027, 1, 31),
        "semantic_fit": 90,
        "match_badges": "Featured Partnership, AI Focus",
        "description": "Frontier research for breakthrough intelligence systems, including language models, retrieval augmentation, and knowledge reasoning.",
        "research_domains": "AI;NLP;Computational Linguistics",
        "technology_areas": "RAG;LLMs;Knowledge Graphs",
        "keywords": "large language models;retrieval augmented generation;semantic search;knowledge reasoning",
        "eligibility": "European or partner-country institutions; collaboration network strongly encouraged.",
        "research_stage": "Exploratory",
        "geographic_scope": "Europe",
        "funding_type": "Research Grant",
        "status": "open",
    },
    {
        "title": "Quantum Computing Advanced Research Program",
        "funder": "Department of Science & Technology",
        "amount_range": "$150,000 - $750,000",
        "deadline": date(2026, 11, 30),
        "semantic_fit": 70,
        "match_badges": "Multi-Disciplinary",
        "description": "Research grants for quantum algorithms, post-quantum cryptography, and quantum information processing.",
        "research_domains": "Quantum Computing;Cryptography",
        "technology_areas": "Quantum Algorithms;Post-Quantum Security",
        "keywords": "quantum;post-quantum;cryptography;quantum error correction",
        "eligibility": "Open to faculty and research groups in computer science and physics.",
        "research_stage": "Exploratory",
        "geographic_scope": "International",
        "funding_type": "Research Grant",
        "status": "open",
    },
    {
        "title": "Blockchain for Open Science Royalties",
        "funder": "Web3 Foundation",
        "amount_range": "$50,000 - $200,000",
        "deadline": date(2027, 2, 28),
        "semantic_fit": 65,
        "match_badges": "Innovation Partner",
        "description": "Smart-contract frameworks for automated IP royalties, decentralized data marketplaces, and transparent research funding distribution.",
        "research_domains": "Blockchain;Distributed Ledger;Data Economy",
        "technology_areas": "Smart Contracts;Tokenomics",
        "keywords": "blockchain;smart contracts;IP royalties;decentralized;token",
        "eligibility": "Research teams prototyping decentralized applications for scholarly publishing.",
        "research_stage": "Prototyping",
        "geographic_scope": "International",
        "funding_type": "Innovation Grant",
        "status": "open",
    },
    {
        "title": "Edge & Embedded AI Systems Grant",
        "funder": "Industrial R&D Consortium",
        "amount_range": "$80,000 - $300,000",
        "deadline": date(2026, 12, 31),
        "semantic_fit": 75,
        "match_badges": "Applied AI",
        "description": "Apply artificial intelligence at the edge: on-device inference, federated learning, and low-power neural networks.",
        "research_domains": "AI;Embedded Systems;IoT",
        "technology_areas": "Edge AI;Federated Learning;On-device Inference",
        "keywords": "edge computing;federated learning;on-device AI;IoT",
        "eligibility": "Universities and applied research labs; collaborations with industry partners preferred.",
        "research_stage": "Applied",
        "geographic_scope": "International",
        "funding_type": "Research Grant",
        "status": "open",
    },
    {
        "title": "Computer Vision & Multimodal Perception Grant",
        "funder": "Vision Research Initiative",
        "amount_range": "$120,000 - $450,000",
        "deadline": date(2027, 3, 15),
        "semantic_fit": 62,
        "match_badges": "Cross-Domain",
        "description": "Cutting-edge research in computer vision, multimodal perception, and vision-language models.",
        "research_domains": "Computer Vision;Multimodal AI",
        "technology_areas": "Vision-Language Models;Object Detection;Image Generation",
        "keywords": "computer vision;image recognition;multimodal;vision-language",
        "eligibility": "Open to computer science departments with active vision research groups.",
        "research_stage": "Applied",
        "geographic_scope": "International",
        "funding_type": "Research Grant",
        "status": "open",
    },
    {
        "title": "Natural Language Processing Fellowship",
        "funder": "Language Technology Trust",
        "amount_range": "$40,000 - $150,000",
        "deadline": date(2027, 4, 30),
        "semantic_fit": 88,
        "match_badges": "Targeted NLP",
        "description": "Fellowships for researchers advancing natural language understanding, sentiment analysis, and multilingual models.",
        "research_domains": "NLP;Computational Linguistics",
        "technology_areas": "Text Mining;Sentiment Analysis;MultilingualNLP",
        "keywords": "NLP;natural language;sentiment;text processing;multilingual",
        "eligibility": "Early-career researchers and doctoral students in computational linguistics.",
        "research_stage": "Exploratory",
        "geographic_scope": "International",
        "funding_type": "Fellowship",
        "status": "open",
    },
    {
        "title": "Responsible and Ethical AI Development Grant",
        "funder": "Ethics & Society Foundation",
        "amount_range": "$60,000 - $200,000",
        "deadline": date(2027, 5, 31),
        "semantic_fit": 72,
        "match_badges": "Societal Impact",
        "description": "Research on AI fairness, transparency, interpretability, and responsible deployment of language models.",
        "research_domains": "AI;Ethics;Social Science",
        "technology_areas": "AI Governance;Model Interpretability",
        "keywords": "responsible AI;fairness;interpretability;AI ethics;transparency",
        "eligibility": "Interdisciplinary teams combining technical and social-science expertise.",
        "research_stage": "Applied",
        "geographic_scope": "International",
        "funding_type": "Research Grant",
        "status": "open",
    },
    {
        "title": "Scientific Knowledge Graph & Semantic Retrieval Grant",
        "funder": "Open Science Data Alliance",
        "amount_range": "$90,000 - $350,000",
        "deadline": date(2027, 1, 15),
        "semantic_fit": 82,
        "match_badges": "Data-driven",
        "description": "Build knowledge graphs and semantic retrieval pipelines for open scientific literature and citation intelligence.",
        "research_domains": "AI;Information Retrieval;Data Science",
        "technology_areas": "Knowledge Graphs;Semantic Retrieval;Vector Search",
        "keywords": "knowledge graph;semantic search;vector database;citation analysis;information retrieval",
        "eligibility": "Open to libraries, research institutes, and computer science labs.",
        "research_stage": "Applied",
        "geographic_scope": "International",
        "funding_type": "Research Grant",
        "status": "open",
    },
    {
        "title": "AI-powered Healthcare Diagnostics Innovation",
        "funder": "MedTech Research Council",
        "amount_range": "$200,000 - $1,000,000",
        "deadline": date(2027, 2, 15),
        "semantic_fit": 58,
        "match_badges": "Applied AI",
        "description": "Machine learning for medical imaging, diagnostic support systems, and clinical NLP applications.",
        "research_domains": "AI;Healthcare;Bioinformatics",
        "technology_areas": "Clinical NLP;Medical Imaging;Predictive Models",
        "keywords": "healthcare AI;medical imaging;clinical NLP;diagnostics",
        "eligibility": "Joint proposals between medical institutions and AI research labs.",
        "research_stage": "Applied",
        "geographic_scope": "International",
        "funding_type": "Research Grant",
        "status": "open",
    },
]

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    inserted = 0
    for g in GRANTS:
        cur.execute("SELECT id FROM funding_opportunities WHERE title = %s", (g["title"],))
        if cur.fetchone():
            continue
        cur.execute(
            """
            INSERT INTO funding_opportunities
                (title, funder, amount_range, deadline, semantic_fit, match_badges,
                 description, research_domains, technology_areas, keywords,
                 eligibility, research_stage, geographic_scope, funding_type, status)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                g["title"], g["funder"], g["amount_range"], g["deadline"],
                g["semantic_fit"], g["match_badges"], g["description"],
                g["research_domains"], g["technology_areas"], g["keywords"],
                g["eligibility"], g["research_stage"], g["geographic_scope"],
                g["funding_type"], g["status"],
            ),
        )
        conn.commit()
        inserted += 1
        print("Seeded:", g["title"])
    print(f"Done. Inserted {inserted} funding opportunities.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()