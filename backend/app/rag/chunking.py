# backend/app/rag/chunking.py

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.document_loader import load_documents

def chunk_documents():
    documents = load_documents()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = []
    for doc in documents:
        text_chunks = splitter.split_text(doc["content"])
        for chunk in text_chunks:
            chunks.append({
                "title": doc["title"],
                "content": chunk,
                "source_type": "pdf"
            })

    return chunks

if __name__ == "__main__":
    chunks = chunk_documents()
    print(f"\nTotal Chunks Created: {len(chunks)}")
    if chunks:
        print("\nSample Chunk:\n", chunks[0]["content"][:300])