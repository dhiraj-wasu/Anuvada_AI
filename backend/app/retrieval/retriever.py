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
    """
    Simple fallback retrieval using raw keyword matching.
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
    results: List[dict] = []

    for p in points:
        payload = p.payload or {}
        text = payload.get("text", "").lower()

        if any(term in text for term in query_terms):
            results.append(payload)

    return results[:limit]


# =================================================
# MAIN HYBRID RETRIEVER
# =================================================

def retrieve(
    book: str,
    query: str,
    router_topics: Optional[List[str]] = None,
    router_keywords: Optional[List[str]] = None,
    top_k: int = 2,
    threshold: float = 0.2
) -> List[dict]:

    collection = BOOK_COLLECTION_MAP.get(book)
    if not collection:
        return []

    router_topics = router_topics or []
    router_keywords = router_keywords or []

    # --------------------------------------------------
    # 1️⃣ QUERY ENRICHMENT
    # --------------------------------------------------

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

    # Generate embedding
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

            # -------------------------
            # 2️⃣ BASE VECTOR SCORE
            # -------------------------
            vector_score = r.score

            # -------------------------
            # 3️⃣ METADATA BOOSTING
            # -------------------------
            topic_boost = 0.0
            keyword_boost = 0.0
            speaker_boost = 0.0

            payload_topic = payload.get("topic", "").lower()
            text = payload.get("text", "").lower()

            # Topic boost (small)
            for topic in router_topics:
                if topic.lower() in payload_topic:
                    topic_boost = 0.10

            # Keyword boost (very small per match)
            for keyword in router_keywords:
                if keyword.lower() in text:
                    keyword_boost += 0.05

            # Cap keyword boost (prevents domination)
            keyword_boost = min(keyword_boost, 0.15)

            # Speaker boost (tiny)
            if payload.get("speaker") == "Meher Baba":
                speaker_boost = 0.05

            # -------------------------
            # 4️⃣ FINAL HYBRID SCORE
            # -------------------------
            final_score = (
                0.8 * vector_score
                + topic_boost
                + keyword_boost
                + speaker_boost
            )

            # Debug print
            print("--------------------------------------------------")
            print("Vector Score:", round(vector_score, 4))
            print("Topic Boost:", topic_boost)
            print("Keyword Boost:", keyword_boost)
            print("Speaker Boost:", speaker_boost)
            print("Final Score:", round(final_score, 4))
            print("Chunk ID:", payload.get("chunk_id"))
            print("Preview:", payload.get("text", "")[:200], "...")
            print("--------------------------------------------------\n")

            ranked.append((final_score, payload))

        # Sort by final score
        ranked.sort(key=lambda x: x[0], reverse=True)

        print("\n🏆 FINAL TOP RANKED CHUNKS:")
        for i, (score, payload) in enumerate(ranked[:top_k], 1):
            print(f"{i}. {payload.get('chunk_id')} | Score: {round(score, 4)}")

        return [payload for _, payload in ranked[:top_k]]

    except Exception as e:
        print("⚠️ Vector search failed, using keyword fallback:", e)
        return keyword_fallback(book, query, limit=top_k)
