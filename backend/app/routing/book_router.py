# backend/app/routing/book_router.py

import os
from typing import Optional
from google import genai


# Models (override from env if you want)
# OPENAI_ROUTER_MODEL = os.getenv("OPENAI_ROUTER_MODEL", "gpt-4o-mini")
GEMINI_ROUTER_MODEL = os.getenv("GEMINI_ROUTER_MODEL", "models/gemini-2.0-flash")


# ---------------- SYSTEM PROMPT (Router Instructions) ----------------
SYSTEM_MESSAGE  = """
You are an expert librarian + router for Meher Baba books.

Your job:
1) Understand the user’s question.
2) Choose the best Meher Baba book(s) to answer it:
   - God Speaks
   - Life Eternal
   no other books are available.on;ly these two.
3) Output routing decision + topic tags + search keywords.

Use this metadata.

======================
BOOK METADATA: LIFE ETERNAL
======================
BOOK: Life Eternal
EDITOR/COMPILATION: Collection of quotations, explanations, stories, and background context related to Meher Baba’s teachings.
CATEGORY: Direct guidance / spiritual counsel / practical spirituality / devotional life
STYLE:
- Highly quotable, topic-wise organized.
- Best for direct, human-level spiritual questions: suffering, love, surrender, prayer, happiness, the path.
- Gives short powerful Baba statements and real-life context stories.

STRUCTURE:
This book has two major parts:

--------------------------
BOOK ONE (46 chapters)
--------------------------
- Made up entirely of explanations given by Meher Baba.
- Divided by subject into chapters.
- Quotes arranged chronologically: earliest to latest inside each chapter.
- Most content is self-explanatory.
- ALL content is Baba’s words (quotes not individually labeled as Baba in Book One).

--------------------------
BOOK TWO (53 chapters)
--------------------------
- Stories, anecdotes, and disciples/devotees quotes + context notes.
- Also contains some Baba quotes that REQUIRE background.
- Quotes are labeled by speaker (Meher Baba / disciples).
- Material is generally chronological.

CORE PURPOSE:
Life Eternal is designed to answer day-to-day spiritual questions using Meher Baba’s direct words,
organized by topics like Love, Suffering, Surrender, Prayer, Happiness, Morality, Meditation, etc.

--------------------------
Life Eternal answers BEST
--------------------------
Use Life Eternal as PRIMARY source when the user asks:

Personal Suffering / Inner Pain
- Why am I suffering?
- How to face problems / hardship?
- Why does God allow pain?
- How to handle sadness, depression, loneliness?
- How to endure without breaking?

Love & Devotion
- What is real love?
- How to love God / Baba?
- Why love is the highest path?
- How love transforms life?
- Love vs attachment

Surrender & Trust
- How do I surrender?
- How to accept God’s will?
- Why surrender is hard?
- How to stop worrying and trust Baba?

Prayer
- How to pray correctly?
- Does prayer help?
- What kind of prayer Baba wants?
- Prayer vs meditation

Happiness / Peace
- How to be happy?
- What is lasting happiness?
- Why world pleasures don’t satisfy?

Spiritual Path (practical)
- How to progress spiritually?
- What should I practice daily?
- How to live as Baba wants?
- What obstacles stop progress?

Following Meher Baba
- How to follow Baba truly?
- What Baba expects from lovers
- obedience, honesty, remembrance

Morality / Right conduct
- truthfulness, purity, integrity
- how to live ethically

Mind & Desires
- controlling mind, anger, lust, greed
- handling temptations
- overcoming fear and ego

General spiritual clarity
- what is spirituality
- difference between intellectual knowledge vs experience
- understanding God, Maya, illusion (simple explanation style)

--------------------------
Life Eternal is NOT primary when
--------------------------
If the user asks heavy metaphysics like:
- cosmic creation structure
- evolution of consciousness through forms
- detailed reincarnation mechanism
- seven planes of consciousness in depth
-> use God Speaks as primary.

If user asks deep “life conduct + structured essays”
-> use Discourses as primary, and Life Eternal as supporting direct quotes.

=========================
OUTPUT FORMAT
=========================
give ouput in this JSON format, strictly:
{
  "book": "",
  "topics": [],
  "keywords": []
}

give only the JSON as output, no explanations, no extra text.
stictly follow the format, and ensure the output is valid JSON.
"""

import os
from typing import Optional
import requests
from google import genai

from app.config import (
    LOCAL_LLM_ENABLED,
    GEMINI_ENABLED,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GEMINI_MODEL,
)



# -------------------------------------------------
# LOCAL OLLAMA CALL
# -------------------------------------------------

import requests

def call_ollama(user_prompt: str) -> str:
    payload = {
        "model": "llama3:8b",
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "stream": False   # 🔑 THIS FIXES YOUR ERROR
    }
    print("📡 Sending request to local Ollama router...")
    r = requests.post(
        "http://localhost:11434/api/chat",
        json=payload,
        timeout=180
    )

    r.raise_for_status()

    data = r.json()   # now safe

    return data["message"]["content"].strip()


# -------------------------------------------------
# GEMINI CALL
# -------------------------------------------------

def call_gemini(prompt: str) -> str:
    try:
        gclient = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        resp = gclient.models.generate_content(
            model=GEMINI_MODEL,
            contents=SYSTEM_MESSAGE + "\n\n" + prompt
        )

        return (resp.text or "").strip()

    except Exception as e:
        print("⚠️ Gemini router failed:", e)
        raise


# -------------------------------------------------
# FINAL ROUTER
# -------------------------------------------------

def run_router_llm(question: str) -> str:

    user_prompt = f"User question:\n{question}"

    # 1️⃣ Try local first
    if LOCAL_LLM_ENABLED:
        try:
            print("🟢 Using LOCAL Ollama router")
            return call_ollama(user_prompt)
        except Exception:
            if not GEMINI_ENABLED:
                raise RuntimeError("Local LLM failed and Gemini disabled.")

    # 2️⃣ Fallback to Gemini (if allowed)
    if GEMINI_ENABLED:
        print("🟡 Using Gemini fallback")
        return call_gemini(user_prompt)

    # 3️⃣ Nothing available
    raise RuntimeError("No LLM available (local disabled and Gemini disabled).")