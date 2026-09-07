# backend/check_users_db.py

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, ResearchProfile, Publication, Patent, FundingOpportunity
from app.services import funding_eligibility_service, funding_matching_service, researcher_feature_service

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Total Users: {len(users)}")
    for u in users:
        prof = db.query(ResearchProfile).filter(ResearchProfile.user_id == u.id).first()
        pubs = db.query(Publication).filter(Publication.user_id == u.id).count()
        pats = db.query(Patent).filter(Patent.user_id == u.id).count()
        print(f"User #{u.id}: {u.full_name} ({u.email}) - Profile: {bool(prof)}, Pubs: {pubs}, Patents: {pats}")
        
        feats = researcher_feature_service.build_researcher_features(db, u.id)
        elig = funding_eligibility_service.filter_eligible_funding(db, u.id)
        recs = funding_matching_service.rank_funding_opportunities(db, u.id, top_k=5)
        print(f"   -> Eligible grants: {len(elig.get('eligible', []))}, Recommendations: {len(recs.get('recommendations', []))}")
finally:
    db.close()
