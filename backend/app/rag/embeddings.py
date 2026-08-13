# backend/app/rag/embeddings.py

from sentence_transformers import SentenceTransformer
from app.rag.chunking import chunk_documents

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def create_embeddings():
    chunks = chunk_documents()
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return chunks, embeddings

if __name__ == "__main__":
    chunks, embeddings = create_embeddings()
    print("\nTotal Chunks:", len(chunks))
    print("Embedding Shape:", embeddings.shape)