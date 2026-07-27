"""Build the Chroma vector database from the trusted PDF documents."""

from backend.rag import build_vector_database

if __name__ == "__main__":
    print("Building vector database...")
    build_vector_database()
    print("✅ Vector database created successfully!")