# backend/seed_user16_profile.py

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import engine
from sqlalchemy import text

def seed_user16_profile():
    with engine.connect() as conn:
        # Check if user 16 exists
        user = conn.execute(text("SELECT id, email, full_name FROM users WHERE id = 16")).first()
        if not user:
            print("User 16 does not exist. Creating User 16...")
            conn.execute(text("""
                INSERT INTO users (id, full_name, email, password, role, login_type, created_at)
                VALUES (16, 'Dr. Sarah Jenkins', 'testresearcher@example.com', 'hashed_pass_123', 'researcher', 'email', NOW())
                ON DUPLICATE KEY UPDATE full_name=VALUES(full_name), email=VALUES(email);
            """))
            conn.commit()

        # Check existing profile for user 16
        profile = conn.execute(text("SELECT profile_id FROM research_profile WHERE user_id = 16")).first()
        if profile:
            conn.execute(text("""
                UPDATE research_profile SET
                    organization = 'Stanford University',
                    designation = 'Associate Professor',
                    research_domain = 'Artificial Intelligence, Computer Science',
                    technology_area = 'Natural Language Processing, Machine Learning, Deep Learning',
                    research_interests = 'Large Language Models, Retrieval-Augmented Generation, Semantic Search, Vector Databases, Graph Neural Networks',
                    keywords = 'LLM, RAG, Transformers, Vector Search, FAISS, Knowledge Graphs, PyTorch',
                    bio = 'Lead Researcher at Stanford AI Lab specializing in RAG architectures and semantic search.'
                WHERE user_id = 16;
            """))
            print("Updated existing Research Profile for User 16.")
        else:
            conn.execute(text("""
                INSERT INTO research_profile (
                    user_id, organization, designation, research_domain, technology_area,
                    research_interests, keywords, bio
                ) VALUES (
                    16, 'Stanford University', 'Associate Professor',
                    'Artificial Intelligence, Computer Science',
                    'Natural Language Processing, Machine Learning, Deep Learning',
                    'Large Language Models, Retrieval-Augmented Generation, Semantic Search, Vector Databases, Graph Neural Networks',
                    'LLM, RAG, Transformers, Vector Search, FAISS, Knowledge Graphs, PyTorch',
                    'Lead Researcher at Stanford AI Lab specializing in RAG architectures and semantic search.'
                );
            """))
            print("Inserted new Research Profile for User 16.")
        conn.commit()
    print("User 16 profile seeding completed successfully!")

if __name__ == "__main__":
    seed_user16_profile()
