from backend.app.embedding import search_vector_db
from backend.app.llm_provider import chat_ollama
from backend.app.database import save_message, get_session_messages


def myrag(userquery: str, session_id: str = None) -> str:
    """
    Stateful RAG (Retrieval-Augmented Generation) pipeline:
    1. Memory Persistence: Saves user message & loads recent conversation history for session_id.
    2. Retrieval: Searches Supabase PostgreSQL for top 2 context chunks matching user query.
    3. Augmentation: Assembles system prompt with explicit Artifact Trigger rules (.md, document, guide, essay, html).
    4. Generation: Passes assembled prompt to local Llama 3.2 via Ollama.
    5. Python Auto-Wrapper: Guarantees <artifact> tags for requested guides, essays, and files.
    6. Memory Saving: Saves generated answer into Supabase messages table.
    """
    history_text = ""

    # 1. Handle session history and save user query if session_id provided
    if session_id:
        save_message(session_id, "user", userquery)

        recent_messages = get_session_messages(session_id, limit=6)
        if len(recent_messages) > 1:
            history_lines = []
            for msg in recent_messages[:-1]:
                role_label = "User" if msg["role"] == "user" else "Assistant"
                history_lines.append(f"{role_label}: {msg['content']}")
            history_text = "\n".join(history_lines)

    # 2. Retrieve relevant context chunks from Supabase PostgreSQL (pgvector)
    retrieved_chunks = search_vector_db(userquery, k=2)
    context = "\n\n".join(retrieved_chunks)

    # Detect if user query explicitly requests HTML/CSS vs Markdown/Document
    query_lower = userquery.lower()
    is_html_request = any(keyword in query_lower for keyword in [
        "html", "css", "component", "webpage", "website", "card component"
    ])
    is_markdown_request = any(keyword in query_lower for keyword in [
        "md", ".md", "markdown", "file", "document", "essay", "guide", "article", "framework", "summary", "burnout", "wisdom"
    ])
    is_artifact_request = is_html_request or is_markdown_request

    if is_html_request:
        artifact_instruction = (
            "CRITICAL OUTPUT RULE: The user is requesting an HTML / CSS web component.\n"
            "You MUST output complete, beautifully-styled HTML + CSS code with realistic sample data inside an artifact tag:\n"
            "Here is your requested HTML component:\n"
            "<artifact type=\"html\" title=\"Contact Card Component\">\n"
            "```html\n"
            "<div class=\"contact-card\">\n"
            "  <img src=\"https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150\" alt=\"Avatar\" class=\"avatar\">\n"
            "  <h2 class=\"name\">Alex Rivera</h2>\n"
            "  <p class=\"title\">Head of Product & Growth</p>\n"
            "  <p class=\"email\">alex.rivera@growth.io</p>\n"
            "  <button class=\"btn\">Connect</button>\n"
            "</div>\n"
            "```\n"
            "```css\n"
            ".contact-card { background: #1e293b; color: #f8fafc; padding: 24px; border-radius: 16px; text-align: center; max-width: 320px; margin: 20px auto; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }\n"
            ".avatar { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 12px; border: 2px solid #6366f1; }\n"
            ".name { font-size: 1.25rem; font-weight: 700; color: #ffffff; margin-bottom: 4px; }\n"
            ".title { font-size: 0.9rem; color: #818cf8; margin-bottom: 8px; }\n"
            ".email { font-size: 0.85rem; color: #94a3b8; margin-bottom: 16px; }\n"
            ".btn { background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%; }\n"
            "```\n"
            "</artifact>\n"
            "IMPORTANT: Include realistic mock text, avatar image URL, and full CSS styling so the component renders beautifully."
        )
    elif is_markdown_request:
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
        "WRITING & FORMATTING RULES:\n"
        "- If generating articles/guides: Use Ship30for30 style (strong hook, bold bullet points, single actionable takeaway).\n"
        "- If generating HTML/CSS: Provide clean, functional code blocks with full CSS styles and sample text, without markdown essay fluff.\n\n"
        f"=== CONVERSATION HISTORY ===\n{history_text if history_text else 'None (First Turn)'}\n\n"
        f"=== RETRIEVED PODCAST CONTEXT ===\n{context}\n\n"
        f"=== USER REQUEST ===\n{userquery}"
    )

    # 4. Generate response using local Llama 3.2
    answer = chat_ollama(system_prompt)

    # 5. BULLETPROOF AUTO-WRAPPER: If artifact was requested but model omitted <artifact> tags, wrap automatically!
    if is_artifact_request and "<artifact" not in answer:
        if is_html_request:
            answer = f"Here is your requested HTML component:\n\n<artifact type=\"html\" title=\"HTML CSS Component\">\n{answer}\n</artifact>"
        else:
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
