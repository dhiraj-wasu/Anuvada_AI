import json
import os
from typing import Dict, List


# =============================
# CONFIG
# =============================
INPUT_FILE = (
    "/home/coffeee/Desktop/project/Anuvada_AI/backend/data/life_eternal_topic_chunks.json"
)

OUTPUT_FILE = (
    "/home/coffeee/Desktop/project/Anuvada_AI/backend/data/normalized/"
    "life_eternal_normalized_chunks.json"
)


# =============================
# NORMALIZATION
# =============================
def normalize_life_eternal_chunk(raw: Dict) -> Dict:
    # ---- Mandatory checks ----
    if "text" not in raw or not raw["text"].strip():
        raise ValueError(f"Missing text in chunk {raw.get('id')}")

    if "topic" not in raw or not raw["topic"].strip():
        raise ValueError(f"Missing topic in chunk {raw.get('id')}")

    # ---- Canonical structure ----
    canonical = {
        "id": raw["id"],
        "book": "Life Eternal",
        "topic": raw["topic"],
        "sub_topic": raw.get("sub_topic", raw["topic"]),
        "chunk_type": "topic_section",
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
        "topic",
        "sub_topic",
        "chunk_type",
        "text"
    ]

    for field in required_fields:
        if field not in chunk or not chunk[field]:
            raise ValueError(
                f"Missing required field '{field}' in chunk {chunk.get('id')}"
            )


# =============================
# PIPELINE
# =============================
def load_raw_chunks(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Life Eternal raw file must contain a list")

    print(f"📥 Loaded {len(data)} raw Life Eternal chunks")
    return data


def normalize_all_chunks(raw_chunks: List[Dict]) -> List[Dict]:
    normalized = []

    for idx, raw in enumerate(raw_chunks, start=1):
        chunk_id = raw.get("id", f"UNKNOWN_{idx}")
        print(f"🔄 Normalizing [{idx}/{len(raw_chunks)}] → {chunk_id}")

        canonical = normalize_life_eternal_chunk(raw)
        validate_chunk(canonical)
        normalized.append(canonical)

    return normalized


def save_normalized_chunks(chunks: List[Dict], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved normalized Life Eternal chunks to:\n   {path}")


# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    print("\n🚀 Starting Life Eternal normalization")

    raw_chunks = load_raw_chunks(INPUT_FILE)
    normalized_chunks = normalize_all_chunks(raw_chunks)
    save_normalized_chunks(normalized_chunks, OUTPUT_FILE)

    print(f"\n✅ DONE — {len(normalized_chunks)} Life Eternal chunks normalized")
