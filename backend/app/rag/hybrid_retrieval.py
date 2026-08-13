# backend/app/rag/hybrid_retrieval.py

import os
import faiss
import pickle
import logging
import numpy as np
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(CURRENT_DIR, "faiss_index.bin")
CHUNKS_PKL_PATH = os.path.join(CURRENT_DIR, "chunks.pkl")

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def search_similar_chunks(query: str, top_k: int = 5):
    """
    Retrieves top_k most relevant content chunks (PDF or DB) for a user query.
    Returns list of dict items containing: content, source_type, source_name, table, record_id.
    """
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(CHUNKS_PKL_PATH):
        logger.error(f"FAISS index or chunks file missing: {FAISS_INDEX_PATH}, {CHUNKS_PKL_PATH}")
        return []

    try:
        index = faiss.read_index(FAISS_INDEX_PATH)
        with open(CHUNKS_PKL_PATH, "rb") as f:
            all_chunks = pickle.load(f)

        model = get_embedding_model()
        encoded = model.encode([query])
        query_vector = np.array(encoded, dtype="float32")

        # Perform L2 vector similarity search
        distances, indices = index.search(query_vector, top_k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(all_chunks):
                chunk_data = all_chunks[idx]
                results.append({
                    "content": chunk_data.get("content", ""),
                    "source_type": chunk_data.get("source_type", "unknown"),
                    "source_name": chunk_data.get("source_name", "Unknown Source"),
                    "table": chunk_data.get("table"),
                    "record_id": chunk_data.get("record_id")
                })

        logger.info(f"Retrieved Results: {len(results)} chunks for query: '{query}'")
        return results

    except Exception as e:
        logger.error(f"Error executing vector retrieval search: {e}", exc_info=True)
        return []

# Convenient aliases
search = search_similar_chunks
retrieve_similar_chunks = search_similar_chunks

if __name__ == "__main__":
    test_results = search("Who invented AI Funding Recommendation Engine?", top_k=3)
    print("Search Results:", test_results)
