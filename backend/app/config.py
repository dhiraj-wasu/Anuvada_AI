import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_PATH = "./qdrant_db"
COLLECTION_NAME = "meher_baba_books"
EMBED_MODEL = "text-embedding-3-large"
CHAT_MODEL = "gpt-4o"
