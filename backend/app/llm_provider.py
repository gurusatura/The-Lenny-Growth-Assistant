import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def chat_ollama(message: str) -> str:
    """
    Flexible LLM Provider Engine supporting Requirement 2:
    - Default Local LLM via Ollama (llama3.2:3b) for local demo.
    - Cloud LLM via OpenAI API (if LLM_PROVIDER=openai and OPENAI_API_KEY set).
    - Cloud LLM via Anthropic API (if LLM_PROVIDER=anthropic and ANTHROPIC_API_KEY set).
    If cloud keys are missing, gracefully falls back to local Ollama.
    """
    if LLM_PROVIDER == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[{"role": "user", "content": message}]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"[LLM Provider] OpenAI API Error: {e}. Falling back to local Ollama...")
        else:
            print("[LLM Provider] OPENAI_API_KEY not found in .env. Using local Ollama...")

    elif LLM_PROVIDER == "anthropic":
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=anthropic_key)
                response = client.messages.create(
                    model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                    max_tokens=1500,
                    messages=[{"role": "user", "content": message}]
                )
                return response.content[0].text
            except Exception as e:
                print(f"[LLM Provider] Anthropic API Error: {e}. Falling back to local Ollama...")
        else:
            print("[LLM Provider] ANTHROPIC_API_KEY not found in .env. Using local Ollama...")

    # Default Local LLM Engine via Ollama (Llama 3.2)
    from ollama import chat
    response = chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": message}]
    )
    return response["message"]["content"]
