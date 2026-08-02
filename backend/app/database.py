import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

# Find .env in backend/.env or root .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """
    Establishes and returns a connection to PostgreSQL (Supabase).
    Registers the pgvector extension type adapter.
    """
    if not DATABASE_URL or "[YOUR-PASSWORD]" in DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is missing or contains placeholder [YOUR-PASSWORD]. "
            "Please update backend/.env with your actual Supabase database password."
        )
    
    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    return conn

def init_db():
    """
    Initializes the Supabase database schema:
    1. Enables vector extension (pgvector).
    2. Creates podcast_chunks table (RAG vectors).
    3. Creates sessions table (Chat sessions).
    4. Creates messages table (Chat history per session).
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Enable vector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # 2. Vector table for chunks
            cur.execute("""
                CREATE TABLE IF NOT EXISTS podcast_chunks (
                    id SERIAL PRIMARY KEY,
                    chunk_text TEXT NOT NULL,
                    embedding vector(384) NOT NULL
                );
            """)
            
            # 3. Sessions table for Chat Threads
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id VARCHAR(100) PRIMARY KEY,
                    title VARCHAR(255) DEFAULT 'New Chat',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # 4. Messages table for Chat Memory
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) REFERENCES sessions(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            print("Successfully initialized PostgreSQL database with pgvector, podcast_chunks, sessions, and messages tables!")
    finally:
        conn.close()

# --- SESSION & CHAT HISTORY DB HELPER FUNCTIONS ---

def create_session(session_id: str, title: str = "New Chat") -> str:
    """Creates a new chat session in the database."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sessions (id, title) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING;",
                (session_id, title)
            )
            conn.commit()
            return session_id
    finally:
        conn.close()

def get_all_sessions() -> list[dict]:
    """Fetches all active chat sessions sorted by newest first."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, created_at FROM sessions ORDER BY created_at DESC;")
            rows = cur.fetchall()
            return [{"id": r[0], "title": r[1], "created_at": r[2].isoformat()} for r in rows]
    finally:
        conn.close()

def delete_session(session_id: str) -> None:
    """Deletes a chat session and all associated messages from the database."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sessions WHERE id = %s;", (session_id,))
            conn.commit()
    finally:
        conn.close()


def save_message(session_id: str, role: str, content: str) -> None:
    """Saves a single message (user or assistant) to the database."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Ensure the session exists first
            cur.execute("INSERT INTO sessions (id, title) VALUES (%s, 'New Chat') ON CONFLICT (id) DO NOTHING;", (session_id,))
            
            # If it's the first user message, update session title based on prompt
            if role == "user":
                short_title = content[:30] + ("..." if len(content) > 30 else "")
                cur.execute("UPDATE sessions SET title = %s WHERE id = %s AND title = 'New Chat';", (short_title, session_id))
            
            # Insert message
            cur.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s);",
                (session_id, role, content)
            )
            conn.commit()
    finally:
        conn.close()

def get_session_messages(session_id: str, limit: int = 10) -> list[dict]:
    """Retrieves recent messages for a session to construct LLM conversation history."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT role, content 
                FROM (
                    SELECT role, content, created_at 
                    FROM messages 
                    WHERE session_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                ) sub 
                ORDER BY created_at ASC;
                """,
                (session_id, limit)
            )
            rows = cur.fetchall()
            return [{"role": r[0], "content": r[1]} for r in rows]
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
