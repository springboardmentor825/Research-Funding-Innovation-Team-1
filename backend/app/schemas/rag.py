# backend/app/schemas/rag.py

from pydantic import BaseModel, Field
from typing import List, Optional, Any

class ChatRequest(BaseModel):
    question: str = Field(..., example="What is Retrieval Augmented Generation?")

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[str] = []

class SearchRequest(BaseModel):
    query: str = Field(..., example="Deep Learning Protein Folding")
    top_k: int = Field(5, ge=1, le=20)

class SearchResultItem(BaseModel):
    title: str
    content: str
    source_type: Optional[str] = None
    table: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]

class StatsResponse(BaseModel):
    total_vectors: int
    total_chunks: int
    index_status: str
    pdf_sources: int
    db_sources: int
