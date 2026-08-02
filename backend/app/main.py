import uuid
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.rag import myrag
from backend.app.database import (
    create_session,
    delete_session,
    get_all_sessions,
    get_session_messages,
    init_db
)

app = FastAPI(title="Lenny Growth Assistant API")

# Initialize DB tables on server startup
@app.on_event("startup")
def on_startup():
    init_db()

# Enable CORS for browser frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Chat"

@app.get("/")
def read_root():
    return {"message": "Lenny Growth Assistant FastAPI + Supabase pgvector API is running"}

# --- CHAT & SESSION ENDPOINTS ---

@app.get("/sessions")
def list_sessions():
    """Returns list of all active conversation sessions for the sidebar."""
    return {"sessions": get_all_sessions()}

@app.post("/sessions")
def new_session(request: CreateSessionRequest):
    """Creates a new session ID and saves it to PostgreSQL."""
    session_id = f"sess_{uuid.uuid4().hex[:10]}"
    create_session(session_id, request.title or "New Chat")
    return {"session_id": session_id, "title": request.title or "New Chat"}

@app.delete("/sessions/{session_id}")
def remove_session(session_id: str):
    """Deletes a chat session and all associated messages."""
    delete_session(session_id)
    return {"status": "success", "session_id": session_id}

@app.get("/sessions/{session_id}/messages")
def get_messages(session_id: str):
    """Returns past chat messages for a specific session."""
    messages = get_session_messages(session_id, limit=50)
    return {"session_id": session_id, "messages": messages}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint:
    Processes user query, retrieves RAG context from Supabase, updates chat history,
    and returns LLM generated response.
    """
    session_id = request.session_id
    if not session_id:
        session_id = f"sess_{uuid.uuid4().hex[:10]}"
        create_session(session_id, "New Chat")

    response = myrag(request.message, session_id=session_id)
    return {
        "session_id": session_id,
        "response": response
    }
