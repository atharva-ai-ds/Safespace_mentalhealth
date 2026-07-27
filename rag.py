"""PDF ingestion and Chroma retrieval for trusted SafeSpace documents."""
from __future__ import annotations

import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import DOCUMENTS_DIR, EMBEDDING_MODEL, OLLAMA_BASE_URL, RETRIEVER_K, VECTOR_DB_DIR

logger = logging.getLogger(__name__)


class RAGError(RuntimeError):
    """Raised when the trusted knowledge base cannot be used."""


def _embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)


def load_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[Document]:
    pdfs = sorted(documents_dir.glob("*.pdf")) if documents_dir.exists() else []
    if not pdfs:
        raise RAGError(f"No PDF files found in {documents_dir}.")
    pages: list[Document] = []
    for pdf in pdfs:
        try:
            for page in PyPDFLoader(str(pdf)).load():
                page.metadata["source"] = pdf.name
                pages.append(page)
        except Exception as exc:
            raise RAGError(f"Could not read {pdf.name}: {exc}") from exc
    return pages


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    return splitter.split_documents(documents)


def build_vector_database() -> Chroma:
    chunks = split_documents(load_documents())

    if not chunks:
        raise RAGError("The PDF documents did not contain readable text.")

    # Remove old DB if rebuilding
    if VECTOR_DB_DIR.exists():
        import shutil
        shutil.rmtree(VECTOR_DB_DIR)

    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    db = None
    batch_size = 100

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        if db is None:
            db = Chroma.from_documents(
                documents=batch,
                embedding=_embeddings(),
                persist_directory=str(VECTOR_DB_DIR),
            )
        else:
            db.add_documents(batch)

        print(f"Stored {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")

    return db

def load_vector_database() -> Chroma:
    if not VECTOR_DB_DIR.exists() or not any(VECTOR_DB_DIR.iterdir()):
        raise RAGError("Vector database is missing. Run: python backend/build_vector_db.py")
    return Chroma(persist_directory=str(VECTOR_DB_DIR), embedding_function=_embeddings())


def retrieve(query: str, k: int = RETRIEVER_K) -> list[Document]:
    try:
        return load_vector_database().similarity_search(query, k=k)
    except RAGError:
        raise
    except Exception as exc:
        logger.exception("Retriever failure")
        raise RAGError("Unable to search the trusted documents. Check that Ollama is running.") from exc


def source_metadata(documents: list[Document]) -> list[dict[str, object]]:
    seen: set[tuple[str, object]] = set()
    sources: list[dict[str, object]] = []
    for document in documents:
        source = str(document.metadata.get("source", "Unknown document"))
        page = document.metadata.get("page")
        key = (source, page)
        if key not in seen:
            seen.add(key)
            sources.append({"document": source, "page": (int(page) + 1) if isinstance(page, int) else page})
    return sources
