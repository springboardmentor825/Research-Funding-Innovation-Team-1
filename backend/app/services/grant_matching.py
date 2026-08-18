"""
Grant Matching Service
======================
Deterministic rule-based algorithm that scores each grant against a
researcher's profile inputs and returns ranked results.

Scoring weights (must sum to 100):
  WEIGHT_RESEARCH_AREA  = 30  — exact / partial research-area match
  WEIGHT_KEYWORDS       = 30  — keyword overlap ratio
  WEIGHT_ELIGIBILITY    = 20  — eligibility substring match
  WEIGHT_COUNTRY        = 10  — country match
  WEIGHT_DESCRIPTION    = 10  — keyword hits inside grant description
"""

from typing import List
from sqlalchemy.orm import Session

from ..models.grant import Grant
from ..schemas.grant import GrantMatchRequest, GrantMatchResult

# ---------- Configurable weights ----------
WEIGHT_RESEARCH_AREA = 30
WEIGHT_KEYWORDS = 30
WEIGHT_ELIGIBILITY = 20
WEIGHT_COUNTRY = 10
WEIGHT_DESCRIPTION = 10


def _normalise(text: str) -> str:
    return text.lower().strip()


def _score_research_area(grant_area: str | None, request_area: str) -> tuple[int, list[str]]:
    """Return (score 0-30, reasons)."""
    if not grant_area:
        return 0, []
    g = _normalise(grant_area)
    r = _normalise(request_area)
    if g == r:
        return WEIGHT_RESEARCH_AREA, ["Research area matches exactly"]
    if r in g or g in r:
        return int(WEIGHT_RESEARCH_AREA * 0.7), ["Research area partially matches"]
    # word-level overlap
    g_words = set(g.split())
    r_words = set(r.split())
    overlap = g_words & r_words
    if overlap:
        ratio = len(overlap) / max(len(r_words), 1)
        score = int(WEIGHT_RESEARCH_AREA * ratio * 0.5)
        if score > 0:
            return score, [f"Research area shares terms: {', '.join(overlap)}"]
    return 0, []


def _score_keywords(grant_keywords: str | None, request_keywords: List[str]) -> tuple[int, list[str]]:
    """Return (score 0-30, reasons)."""
    if not grant_keywords or not request_keywords:
        return 0, []
    grant_kw_list = [_normalise(k) for k in grant_keywords.split(",")]
    reasons = []
    matched = 0
    for kw in request_keywords:
        kw_norm = _normalise(kw)
        for gkw in grant_kw_list:
            if kw_norm in gkw or gkw in kw_norm:
                reasons.append(f"'{kw}' keyword matched")
                matched += 1
                break
    if not matched:
        return 0, []
    ratio = matched / len(request_keywords)
    return int(WEIGHT_KEYWORDS * ratio), reasons


def _score_eligibility(grant_eligibility: str | None, request_eligibility: str | None) -> tuple[int, list[str]]:
    """Return (score 0-20, reasons)."""
    if not grant_eligibility or not request_eligibility:
        return 0, []
    g = _normalise(grant_eligibility)
    r = _normalise(request_eligibility)
    if r in g or g in r:
        return WEIGHT_ELIGIBILITY, ["Eligibility criteria matched"]
    # word overlap
    g_words = set(g.split())
    r_words = set(r.split())
    overlap = g_words & r_words
    if overlap:
        ratio = len(overlap) / max(len(r_words), 1)
        score = int(WEIGHT_ELIGIBILITY * ratio * 0.6)
        if score > 0:
            return score, ["Eligibility partially matched"]
    return 0, []


def _score_country(grant_country: str | None, request_country: str | None) -> tuple[int, list[str]]:
    """Return (score 0-10, reasons)."""
    if not grant_country or not request_country:
        return 0, []
    if _normalise(grant_country) == _normalise(request_country):
        return WEIGHT_COUNTRY, ["Country eligibility matched"]
    # "International" / "Global" grants match any country
    if _normalise(grant_country) in ("international", "global", "worldwide"):
        return WEIGHT_COUNTRY, ["Grant is open internationally"]
    return 0, []


def _score_description(grant_description: str | None, request_keywords: List[str]) -> tuple[int, list[str]]:
    """Return (score 0-10, reasons)."""
    if not grant_description or not request_keywords:
        return 0, []
    desc = _normalise(grant_description)
    hits = [kw for kw in request_keywords if _normalise(kw) in desc]
    if not hits:
        return 0, []
    ratio = len(hits) / len(request_keywords)
    return int(WEIGHT_DESCRIPTION * ratio), [f"Description mentions: {', '.join(hits)}"]


def compute_match_score(grant: Grant, request: GrantMatchRequest) -> GrantMatchResult:
    """Score a single grant against the match request."""
    reasons: list[str] = []
    total = 0

    s, r = _score_research_area(grant.research_area, request.research_area)
    total += s; reasons.extend(r)

    s, r = _score_keywords(grant.keywords, request.keywords)
    total += s; reasons.extend(r)

    s, r = _score_eligibility(grant.eligibility, request.eligibility)
    total += s; reasons.extend(r)

    s, r = _score_country(grant.country, request.country)
    total += s; reasons.extend(r)

    s, r = _score_description(grant.description, request.keywords)
    total += s; reasons.extend(r)

    return GrantMatchResult(
        grant_id=grant.id,
        grant_name=grant.grant_name,
        organization=grant.funding_organization,
        match_score=min(total, 100),
        matching_reasons=reasons if reasons else ["No strong match found"],
        deadline=grant.deadline,
        funding_amount=grant.funding_amount,
        application_url=grant.application_url,
    )


def match_grants(db: Session, request: GrantMatchRequest) -> list[GrantMatchResult]:
    """Score all open grants and return sorted by match_score descending."""
    grants = db.query(Grant).filter(Grant.status == "open").all()
    results = [compute_match_score(g, request) for g in grants]
    results.sort(key=lambda x: x.match_score, reverse=True)
    return results
