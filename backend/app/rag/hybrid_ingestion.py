# backend/app/rag/hybrid_ingestion.py

import os
import faiss
import numpy as np
import pickle
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from app.rag.database_loader import load_hybrid_documents

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(CURRENT_DIR, "faiss_index.bin")
CHUNKS_PKL_PATH = os.path.join(CURRENT_DIR, "chunks.pkl")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def run_hybrid_ingestion():
    """
    Ingests hybrid documents (PDFs + Database records), generates sentence embeddings,
    and builds and persists FAISS vector index alongside chunks metadata.
    """
    logger.info("=" * 70)
    logger.info("HYBRID RAG INGESTION PIPELINE STARTED")
    logger.info("=" * 70)

    # 1. Load Hybrid Documents
    hybrid_docs = load_hybrid_documents()

    pdf_count = sum(1 for d in hybrid_docs if d["metadata"]["source_type"] == "pdf")
    db_count = sum(1 for d in hybrid_docs if d["metadata"]["source_type"] == "database")

    logger.info(f"Loaded PDF Documents: {pdf_count}")
    logger.info(f"Loaded Database Records: {db_count}")

    # 2. Text Chunking with Metadata Propagation
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    all_chunks = []

    for doc in hybrid_docs:
        meta = doc["metadata"]
        text_content = doc["content"]

        if meta["source_type"] == "pdf":
            text_chunks = splitter.split_text(text_content)
            for chunk in text_chunks:
                all_chunks.append({
                    "content": chunk,
                    "source_type": "pdf",
                    "source_name": meta.get("source_name", "PDF Document"),
                    "table": None,
                    "record_id": None
                })
        else:
            # Database records are pre-formatted structured strings
            all_chunks.append({
                "content": text_content,
                "source_type": "database",
                "source_name": meta.get("source_name", "Database Record"),
                "table": meta.get("table"),
                "record_id": meta.get("record_id")
            })

    logger.info(f"Created Chunks Total: {len(all_chunks)}")
    pdf_chunks_cnt = sum(1 for c in all_chunks if c["source_type"] == "pdf")
    db_chunks_cnt = sum(1 for c in all_chunks if c["source_type"] == "database")
    logger.info(f" -> PDF Chunks: {pdf_chunks_cnt}")
    logger.info(f" -> Database Chunks: {db_chunks_cnt}")

    # 3. Generate Embeddings
    texts = [c["content"] for c in all_chunks]
    logger.info("Generating embeddings using SentenceTransformer...")
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings_np = np.array(embeddings, dtype="float32")

    # 4. Build FAISS Index
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)

    # 5. Persist Index and Chunks
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_PKL_PATH, "wb") as f:
        pickle.dump(all_chunks, f)

    logger.info(f"Saved FAISS Index to: {FAISS_INDEX_PATH}")
    logger.info(f"Saved Chunks Metadata to: {CHUNKS_PKL_PATH}")
    logger.info(f"Total Vectors Stored: {index.ntotal}")
    logger.info("=" * 70)

    return index, all_chunks

if __name__ == "__main__":
    run_hybrid_ingestion()
