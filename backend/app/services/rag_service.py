# backend/app/services/rag_service.py

import os
import pickle
import faiss
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

from app.rag.hybrid_retrieval import search_similar_chunks
from app.rag.rag_chat import generate_grounded_answer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RAG_DIR = os.path.join(CURRENT_DIR, "..", "rag")
FAISS_INDEX_PATH = os.path.abspath(os.path.join(RAG_DIR, "faiss_index.bin"))
CHUNKS_PKL_PATH = os.path.abspath(os.path.join(RAG_DIR, "chunks.pkl"))

class RAGService:
    @staticmethod
    def answer_question(question: str) -> Dict[str, Any]:
        """
        Executes the Hybrid RAG flow:
        1. Retrieve top chunks (PDFs & MySQL Database records)
        2. Format source metadata
        3. Synthesize grounded LLM answer via Gemini
        4. Return structured JSON response
        """
        logger.info(f"Processing RAG Question: '{question}'")

        # 1. Retrieve relevant chunks
        chunks = search_similar_chunks(question, top_k=5)

        if not chunks:
            logger.warning("No context chunks retrieved for query.")
            return {
                "answer": "I could not find sufficient information in the documents.",
                "sources": []
            }

        # 2. Extract and format structured sources metadata
        sources = []
        seen_sources = set()

        for c in chunks:
            stype = c.get("source_type", "unknown")
            sname = c.get("source_name", "Unknown Source")
            table = c.get("table")
            record_id = c.get("record_id")

            dedup_key = f"{stype}:{table}:{record_id}:{sname}"
            if dedup_key not in seen_sources:
                seen_sources.add(dedup_key)
                sources.append({
                    "type": stype,
                    "name": sname,
                    "table": table,
                    "id": record_id
                })

        # 3. Build text context for Gemini LLM synthesis
        context_blocks = []
        for idx, c in enumerate(chunks, 1):
            src_lbl = f"[{c['source_type'].upper()}"
            if c.get("table"):
                src_lbl += f" - {c['table']} Record #{c.get('record_id')}"
            src_lbl += f" ({c['source_name']})]"

            context_blocks.append(f"Source {idx} {src_lbl}:\n{c['content']}")

        context_text = "\n\n".join(context_blocks)

        # 4. Generate grounded LLM response using Gemini
        answer = generate_grounded_answer(question, context_text)

        logger.info(f"RAG Synthesis Completed with {len(sources)} source references.")

        return {
            "answer": answer,
            "sources": sources
        }

    @staticmethod
    def search_chunks(query: str, top_k: int = 5) -> Dict[str, Any]:
        """Direct vector search endpoint service returning chunks directly."""
        chunks = search_similar_chunks(query, top_k=top_k)
        
        formatted_results = []
        for c in chunks:
            formatted_results.append({
                "title": c.get("source_name", "Source"),
                "content": c.get("content", ""),
                "source_type": c.get("source_type"),
                "table": c.get("table"),
                "record_id": c.get("record_id")
            })

        return {
            "query": query,
            "total_results": len(formatted_results),
            "results": formatted_results
        }

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Calculate and return FAISS index vector count and source breakdowns."""
        pdf_chunks_count = 0
        db_chunks_count = 0
        total_chunks = 0
        index_status = "offline"

        if os.path.exists(CHUNKS_PKL_PATH):
            try:
                with open(CHUNKS_PKL_PATH, "rb") as f:
                    all_chunks = pickle.load(f)
                total_chunks = len(all_chunks)
                pdf_chunks_count = sum(1 for c in all_chunks if c.get("source_type") == "pdf")
                db_chunks_count = sum(1 for c in all_chunks if c.get("source_type") == "database")
                index_status = "online"
            except Exception as e:
                logger.error(f"Error reading chunks.pkl: {e}")

        total_vectors = 0
        if os.path.exists(FAISS_INDEX_PATH):
            try:
                idx = faiss.read_index(FAISS_INDEX_PATH)
                total_vectors = idx.ntotal
            except Exception as e:
                logger.error(f"Error reading FAISS index: {e}")

        return {
            "pdf_chunks": pdf_chunks_count,
            "database_chunks": db_chunks_count,
            "total_chunks": total_chunks,
            "total_vectors": total_vectors,
            "index_status": index_status
        }
