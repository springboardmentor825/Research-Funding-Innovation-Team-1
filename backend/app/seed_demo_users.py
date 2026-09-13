import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine, SessionLocal
from app.models import User, ResearchProfile
from app.auth import get_password_hash

def seed_demo_accounts():
    db = SessionLocal()
    try:
        # 1. Startup Founder User: startup1@example.com / startu1
        startup_email = "startup1@example.com"
        startup_user = db.query(User).filter(User.email == startup_email).first()
        if not startup_user:
            startup_user = User(
                full_name="Alex Rivera (Startup Founder)",
                email=startup_email,
                password=get_password_hash("startu1"),
                role="startup_founder",
                login_type="email",
                auth_provider="email"
            )
            startup_user.account_status = "active"
            db.add(startup_user)
            db.commit()
            db.refresh(startup_user)
            print(f"Created demo startup founder account: {startup_email}")
        else:
            startup_user.password = get_password_hash("startu1")
            startup_user.role = "startup_founder"
            startup_user.account_status = "active"
            db.commit()
            print(f"Updated demo startup founder account: {startup_email}")

        # Ensure Research Profile for startup founder
        if not db.query(ResearchProfile).filter(ResearchProfile.user_id == startup_user.id).first():
            profile = ResearchProfile(
                user_id=startup_user.id,
                organization="Apex AI Technologies",
                designation="Founder & CEO",
                research_domain="Artificial Intelligence & Commercialization",
                technology_area="Vector Search & LLMs",
                research_interests="Deep Tech Startup, Grant Funding, Patent Licensing",
                keywords="ai, rag, startup, patent"
            )
            db.add(profile)
            db.commit()

        # 2. Researcher User: test@example.com / passowrd123
        researcher_email = "test@example.com"
        researcher_user = db.query(User).filter(User.email == researcher_email).first()
        if not researcher_user:
            researcher_user = User(
                full_name="Dr. Sarah Chen",
                email=researcher_email,
                password=get_password_hash("passowrd123"),
                role="researcher",
                login_type="email",
                auth_provider="email"
            )
            researcher_user.account_status = "active"
            db.add(researcher_user)
            db.commit()
            db.refresh(researcher_user)
            print(f"Created demo researcher account: {researcher_email}")
        else:
            researcher_user.password = get_password_hash("passowrd123")
            researcher_user.role = "researcher"
            researcher_user.account_status = "active"
            db.commit()
            print(f"Updated demo researcher account: {researcher_email}")

        # Ensure Research Profile for researcher
        if not db.query(ResearchProfile).filter(ResearchProfile.user_id == researcher_user.id).first():
            profile = ResearchProfile(
                user_id=researcher_user.id,
                organization="Stanford AI Lab",
                designation="Principal Investigator",
                research_domain="Machine Learning & Robotics",
                technology_area="Neural Architectures",
                research_interests="RAG Systems, Computer Vision, Academic Publications",
                keywords="research, publications, grant"
            )
            db.add(profile)
            db.commit()

        print("Demo account seeding completed successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_accounts()
