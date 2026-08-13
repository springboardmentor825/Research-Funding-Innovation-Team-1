# backend/app/rag/vector_store.py

import os
import faiss
import numpy as np
import pickle
from app.rag.embeddings import create_embeddings

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(CURRENT_DIR, "faiss_index.bin")
CHUNKS_PKL_PATH = os.path.join(CURRENT_DIR, "chunks.pkl")

def create_vector_store():
    chunks, embeddings = create_embeddings()
    embeddings = np.array(embeddings, dtype="float32")
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_PKL_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print("\nFAISS Index Created Successfully")
    print(f"Vectors Stored: {index.ntotal}")

if __name__ == "__main__":
    create_vector_store()