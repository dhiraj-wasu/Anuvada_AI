from typing import List
from app.llm.explainer_client import get_explainer_gemini_client


def generate(context_chunks: List[dict], question: str) -> str:
    """
    Generate answer STRICTLY based on Meher Baba's words.
    Uses ONLY Gemini (no OpenAI).
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
        f"SPEAKER: {c.get('speaker', 'Meher Baba')}\n"
        f"TEXT:\n{c.get('text')}"
        for c in baba_quotes[:6]
    )

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
    # 3️⃣ GEMINI ONLY
    # --------------------------------------------------
    try:
        gclient = get_explainer_gemini_client()

        response = gclient.models.generate_content(
            model="models/gemini-2.0-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as gemini_err:
        print("❌ Gemini explainer failed:", gemini_err)

        return (
            "Meher Baba has not spoken directly on this question "
            "in the available authoritative texts."
        )
