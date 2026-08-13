# backend/app/rag/document_loader.py

import os
import pymupdf


# Get current file location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to backend/data/papers
PDF_FOLDER = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "..",
        "data",
        "papers"
    )
)


def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF file
    """

    text = ""

    try:
        pdf = pymupdf.open(pdf_path)

        for page_num in range(len(pdf)):
            page = pdf[page_num]
            text += page.get_text()

        pdf.close()

    except Exception as e:
        print(f"❌ Error reading {pdf_path}")
        print(e)

    return text


def load_documents():
    """
    Load all PDFs from papers folder
    """

    documents = []

    print("\n" + "=" * 70)
    print("LOADING PDF DOCUMENTS")
    print("=" * 70)

    print(f"\nPDF Folder:")
    print(PDF_FOLDER)

    if not os.path.exists(PDF_FOLDER):
        print(f"\n❌ Folder not found: {PDF_FOLDER}")
        return []

    pdf_files = [
        file
        for file in os.listdir(PDF_FOLDER)
        if file.lower().endswith(".pdf")
    ]

    print(f"\nFound {len(pdf_files)} PDF files\n")

    for file in pdf_files:

        pdf_path = os.path.join(PDF_FOLDER, file)

        print(f"📄 Loading: {file}")

        text = extract_text_from_pdf(pdf_path)

        documents.append(
            {
                "title": file,
                "content": text
            }
        )

        print(f"   Characters: {len(text):,}")
        print("-" * 70)

    return documents


def show_sample_text(documents):

    if not documents:
        print("\n❌ No documents loaded")
        return

    print("\n" + "=" * 70)
    print("SAMPLE TEXT")
    print("=" * 70)

    print(f"\nDocument: {documents[0]['title']}\n")

    sample = documents[0]["content"][:1000]

    print(sample)

    print("\n" + "=" * 70)


if __name__ == "__main__":

    documents = load_documents()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\n✅ Total Documents Loaded: {len(documents)}")

    total_chars = sum(
        len(doc["content"])
        for doc in documents
    )

    print(f"✅ Total Characters Extracted: {total_chars:,}")

    show_sample_text(documents)