from typing import List
import requests
import os
from google import genai

from app.config import (
    LOCAL_LLM_ENABLED,
    GEMINI_ENABLED,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GEMINI_MODEL,
)


def generate(context_chunks: List[dict], question: str) -> str:
    """
    Generate answer STRICTLY based on Meher Baba's words.
    Local Ollama first. Gemini optional fallback.
    """

    # --------------------------------------------------
    # 1️⃣ Quote Gate
    # --------------------------------------------------
    baba_quotes = [
        c for c in context_chunks
        if c.get("speaker") == "Meher Baba" and c.get("text")
    ]
    # print(f"🔍 Found {len(baba_quotes)} relevant Baba quotes in context.")
    
    # --------------------------------------------------
    # 2️⃣ Build Context
    # --------------------------------------------------
    context_text = "\n\n".join(
        f"QUOTE SOURCE: {c.get('source', 'Unknown source')}\n"
        f"SPEAKER: {c.get('speaker')}\n"
        f"TEXT:\n{c.get('text')}"
        for c in baba_quotes[:6]
    )
    print(context_text)
    prompt = f"""
You are NOT allowed to invent explanations.

RULES (STRICT):
- Use ONLY Meher Baba’s words from the context
- Quote Baba clearly
- Do NOT add philosophy
- Do NOT add new ideas
- Do NOT explain beyond the quotes
- After quoting, give a VERY SIMPLE human explanation
- Relate it gently to the user's problem
- If something is not in context, say exactly:
  "Meher Baba has not spoken directly on this."

FORMAT (STRICT):

1) Baba's Words (quoted)
2) Simple Meaning (1–2 lines)
3) How this helps the person

CONTEXT (AUTHORITATIVE):
{context_text}

USER QUESTION:
{question}
"""

    # --------------------------------------------------
    # 3️⃣ LOCAL OLLAMA FIRST
    # --------------------------------------------------
    if LOCAL_LLM_ENABLED:
        try:
            print("🟢 Using LOCAL Ollama explainer")

            payload = {
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a strict spiritual text explainer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }

            r = requests.post(
             "http://localhost:11434/api/chat",
                json=payload,
                timeout=60
            )

            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()

        except Exception as local_err:
            print("⚠️ Ollama explainer failed:", local_err)

            if not GEMINI_ENABLED:
                return (
                    "Meher Baba has not spoken directly on this question "
                    "in the available authoritative texts."
                )

    # --------------------------------------------------
    # 4️⃣ GEMINI FALLBACK (OPTIONAL)
    # --------------------------------------------------
    else:
        try:
            print("🟡 Using Gemini fallback")

            gclient = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

            response = gclient.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            return (response.text or "").strip()

        except Exception as gemini_err:
            print("❌ Gemini explainer failed:", gemini_err)

    # --------------------------------------------------
    # 5️⃣ FINAL SAFE FALLBACK
    # --------------------------------------------------
    return (
        "Meher Baba has not spoken directly on this question "
        "in the available authoritative texts."
    )
