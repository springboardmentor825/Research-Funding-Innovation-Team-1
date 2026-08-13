# backend/app/api/v1/endpoints/rag.py

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.rag_service import RAGService

router = APIRouter()

# Request & Response Models
class ChatRequest(BaseModel):
    question: str = Field(..., example="Who invented AI Funding Recommendation Engine?")

class SourceItem(BaseModel):
    type: str
    name: str
    table: Optional[str] = None
    id: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]

class SearchRequest(BaseModel):
    query: str = Field(..., example="AI funding")
    top_k: int = Field(5, ge=1, le=20)

class SearchResultItem(BaseModel):
    title: str
    content: str
    source_type: Optional[str] = None
    table: Optional[str] = None
    record_id: Optional[int] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]

class StatsResponse(BaseModel):
    pdf_chunks: int
    database_chunks: int
    total_chunks: int
    total_vectors: int
    index_status: str

@router.post("/chat", response_model=ChatResponse)
def rag_chat(request: ChatRequest):
    """
    Submits user question to Hybrid RAG system (PDFs + MySQL Database).
    Returns synthesized answer with structured source citations.
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question string cannot be empty."
        )
    return RAGService.answer_question(request.question)

@router.post("/search", response_model=SearchResponse)
def rag_search(request: SearchRequest):
    """
    Performs direct semantic vector search across PDF and DB content chunks.
    Returns matched chunks directly without LLM answer generation.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query string cannot be empty."
        )
    return RAGService.search_chunks(request.query, top_k=request.top_k)

@router.get("/stats", response_model=StatsResponse)
def rag_stats():
    """
    Returns index status, vector count, and breakdown of PDF vs Database chunks.
    """
    return RAGService.get_stats()
