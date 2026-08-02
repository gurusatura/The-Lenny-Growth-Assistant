# Agentic Coding Transcripts & Development Log

This directory contains the paired coding agent execution transcript for **The Lenny Growth Assistant**. It documents the complete iterative engineering workflow, key architecture decisions, edge-case debugging, failed attempts, and how they were resolved.

---

## 📅 Session Overview
- **Project**: The Lenny Growth Assistant
- **AI Agent**: Antigravity (Google DeepMind Agentic Coding Assistant)
- **Primary Goal**: Build a full-stack, RAG-powered conversational workspace with Supabase pgvector, stateful session memory, flexible LLM configuration, and side-by-side Claude-style artifact rendering.

---

## 📑 Key Milestones & Debugging Log

### Milestone 1: Local Ingestion & Vector DB Migration (FAISS -> Supabase pgvector)
- **Initial State**: Early prototype used local FAISS index files (`index.faiss`) saved to disk.
- **Challenge**: The assignment requires a robust PostgreSQL vector database setup suitable for cloud deployment and session persistence.
- **Action & Solution**:
  - Migrated `backend/app/embedding.py` to use **Supabase PostgreSQL** with the `pgvector` extension.
  - Initialized `podcast_chunks` table storing 384-dimensional embeddings generated via `SentenceTransformer('all-MiniLM-L6-v2')`.
  - Configured native vector similarity queries using the `<=>` cosine distance operator.

### Milestone 2: Stateful Session Memory & Schema Design
- **Challenge**: Initial endpoints treated every chat turn as a stateless request, causing the AI to lose context across multi-turn conversations.
- **Action & Solution**:
  - Designed relational PostgreSQL schema in `backend/app/database.py`:
    - `sessions` table (`id`, `title`, `created_at`).
    - `messages` table (`id`, `session_id`, `role`, `content`, `created_at`).
  - Added RESTful endpoints in `backend/app/main.py`:
    - `GET /sessions`: List chat threads for sidebar.
    - `POST /sessions`: Spawn new chat session.
    - `DELETE /sessions/{session_id}`: Remove chat thread.
    - `GET /sessions/{session_id}/messages`: Fetch multi-turn history.
  - Integrated conversation history lookup into `rag.py` to prepend prior turns to Llama 3.2 system prompts.

### Milestone 3: Ship30for30 Prompt Guardrails & Artifact Triggers
- **Issue #1 (Greeting Bug)**:
  - *Symptom*: When a user typed casual greetings like `"hi"` or `"hello"`, the model wrapped the response inside `<artifact>` tags, opening the right panel unnecessarily.
  - *Fix*: Implemented strict intent classification in `rag.py`. Casual greetings are flagged to return standard plain-text chat bubbles without triggering `<artifact>` tags.
- **Issue #2 (Model Skipping Tags for Guides)**:
  - *Symptom*: When a user asked for a 4-step guide or `.md` file, local Llama 3.2 focused heavily on markdown headers and occasionally omitted the `<artifact>` XML wrapper.
  - *Fix*: Created a **Python Auto-Wrapper** in `rag.py`. If an artifact is requested but the model output lacks `<artifact>` tags, Python automatically wraps the markdown content inside `<artifact type="markdown" title="...">` tags.

### Milestone 4: Claude-Style Split-Screen UI & Live HTML/CSS Component Rendering
- **Challenge**: Markdown preview worked fine, but HTML/CSS code artifacts initially displayed raw HTML code snippets rather than live visual components.
- **Action & Solution**:
  - Upgraded `frontend/index.html` `switchArtifactTab('preview')`:
    - Automatically extracts HTML/CSS code blocks from markdown backticks (` ```html `).
    - Injects combined HTML & CSS into a sandboxed `<iframe>`.
    - Allows users to see **LIVE VISUAL UI COMPONENTS** (buttons, cards, styled layouts) in the **Preview** tab, and raw monospaced code in the **Code** tab!

### Milestone 5: Flexible LLM Provider Configuration
- **Requirement**: Support switching between Local LLM (Ollama) and Cloud LLMs (OpenAI, Anthropic).
- **Implementation**:
  - Built `backend/app/llm_provider.py` reading `LLM_PROVIDER` environment variable.
  - Added graceful fallback: If an evaluator specifies `openai` or `anthropic` but does not provide an API key, the system automatically falls back to local **Ollama (`llama3.2:3b`)** without crashing.

---

## 🛠️ Summary of Final Verified Stack
- **Backend**: FastAPI + Uvicorn
- **Database**: Supabase PostgreSQL + `pgvector`
- **LLM Engine**: Ollama (Llama 3.2:3b) + SentenceTransformers
- **Frontend**: Vanilla HTML5/CSS3 + marked.js + FontAwesome
- **Documentation**: `README.md`, `PRD.md`, `design.md`, `agent_transcripts/transcript_log.md`
