# backend/get_target_user.py
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app.models import User, ResearchProfile
from app.services import funding_matching_service

db = SessionLocal()
try:
    profiles = db.query(ResearchProfile).all()
    for p in profiles:
        u = db.query(User).filter(User.id == p.user_id).first()
        recs = funding_matching_service.rank_funding_opportunities(db, p.user_id, top_k=5)
        count = len(recs.get("recommendations", []))
        print(f"User ID #{p.user_id} ({u.full_name if u else 'N/A'}): Recommendations = {count}")
finally:
    db.close()
