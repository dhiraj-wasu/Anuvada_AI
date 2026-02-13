import os
from dotenv import load_dotenv

load_dotenv()  # ✅ loads variables from .env into environment

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "meher_baba_books")

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-large")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o")
LOCAL_LLM_ENABLED = True      
GEMINI_ENABLED = False        



OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL = "llama3:8b"

    
GEMINI_MODEL = "models/gemini-2.0-flash"  