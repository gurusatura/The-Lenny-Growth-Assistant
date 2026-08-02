from backend.app.embedding import search_vector_db
from backend.app.llm_provider import chat_ollama
from backend.app.database import save_message, get_session_messages


def myrag(userquery: str, session_id: str = None) -> str:
    """
    Stateful RAG (Retrieval-Augmented Generation) pipeline:
    1. Memory Persistence: Saves user message & loads recent conversation history for session_id.
    2. Retrieval: Searches Supabase PostgreSQL for top 2 context chunks matching user query.
    3. Augmentation: Assembles system prompt with explicit Artifact Trigger rules (.md, document, guide, essay).
    4. Generation: Passes assembled prompt to local Llama 3.2 via Ollama.
    5. Python Auto-Wrapper: Guarantees <artifact> tags for requested guides, essays, and files.
    6. Memory Saving: Saves generated answer into Supabase messages table.
    """
    history_text = ""

    # 1. Handle session history and save user query if session_id provided
    if session_id:
        # Save current user message
        save_message(session_id, "user", userquery)

        # Retrieve prior chat history (up to 6 recent messages)
        recent_messages = get_session_messages(session_id, limit=6)
        if len(recent_messages) > 1:
            history_lines = []
            for msg in recent_messages[:-1]:  # Prior turns before current question
                role_label = "User" if msg["role"] == "user" else "Assistant"
                history_lines.append(f"{role_label}: {msg['content']}")
            history_text = "\n".join(history_lines)

    # 2. Retrieve relevant context chunks from Supabase PostgreSQL (pgvector)
    retrieved_chunks = search_vector_db(userquery, k=2)
    context = "\n\n".join(retrieved_chunks)

    # Detect if user query explicitly requests a document, file, .md, guide, or essay
    query_lower = userquery.lower()
    is_artifact_request = any(keyword in query_lower for keyword in [
        "md", ".md", "markdown", "file", "document", "essay", "guide", "article", "framework", "code", "summary"
    ])

    if is_artifact_request:
        artifact_instruction = (
            "CRITICAL OUTPUT RULE: The user is requesting a document, .md file, guide, or essay.\n"
            "You MUST structure your response as an Artifact wrapped in tags:\n"
            "Here is your requested document:\n"
            "<artifact type=\"markdown\" title=\"Lenny Growth Document\">\n"
            "# [Title Here]\n\n"
            "[Your complete Ship30for30 formatted article/essay/guide here]\n"
            "</artifact>\n"
        )
    else:
        artifact_instruction = (
            "GREETING & CHAT RULE: For casual greetings (like 'hi', 'hello'), reply in 1 short sentence WITHOUT <artifact> tags.\n"
        )

    # 3. Formulate System Prompt
    system_prompt = (
        "You are 'The Lenny Growth Assistant', a world-class Product Management & Growth expert.\n\n"
        f"{artifact_instruction}\n"
        "WRITING & FORMATTING RULES (Ship30for30 Style for Articles/Artifacts):\n"
        "- HOOK: Start with a strong, attention-grabbing opening sentence.\n"
        "- SKIMMABILITY: Bold headings, bullet points, 1-2 sentence paragraphs.\n"
        "- TAKEAWAY: End with a single bold actionable takeaway.\n\n"
        f"=== CONVERSATION HISTORY ===\n{history_text if history_text else 'None (First Turn)'}\n\n"
        f"=== RETRIEVED PODCAST CONTEXT ===\n{context}\n\n"
        f"=== USER REQUEST ===\n{userquery}"
    )

    # 4. Generate response using local Llama 3.2
    answer = chat_ollama(system_prompt)

    # 5. BULLETPROOF AUTO-WRAPPER: If artifact was requested but model omitted <artifact> tags, wrap automatically!
    if is_artifact_request and "<artifact" not in answer:
        # Extract title from first markdown header if available
        lines = [line.strip() for line in answer.split("\n") if line.strip()]
        doc_title = "Actionable Growth Guide"
        for line in lines:
            if line.startswith("#"):
                doc_title = line.replace("#", "").strip()
                break

        answer = f"Here is your requested guide:\n\n<artifact type=\"markdown\" title=\"{doc_title}\">\n{answer}\n</artifact>"

    # 6. Save assistant response to database if session_id is provided
    if session_id:
        save_message(session_id, "assistant", answer)

    return answer
