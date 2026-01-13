from typing import List
from qdrant_client import QdrantClient

from app.config import QDRANT_HOST, QDRANT_PORT
from app.retrieval.embedding import embed

# -------------------------------------------------
# Qdrant client
# -------------------------------------------------

qdrant = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
    check_compatibility=False  # avoid client/server version warnings
)

# -------------------------------------------------
# Book → Collection mapping (AUTHORITATIVE)
# -------------------------------------------------

BOOK_COLLECTION_MAP = {
    "God Speaks": "god_speaks_collection",
    "Life Eternal": "life_eternal_collection",
}

# -------------------------------------------------
# Keyword fallback (NO embeddings)
# -------------------------------------------------

def keyword_fallback(book: str, query: str, limit: int = 5) -> List[dict]:
    """
    Simple keyword-based fallback retrieval.
    Used only if vector search fails.
    """
    collection = BOOK_COLLECTION_MAP.get(book)
    if not collection:
        return []

    points, _ = qdrant.scroll(
        collection_name=collection,
        limit=300,
        with_payload=True
    )

    query_terms = query.lower().split()
    scored = []

    for p in points:
        payload = p.payload or {}
        text = payload.get("text", "").lower()

        score = sum(1 for term in query_terms if term in text)
        if score > 0:
            scored.append((score, payload))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [payload for _, payload in scored[:limit]]

# -------------------------------------------------
# MAIN RETRIEVER (VECTOR + FALLBACK)
# -------------------------------------------------

def retrieve(
    book: str,
    query: str,
    top_k: int = 6,
    threshold: float = 0.2
) -> List[dict]:
    """
    Retrieve relevant chunks for a given book and query.
    Uses SentenceTransformer embeddings + Qdrant vector search.
    Falls back to keyword search if vector search fails.
    """

    collection = BOOK_COLLECTION_MAP.get(book)
    if not collection:
        return []

    # Generate embedding locally (SentenceTransformer)
    vector = embed(query)

    try:
        # ✅ CORRECT Qdrant API (query_points + query)
        results = qdrant.query_points(
            collection_name=collection,
            query=vector,
            limit=top_k * 2,
            score_threshold=threshold,
            with_payload=True
        )

        ranked = []

        for r in results:
            payload = r.payload or {}

            # Base similarity score
            score = 0.6 * r.score

            # Topic boost
            if payload.get("topic", "").lower() in query.lower():
                score += 0.2

            # Meher Baba quote boost
            if payload.get("speaker") == "Meher Baba":
                score += 0.2

            ranked.append((score, payload))

        ranked.sort(key=lambda x: x[0], reverse=True)
        return [payload for _, payload in ranked[:top_k]]

    except Exception as e:
        print("⚠️ Vector search failed, using keyword fallback:", e)
        return keyword_fallback(book, query, limit=top_k)
