import json
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
from openai import OpenAI
from app.config import *

client = OpenAI()
qdrant = QdrantClient(path=QDRANT_PATH)

def embed(text):
    return client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    ).data[0].embedding

def run():
    with open("data/chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)

    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=3072, distance="Cosine")
    )

    points = []
    for i, chunk in enumerate(chunks):
        points.append(
            PointStruct(
                id=i,
                vector=embed(chunk["text"]),
                payload=chunk
            )
        )

    qdrant.upsert(COLLECTION_NAME, points)

if __name__ == "__main__":
    run()
