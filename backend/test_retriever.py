from app.retrieval.retriever import retrieve

question = "what is suffering"

results = retrieve(
    book="Life Eternal",
    query=question,
    top_k=5
)

print(f"Retrieved {len(results)} chunks\n")

for i, r in enumerate(results, start=1):
    print("=" * 50)
    print(f"Result {i}")
    print("Topic:", r.get("topic"))
    print("Chunk ID:", r.get("chunk_id"))
    print("Text:\n", r.get("text")[:500])
