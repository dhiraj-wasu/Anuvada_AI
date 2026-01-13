from typing import List
from app.llm.explainer_client import (
    get_explainer_openai_client,
    get_explainer_gemini_client,
)

def generate(context_chunks: List[dict], question: str) -> str:
    """
    Generate answer STRICTLY based on Meher Baba's words.
    OpenAI primary, Gemini fallback.
    context_chunks are DICTIONARIES.
    """

    # --------------------------------------------------
    # 1️⃣ QUOTE CONFIDENCE GATE (NON-NEGOTIABLE)
    # --------------------------------------------------
    baba_quotes = [
        c for c in context_chunks
        if c.get("speaker") == "Meher Baba" and c.get("text")
    ]

    if not baba_quotes:
        return (
            "Meher Baba has not spoken directly on this question "
            "in the available authoritative texts."
        )

    # --------------------------------------------------
    # 2️⃣ BUILD AUTHORITATIVE CONTEXT
    # --------------------------------------------------
    context_text = "\n\n".join(
        f"QUOTE SOURCE: {c.get('source', 'Unknown source')}\n"
        f"SPEAKER: {c.get('speaker', 'Unknown')}\n"
        f"TEXT:\n{c.get('text', '')}"
        for c in baba_quotes
    )

    prompt = f"""
You are NOT allowed to invent explanations.

RULES (STRICT):
- Use ONLY Meher Baba’s words from the context
- Quote Baba clearly
- Do NOT add philosophy
- Do NOT explain beyond the quotes
- After quoting, give a SIMPLE human explanation
- Relate it to the user's problem gently
- If something is not in context, say:
  "Meher Baba has not spoken directly on this."

FORMAT:

1) Baba's Words (quoted)
2) Simple Meaning (very short)
3) How this helps the person

CONTEXT (AUTHORITATIVE):
{context_text}

USER QUESTION:
{question}
"""

    # --------------------------------------------------
    # 3️⃣ OPENAI (PRIMARY)
    # --------------------------------------------------
    try:
        client = get_explainer_openai_client()

        response = client.responses.create(
            model="gpt-4.1",
            input=prompt,
            temperature=0.2
        )

        return response.output_text.strip()

    except Exception as openai_err:
        print("⚠️ OpenAI explainer failed:", openai_err)

    # --------------------------------------------------
    # 4️⃣ GEMINI (FALLBACK)
    # --------------------------------------------------
    try:
        gclient = get_explainer_gemini_client()

        response = gclient.models.generate_content(
            model="gemini-1.5-pro",
            contents=prompt
        )

        return response.text.strip()

    except Exception as gemini_err:
        print("❌ Gemini explainer failed:", gemini_err)

    # --------------------------------------------------
    # 5️⃣ FINAL SAFE FALLBACK
    # --------------------------------------------------
    return (
        "Meher Baba has not spoken directly on this question "
        "in the available authoritative texts."
    )
