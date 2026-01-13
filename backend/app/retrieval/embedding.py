from sentence_transformers import SentenceTransformer

# Load model once
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text: str) -> list[float]:
    """
    Generate embedding locally (no API, no quota).
    """
    return _model.encode(text, normalize_embeddings=True).tolist()
