from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "life_eternal_collection"
VECTOR_SIZE = 384

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

if qdrant.collection_exists(COLLECTION_NAME):
    print("⚠️ Collection already exists")
else:
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
    print("✅ life_eternal_collection created")

