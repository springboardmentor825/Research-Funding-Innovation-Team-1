from app.database import SessionLocal
from app.services.funding_matching_service import rank_funding_opportunities

db = SessionLocal()
res = rank_funding_opportunities(db, user_id=16, top_k=10)

print(f"\n==========================================")
print(f"MATHEMATICAL SCORE RECONCILIATION VERIFICATION")
print(f"==========================================\n")

all_passed = True
for idx, r in enumerate(res['recommendations'], 1):
    bd = r['match_breakdown']
    bd_sum = round(sum(bd.values()))
    score = r['match_score']
    match_ok = (score == bd_sum)
    if not match_ok:
        all_passed = False

    print(f"{idx}. {r['title']}")
    print(f"   Displayed Match Score: {score}% [{r['match_level']}]")
    print(f"   Sub-Score Sum: {bd_sum} | Exact Match: {match_ok}")
    print(f"   Breakdown: {bd}")
    print(f"   Matched Signals: {r['matched_signals']}")
    print(f"   Unmatched Signals: {r['unmatched_signals']}")
    print(f"   Pub Matches: {r['publication_match_count']} | Pat Matches: {r['patent_match_count']}")
    print("-" * 60)

print(f"\nMath Reconciliation Status: {'ALL PASSED 100%' if all_passed else 'FAILED'}")
