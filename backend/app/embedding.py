import os
import numpy as np
import ollama
from backend.app.chunking import chunk_by_words, load_transcript
from backend.app.database import get_db_connection, init_db

EMBEDDING_MODEL = "all-minilm"
DIMENSION = 384  # all-minilm embeds to 384 dimensions


def get_embedding(text: str) -> np.ndarray:
    """
    Get embedding for a piece of text using Ollama's all-minilm model.
    Returns a numpy array of shape (DIMENSION,).
    """
    response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
    embedding = response["embedding"]
    return np.array(embedding, dtype="float32")


def create_vector_db():
    """
    Loads raw text from transcript.txt, chunks it, generates embeddings,
    and inserts chunks + vector embeddings directly into Supabase PostgreSQL (podcast_chunks table).
    """
    # 1. Initialize DB schema (enables vector extension & podcast_chunks table)
    init_db()

    print("Step 1: Loading raw transcript data...")
    raw_data = load_transcript()

    print("Step 2: Chunking text...")
    chunks = chunk_by_words(raw_data, chunk_size=80, overlap=15)
    print(f"Generated {len(chunks)} chunks.")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Clear existing table data to avoid duplicates on re-indexing
            cur.execute("TRUNCATE TABLE podcast_chunks;")

            print("Step 3: Creating embeddings and inserting into Supabase PostgreSQL...")
            for i, chunk in enumerate(chunks):
                if (i + 1) % 25 == 0 or i == len(chunks) - 1:
                    print(f"  Processing chunk {i+1}/{len(chunks)}...")
                embed = get_embedding(chunk)
                cur.execute(
                    "INSERT INTO podcast_chunks (chunk_text, embedding) VALUES (%s, %s);",
                    (chunk, embed),
                )
            conn.commit()
            print("Successfully populated Supabase PostgreSQL vector database!")
    finally:
        conn.close()


def search_vector_db(query: str, k: int = 2) -> list[str]:
    """
    Searches Supabase PostgreSQL database for top K relevant chunks using Cosine Distance (`<=>`).
    """
    query_vector = get_embedding(query)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # <=> operator calculates Cosine Distance in pgvector
            cur.execute(
                """
                SELECT chunk_text 
                FROM podcast_chunks 
                ORDER BY embedding <=> %s 
                LIMIT %s;
                """,
                (query_vector, k),
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]
    finally:
        conn.close()


if __name__ == "__main__":
    create_vector_db()

    print("\n--- Testing Supabase Vector DB Search ---")
    query = "What is Andy Johns advice on burnout?"
    print(f"Query: '{query}'")

    matched_chunks = search_vector_db(query, k=2)
    for idx, chunk in enumerate(matched_chunks, 1):
        print(f"\nResult #{idx}:")
        print(chunk)
        print("-" * 50)
