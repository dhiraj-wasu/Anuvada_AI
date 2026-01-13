from fastapi import FastAPI
from app.routing.book_router import run_router_llm
from app.retrieval.retriever import retrieve
from app.generation.explainer import generate

app = FastAPI(title="Claritas")


@app.post("/ask")
def ask_question(question: str):
    """
    Full RAG pipeline:
    1) Route question to book
    2) Retrieve ranked Baba passages
    3) Generate Baba-grounded answer
    """

    # -------------------------------
    # 1️⃣ ROUTING
    # -------------------------------
    book = run_router_llm(question)
    print(f"📚 Routing to book: {book}")

    # -------------------------------
    # 2️⃣ RETRIEVAL (RANK-BASED)
    # -------------------------------
    chunks = retrieve(
        book=book,
        query=question,
        top_k=6
    )

    if not chunks:
        return {
            "book_used": book,
            "answer": (
                "Meher Baba has not spoken directly on this question "
                "in the available texts."
            )
        }

    answer = generate(
        chunks,
        question
    )

    return {
        "book_used": book,
        "answer": answer
    }
