from typing import List, Optional
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
# BOOK → COLLECTION MAP
# =================================================

BOOK_COLLECTION_MAP = {
    "God Speaks": "god_speaks_collection",
    "Life Eternal": "life_eternal_collection",
}


# =================================================
# KEYWORD FALLBACK
# =================================================

def keyword_fallback(book: str, query: str, limit: int = 5) -> List[dict]:

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
# MAIN RETRIEVER (HYBRID READY)
# =================================================

def retrieve(
    book: str,
    query: str,
    router_topics: Optional[List[str]] = None,
    router_keywords: Optional[List[str]] = None,
    top_k: int = 6,
    threshold: float = 0.2
) -> List[dict]:

    collection = BOOK_COLLECTION_MAP.get(book)
    if not collection:
        return []

    router_topics = router_topics or []
    router_keywords = router_keywords or []

    enhanced_query = query

    if router_topics or router_keywords:
        enhanced_query = (
            query
            + " "
            + " ".join(router_topics)
            + " "
            + " ".join(router_keywords)
        )

    print("\n🔎 Enhanced Query Used For Embedding:")
    print(enhanced_query)

    vector = embed(enhanced_query)

    try:
        response = qdrant.query_points(
            collection_name=collection,
            query=vector,
            limit=top_k * 3,
            score_threshold=threshold,
            with_payload=True
        )

        results = response.points
        ranked = []

        print("\n📦 RAW RESULTS FROM QDRANT:")
        print(f"Total returned: {len(results)}\n")

        for r in results:
            payload = r.payload or {}
            score = 0.6 * r.score

            payload_topic = payload.get("topic", "").lower()

            for topic in router_topics:
                if topic.lower() in payload_topic:
                    score += 0.25

            text = payload.get("text", "").lower()

            for keyword in router_keywords:
                if keyword.lower() in text:
                    score += 0.15

            if payload.get("speaker") == "Meher Baba":
                score += 0.1

            # 🔥 DEBUG PRINT
            print("--------------------------------------------------")
            print("Vector Score:", round(r.score, 4))
            print("Final Score:", round(score, 4))
            print("Chunk ID:", payload.get("chunk_id"))
            print("Topic:", payload.get("topic"))
            print("Preview:", payload.get("text", "")[:200], "...")
            print("--------------------------------------------------\n")

            ranked.append((score, payload))

        ranked.sort(key=lambda x: x[0], reverse=True)

        print("\n🏆 FINAL TOP RANKED CHUNKS:")
        for i, (score, payload) in enumerate(ranked[:top_k], 1):
            print(f"{i}. {payload.get('chunk_id')} | Score: {round(score, 4)}")

        return [payload for _, payload in ranked[:top_k]]

    except Exception as e:
        print("⚠️ Vector search failed, using keyword fallback:", e)
        return keyword_fallback(book, query, limit=top_k)
