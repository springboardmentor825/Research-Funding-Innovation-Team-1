import os
from typing import List, Dict, Any, Tuple
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Publication, Patent, ResearchProfile, FundingOpportunity, User
from app.schemas import RAGChatRequest, RAGChatResponse

router = APIRouter()

def query_database_context(db: Session, query_text: str) -> Tuple[List[str], List[Dict[str, Any]], str]:
    """
    Search database tables (Publications, Patents, Profiles, Funding Opportunities)
    using strict token matching relevant to the user's query text.
    Returns (context_passages, sources, primary_intent).
    """
    context_passages = []
    sources = []
    
    q_lower = query_text.lower().strip()
    stop_words = {"what", "where", "show", "list", "tell", "available", "about", "with", "from", "the", "that", "this", "some", "have", "please", "help"}
    words = [w.strip() for w in q_lower.split() if len(w) > 2 and w not in stop_words]

    # Determine intent
    is_funding_query = any(k in q_lower for k in ["fund", "grant", "scheme", "money", "opportunity", "deadline", "budget", "finance", "call", "apply"])
    is_pub_query = any(k in q_lower for k in ["paper", "publi", "journal", "article", "author", "doi", "conference", "write"])
    is_patent_query = any(k in q_lower for k in ["patent", "ip ", "invent", "intellectual", "assignee", "claim"])
    is_profile_query = any(k in q_lower for k in ["profile", "researcher", "interest", "domain", "skill", "user"])

    primary_intent = "general"
    if is_funding_query: primary_intent = "funding"
    elif is_pub_query: primary_intent = "publication"
    elif is_patent_query: primary_intent = "patent"
    elif is_profile_query: primary_intent = "profile"

    # 1. Search Funding Opportunities ONLY if funding intent OR specific matching words exist
    if is_funding_query or words:
        fo_query = db.query(FundingOpportunity)
        if words:
            filters = [
                or_(
                    FundingOpportunity.title.like(f"%{w}%"),
                    FundingOpportunity.keywords.like(f"%{w}%"),
                    FundingOpportunity.research_domains.like(f"%{w}%"),
                    FundingOpportunity.funder.like(f"%{w}%"),
                    FundingOpportunity.technology_areas.like(f"%{w}%")
                ) for w in words
            ]
            fo_query = fo_query.filter(or_(*filters))
        
        fos = fo_query.filter(FundingOpportunity.status == "open").limit(5).all()
        # If explicit funding query and no specific word filters matched, return open opportunities
        if not fos and is_funding_query and not words:
            fos = db.query(FundingOpportunity).filter(FundingOpportunity.status == "open").limit(5).all()

        for fo in fos:
            passage = f"Funding Opportunity: '{fo.title}' by {fo.funder} | Funding: {fo.amount_range} | Deadline: {fo.deadline}. Description: {fo.description or 'N/A'}"
            context_passages.append(passage)
            sources.append({"type": "funding_opportunity", "title": fo.title, "id": fo.id})

    # 2. Search Publications if publication intent OR matching words exist
    if is_pub_query or (words and not is_funding_query):
        pub_query = db.query(Publication)
        if words:
            filters = [
                or_(
                    Publication.title.like(f"%{w}%"),
                    Publication.authors.like(f"%{w}%"),
                    Publication.journal.like(f"%{w}%")
                ) for w in words
            ]
            pub_query = pub_query.filter(or_(*filters))
        
        pubs = pub_query.limit(5).all()
        for p in pubs:
            passage = f"Publication: '{p.title}' published in {p.journal} ({p.publication_year}) by {p.authors}."
            context_passages.append(passage)
            sources.append({"type": "publication", "title": p.title, "id": p.publication_id})

    # 3. Search Patents if patent intent OR matching words exist
    if is_patent_query or (words and not is_funding_query):
        pat_query = db.query(Patent)
        if words:
            filters = [
                or_(
                    Patent.title.like(f"%{w}%"),
                    Patent.technology_domain.like(f"%{w}%"),
                    Patent.inventor.like(f"%{w}%"),
                    Patent.assignee.like(f"%{w}%")
                ) for w in words
            ]
            pat_query = pat_query.filter(or_(*filters))
        
        pats = pat_query.limit(5).all()
        for pt in pats:
            passage = f"Patent: '{pt.title}' (Inventor: {pt.inventor}, Assignee: {pt.assignee}, Domain: {pt.technology_domain}, Filed: {pt.filing_date})."
            context_passages.append(passage)
            sources.append({"type": "patent", "title": pt.title, "id": pt.patent_id})

    # 4. Search Profiles if profile intent
    if is_profile_query:
        profiles = db.query(ResearchProfile).limit(3).all()
        for prof in profiles:
            passage = f"Researcher Profile: Organization: {prof.organization}, Designation: {prof.designation}, Domain: {prof.research_domain}, Tech Focus: {prof.technology_area}."
            context_passages.append(passage)
            sources.append({"type": "profile", "title": f"Profile: {prof.research_domain}", "id": prof.profile_id})

    return context_passages, sources, primary_intent

def generate_rag_answer(query: str, context_passages: List[str], sources: List[Dict[str, Any]], primary_intent: str) -> str:
    """
    Generate accurate answer using Gemini or query-specific conversational synthesis.
    """
    q_lower = query.lower().strip()

    # 1. Handle common conversational greetings
    if q_lower in {"hi", "hello", "hey", "greetings", "good morning", "good afternoon"}:
        return (
            "Hello! 👋 I am your AI Research Assistant on the Research Funding & Innovation Platform.\n\n"
            "How can I help you today? You can ask me to:\n"
            "• Search active funding grants & deadlines (e.g., 'Show AI funding grants')\n"
            "• Find research publications (e.g., 'Show papers on machine learning')\n"
            "• Review registered patents & intellectual property\n"
            "• Explain RAG and platform AI match scores"
        )

    # 2. Handle capability & help questions
    if any(k in q_lower for k in ["what can you do", "help me", "how to use", "who are you", "what is this"]):
        return (
            "I am the platform's Hybrid RAG AI Assistant. I synthesize real-time data from database records and academic papers to assist researchers.\n\n"
            "Try asking questions like:\n"
            "1. 'What funding opportunities are open for Quantum Computing?'\n"
            "2. 'List my registered patents and technology domains'\n"
            "3. 'Show publications written by Madhu Krishna'\n"
            "4. 'How are funding match scores calculated?'"
        )

    # 3. Handle RAG architectural questions
    if "retrieval augmented generation" in q_lower or "rag" in q_lower:
        return (
            "Retrieval-Augmented Generation (RAG) is an AI architecture that enhances Large Language Models (LLMs) "
            "by connecting them with real-time external databases and vector stores.\n\n"
            "In this platform, Hybrid RAG combines:\n"
            "• Structured MySQL database records (funding opportunities, publications, patents, profiles)\n"
            "• Semantic vector embeddings (Sentence Transformers) to retrieve relevant research context before generating answers."
        )

    # 4. Try Gemini API generation if key is present
    context_str = "\n".join(context_passages) if context_passages else "No direct database records found."
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
You are an expert AI research funding consultant and assistant on the Research Funding & Innovation Platform.
Answer the user's question accurately, concisely, and informatively based on the retrieved platform records below.

Database Records Context:
{context_str}

User Question: {query}

Guidelines:
- If asked about funding opportunities, highlight grant titles, funding amounts, funders, and deadlines.
- Use clear bullet points and professional formatting.
- Keep responses factual based on the records.
"""
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini generation error in RAG: {e}")

    # 5. Query-Specific Synthesis Based on Retrieved Context
    if primary_intent == "funding" and context_passages:
        fo_items = [f"• {p.replace('Funding Opportunity: ', '')}" for p in context_passages if p.startswith("Funding Opportunity:")]
        if fo_items:
            return f"Here are the active funding opportunities matching '{query}':\n\n" + "\n\n".join(fo_items[:4]) + "\n\nYou can explore full details on the Funding directory page."

    if primary_intent == "publication" and context_passages:
        pub_items = [f"• {p.replace('Publication: ', '')}" for p in context_passages if p.startswith("Publication:")]
        if pub_items:
            return f"Here are the relevant research publications for '{query}':\n\n" + "\n".join(pub_items[:4])

    if primary_intent == "patent" and context_passages:
        pat_items = [f"• {p.replace('Patent: ', '')}" for p in context_passages if p.startswith("Patent:")]
        if pat_items:
            return f"Here are the registered intellectual property and patent assets for '{query}':\n\n" + "\n".join(pat_items[:4])

    # 6. General Keyword Matches Found
    if context_passages:
        formatted = [f"• {p}" for p in context_passages[:4]]
        return f"Based on your query '{query}', here are the matching platform records:\n\n" + "\n\n".join(formatted)

    # 7. No Database Matches Found
    return (
        f"I searched the platform database for '{query}', but found no specific matching records.\n\n"
        "Try asking about specific research areas such as 'Quantum', 'Artificial Intelligence', 'Clean Energy', 'Patents', or 'Publications'."
    )

@router.post("/chat", response_model=RAGChatResponse)
def rag_chat(request: RAGChatRequest, db: Session = Depends(get_db)):
    """
    RAG Chat API: Retrieves database & document context and generates an answer.
    """
    context_passages, sources, primary_intent = query_database_context(db, request.query)
    answer = generate_rag_answer(request.query, context_passages, sources, primary_intent)

    return {
        "query": request.query,
        "answer": answer,
        "sources": sources
    }

@router.post("/search")
def rag_search(request: RAGChatRequest, db: Session = Depends(get_db)):
    """
    RAG Search API: Returns retrieved passages and sources for a query.
    """
    context_passages, sources, primary_intent = query_database_context(db, request.query)
    return {
        "query": request.query,
        "passages": context_passages,
        "sources": sources,
        "intent": primary_intent
    }
