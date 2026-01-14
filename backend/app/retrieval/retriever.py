from typing import List
from qdrant_client import QdrantClient

from app.config import QDRANT_HOST, QDRANT_PORT
from app.retrieval.embedding import embed


# =================================================
# QDRANT CLIENT
# =================================================

qdrant = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT
)


# =================================================
# BOOK → COLLECTION MAP (AUTHORITATIVE)
# =================================================

BOOK_COLLECTION_MAP = {
    "God Speaks": "god_speaks_collection",
    "Life Eternal": "life_eternal_collection",
}


# =================================================
# KEYWORD FALLBACK (NO VECTORS)
# =================================================

def keyword_fallback(book: str, query: str, limit: int = 5) -> List[dict]:
    """
    Fallback retrieval when vector search fails.
    Simple keyword matching on stored text.
    ALWAYS returns List[dict].
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
    results: List[dict] = []

    for p in points:
        payload = p.payload or {}
        text = payload.get("text", "").lower()

        if any(term in text for term in query_terms):
            results.append(payload)

    return results[:limit]


# =================================================
# MAIN RETRIEVER (VECTOR → FALLBACK)
# =================================================

def retrieve(
    book: str,
    query: str,
    top_k: int = 6,
    threshold: float = 0.2
) -> List[dict]:
    """
    Retrieve relevant chunks for a given book & query.

    1. Vector search using local embeddings
    2. Rank results
    3. Fallback to keyword search if vector fails

    RETURNS:
    - List[dict] payloads ONLY
    """

    collection = BOOK_COLLECTION_MAP.get(book)
    if not collection:
        return []

    # Local embedding
    vector = embed(query)

    try:
        # 🔑 CORRECT QDRANT API FOR v1.9+
        response = qdrant.query_points(
            collection_name=collection,
            query=vector,
            limit=top_k * 2,
            score_threshold=threshold,
            with_payload=True
        )

        results = response.points
        ranked = []

        for r in results:
            payload = r.payload or {}

            # Base similarity
            score = 0.6 * r.score

            # Topic boost (Life Eternal)
            topic = payload.get("topic", "")
            if topic and topic.lower() in query.lower():
                score += 0.2

            # Speaker boost (if present)
            if payload.get("speaker") == "Meher Baba":
                score += 0.2

            ranked.append((score, payload))

        ranked.sort(key=lambda x: x[0], reverse=True)
        return [payload for _, payload in ranked[:top_k]]

    except Exception as e:
        print("⚠️ Vector search failed, using keyword fallback:", e)
        return keyword_fallback(book, query, limit=top_k)
