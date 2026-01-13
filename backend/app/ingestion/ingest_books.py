import json
import uuid
from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct
from sentence_transformers import SentenceTransformer


# =============================
# CONFIG
# =============================
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

COLLECTION_NAME = "god_speaks_collection"

# Local embedding model
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384

INPUT_FILE = (
    "/home/coffeee/Desktop/project/Anuvada_AI/backend/data/normalized/"
    "god_speaks_normalized_chunks.json"
)


# =============================
# LOAD MODEL & CLIENT
# =============================
print("🧠 Loading local embedding model...")
embedder = SentenceTransformer(EMBED_MODEL_NAME)

print("🗄️ Connecting to Qdrant...")
qdrant = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
    check_compatibility=False
)


# =============================
# HELPERS
# =============================
def load_chunks(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Normalized file must contain a list")

    return data


def embed_text(text: str) -> List[float]:
    return embedder.encode(text).tolist()


# =============================
# COLLECTION SETUP
# =============================
def reset_collection():
    if qdrant.collection_exists(COLLECTION_NAME):
        print("🗑️ Deleting existing collection")
        qdrant.delete_collection(COLLECTION_NAME)

    print("📦 Creating collection:", COLLECTION_NAME)
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance="Cosine"
        )
    )


# =============================
# INGESTION
# =============================
def ingest_chunks(chunks: List[Dict]):
    print(f"🔢 Ingesting {len(chunks)} chunks into Qdrant")

    points = []

    for idx, chunk in enumerate(chunks, start=1):
        print(f"➡️  [{idx}/{len(chunks)}] Embedding {chunk['id']}")

        vector = embed_text(chunk["text"])

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),   # ✅ Qdrant-compatible ID
                vector=vector,
                payload={
                    # Preserve original semantic ID
                    "chunk_id": chunk["id"],

                    "book": chunk["book"],
                    "part": chunk["part"],
                    "chapter": chunk["chapter"],
                    "sub_topic": chunk["sub_topic"],
                    "chunk_type": chunk["chunk_type"],
                    "page_range": chunk["page_range"],

                    # Keep text for quoting later
                    "text": chunk["text"]
                }
            )
        )

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(f"✅ Inserted {len(points)} chunks")


# =============================
# VERIFY
# =============================
def verify_count(expected: int):
    info = qdrant.get_collection(COLLECTION_NAME)
    stored = info.points_count

    print(f"📊 Qdrant contains {stored} vectors")

    if stored != expected:
        print("⚠️ WARNING: Vector count mismatch")
    else:
        print("✅ Vector count verified")


# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    print("\n🚀 Starting LOCAL God Speaks ingestion")

    chunks = load_chunks(INPUT_FILE)
    print(f"📥 Loaded {len(chunks)} normalized chunks")

    reset_collection()
    ingest_chunks(chunks)
    verify_count(len(chunks))

    print("\n🎉 DONE — God Speaks successfully ingested using LOCAL embeddings")
