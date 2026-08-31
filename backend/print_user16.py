from app.database import SessionLocal
from app.services.funding_matching_service import rank_funding_opportunities

db = SessionLocal()
res = rank_funding_opportunities(db, user_id=16, top_k=10)

print(f"\n==========================================")
print(f"USER 16 RECOMMENDATION RESULTS ({len(res['recommendations'])} items)")
print(f"==========================================\n")

for r in res['recommendations']:
    print(f"Title: {r['title']}")
    print(f"Score: {r['match_score']}% | Match Level: {r['match_level']}")
    print(f"Pub Matches: {r['publication_match_count']} | Pat Matches: {r['patent_match_count']}")
    print(f"Matched Signals: {r['matched_signals']}")
    print(f"Unmatched Signals: {r['unmatched_signals']}")
    print(f"Reason: {r['reason']}")
    print(f"Breakdown: {r['match_breakdown']}\n" + "-"*60)
