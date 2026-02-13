from fastapi import FastAPI
import json

from app.routing.book_router import run_router_llm
from app.retrieval.retriever import retrieve
from app.generation.explainer import generate

app = FastAPI(title="Claritas")


@app.post("/ask")
def ask_question(question: str):

    # -------------------------------
    # 1️⃣ ROUTING (Structured)
    # -------------------------------
    router_response = run_router_llm(question)
    print("📡 Router response:", router_response)

    try:
        routing_data = json.loads(router_response)
    except Exception:
        return {
            "error": "Router did not return valid JSON",
            "raw_router_output": router_response
        }

    book = routing_data.get("book")
    topics = routing_data.get("topics", [])
    keywords = routing_data.get("keywords", [])

    print(f"📚 Routing to book: {book}")
    print(f"🏷 Topics: {topics}")
    print(f"🔎 Keywords: {keywords}")

    # -------------------------------
    # 2️⃣ RETRIEVAL (Hybrid)
    # -------------------------------
    chunks = retrieve(
        book=book,
        query=question,
        router_topics=topics,
        router_keywords=keywords,
        top_k=6
    )
    
    if not chunks:
        return {
            "book_used": book,
            "answer": "Meher Baba has not spoken directly on this question."
        }

    # -------------------------------
    # 3️⃣ GENERATION
    # -------------------------------
    answer = generate(chunks, question)

    return {
        "book_used": book,
        "answer": answer
    }
