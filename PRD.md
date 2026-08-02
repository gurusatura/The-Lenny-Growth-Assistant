# Product Requirements Document (PRD): The Lenny Growth Assistant

## 1. Product Overview & Vision
**The Lenny Growth Assistant** is an AI-powered conversational workspace that ingests podcast transcripts from Lenny's Podcast and enables Product Managers, Founders, and Growth Engineers to ask complex Q&A questions, generate formatted content following **Ship30for30** digital writing rules, and dynamically render Markdown documents and HTML/CSS UI components natively side-by-side.

---

## 2. Target Personas
- **Product Managers & Growth Leaders**: Seeking actionable frameworks and growth advice grounded strictly in Lenny's Podcast knowledge base.
- **Content Creators**: Requesting Ship30for30 formatted essays, guides, and articles with strong hooks and bold skimmable sections.
- **Technical Evaluators**: Testing multi-turn session persistence, vector retrieval accuracy, flexible LLM switching, and native artifact rendering.

---

## 3. Engineering & Software Methodology
This application was built following the **Compound Engineering** and **Software Factory** methodology:
1. **Requirements & Intent Decomposition**: Defining explicit guardrails for casual conversation vs. artifact synthesis.
2. **Modular Architecture**: Decoupling vector retrieval (`embedding.py`), database persistence (`database.py`), LLM provider abstraction (`llm_provider.py`), and RAG orchestration (`rag.py`).
3. **Fail-Safe Auto-Wrapping**: Implementing defensive Python wrappers around LLM outputs to guarantee artifact tags are never omitted during synthesis.

---

## 4. Key Functional Requirements

### 4.1 Vector Retrieval & Knowledge Grounding
- Embeds transcripts into 384-dimensional vectors using `all-MiniLM-L6-v2`.
- Stores vectors in Supabase PostgreSQL (`pgvector`) and queries top context using native Cosine Distance (`<=>`).

### 4.2 Multi-Turn Session Persistence
- Persists user & assistant turns in `messages` linked to `sessions` table.
- Provides session restoration in sidebar and inline thread deletion (`DELETE /sessions/{session_id}`).

### 4.3 Ship30for30 Content Styling
- **Hook**: Counter-intuitive opening sentence.
- **Skimmability**: Bold headers, bullet points, 1-2 sentence paragraphs.
- **Takeaway**: Actionable closing statement.

### 4.4 Claude-Style Split-Screen Artifact Viewer
- **Center Chat**: Shows conversation thread and inline artifact badges.
- **Right Panel**: Auto-expands on artifact generation with **[Preview]** (live iframe / rendered markdown) vs **[Code]** (raw source) toggle switch.

---

## 5. Non-Functional Requirements
- **Response Time**: Sub-second vector retrieval from Supabase.
- **Security**: `.env` credential isolation via `.gitignore`.
- **Reliability**: Graceful fallback from cloud APIs to local Ollama.
