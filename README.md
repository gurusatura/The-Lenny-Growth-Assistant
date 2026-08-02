# 🧠 The Lenny Growth Assistant

**The Lenny Growth Assistant** is a full-stack, AI-powered conversational workspace built with **FastAPI**, **Supabase PostgreSQL (`pgvector`)**, **Ollama (Llama 3.2)**, and a **Claude-Style Split-Screen UI**.

The application ingests transcripts from Lenny's Podcast, answers high-context Product Management & Growth questions grounded in vector retrieval, formats content using **Ship30for30** digital writing rules, and dynamically renders HTML/Markdown artifacts side-by-side in an in-app viewer.

---

## 🏗️ Technical Architecture & Workflow

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Browser Split-Screen UI                                  │
│ ┌──────────────────────────┬─────────────────────────────────┬─────────────────────────┐ │
│ │ Left Sidebar             │ Center Chat Window              │ Right Artifact Viewer   │ │
│ │ - Session Management     │ - Multi-Turn Chat               │ - Live HTML iFrame      │ │
│ │ - Trash Delete           │ - Intent Guardrails             │ - Rendered Markdown     │ │
│ └────────────┬─────────────┴────────────────┬────────────────┴────────────┬────────────┘ │
└──────────────┼──────────────────────────────┼─────────────────────────────┼──────────────┘
               │                              │                             │
               ▼                              ▼                             ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FastAPI Backend Server                                 │
│ ┌──────────────────────────┬─────────────────────────────────┬─────────────────────────┐ │
│ │ Session & Messages API   │ Stateful RAG Engine (rag.py)    │ LLM Provider Engine     │ │
│ │ - GET/POST/DELETE        │ - Vector Context Search         │ - Ollama (Llama 3.2)    │ │
│ │ - Chat History Memory    │ - Ship30for30 Prompting         │ - OpenAI / Anthropic    │ │
│ └────────────┬─────────────┴────────────────┬────────────────┴────────────┬────────────┘ │
└──────────────┼──────────────────────────────┼─────────────────────────────┼──────────────┘
               │                              │                             │
               ▼                              ▼                             ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                              Supabase PostgreSQL Vector DB                               │
│  - podcast_chunks (384d pgvector embeddings via SentenceTransformer)                    │
│  - sessions & messages relational tables (ON DELETE CASCADE)                            │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

The database uses PostgreSQL with the `pgvector` extension enabled in Supabase:

### 1. `podcast_chunks` (Vector Table)
```sql
CREATE TABLE podcast_chunks (
    id SERIAL PRIMARY KEY,
    chunk_text TEXT NOT NULL,
    embedding vector(384) NOT NULL
);
```

### 2. `sessions` (Chat Thread Table)
```sql
CREATE TABLE sessions (
    id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. `messages` (Multi-Turn Chat History Table)
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔀 Agentic Routing Logic & LLM Toggle Switch

### 1. Intent Guardrails & Artifact Routing (`rag.py`)
- **Casual Chat Routing**: Greetings like `"hi"` or `"hello"` are routed to standard inline chat responses without triggering `<artifact>` tags.
- **Artifact Document Routing**: When the user query requests a **.md file**, **document**, **essay**, **guide**, **article**, or **code**, the RAG engine wraps the output inside `<artifact type="markdown" title="..."> ... </artifact>` tags.
- **Python Auto-Wrapper**: If the LLM omits the `<artifact>` XML tags for a requested document/guide, Python automatically wraps the response before returning it to the UI, guaranteeing 100% artifact rendering.

### 2. LLM Engine Toggle Switch (`llm_provider.py`)
The system features a flexible LLM provider configuration via environment variable `LLM_PROVIDER`:
- `LLM_PROVIDER=ollama`: Uses local **Ollama (`llama3.2:3b`)** for mandatory local evaluator demo.
- `LLM_PROVIDER=openai`: Uses OpenAI Cloud API (`OPENAI_API_KEY`).
- `LLM_PROVIDER=anthropic`: Uses Anthropic Cloud API (`ANTHROPIC_API_KEY`).
- **Automatic Fallback**: If cloud keys are missing, the system gracefully defaults to local **Ollama** without throwing errors.

---

## 🔌 API Endpoints

- `GET /sessions`: List all active chat sessions for sidebar.
- `POST /sessions`: Create a new chat session thread.
- `DELETE /sessions/{session_id}`: Delete a session and its message history.
- `GET /sessions/{session_id}/messages`: Retrieve past conversation turns.
- `POST /chat`: Execute stateful RAG pipeline (`{ "message": "...", "session_id": "..." }`).

---

## 🚀 Step-by-Step Local Deployment Guide for Evaluators

### 1. Prerequisites
- Python 3.10+ installed
- [Ollama](https://ollama.com/) installed with `llama3.2:3b` model downloaded:
  ```bash
  ollama pull llama3.2:3b
  ```

### 2. Clone Repository & Setup Environment
```bash
git clone https://github.com/gurusatura/lenny-growth-assistant.git
cd lenny-growth-assistant
```

Create file `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
```
*(Note: Never push `.env` to Git repository).*

### 3. Install Dependencies
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run Ingestion (Populates Supabase Vector DB)
```powershell
python -m backend.app.embedding
```

### 5. Start Backend Server
```powershell
python -m uvicorn backend.app.main:app --reload
```
Server runs at `http://127.0.0.1:8000`.

### 6. Launch Frontend UI
Open `frontend/index.html` directly in any web browser (Chrome/Edge/Brave).

---

## 📂 Documentation & Transcripts
- **[PRD.md](PRD.md)**: Product Requirements Document.
- **[design.md](design.md)**: UI/UX Design System Document.
- **[agent_transcripts/transcript_log.md](agent_transcripts/transcript_log.md)**: Complete Coding Agent execution log & edge-case debugging history.
