import json
import uuid
from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer

# =============================
# CONFIG
# =============================
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

COLLECTION_NAME = "life_eternal_collection"

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

INPUT_FILE = (
    "/home/coffeee/Desktop/project/Anuvada_AI/backend/data/normalized/life_eternal_normalized_chunks.json"
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
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "chunk_id": chunk["id"],
                    "book": chunk["book"],
                    "part": chunk["part"],
                    "chapter": chunk["chapter"],
                    "sub_topic": chunk["sub_topic"],
                    "chunk_type": chunk["chunk_type"],
                    "page_range": chunk["page_range"],
                    "text": chunk["text"],
                    "speaker": "Meher Baba"  # 🔑 IMPORTANT for ranking
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
    print(f"📊 Stored vectors: {info.points_count}")
    print(f"📈 Indexed vectors: {info.indexed_vectors_count}")

# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    print("\n🚀 Starting God Speaks ingestion")

    chunks = load_chunks(INPUT_FILE)
    print(f"📥 Loaded {len(chunks)} chunks")

    ingest_chunks(chunks)
    verify_count(len(chunks))

    print("\n🎉 DONE — God Speaks ingestion complete")
