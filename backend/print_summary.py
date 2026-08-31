from app.database import SessionLocal
from app.services.funding_matching_service import rank_funding_opportunities

db = SessionLocal()
res = rank_funding_opportunities(db, user_id=16, top_k=10)

print("RANKED RECOMMENDATIONS FOR USER 16:")
for idx, r in enumerate(res['recommendations'], 1):
    print(f"{idx}. {r['title']}")
    print(f"   Score: {r['match_score']}% [{r['match_level']}]")
    print(f"   Pub Matches: {r['publication_match_count']} | Pat Matches: {r['patent_match_count']}")
    print(f"   Matched Signals: {r['matched_signals']}")
    print(f"   Unmatched Signals: {r['unmatched_signals']}")
    print()
