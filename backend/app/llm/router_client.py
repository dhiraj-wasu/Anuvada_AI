import os
from openai import OpenAI
from google import genai

# ---------- OpenAI ----------
def get_router_openai_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------- Gemini ----------
def get_router_gemini_client() -> genai.Client:
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


