import os
from typing import List, Dict, Any, Tuple

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Publication, Patent, ResearchProfile, FundingOpportunity, User
from app.schemas import RAGChatRequest, RAGChatResponse
from app.auth import get_current_user
from app.services import rag_retrieval

router = APIRouter()

_FUNDING_HINTS = ["fund", "grant", "scheme", "money", "opportunity", "deadline", "budget", "finance", "call", "apply", "stipend", "scholarship", "fellowship"]
_PUB_HINTS = ["paper", "publi", "journal", "article", "author", "doi", "conference", "write", "citation", "cited"]
_PATENT_HINTS = ["patent", "ip ", "invent", "intellectual", "assignee", "claim", "technology domain"]
_PROFILE_HINTS = ["profile", "researcher", "interest", "domain", "skill", "user", "organization"]
_MY_HINTS = ["my", "mine", "i have", "i filed", "my patents", "my papers"]


def detect_intent(q: str) -> str:
    q_lower = q.lower().strip()
    # Meta / capability questions take priority
    if q_lower in {"hi", "hello", "hey", "greetings"} or any(k in q_lower for k in ["what can you do", "help me", "how to use", "who are you"]):
        return "meta"
    if "retrieval augmented generation" in q_lower or "what is rag" in q_lower or "rag" == q_lower.strip():
        return "explain_rag"
    if any(k in q_lower for k in ["match score", "scored", "how do you score", "how are", "rule-based", "semantic similarity", "calculate"]):
        return "explain_score"

    scores = {
        "funding": sum(1 for k in _FUNDING_HINTS if k in q_lower),
        "publication": sum(1 for k in _PUB_HINTS if k in q_lower),
        "patent": sum(1 for k in _PATENT_HINTS if k in q_lower),
        "profile": sum(1 for k in _PROFILE_HINTS if k in q_lower),
    }
    top = max(scores, key=lambda x: scores[x])
    if scores[top] > 0:
        return top
    return "general"


def _my_publication_hits(db: Session, user: User, words: List[str]) -> List[Publication]:
    q = db.query(Publication).filter(Publication.user_id == user.id)
    if words:
        filters = [or_(Publication.title.like(f"%{w}%"), Publication.authors.like(f"%{w}%"), Publication.journal.like(f"%{w}%")) for w in words]
        q = q.filter(or_(*filters))
    return q.limit(5).all()


def _my_patent_hits(db: Session, user: User, words: List[str]) -> List[Patent]:
    q = db.query(Patent).filter(Patent.user_id == user.id)
    if words:
        filters = [or_(Patent.title.like(f"%{w}%"), Patent.technology_domain.like(f"%{w}%"), Patent.inventor.like(f"%{w}%"), Patent.assignee.like(f"%{w}%")) for w in words]
        q = q.filter(or_(*filters))
    return q.limit(5).all()


def build_context(db: Session, user: User, query_text: str) -> Tuple[List[Dict[str, Any]], str]:
    """Hybrid retrieval across funding, corpus, patents, and the user's own records."""
    intent = detect_intent(query_text)
    words = [w for w in rag_retrieval.tokenize(query_text)]

    sources: List[Dict[str, Any]] = []
    is_my = any(k in query_text.lower() for k in ["my ", "mine"])

    # 1. Funding — generic intent lists all open grants by platform fit; specific domain terms are BM25-ranked
    domain_signals = {"quantum", "ai", "machine", "learning", "deep", "neural", "nlp", "llm", "rag",
                      "blockchain", "clean", "energy", "health", "medical", "climate", "robotics",
                      "nano", "nanotech", "cyber", "security", "data", "genomics", "bio", "biology",
                      "solar", "cancer", "drug", "materials", "space", "robust", "semantic", "knowledge",
                      "graph", "graph", "iot", "cloud", "edge", "agriculture", "ocean", "education"}
    tokens = rag_retrieval.tokenize(query_text)
    specific = [t for t in tokens if t in domain_signals]
    funding_hits = []
    if intent == "funding" and not specific:
        occ = db.query(FundingOpportunity).filter(FundingOpportunity.status == "open").all()
        occ = sorted(occ, key=lambda o: (o.semantic_fit or 0), reverse=True)
        for o in occ[:5]:
            funding_hits.append({
                "type": "funding_opportunity", "id": o.id, "score": round(o.semantic_fit or 0, 1),
                "title": o.title, "funder": o.funder, "amount_range": o.amount_range,
                "deadline": str(o.deadline) if o.deadline else None, "description": o.description,
                "research_domains": o.research_domains, "technology_areas": o.technology_areas,
                "semantic_fit": o.semantic_fit,
            })
    else:
        funding_hits = rag_retrieval.retrieve_funding(query_text, db, top_k=5)
    if funding_hits:
        sources.extend(funding_hits)
    elif intent == "funding":
        occ = db.query(FundingOpportunity).filter(FundingOpportunity.status == "open").limit(5).all()
        for o in occ:
            sources.append({
                "type": "funding_opportunity", "id": o.id, "score": 0.0,
                "title": o.title, "funder": o.funder, "amount_range": o.amount_range,
                "deadline": str(o.deadline) if o.deadline else None, "description": o.description,
                "research_domains": o.research_domains, "technology_areas": o.technology_areas,
                "semantic_fit": o.semantic_fit,
            })

    # 2. Publications — global corpus OR the user's own records
    if is_my:
        mine = _my_publication_hits(db, user, words)
        for p in mine:
            sources.append({
                "type": "publication", "id": p.publication_id, "score": 0.5, "mine": True,
                "title": p.title, "year": None, "source": p.journal, "authors": p.authors,
            })
    if not is_my or intent == "publication":
        pub_hits = rag_retrieval.retrieve_publications(query_text, db, top_k=5)
        if pub_hits:
            sources.extend(pub_hits)

    # 3. Patents — user's own first, then global index
    if is_my:
        mine_pat = _my_patent_hits(db, user, words)
        for pt in mine_pat:
            sources.append({
                "type": "patent", "id": pt.patent_id, "score": 0.5, "mine": True,
                "title": pt.title, "technology_domain": pt.technology_domain,
                "inventor": pt.inventor, "assignee": pt.assignee,
                "filing_date": str(pt.filing_date) if pt.filing_date else None,
            })
    pat_hits = rag_retrieval.retrieve_patents(query_text, db, top_k=4)
    if pat_hits and (intent == "patent" or intent == "general") and not is_my:
        existing = {s["id"] for s in sources if s["type"] == "patent"}
        pat_hits = [p for p in pat_hits if p["id"] not in existing][:4]
        sources.extend(pat_hits)

    # 4. Profile records
    if intent == "profile":
        profiles = db.query(ResearchProfile).limit(3).all()
        for prof in profiles:
            sources.append({
                "type": "profile", "id": prof.profile_id, "score": 0.5,
                "title": prof.research_domain or "Researcher Profile",
                "organization": prof.organization, "designation": prof.designation,
                "research_domain": prof.research_domain, "technology_area": prof.technology_area,
            })

    # Deduplicate preserving order
    seen = set()
    deduped = []
    for s in sources:
        key = (s["type"], s.get("id"))
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    return deduped, intent


def format_passage(s: Dict[str, Any]) -> str:
    t = s.get("type")
    if t == "funding_opportunity":
        return (f"Funding Opportunity: '{s.get('title')}' by {s.get('funder')} | Funding: {s.get('amount_range')} "
                f"| Deadline: {s.get('deadline')}. {s.get('description') or ''}".strip())
    if t == "publication":
        base = f"Publication: '{s.get('title')}'"
        if s.get("source"):
            base += f" | Source: {s.get('source')}"
        if s.get("year"):
            base += f" ({s.get('year')})"
        if s.get("authors"):
            base += f" | Authors: {s.get('authors')}"
        if s.get("cited_by_count") not in (None, 0):
            base += f" | Citations: {s.get('cited_by_count')}"
        return base
    if t == "patent":
        return (f"Patent: '{s.get('title')}' (Inventor: {s.get('inventor')}, Assignee: {s.get('assignee')}, "
                f"Domain: {s.get('technology_domain')}, Filed: {s.get('filing_date')}).")
    if t == "profile":
        return (f"Researcher Profile: Organization: {s.get('organization')}, Designation: {s.get('designation')}, "
                f"Domain: {s.get('research_domain')}, Tech Focus: {s.get('technology_area')}.")
    return str(s)


def generate_gemini_answer(query: str, context_str: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return ""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
You are an expert AI research funding consultant and assistant on the Research Funding & Innovation Platform (Infera).
Answer the user's question accurately, concisely, and helpfully based ONLY on the retrieved platform records below.
When grants are mentioned, highlight title, funder, funding amount, and deadline, and advise the next step (save or apply).
Keep responses factual and use clear bullet points.

Database Records Context:
{context_str}

User Question: {query}
"""
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini generation error in RAG: {e}")
    return ""


def synthesize_answer(query: str, sources: List[Dict[str, Any]], intent: str, context_str: str) -> str:
    q_lower = query.lower().strip()

    # Static helpful answers
    if intent == "meta":
        return (
            "Hello! 👋 I am your AI Research Assistant on the Infera platform.\n\n"
            "I can help you with:\n"
            "• Funding guidance — active grants, amounts & deadlines (e.g., 'Which AI funding schemes are open?')\n"
            "• Research discovery — papers from the global corpus (e.g., 'Show papers on quantum computing')\n"
            "• Patent intelligence — registered IP and technology domains\n"
            "• Platform help — how match scores work, how RAG works\n\n"
            "Try a question, or use the example chips below."
        )
    if intent == "explain_rag":
        return (
            "Retrieval-Augmented Generation (RAG) is an AI architecture that grounds LLM answers in real, "
            "up-to-date data instead of pure model memory.\n\n"
            "In this platform, Hybrid RAG:\n"
            "• Retrieves ranked context from structured MySQL records (funding, publications, patents, profiles)\n"
            "• Uses a BM25 vector retrieval index over 50,000+ scholarly records for lexical ranking\n"
            "• Generates a grounded, guidance-oriented answer with the sources shown below each reply"
        )
    if intent == "explain_score":
        return (
            "Funding match scores (0–100) are computed deterministically by the recommendation engine with these weights:\n\n"
            "• Research Domain match — 25%\n"
            "• Technology Area match — 20%\n"
            "• Research Interests overlap — 15%\n"
            "• Keyword overlap — 15%\n"
            "• Publication evidence — 10%\n"
            "• Patent / IP evidence — 10%\n"
            "• Deadline urgency bonus — 5%\n\n"
            "The rule-based score is blended 70/30 with a semantic similarity component. Higher is better; ≥75% is a strong match.\n"
            "You can view ranked results with per-grant reasons on the Recommendations page."
        )

    funding = [s for s in sources if s["type"] == "funding_opportunity"]
    pubs = [s for s in sources if s["type"] == "publication"]
    pats = [s for s in sources if s["type"] == "patent"]

    if intent in ("funding", "general") and funding:
        lines = []
        for s in funding[:4]:
            amt = s.get("amount_range") or "Varies"
            dl = s.get("deadline") or "See funding page"
            match = s.get("semantic_fit") or s.get("score") or 0
            lines.append(f"• {s['title']} — {s.get('funder')} | Amount: {amt} | Deadline: {dl} | Fit: {match}%")
        answer = f"Here are the most relevant funding opportunities for \"{query}\":\n\n" + "\n".join(lines)
        answer += (
            "\n\n**How to proceed:** open the card for details and use Save to track it, or Apply Now to initiate "
            "your application on the Funding page (/funding). Your ranked personal list is on /recommendations."
        )
        return answer

    if intent == "publication" or (intent == "general" and pubs):
        lines = []
        for s in pubs[:4]:
            extra = []
            if s.get("year"):
                extra.append(str(s["year"]))
            if s.get("source"):
                extra.append(str(s["source"]))
            cite = s.get("cited_by_count")
            if cite:
                extra.append(f"{cite} citations")
            lines.append(f"• {s['title']}" + (f" ({', '.join(extra)})" if extra else ""))
        answer = f"Here are relevant research publications for \"{query}\":\n\n" + "\n".join(lines)
        answer += "\n\n**Next step:** add any of these to your Publications page by its DOI to grow your research profile and sharpen funding matches."
        return answer

    if intent == "patent" or (intent == "general" and pats):
        lines = [f"• {s['title']} — Domain: {s.get('technology_domain') or 'N/A'} | Assignee: {s.get('assignee') or 'N/A'} | Filed: {s.get('filing_date') or 'N/A'}" for s in pats[:4]]
        answer = f"Registered patent & IP assets matching \"{query}\":\n\n" + "\n".join(lines)
        answer += f"\n\n**Next step:** view domain growth and innovation gaps in the Innovation Hub (/innovation)."
        return answer

    if intent == "profile":
        return (
            "Your researcher profile drives personalization.\n\n"
            "Keep these fields up to date so the AI ranking stays sharp:\n"
            "• Research domain & technology area\n"
            "• Research interests & keywords\n\n"
            "Edit them on the Profile page (/profile). While the profile is incomplete, recommendations fall back to the platform's most active domains."
        )

    if pubs or pats:
        lines = [f"• {format_passage(s)}" for s in sources[:4]]
        return f"Based on your query, here are the matching platform records:\n\n" + "\n\n".join(lines)

    return (
        f"I couldn't find direct records for \"{query}\" in the platform data.\n\n"
        "Try rephrasing with specifics, for example:\n"
        "• 'Which AI funding grants are open?'\n"
        "• 'Show papers on quantum computing'\n"
        "• 'List my patents and domains'\n"
        "• 'How are funding match scores calculated?'"
    )


@router.post("/chat", response_model=RAGChatResponse)
def rag_chat(request: RAGChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    RAG Chat API: hybrid retrieval over funding, corpus, patents & user records,
    then a grounded, guidance-oriented answer.
    """
    sources, intent = build_context(db, user, request.query)
    context_str = "\n".join(format_passage(s) for s in sources[:6]) or "No direct records found."
    answer = generate_gemini_answer(request.query, context_str)
    if not answer:
        answer = synthesize_answer(request.query, sources, intent, context_str)
    return {"query": request.query, "answer": answer, "sources": sources}


@router.post("/search")
def rag_search(request: RAGChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    RAG Search API: returns retrieved passages and source metadata for debugging.
    """
    sources, intent = build_context(db, user, request.query)
    return {
        "query": request.query,
        "passages": [format_passage(s) for s in sources],
        "sources": sources,
        "intent": intent
    }