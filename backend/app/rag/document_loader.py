import os
from typing import List, Dict, Any

def load_documents(data_dir: str = None) -> List[Dict[str, Any]]:
    """
    Scans data directory for PDF files or documents and extracts text content.
    Returns a list of dictionaries with 'title', 'content', and metadata.
    """
    if data_dir is None:
        # Default to backend/data/ directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, "data")

    documents = []
    
    if not os.path.exists(data_dir):
        return documents

    # Walk through data directory for pdf or text files
    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".pdf"):
                content = _extract_pdf_text(file_path)
                if content:
                    documents.append({
                        "title": file,
                        "content": content,
                        "file_path": file_path,
                        "source_type": "pdf"
                    })
            elif file.endswith(".txt") or file.endswith(".md"):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    if content.strip():
                        documents.append({
                            "title": file,
                            "content": content,
                            "file_path": file_path,
                            "source_type": "text"
                        })
                except Exception:
                    pass

    return documents


def _extract_pdf_text(pdf_path: str) -> str:
    """Helper to extract text from a PDF file using available libraries."""
    text = ""
    # Try pypdf or PyPDF2
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except ImportError:
        pass
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception:
        pass

    return text
