import json
import os
from pathlib import Path
from typing import Dict, List


# =============================
# CONFIG
# =============================
RAW_CHUNKS_DIR = "/home/coffeee/Desktop/project/Anuvada_AI/backend/data/god_chunks"
OUTPUT_FILE = "/home/coffeee/Desktop/project/Anuvada_AI/backend/data/normalized/god_speaks_normalized_chunks.json"


# =============================
# NORMALIZATION LOGIC
# =============================
def normalize_god_speaks_chunk(raw: Dict) -> Dict:
    """
    Convert a raw God Speaks chunk into canonical format.
    """

    # ---- Mandatory text check ----
    if "text" not in raw or not isinstance(raw["text"], str) or not raw["text"].strip():
        raise ValueError(f"Chunk {raw.get('id')} has missing or empty 'text'")

    # ---- Determine chunk type ----
    if raw.get("chapter") == "Supplement" or "supplement" in raw.get("id", "").lower():
        chunk_type = "supplement"
        sub_topic = raw.get("topic", "Supplement")
        part = None

    elif "section" in raw:
        chunk_type = "section"
        sub_topic = raw["section"]
        part = raw.get("part")

    else:
        chunk_type = "full"
        sub_topic = "Complete Chapter"
        part = raw.get("part")

    # ---- Canonical structure ----
    canonical = {
        "id": raw.get("id"),
        "book": "God Speaks",
        "part": part,
        "chapter": raw.get("chapter", "Unknown"),
        "sub_topic": sub_topic,
        "chunk_type": chunk_type,
        "text": raw["text"].strip(),
        "page_range": raw.get("page_range")
    }

    return canonical


# =============================
# VALIDATION
# =============================
def validate_chunk(chunk: Dict):
    required_fields = [
        "id",
        "book",
        "chapter",
        "sub_topic",
        "chunk_type",
        "text"
    ]

    for field in required_fields:
        if field not in chunk or not chunk[field]:
            raise ValueError(
                f"Missing required field '{field}' in chunk {chunk.get('id')}"
            )

    if chunk["chunk_type"] not in {"full", "section", "supplement"}:
        raise ValueError(
            f"Invalid chunk_type '{chunk['chunk_type']}' in chunk {chunk['id']}"
        )


# =============================
# FILE LOADING WITH DEBUG
# =============================
def load_raw_chunks(directory: str) -> List[Dict]:
    chunks = []

    if not os.path.exists(directory):
        raise FileNotFoundError(f"Raw chunks directory does not exist: {directory}")

    for file in Path(directory).glob("*.json"):
        print(f"\n📂 Reading file: {file}")

        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print("\n❌ JSONDecodeError")
            print("👉 File:", file)
            print("👉 Error:", e)
            print("⚠️ Fix this file before continuing.\n")
            raise

        if not isinstance(data, list):
            raise ValueError(f"❌ File {file} does not contain a LIST of chunks")

        print(f"✅ Loaded {len(data)} chunks from {file}")
        chunks.extend(data)

    print(f"\n📦 Total raw chunks loaded: {len(chunks)}")
    return chunks


# =============================
# NORMALIZE ALL WITH DEBUG
# =============================
def normalize_all_chunks(raw_chunks: List[Dict]) -> List[Dict]:
    normalized = []

    for idx, raw in enumerate(raw_chunks):
        chunk_id = raw.get("id", f"UNKNOWN_ID_{idx}")

        print(f"🔄 Normalizing chunk {idx + 1}/{len(raw_chunks)} → {chunk_id}")

        try:
            canonical = normalize_god_speaks_chunk(raw)
            validate_chunk(canonical)
        except Exception as e:
            print("\n❌ ERROR DURING NORMALIZATION")
            print("👉 Chunk index:", idx)
            print("👉 Chunk ID:", chunk_id)
            print("👉 Raw chunk data:")
            print(json.dumps(raw, indent=2, ensure_ascii=False))
            print("👉 Error:", e)
            raise

        normalized.append(canonical)

    return normalized


# =============================
# SAVE OUTPUT
# =============================
def save_normalized_chunks(chunks: List[Dict], output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved normalized chunks to:\n   {output_path}")


# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    print("\n🚀 Starting God Speaks chunk normalization")

    raw_chunks = load_raw_chunks(RAW_CHUNKS_DIR)

    print(f"\n🔧 Normalizing {len(raw_chunks)} chunks...")
    normalized_chunks = normalize_all_chunks(raw_chunks)

    save_normalized_chunks(normalized_chunks, OUTPUT_FILE)

    print(f"\n✅ DONE — {len(normalized_chunks)} chunks normalized successfully")
